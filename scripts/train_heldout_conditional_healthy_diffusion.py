"""Participant-held-out, source-conditioned DDPM for 500x3 healthy IMU gait windows.

This is an evidence experiment, not a mechanism for creating new participants.
The generator sees only MAREA/DUO-GAIT training participants.  It is judged against
unseen participants from each source before any classifier augmentation is allowed.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.signal import welch
from scipy.spatial.distance import cdist
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader, TensorDataset


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = int(os.getenv("RUN_SEED", "42"))
EPOCHS = int(os.getenv("EPOCHS", "100"))
TIMESTEPS = int(os.getenv("TIMESTEPS", "100"))
N_PER_SOURCE = int(os.getenv("N_PER_SOURCE", "400"))
HOLDOUT_FRACTION = float(os.getenv("HOLDOUT_FRACTION", "0.20"))
RNG = np.random.default_rng(SEED)
torch.manual_seed(SEED)
np.random.seed(SEED)


def window_conditions(x: np.ndarray) -> np.ndarray:
    """Per-channel log amplitude and dominant walking-band frequency, 6 values."""
    scale = np.log(np.std(x, axis=1).clip(1e-4, None))
    freq = np.fft.rfftfreq(x.shape[1], 1 / 100.0)
    power = np.abs(np.fft.rfft(x - x.mean(axis=1, keepdims=True), axis=1)) ** 2
    gait_band = (freq >= 0.35) & (freq <= 4.0)
    dominant = freq[gait_band][power[:, gait_band, :].argmax(axis=1)]
    return np.concatenate([scale, dominant], axis=1).astype("float32")


def split_people(meta: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    people = meta[["participant_key", "dataset_id"]].drop_duplicates().copy()
    held_out: set[str] = set()
    for _, group in people.groupby("dataset_id", sort=True):
        keys = group.participant_key.to_numpy().copy()
        RNG.shuffle(keys)
        n = max(1, int(round(len(keys) * HOLDOUT_FRACTION)))
        held_out.update(keys[:n])
    test = meta.participant_key.isin(held_out).to_numpy()
    return ~test, test


def cosine_schedule(steps: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    t = torch.linspace(0, steps, steps + 1, device=DEVICE) / steps
    alpha_bar = torch.cos(((t + 0.008) / 1.008) * math.pi / 2).pow(2)
    alpha_bar = alpha_bar / alpha_bar[0]
    beta = (1 - alpha_bar[1:] / alpha_bar[:-1]).clip(1e-5, 0.999)
    alpha = 1 - beta
    return beta, alpha, torch.cumprod(alpha, dim=0)


def time_embedding(t: torch.Tensor, width: int = 32) -> torch.Tensor:
    half = width // 2
    omega = torch.exp(torch.linspace(0, math.log(10_000), half, device=t.device) * -1)
    phase = t.float().unsqueeze(1) * omega.unsqueeze(0)
    return torch.cat([phase.sin(), phase.cos()], dim=1)


class ResidualBlock(torch.nn.Module):
    def __init__(self, channels: int, condition_width: int):
        super().__init__()
        self.norm1 = torch.nn.GroupNorm(8, channels)
        self.conv1 = torch.nn.Conv1d(channels, channels, 5, padding=2)
        self.norm2 = torch.nn.GroupNorm(8, channels)
        self.conv2 = torch.nn.Conv1d(channels, channels, 5, padding=2)
        self.film = torch.nn.Linear(condition_width, channels * 2)

    def forward(self, x: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        scale, shift = self.film(c).chunk(2, dim=1)
        h = self.norm1(x) * (1 + scale.unsqueeze(-1)) + shift.unsqueeze(-1)
        h = self.conv1(torch.nn.functional.gelu(h))
        h = self.conv2(torch.nn.functional.gelu(self.norm2(h)))
        return x + h


class MultiResolutionDenoiser(torch.nn.Module):
    """A small U-Net: coarse gait trajectory plus fine 100-Hz residual structure."""
    def __init__(self):
        super().__init__()
        self.source = torch.nn.Embedding(2, 16)
        self.condition = torch.nn.Sequential(torch.nn.Linear(32 + 6 + 16, 96), torch.nn.GELU(), torch.nn.Linear(96, 96))
        self.inp = torch.nn.Conv1d(3, 48, 5, padding=2)
        self.high = ResidualBlock(48, 96)
        self.down = torch.nn.Conv1d(48, 96, 4, stride=2, padding=1)
        self.low1 = ResidualBlock(96, 96)
        self.low2 = ResidualBlock(96, 96)
        self.up = torch.nn.ConvTranspose1d(96, 48, 4, stride=2, padding=1)
        self.out_block = ResidualBlock(48, 96)
        self.out = torch.nn.Conv1d(48, 3, 5, padding=2)

    def forward(self, x: torch.Tensor, t: torch.Tensor, source: torch.Tensor, condition: torch.Tensor) -> torch.Tensor:
        c = self.condition(torch.cat([time_embedding(t), condition, self.source(source)], dim=1))
        h = self.high(self.inp(x), c)
        low = self.low2(self.low1(self.down(h), c), c)
        h = self.up(low) + h
        return self.out(self.out_block(h, c))


def sample(model: torch.nn.Module, source: int, condition: np.ndarray, beta: torch.Tensor, alpha: torch.Tensor, alpha_bar: torch.Tensor) -> np.ndarray:
    n = len(condition)
    x = torch.randn(n, 3, 500, device=DEVICE)
    s = torch.full((n,), source, dtype=torch.long, device=DEVICE)
    c = torch.from_numpy(condition).to(DEVICE)
    model.eval()
    with torch.no_grad():
        for step in range(TIMESTEPS - 1, -1, -1):
            ts = torch.full((n,), step, dtype=torch.long, device=DEVICE)
            noise = model(x, ts, s, c)
            mean = (x - beta[step] / (1 - alpha_bar[step]).sqrt() * noise) / alpha[step].sqrt()
            if step:
                posterior_variance = beta[step] * (1 - alpha_bar[step - 1]) / (1 - alpha_bar[step])
                x = mean + posterior_variance.sqrt() * torch.randn_like(x)
            else:
                x = mean
    return x.transpose(1, 2).cpu().numpy()


def roughness(x: np.ndarray) -> float:
    return float(np.mean(np.abs(np.diff(x, axis=1))))


def psd_vector(x: np.ndarray) -> np.ndarray:
    return welch(x, fs=100, nperseg=128, axis=1)[1].mean(axis=0).ravel()


def feature_rows(x: np.ndarray) -> np.ndarray:
    # Compact global/temporal/spectral signatures for an explicit distinguishability test.
    means = x.mean(axis=1)
    stds = x.std(axis=1)
    diffs = np.abs(np.diff(x, axis=1)).mean(axis=1)
    corr = np.array([np.corrcoef(v.T)[np.triu_indices(3, 1)] for v in x])
    psd = welch(x, fs=100, nperseg=128, axis=1)[1]
    bands = np.stack([psd[:, (np.fft.rfftfreq(128, .01) >= a) & (np.fft.rfftfreq(128, .01) < b), :].mean(axis=1) for a, b in ((.35, 1), (1, 2), (2, 4), (4, 10))], axis=1).reshape(len(x), -1)
    return np.concatenate([means, stds, diffs, corr, bands], axis=1)


def discriminator_auc(real: np.ndarray, synthetic: np.ndarray) -> float:
    n = min(len(real), len(synthetic), 300)
    x = np.concatenate([feature_rows(real[:n]), feature_rows(synthetic[:n])])
    y = np.r_[np.ones(n), np.zeros(n)]
    folds = StratifiedKFold(5, shuffle=True, random_state=SEED)
    p = np.zeros(len(y))
    for tr, va in folds.split(x, y):
        clf = LogisticRegression(max_iter=1000, C=0.2)
        clf.fit(x[tr], y[tr])
        p[va] = clf.predict_proba(x[va])[:, 1]
    return float(roc_auc_score(y, p))


def assess(real: np.ndarray, synthetic: np.ndarray, source_name: str) -> dict[str, float | str | bool]:
    real_sample = real[RNG.choice(len(real), min(300, len(real)), replace=False)]
    syn_sample = synthetic[RNG.choice(len(synthetic), min(300, len(synthetic)), replace=False)]
    real_psd, syn_psd = psd_vector(real_sample), psd_vector(syn_sample)
    psd_l1 = float(np.abs(real_psd - syn_psd).sum() / (np.abs(real_psd).sum() + 1e-8))
    real_corr = np.corrcoef(real_sample.reshape(-1, 3).T)[np.triu_indices(3, 1)]
    syn_corr = np.corrcoef(syn_sample.reshape(-1, 3).T)[np.triu_indices(3, 1)]
    flat_r = real_sample.reshape(len(real_sample), -1)
    half = len(flat_r) // 2
    real_nn = cdist(flat_r[:half], flat_r[half:]).min(axis=1).mean()
    syn_nn = cdist(syn_sample.reshape(len(syn_sample), -1), flat_r).min(axis=1).mean()
    std_ratio = float(syn_sample.std() / (real_sample.std() + 1e-8))
    rough_ratio = roughness(syn_sample) / (roughness(real_sample) + 1e-8)
    auc = discriminator_auc(real_sample, syn_sample)
    # Predeclared research screen; passing it does not confer clinical validity.
    passed = bool(0.85 <= std_ratio <= 1.15 and 0.85 <= rough_ratio <= 1.15 and psd_l1 <= 0.20 and np.abs(real_corr - syn_corr).mean() <= 0.10 and syn_nn / real_nn <= 1.20 and auc <= 0.70)
    return {"source": source_name, "heldout_real_windows": len(real), "synthetic_windows": len(synthetic), "std_ratio": std_ratio, "roughness_ratio": rough_ratio, "psd_relative_l1": psd_l1, "cross_channel_corr_mae": float(np.abs(real_corr - syn_corr).mean()), "synthetic_to_real_nn_ratio": float(syn_nn / real_nn), "real_vs_synthetic_feature_auc": auc, "all_fidelity_gates_pass": passed}


def main() -> None:
    x = np.load(PROCESSED / "tier1_healthy_marea_duogait_windows_float32.npy")
    meta = pd.read_csv(PROCESSED / "tier1_healthy_marea_duogait_window_metadata.csv")
    keep = meta.dataset_id.isin(["marea_2017", "duogait_2023"]).to_numpy()
    x, meta = x[keep].astype("float32"), meta.loc[keep].reset_index(drop=True)
    train, test = split_people(meta)
    mu = x[train].mean(axis=(0, 1))
    sd = x[train].std(axis=(0, 1)).clip(1e-4)
    z = ((x - mu) / sd).transpose(0, 2, 1).astype("float32")
    conditions = window_conditions(x)
    cm, cs = conditions[train].mean(axis=0), conditions[train].std(axis=0).clip(1e-4)
    cz = ((conditions - cm) / cs).astype("float32")
    source = meta.dataset_id.map({"marea_2017": 0, "duogait_2023": 1}).astype("int64").to_numpy()
    loader = DataLoader(TensorDataset(torch.from_numpy(z[train]), torch.from_numpy(source[train]), torch.from_numpy(cz[train])), batch_size=128, shuffle=True, pin_memory=DEVICE.type == "cuda")
    model = MultiResolutionDenoiser().to(DEVICE)
    optimiser = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
    beta, alpha, alpha_bar = cosine_schedule(TIMESTEPS)
    for epoch in range(1, EPOCHS + 1):
        model.train()
        losses = []
        for xb, sb, cb in loader:
            xb, sb, cb = xb.to(DEVICE), sb.to(DEVICE), cb.to(DEVICE)
            t = torch.randint(0, TIMESTEPS, (len(xb),), device=DEVICE)
            eps = torch.randn_like(xb)
            noisy = alpha_bar[t, None, None].sqrt() * xb + (1 - alpha_bar[t, None, None]).sqrt() * eps
            loss = torch.nn.functional.mse_loss(model(noisy, t, sb, cb), eps)
            optimiser.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            losses.append(float(loss.detach()))
        if epoch % 20 == 0 or epoch == 1:
            print(f"epoch={epoch} loss={np.mean(losses):.5f}", flush=True)

    all_synthetic, all_metadata, rows = [], [], []
    for source_id, source_name in enumerate(("marea_2017", "duogait_2023")):
        candidates = np.flatnonzero(train & (source == source_id))
        selected = RNG.choice(candidates, N_PER_SOURCE, replace=len(candidates) < N_PER_SOURCE)
        generated_z = sample(model, source_id, cz[selected], beta, alpha, alpha_bar)
        generated = (generated_z * sd + mu).astype("float32")
        heldout = x[test & (source == source_id)]
        rows.append(assess(heldout, generated, source_name))
        all_synthetic.append(generated)
        all_metadata.extend({"dataset_condition": source_name, "synthetic": True, "parent_participant": None, "generation_role": "heldout_subject_fidelity_experiment_only"} for _ in generated)
    output = np.concatenate(all_synthetic)
    report = pd.DataFrame(rows)
    np.save(PROCESSED / "healthy_window_ddpm_v2_heldout_synthetic_500x3_float32.npy", output)
    pd.DataFrame(all_metadata).to_csv(PROCESSED / "healthy_window_ddpm_v2_heldout_synthetic_metadata.csv", index=False)
    report.to_csv(PROCESSED / "healthy_window_ddpm_v2_heldout_fidelity.csv", index=False)
    torch.save({"state_dict": model.state_dict(), "mean": mu, "std": sd, "condition_mean": cm, "condition_std": cs, "train_participants": sorted(meta.loc[train, "participant_key"].unique()), "heldout_participants": sorted(meta.loc[test, "participant_key"].unique()), "contract": "500x3 acceleration magnitude; source-conditioned; participant-held-out fidelity experiment", "timesteps": TIMESTEPS, "device": str(DEVICE)}, PROCESSED / "healthy_window_ddpm_v2_heldout.pt")
    (PROCESSED / "healthy_window_ddpm_v2_heldout_split.json").write_text(json.dumps({"seed": SEED, "holdout_fraction": HOLDOUT_FRACTION, "train_participants": sorted(meta.loc[train, "participant_key"].unique()), "heldout_participants": sorted(meta.loc[test, "participant_key"].unique())}, indent=2))
    print(report.to_string(index=False))
    print(f"device={DEVICE}; train_people={meta.loc[train, 'participant_key'].nunique()}; heldout_people={meta.loc[test, 'participant_key'].nunique()}")


if __name__ == "__main__":
    main()
