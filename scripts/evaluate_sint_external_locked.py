"""Locked participant-level evaluation of Sint Maartenskliniek."""
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score, brier_score_loss, balanced_accuracy_score
import joblib

R = Path(__file__).resolve().parents[1]
P = R / "data/processed"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class InceptionBlock(torch.nn.Module):
    def __init__(self, in_ch, out_ch=16):
        super().__init__()
        bottleneck = min(32, in_ch)
        self.bottleneck = torch.nn.Conv1d(in_ch, bottleneck, 1, bias=False)
        self.branches = torch.nn.ModuleList([torch.nn.Conv1d(bottleneck, out_ch, 7, padding=3, bias=False), torch.nn.Conv1d(bottleneck, out_ch, 15, padding=7, bias=False), torch.nn.Conv1d(bottleneck, out_ch, 25, padding=12, bias=False)])
        self.pool_branch = torch.nn.Conv1d(in_ch, out_ch, 1, bias=False)
        self.bn = torch.nn.BatchNorm1d(out_ch * 4)
        self.residual = torch.nn.Conv1d(in_ch, out_ch * 4, 1, bias=False) if in_ch != out_ch * 4 else torch.nn.Identity()
    def forward(self, x):
        z = self.bottleneck(x); branches = [branch(z) for branch in self.branches]
        branches.append(self.pool_branch(torch.nn.functional.max_pool1d(x, 3, stride=1, padding=1)))
        return torch.nn.functional.gelu(self.bn(torch.cat(branches, dim=1)) + self.residual(x))


class InceptionCNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.features = torch.nn.Sequential(InceptionBlock(3), torch.nn.MaxPool1d(2), InceptionBlock(64), torch.nn.AdaptiveAvgPool1d(1))
        self.classifier = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Dropout(0.30), torch.nn.Linear(64, 1))
    def forward(self, x): return self.classifier(self.features(x)).squeeze(1)


def metrics(frame, prob):
    g = frame.assign(prob=prob).groupby(["participant_key", "label_binary"], as_index=False).prob.mean()
    y, p = g.label_binary.to_numpy(), g.prob.to_numpy()
    return g, {"participants": len(g), "healthy": int((y == 0).sum()), "stroke": int((y == 1).sum()), "auroc": roc_auc_score(y, p), "brier": brier_score_loss(y, p), "balanced_accuracy_at_0.5": balanced_accuracy_score(y, p >= .5)}


def main():
    x = np.load(P / "sint_maartenskliniek_external_windows_float32.npy")
    m = pd.read_csv(P / "sint_maartenskliniek_external_window_metadata.csv")
    inception_probs, rocket_probs = [], []
    for fold in range(5):
        ck = torch.load(P / f"inception_source_class_balanced_global_fold_{fold}_seed_42.pt", map_location="cpu", weights_only=False)
        model = InceptionCNN(); model.load_state_dict(ck["model_state_dict"]); model.to(DEVICE).eval()
        mean, std = np.asarray(ck["mean"], dtype=np.float32), np.asarray(ck["std"], dtype=np.float32)
        z = torch.from_numpy(((x - mean) / np.maximum(std, 1e-6)).transpose(0, 2, 1).astype("float32"))
        with torch.no_grad():
            p = torch.sigmoid(model(z.to(DEVICE))).cpu().numpy()
        inception_probs.append(p)
        art = joblib.load(P / f"minirocket_ridge_fold_{fold}_seed_42_calibrated.joblib")
        rz = ((x - np.asarray(art["mean"])) / np.maximum(np.asarray(art["std"]), 1e-6)).transpose(0, 2, 1)
        feat = art["transformer"].transform(rz)
        raw = art["classifier"].decision_function(feat).reshape(-1, 1)
        rocket_probs.append(art["calibrator"].predict_proba(raw)[:, 1])
    for name, probs in [("inception", np.mean(inception_probs, 0)), ("minirocket", np.mean(rocket_probs, 0))]:
        participant, summary = metrics(m, probs)
        participant.to_csv(P / f"sint_{name}_external_participant_predictions.csv", index=False)
        print(name, summary)
        pd.DataFrame([summary | {"model": name}]).to_csv(P / f"sint_{name}_external_metrics.csv", index=False)


if __name__ == "__main__": main()
