---
theme: seriph
layout: default
highlighter: shiki
lineNumbers: false
transition: slide-left
title: Wearable-IMU Experiments — 27 August to Present
aspectRatio: '16/9'
canvasWidth: 980
colorSchema: 'dark'
style: |
  .slidev-layout {
    background-color: #0b0f19 !important;
    color: #f1f5f9 !important;
    padding: 2.0rem 2.8rem !important;
    font-size: 0.82rem !important;
    line-height: 1.45 !important;
    position: relative !important;
    overflow: hidden !important;
  }
  h1 { font-size: 1.75rem !important; line-height: 1.08 !important; font-weight: 700 !important; color: #ffffff !important; margin-bottom: 0.3rem !important; overflow-wrap: anywhere; }
  h2 { font-size: 1.15rem !important; font-weight: 600 !important; color: #38bdf8 !important; margin-bottom: 0.35rem !important; }
  h3 { font-size: 0.95rem !important; font-weight: 600 !important; color: #7dd3fc !important; margin-bottom: 0.2rem !important; }
  
  /* High-Contrast Card Backgrounds & Borders */
  .bg-slate-800\/40, .bg-slate-800\/50, .bg-slate-800\/60, .bg-slate-800\/70, .bg-slate-800\/80, .bg-slate-800 {
    background-color: #161e2e !important;
    border: 1px solid #334155 !important;
  }
  
  /* Text Brightness */
  .text-slate-200, .text-slate-300 { color: #f8fafc !important; }
  .text-slate-400 { color: #cbd5e1 !important; }
  .text-slate-500 { color: #94a3b8 !important; }
  .text-amber-300, .text-amber-400 { color: #fbbf24 !important; }
  .text-rose-300, .text-rose-400 { color: #f87171 !important; }
  .text-emerald-300, .text-emerald-400 { color: #34d399 !important; }
  .text-sky-300, .text-sky-400 { color: #38bdf8 !important; }
  .text-violet-300, .text-violet-400 { color: #a78bfa !important; }

  /* Tables in Dark Mode */
  .slidev-layout p, .slidev-layout li { white-space: normal !important; overflow-wrap: break-word; }
  table { font-size: 11px !important; width: 100% !important; margin: 0.35rem 0 !important; border-collapse: collapse !important; }
  th { background: #1e293b !important; color: #f8fafc !important; font-weight: 700 !important; border-bottom: 2px solid #475569 !important; padding: 5px 8px !important; }
  td { padding: 4px 8px !important; border-bottom: 1px solid #1e293b !important; color: #e2e8f0 !important; }
  tr:nth-child(even) td { background: #0f172a !important; }
  
  .source-footer { position: absolute !important; bottom: 10px !important; left: 48px !important; right: 48px !important; width: auto !important; max-width: calc(100% - 96px) !important; font-size: 9px !important; line-height: 1.2 !important; overflow-wrap: anywhere; word-break: break-word; opacity: 0.75; border-top: 1px solid #334155; padding-top: 4px; color: #94a3b8; }

  /* Pill badges (restored — required across every slide) */
  .pill { display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 0.65rem; font-weight: 700; border: 1px solid; white-space: nowrap; }
  .pill-sky  { background: rgba(14,165,233,0.18);  color: #7dd3fc; border-color: rgba(56,189,248,0.45); }
  .pill-grn  { background: rgba(16,185,129,0.18);  color: #6ee7b7; border-color: rgba(52,211,153,0.45); }
  .pill-prp  { background: rgba(139,92,246,0.18);  color: #c4b5fd; border-color: rgba(167,139,250,0.45); }
  .pill-amb  { background: rgba(245,158,11,0.18);  color: #fcd34d; border-color: rgba(251,191,36,0.45); }
  .pill-red  { background: rgba(239,68,68,0.18);   color: #fca5a5; border-color: rgba(248,113,113,0.45); }
  .pill-gray { background: rgba(100,116,139,0.18); color: #cbd5e1; border-color: rgba(148,163,184,0.4); }

  /* Compact overflow-safe helpers for dense sprint slides */
  .slidev-layout .tiny-table table, .slidev-layout table.tiny-table { table-layout: fixed !important; font-size: 9px !important; }
  .slidev-layout .tiny-table th, .slidev-layout .tiny-table td, .slidev-layout table.tiny-table th, .slidev-layout table.tiny-table td { font-size: inherit !important; padding: 2px 4px !important; line-height: 1.15 !important; white-space: normal !important; overflow-wrap: anywhere !important; word-break: break-word; }
  .card { border-radius: 0.75rem; border: 1px solid #334155; background: #161e2e; padding: 0.7rem 0.85rem; }
---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 1 — Section Divider: Sprint Update
      ──────────────────────────────────────────────────────── -->
<div class="flex h-full flex-col items-center justify-center text-center">

<span class="pill pill-amb">Sprint Update</span>

# Week 2 — 27 August to 4 September

<p class="text-slate-300 text-sm mt-2 max-w-2xl">Eighteen executed experiments re-tested the lower-back-first research question, probed data enrichment, synthetic generation, representation choice, and model architecture — under the same participant-disjoint, source-held-out, frozen-external discipline as Week 1.</p>

<div class="grid grid-cols-4 gap-3 mt-8 max-w-3xl">
  <div class="card text-center"><div class="text-xl font-bold text-emerald-400">1</div><div class="text-[10px] text-slate-400 mt-1">Model improvement<br>admitted</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-rose-400">11+</div><div class="text-[10px] text-slate-400 mt-1">Enrichment / rescue<br>experiments rejected</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-sky-400">34</div><div class="text-[10px] text-slate-400 mt-1">Notebooks executed<br>to date</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-amber-400">114.75 GiB</div><div class="text-[10px] text-slate-400 mt-1">Redundant storage<br>reclaimed</div></div>
</div>

<div class="source-footer">Source: reports/PROGRESS_REPORT_WEEK_01_2026-08-27.md · wiki/log.md · reports/MODEL_IMPROVEMENT_GATE_2026-09-03.md · reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md</div>
</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 2 — Executive Summary of New Work
      ──────────────────────────────────────────────────────── -->

# What Changed This Sprint

<div class="grid grid-cols-4 gap-2.5 my-3">
  <div class="card text-center"><div class="text-xl font-bold text-emerald-400">0.8882</div><div class="text-[10px] text-slate-400 mt-0.5">New incumbent AUROC</div><div class="text-[9px] text-slate-500">Lower-back ensemble</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-rose-400">0.757</div><div class="text-[10px] text-slate-400 mt-0.5">Lower-back-only external</div><div class="text-[9px] text-slate-500">Failed RevalExo gate</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-amber-400">52.2%</div><div class="text-[10px] text-slate-400 mt-0.5">Non-stroke false-positive rate</div><div class="text-[9px] text-slate-500">138 hard negatives, 0.50 cutoff</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-sky-400">93.1%</div><div class="text-[10px] text-slate-400 mt-0.5">NONAN healthy specificity</div><div class="text-[9px] text-slate-500">29 frozen participants</div></div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div class="card" style="border-color:rgba(52,211,153,0.4)">
    <h3 class="text-emerald-400">✅ What was admitted</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>A fixed equal-probability <strong>ERM + Deep CORAL + ERM++ ensemble</strong> on lower-back acceleration — passed every non-inferiority and material-gain gate</li>
      <li>A rigorous <strong>test-set credibility audit</strong> quantifying exactly how much more paired data is required</li>
      <li>A formal <strong>cross-dataset evidence gate</strong> that now governs every future enrichment attempt</li>
    </ul>
  </div>
  <div class="card" style="border-color:rgba(248,113,113,0.4)">
    <h3 class="text-rose-400">🚫 What was rejected</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>Lower-back-only as a replacement prototype (failed external gate)</li>
      <li>MAREA/DUO-GAIT/NONAN healthy-pool enrichment (domain-shift false positives)</li>
      <li>Six synthetic-data generators (interpolation, recombination, VAE ×2, diffusion)</li>
      <li>Signed-axis representation, pooled gyroscope, MiniROCKET fusion, MIL, canonical architecture swaps</li>
    </ul>
  </div>
</div>

<div class="source-footer">Source: reports/MODEL_IMPROVEMENT_GATE_2026-09-03.md · reports/LOWER_BACK_ONLY_EXTERNAL_BENCHMARK.md · reports/VOISARD_NONSTROKE_HARD_NEGATIVE_EVALUATION_2026-09-01.md · wiki/log.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 3 — Lower-Back-First Direction: Internal + External
      ──────────────────────────────────────────────────────── -->

# The Lower-Back-First Research Question

<p class="text-slate-300 text-xs -mt-1">A single lumbar sensor is the more deployable prototype. It was tested as a candidate primary model under the same folds as the 3-channel comparator.</p>

<div class="grid grid-cols-2 gap-4 my-2">
  <div>
    <h2>Internal 5-Fold (matched protocol)</h2>
    <table>
      <thead><tr><th>Model</th><th>AUROC</th><th>Brier</th><th>Bal. Acc.</th></tr></thead>
      <tbody>
        <tr><td><span class="pill pill-prp">3-channel LB/LF/RF</span></td><td class="text-emerald-300 font-bold">0.966</td><td class="text-emerald-300 font-bold">0.074</td><td class="text-emerald-300 font-bold">0.926</td></tr>
        <tr><td><span class="pill pill-sky">Lower-back only</span></td><td>0.933</td><td>0.121</td><td>0.829</td></tr>
      </tbody>
    </table>
    <p class="text-[10px] text-slate-400 mt-1">Lower-back-only trails by 0.033 AUROC and 0.096 balanced accuracy — a credible single-sensor baseline, not yet equivalent.</p>
  </div>
  <div>
    <h2>Frozen RevalExo Gate (n=17)</h2>
    <table>
      <thead><tr><th>Model</th><th>AUROC</th><th>Brier</th><th>Bal. Acc.</th></tr></thead>
      <tbody>
        <tr><td><span class="pill pill-prp">3-channel comparator</span></td><td class="text-emerald-300 font-bold">0.914</td><td class="text-emerald-300 font-bold">0.161</td><td class="text-emerald-300 font-bold">0.714</td></tr>
        <tr><td><span class="pill pill-red">Lower-back only</span></td><td class="text-rose-400">0.757</td><td class="text-rose-400">0.217</td><td class="text-rose-400">0.571</td></tr>
      </tbody>
    </table>
    <div class="card mt-2" style="border-color:rgba(248,113,113,0.4)"><p class="text-[11px] text-rose-300">🚫 <strong>Lower-back-only fails the external robustness gate.</strong> Decision: retain it as a transparent single-sensor comparator, not the final prototype.</p></div>
  </div>
</div>

<div class="source-footer">Source: reports/LOWER_BACK_VS_THREE_CHANNEL_BENCHMARK.md · reports/LOWER_BACK_ONLY_EXTERNAL_BENCHMARK.md · reports/LOWER_BACK_CHANNEL_FAILURE_ANALYSIS.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 4 — Healthy-Pool Enrichment Attempts
      ──────────────────────────────────────────────────────── -->

# Healthy-Pool Enrichment — Rejected

<div class="grid grid-cols-2 gap-4 my-2">
  <div>
    <h2>Tier-1 MAREA + DUO-GAIT Enrichment</h2>
    <p class="text-xs text-slate-300">5,938 adapted healthy windows from 36 participants (MAREA 3,526 · DUO-GAIT 2,412) were added to training, matched units and resampling verified first.</p>
    <table class="mt-2">
      <thead><tr><th>Frozen RevalExo</th><th>Baseline</th><th>Enriched</th></tr></thead>
      <tbody>
        <tr><td>AUROC</td><td>0.914</td><td class="text-emerald-300">0.929 ↑</td></tr>
        <tr><td>Brier</td><td class="text-emerald-300">0.161</td><td class="text-rose-400">0.177 ↓</td></tr>
        <tr><td>Balanced accuracy</td><td class="text-emerald-300">0.714</td><td class="text-rose-400">0.571 ↓</td></tr>
        <tr><td>Healthy FP</td><td class="text-emerald-300">4/7</td><td class="text-rose-400">6/7 ↓</td></tr>
      </tbody>
    </table>
  </div>
  <div>
    <h2>Root-Cause Diagnosis</h2>
    <div class="card"><p class="text-xs text-slate-300">MAREA lower-back magnitude (1.059) is measurably higher than every existing healthy source, despite verified unit conversion and resampling.</p>
    <table class="mt-2 tiny-table">
      <thead><tr><th>Source</th><th>LB mean</th><th>LF mean</th><th>RF mean</th></tr></thead>
      <tbody>
        <tr><td>Felius</td><td>1.023</td><td>1.740</td><td>1.790</td></tr>
        <tr><td>Voisard</td><td>1.030</td><td>1.535</td><td>1.586</td></tr>
        <tr><td>DUO-GAIT</td><td>1.032</td><td>1.649</td><td>1.704</td></tr>
        <tr><td class="text-amber-300">MAREA</td><td class="text-amber-300">1.059</td><td class="text-amber-300">1.615</td><td class="text-amber-300">1.618</td></tr>
      </tbody>
    </table></div>
    <p class="text-[10px] text-slate-400 mt-1">Verdict: residual domain shift + probability miscalibration, not "enrichment is useless." Not re-attempted without source-conditional calibration.</p>
  </div>
</div>

<div class="source-footer">Source: wiki/log.md (2026-09-01) · reports/HEALTHY_ENRICHMENT_FALSE_POSITIVE_DIAGNOSIS.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 5 — Synthetic Data Generation Pipeline
      ──────────────────────────────────────────────────────── -->

# Synthetic Healthy-Data Generation — All Candidates Rejected

<p class="text-slate-300 text-xs -mt-1">Every generator remained training-excluded pending realism, memorisation, and downstream frozen-external gates. None reached admission.</p>

<table class="my-2 tiny-table">
  <thead><tr><th>Method</th><th>Source</th><th>Quality result</th><th>Downstream ablation</th><th>Verdict</th></tr></thead>
  <tbody>
    <tr><td>Convex phase-mixing</td><td>MAREA</td><td>Std. dev. 0.661 vs 0.882 real; spectral energy 0.0058 vs 0.0139 real</td><td>Not run — failed realism first</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Cross-fade recombination</td><td>MAREA</td><td>Passed structural checks</td><td>RevalExo Brier 0.161→0.172, Bal. Acc. 0.714→0.643</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Convolutional VAE (v1)</td><td>MAREA cycles</td><td>Oversmoothed; not admitted</td><td>Not run</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Convolutional VAE (v2)</td><td>MAREA cycles</td><td>Std. dev. 4.66 vs 8.46 real; low-freq power 54.95 vs 216.29</td><td>Not run</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Unconditional diffusion (DDPM)</td><td>MAREA cycles</td><td>Std. dev. 4.09 vs 8.46 real; low-freq power 57.9 vs 216.3</td><td>Not run</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Source-conditioned diffusion</td><td>MAREA + DUO-GAIT</td><td>Implemented; not yet quality-gated</td><td>Not run</td><td><span class="pill pill-gray">In progress</span></td></tr>
  </tbody>
</table>

<div class="grid grid-cols-2 gap-3 mt-1">
  <div class="card"><h3 class="text-sky-300">Structural corrections along the way</h3><p class="text-xs text-slate-300 mt-1">DUO-GAIT unit mismatch found (g vs m/s², ~9.8× factor) and corrected before pooling. Official Tunca-style event detection recovered from the authors' own repository to produce clean synchronized cycles.</p></div>
  <div class="card"><h3 class="text-amber-300">Why this matters</h3><p class="text-xs text-slate-300 mt-1">Every generator failed a <em>realism</em> gate before ever reaching a classifier. No synthetic window has touched training data. Assigning multiple synthetic cycles to one parent ID was also caught and corrected — synthetic cycles are not new participants.</p></div>
</div>

<div class="source-footer">Source: reports/MAREA_SYNTHETIC_HEALTHY_TRIAL.md · reports/SYNTHETIC_HEALTHY_DATA_TRIAL.md · reports/SYNTHESIS_REALISM_REVIEW_2026-09-01.md · wiki/log.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 6 — NONAN GaitPrint Healthy Specificity
      ──────────────────────────────────────────────────────── -->

# NONAN GaitPrint — Large-Scale Healthy Specificity Test

<div class="grid grid-cols-4 gap-2.5 my-3">
  <div class="card text-center"><div class="text-xl font-bold text-sky-400">29</div><div class="text-[10px] text-slate-400 mt-0.5">Frozen participants</div><div class="text-[9px] text-slate-500">23,657 windows</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-emerald-400">93.1%</div><div class="text-[10px] text-slate-400 mt-0.5">Healthy specificity</div><div class="text-[9px] text-slate-500">Wilson CI 78.0–98.1%</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-amber-400">80</div><div class="text-[10px] text-slate-400 mt-0.5">Candidate participants</div><div class="text-[9px] text-slate-500">68,398 windows</div></div>
  <div class="card text-center"><div class="text-xl font-bold text-rose-400">Not admitted</div><div class="text-[10px] text-slate-400 mt-0.5">Repeated paired gate</div><div class="text-[9px] text-slate-500">No durable benefit</div></div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div class="card">
    <h3 class="text-sky-300">Frozen score (reporting-only)</h3>
    <p class="text-xs text-slate-300 mt-1">At the fixed 0.50 reference, 2/29 healthy participants were misclassified (specificity 93.1%). The two false positives share no age group, mobility-screen flag, or amplitude profile — ruling out a simplistic clipping/scaling explanation.</p>
  </div>
  <div class="card">
    <h3 class="text-amber-300">Candidate enrichment — rejected</h3>
    <p class="text-xs text-slate-300 mt-1">A bounded, capped, source-downweighted candidate addition looked promising in one pass (candidate specificity 0.9107→0.9630), but the <strong>repeated 15-unit paired gate</strong> found no durable benefit: AUROC Δ +0.0002 (CI −0.0039 to +0.0049), specificity Δ −0.0166 (CI −0.0901 to +0.0480). A class-aware CORAL alignment variant also failed.</p>
  </div>
</div>

<div class="source-footer">Source: notebooks/14_nonan_candidate_healthy_materialization.ipynb · notebooks/15_nonan_source_compatibility_gate.ipynb · notebooks/16_bounded_nonan_enrichment_ablation.ipynb · notebooks/17_repeated_paired_nonan_enrichment_gate.ipynb · notebooks/18_class_aware_nonan_alignment_pilot.ipynb</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 7 — Representation Audits
      ──────────────────────────────────────────────────────── -->

# Representation Audits — Magnitude Confirmed as the Deployment Contract

<div class="grid grid-cols-2 gap-4 my-2">
  <div>
    <h2>Signed Axes vs. Magnitude</h2>
    <table>
      <thead><tr><th>Representation</th><th>Internal AUROC</th><th>RevalExo AUROC</th><th>Healthy FP</th></tr></thead>
      <tbody>
        <tr><td><span class="pill pill-prp">Magnitude (3ch)</span></td><td>0.979</td><td class="text-emerald-300 font-bold">0.914</td><td class="text-emerald-300">4/7</td></tr>
        <tr><td><span class="pill pill-red">Signed axes (9ch)</span></td><td>0.974</td><td class="text-rose-400 font-bold">0.457</td><td class="text-rose-400">7/7</td></tr>
      </tbody>
    </table>
    <p class="text-[10px] text-slate-400 mt-1">Signed axes look competitive internally but collapse externally — not orientation/domain invariant across source hardware. Magnitude remains the official contract.</p>
  </div>
  <div>
    <h2>Lower-Back Gyroscope (6-DoF)</h2>
    <table>
      <thead><tr><th>Held-out source</th><th>Accel-only</th><th>+Gyroscope</th></tr></thead>
      <tbody>
        <tr><td>Felius (transport gain)</td><td>0.850</td><td class="text-emerald-300">0.859</td></tr>
        <tr><td>Sint (transport loss)</td><td class="text-emerald-300">0.870</td><td class="text-rose-400">0.772</td></tr>
        <tr><td>Sint healthy specificity</td><td class="text-emerald-300">0.750</td><td class="text-rose-400">0.433</td></tr>
      </tbody>
    </table>
    <p class="text-[10px] text-slate-400 mt-1">Gyroscope magnitude verified via a new Sint 6-DoF adapter (4,053 windows). Rejected as a pooled replacement — helps one transport direction, materially hurts another.</p>
  </div>
</div>

<div class="source-footer">Source: reports/PIPELINE_RESEARCH_COMPARISON_AND_PROCESSING_AUDIT_2026-09-01.md · wiki/log.md (2026-09-02, lower-back 6-DoF)</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 8 — Normalization & Augmentation Probes
      ──────────────────────────────────────────────────────── -->

# Normalization & Augmentation Probes — Baseline Retained

<div class="grid grid-cols-2 gap-4 my-2">
  <div>
    <h2>Global Z-Score vs. Robust Median/IQR</h2>
    <table class="tiny-table">
      <thead><tr><th>Track</th><th>Norm.</th><th>AUROC</th><th>Bal.Acc</th><th>Healthy FP</th></tr></thead>
      <tbody>
        <tr><td>Lower back</td><td>Z-score</td><td>0.767±.058</td><td>0.591</td><td>5.53</td></tr>
        <tr><td>Lower back</td><td>Robust</td><td>0.772±.032</td><td>0.591</td><td>5.53</td></tr>
        <tr><td>3-channel</td><td>Z-score</td><td class="text-emerald-300">0.917</td><td>0.661</td><td class="text-emerald-300">4.33</td></tr>
        <tr><td>3-channel</td><td>Robust</td><td>0.916</td><td>0.651</td><td>4.80</td></tr>
      </tbody>
    </table>
    <p class="text-[10px] text-slate-400 mt-1">3-seed repeat confirms no material difference. Global z-score <strong>remains locked</strong>.</p>
  </div>
  <div>
    <h2>Nuisance-Augmentation Probe</h2>
    <p class="text-xs text-slate-300">Per-window gain (±10%), Gaussian noise, and ±8-sample temporal roll during training only.</p>
    <div class="card mt-2" style="border-color:rgba(248,113,113,0.4)">
      <table class="tiny-table">
        <thead><tr><th>Track</th><th>AUROC</th><th>Brier</th><th>Healthy FP</th></tr></thead>
        <tbody>
          <tr><td>Lower-back (aug.)</td><td class="text-rose-400">0.751</td><td class="text-rose-400">0.224</td><td class="text-rose-400">6.2</td></tr>
          <tr><td>3-channel (aug.)</td><td>0.917</td><td>0.163</td><td>5.0</td></tr>
        </tbody>
      </table>
      <p class="text-[10px] text-rose-300 mt-1">🚫 Degraded external calibration and specificity — rejected outright.</p>
    </div>
  </div>
</div>

<div class="source-footer">Source: reports/NORMALIZATION_VARIANT_BENCHMARK.md · data/processed/normalization_variant_benchmark_repeated_seeds.csv</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 9 — Non-Stroke Hard-Negative Stress Test
      ──────────────────────────────────────────────────────── -->

# The Critical Gap: Non-Stroke Hard Negatives

<p class="text-slate-300 text-xs -mt-1">Same-protocol Voisard cohorts with other neurological/orthopedic conditions — never relabelled, never pooled into training.</p>

<div class="grid grid-cols-2 gap-4 my-1">
  <div>
    <table class="tiny-table">
      <thead><tr><th>Cohort</th><th>N</th><th>Meaning</th><th>FP @ 0.50</th></tr></thead>
      <tbody>
        <tr><td>ACL</td><td>11</td><td>Orthopedic</td><td>36.4%</td></tr>
        <tr><td>CIPN</td><td>19</td><td>Neurological</td><td>52.6%</td></tr>
        <tr><td>HOA</td><td>15</td><td>Orthopedic</td><td>26.7%</td></tr>
        <tr><td>KOA</td><td>18</td><td>Orthopedic</td><td>38.9%</td></tr>
        <tr><td>PD</td><td>24</td><td>Neurological</td><td class="text-rose-400">62.5%</td></tr>
        <tr><td>RIL</td><td>51</td><td>Neurological</td><td class="text-rose-400">62.7%</td></tr>
        <tr class="font-bold"><td>Pooled</td><td>138</td><td>Non-stroke only</td><td class="text-rose-400">52.2%</td></tr>
      </tbody>
    </table>
  </div>
  <div class="space-y-2">
    <div class="card" style="border-color:rgba(248,113,113,0.4)"><h3 class="text-rose-300">Not a stroke-specific classifier</h3><p class="text-xs text-slate-300 mt-1">Parkinson's disease and radiation-induced leukoencephalopathy score stroke-like most often. Raising the threshold to 0.78 reduces pooled FP to 31.2% but also reduces stroke sensitivity.</p></div>
    <div class="card"><h3 class="text-sky-300">Binary exposure experiment — also rejected</h3><p class="text-xs text-slate-300 mt-1">Adding a temporary hard-negative exposure target during training either damaged primary calibration (25% dose: Brier 0.090→0.140) or gave an insufficient specificity gain (7.7% dose: FP only 52.2%→46.4%). Neither replaces the binary baseline.</p></div>
  </div>
</div>

<div class="source-footer">Source: reports/VOISARD_NONSTROKE_HARD_NEGATIVE_EVALUATION_2026-09-01.md · data/processed/voisard_nonstroke_hard_negative_summary.csv</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 10 — Cross-Dataset Evidence Gate
      ──────────────────────────────────────────────────────── -->

# Cross-Dataset Evidence Gate — Research Discipline Formalised

<p class="text-slate-300 text-xs -mt-1">Before proposing another modelling approach, eight literature/code bases (BenchHAR, HAROOD, ContrastSense, CALDA/CALDG, DAGHAR, IMUDiffusion, PPDA/WIMUSim, stroke/lower-back studies) were audited against this project's exact task, sensors, and split rules.</p>

<div class="grid grid-cols-2 gap-3 my-2">
  <div class="card">
    <h3 class="text-sky-300">Why past negative results don't contradict the literature</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>Many reported successes concern generic HAR or gait detection, not disease classification</li>
      <li>Many use target-domain data during fitting — this project explicitly forbids that</li>
      <li>Accelerometer-only can outperform accelerometer+gyroscope — consistent with this project's own finding</li>
      <li>Synthetic gains can reverse for individual held-out people or larger configurations</li>
    </ul>
  </div>
  <div class="card">
    <h3 class="text-emerald-300">Mandatory checklist for every future experiment</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>Official-code trace before re-implementing any method</li>
      <li>Matched ERM baseline under the same protocol</li>
      <li>Participant/source-disjoint validation, always</li>
      <li>Training-only generator fitting; real-only validation/testing</li>
      <li>Worst-source clinical metrics reported, not just pooled means</li>
      <li>No RevalExo/NONAN used for model selection — ever</li>
    </ul>
  </div>
</div>

<div class="source-footer">Source: reports/EVIDENCE_GATE_CROSS_DATASET_IMU_2026-09-03.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 11 — Model Breakthrough: Lower-Back Ensemble Admitted
      ──────────────────────────────────────────────────────── -->

# Admitted: The Lower-Back ERM + CORAL + ERM++ Ensemble

<div class="grid grid-cols-5 gap-2 my-3">
  <div class="card text-center"><div class="text-lg font-bold text-emerald-400">0.8882</div><div class="text-[9px] text-slate-400">AUROC</div><div class="text-[8px] text-slate-500">was 0.8737</div></div>
  <div class="card text-center"><div class="text-lg font-bold text-emerald-400">0.1425</div><div class="text-[9px] text-slate-400">Brier</div><div class="text-[8px] text-slate-500">was 0.1664</div></div>
  <div class="card text-center"><div class="text-lg font-bold text-emerald-400">0.8140</div><div class="text-[9px] text-slate-400">Bal. accuracy</div><div class="text-[8px] text-slate-500">was 0.7834</div></div>
  <div class="card text-center"><div class="text-lg font-bold text-emerald-400">0.7743</div><div class="text-[9px] text-slate-400">Specificity</div><div class="text-[8px] text-slate-500">was 0.7145</div></div>
  <div class="card text-center"><div class="text-lg font-bold text-sky-400">0.8537</div><div class="text-[9px] text-slate-400">Sensitivity</div><div class="text-[8px] text-slate-500">was 0.8523</div></div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div class="card">
    <h3 class="text-sky-300">Protocol</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>314 participants, 22,506 lower-back windows, Felius + Voisard + Sint</li>
      <li>Leave-one-complete-source-out outer evaluation, 5 seeds</li>
      <li>Fixed equal-probability average of ERM, Deep CORAL, ERM++-style head warm-up</li>
      <li>RevalExo and NONAN <strong>not loaded</strong> for training, tuning, or selection</li>
    </ul>
  </div>
  <div class="card">
    <h3 class="text-emerald-300">Paired bootstrap (ensemble − ERM)</h3>
    <table class="tiny-table">
      <thead><tr><th>Metric</th><th>Δ mean</th><th>95% CI</th></tr></thead>
      <tbody>
        <tr><td>Balanced accuracy</td><td class="text-emerald-300">+0.0306</td><td>+0.004 to +0.064</td></tr>
        <tr><td>Specificity</td><td class="text-emerald-300">+0.0599</td><td>−0.001 to +0.132</td></tr>
        <tr><td>AUROC</td><td class="text-emerald-300">+0.0146</td><td>+0.001 to +0.032</td></tr>
        <tr><td>Brier</td><td class="text-emerald-300">−0.0239</td><td>−0.049 to −0.002</td></tr>
      </tbody>
    </table>
    <p class="text-[10px] text-amber-300 mt-1">⚠️ Development-selection evidence only — not external or clinical validation. Standalone CORAL / ERM++ alone did <em>not</em> pass.</p>
  </div>
</div>

<div class="source-footer">Source: reports/MODEL_IMPROVEMENT_GATE_2026-09-03.md · notebooks/29_evidence_gated_source_only_domain_generalization.ipynb</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 12 — Rescue Attempts After the Ensemble
      ──────────────────────────────────────────────────────── -->

# Rescue Attempts After the Ensemble — All Rejected

<p class="text-slate-300 text-xs -mt-1">Every candidate had to beat the incumbent ensemble (FP 9.80, FN 11.93, 21.73 total errors per source/seed) on the same three-source, five-seed, leakage-safe protocol.</p>

<table class="my-2 tiny-table">
  <thead><tr><th>Candidate</th><th>AUROC</th><th>Bal.Acc</th><th>FP</th><th>FN</th><th>Total errors</th><th>Verdict</th></tr></thead>
  <tbody>
    <tr class="font-bold"><td>Incumbent ensemble</td><td class="text-emerald-300">0.8882</td><td>0.8140</td><td>9.80</td><td class="text-emerald-300">11.93</td><td class="text-emerald-300">21.73</td><td><span class="pill pill-grn">Selected</span></td></tr>
    <tr><td>+ MiniROCKET fusion (50:50)</td><td>0.8869</td><td class="text-emerald-300">0.8145</td><td class="text-emerald-300">9.33</td><td>12.80</td><td>22.13</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Canonical 10k MiniROCKET</td><td>0.8572</td><td>0.8029</td><td>9.40</td><td>13.87</td><td>23.27</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Canonical InceptionTime</td><td>0.8273</td><td>0.7418</td><td>13.07</td><td>19.07</td><td>32.13</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Participant mean-pooling MIL</td><td>0.8442</td><td>0.7691</td><td>9.80</td><td>11.53</td><td>21.33</td><td><span class="pill pill-red">Rejected</span></td></tr>
    <tr><td>Participant gated-attention MIL</td><td>0.8043</td><td>0.7528</td><td>11.00</td><td>12.33</td><td>23.33</td><td><span class="pill pill-red">Rejected</span></td></tr>
  </tbody>
</table>

<div class="grid grid-cols-2 gap-3 mt-1">
  <div class="card"><h3 class="text-amber-300">Threshold sweep confirms overlap, not miscalibration</h3><p class="text-xs text-slate-300 mt-1">Minimum achievable total error is 58/314. Zero FP requires 157 FN; zero FN requires 87 FP. Score distributions genuinely overlap.</p></div>
  <div class="card"><h3 class="text-rose-300">Stop rule invoked</h3><p class="text-xs text-slate-300 mt-1">MIL reduced total errors by only 1.8% (needed ≥10%) and traded errors between sources rather than resolving them. Architecture rotation on these 314 participants is now closed.</p></div>
</div>

<div class="source-footer">Source: reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md · reports/PARTICIPANT_MIL_GATE_2026-09-03.md · reports/SCORE_OVERLAP_AND_HETEROGENEOUS_RESCUE_2026-09-03.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 13 — Test-Set Credibility Audit
      ──────────────────────────────────────────────────────── -->

# Test-Set Credibility Audit — Why More Data Is the Limiting Factor

<div class="grid grid-cols-2 gap-4 my-2">
  <div>
    <h2>Seed-Consensus Confusion (development)</h2>
    <div class="grid grid-cols-3 gap-1.5 text-center text-xs max-w-xs mt-2">
      <div class="card p-1.5"></div>
      <div class="card p-1.5 font-semibold">Pred: Healthy</div>
      <div class="card p-1.5 font-semibold">Pred: Stroke</div>
      <div class="card p-1.5 font-semibold">True: Healthy</div>
      <div class="p-1.5 bg-emerald-500/20 border border-emerald-500/40 rounded font-bold text-emerald-300">TN: 99</div>
      <div class="p-1.5 bg-rose-500/20 border border-rose-500/30 rounded text-rose-300">FP: 27</div>
      <div class="card p-1.5 font-semibold">True: Stroke</div>
      <div class="p-1.5 bg-rose-500/20 border border-rose-500/30 rounded text-rose-300">FN: 33</div>
      <div class="p-1.5 bg-emerald-500/20 border border-emerald-500/40 rounded font-bold text-emerald-300">TP: 155</div>
    </div>
    <p class="text-[10px] text-slate-400 mt-1.5">Pooled specificity 78.6% (CI 70.6–84.8%) · sensitivity 82.4% (CI 76.4–87.2%). Diagnostic summary, not an independent test — every source influenced selection.</p>
  </div>
  <div class="space-y-2">
    <div class="card"><h3 class="text-amber-300">Planning target</h3><p class="text-xs text-slate-300 mt-1">At current development rates, a two-sided 95% Wilson interval no wider than 10 points needs approximately <strong class="text-amber-300">257 independent healthy</strong> and <strong class="text-amber-300">222 independent stroke</strong> participants — illustrating why 7 healthy / 10 stroke (RevalExo) cannot be a reliability claim.</p></div>
    <div class="card"><h3 class="text-sky-300">Required final-test contract (7 rules)</h3><p class="text-xs text-slate-300 mt-1">Freeze everything before access · new untouched multi-site participants · participant is the statistical unit · represent age/sex/severity/speed/aids/non-stroke confounders · independent clinical reference diagnosis · full 2×2 + CI reporting · no post-hoc model or threshold update.</p></div>
  </div>
</div>

<div class="source-footer">Source: reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md · notebooks/30_fp_fn_and_test_set_credibility_audit.ipynb</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 14 — New Candidate Sources & Specificity Wins
      ──────────────────────────────────────────────────────── -->

# New External Evidence: Specificity Wins and Candidate Sources

<div class="grid grid-cols-2 gap-4 my-1">
  <div>
    <h2>Component Robustness Results</h2>
    <div class="card"><p class="text-xs text-slate-300"><strong class="text-emerald-300">Carpinella 6MWT healthy cohort</strong> — 60 healthy participants, 6,109 windows. Lower-back-only baseline made <strong>0 stroke predictions</strong> at 0.50 (Wilson upper bound 6.0%).</p></div>
    <div class="card mt-2"><p class="text-xs text-slate-300"><strong class="text-sky-300">Zenodo stroke-only cohort</strong> — 3-channel detected 9/10 stroke (95% CI 59.6–98.2%); lower-back-only detected 10/10 (95% CI 72.2–100%).</p></div>
    <div class="card mt-2" style="border-color:rgba(248,113,113,0.4)"><p class="text-xs text-rose-300"><strong>Triaxial older-healthy cohort</strong> — 53/59 (89.8%) false positives. Diagnosed as a signal-domain/device mismatch (median magnitude 0.578g vs the model's fitted 1.016g), <strong>not</strong> an age effect — must not be pooled or reinterpreted as age bias.</p></div>
  </div>
  <div>
    <h2>Screened Candidate Sources (not yet acquired for training)</h2>
    <table class="tiny-table">
      <thead><tr><th>Source</th><th>Composition</th><th>Role</th></tr></thead>
      <tbody>
        <tr><td>WearGait-PD</td><td>85 healthy + 100 PD, full-body IMU</td><td>Non-stroke hard-negative test</td></tr>
        <tr><td>6MWT normative</td><td>60 healthy, lower-back only</td><td>Healthy age/domain reference</td></tr>
        <tr><td>BLISS</td><td>21 mixed impairment, lower-limb</td><td>Foot/impairment stress test</td></tr>
        <tr><td>Soangra/John</td><td>13 stroke + 19 healthy, L5/S1</td><td>Ruled out — no verified gait labels</td></tr>
        <tr><td>Kiel / Wang 2021</td><td>Healthy-only or unreachable archive</td><td>Not currently acquirable</td></tr>
      </tbody>
    </table>
    <p class="text-[10px] text-slate-400 mt-2">Screening rule: a source enters the binary training pool only with independently identified healthy <em>and</em> stroke participants, raw walking IMU signals, and a defensible LB+bilateral-foot mapping.</p>
  </div>
</div>

<div class="source-footer">Source: reports/BINARY_DATA_READINESS_AND_PUBLIC_RECRUITMENT_2026-09-01.md · reports/TRIAXIAL_OLDER_HEALTHY_LOWER_BACK_FROZEN_AUDIT_2026-09-02.md · reports/EXTERNAL_VALIDATION_STATUS_AND_PUBLIC_RECRUITMENT_2026-09-02.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 15 — Data Storage Retention Cleanup
      ──────────────────────────────────────────────────────── -->

# Housekeeping: Data Storage Retention Audit

<div class="grid grid-cols-3 gap-3 my-3">
  <div class="card text-center"><div class="text-2xl font-bold text-sky-400">268.68 GiB</div><div class="text-[10px] text-slate-400 mt-0.5">Before cleanup</div></div>
  <div class="card text-center"><div class="text-2xl font-bold text-emerald-400">153.93 GiB</div><div class="text-[10px] text-slate-400 mt-0.5">After Tier-A cleanup</div></div>
  <div class="card text-center"><div class="text-2xl font-bold text-amber-400">114.75 GiB</div><div class="text-[10px] text-slate-400 mt-0.5">Reclaimed</div></div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div class="card">
    <h3 class="text-emerald-300">Removed (Tier A — executed)</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>80 candidate-NONAN source archives (107.32 GiB) — enrichment already rejected</li>
      <li>3 structural-audit NONAN archives (4.07 GiB) — already materialized</li>
      <li>Redundant Sint release ZIP (2.41 GiB) — extraction already verified</li>
      <li>Redundant Mobilise-D ZIP copies (0.95 GiB) — already extracted</li>
    </ul>
  </div>
  <div class="card">
    <h3 class="text-sky-300">Protected — verified intact after cleanup</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>Felius, Voisard, extracted Sint, RevalExo (all active sources)</li>
      <li><code>data/processed/</code> — every tensor, metric, and checkpoint</li>
      <li>NONAN compact processed tensors and manifests</li>
      <li>All executed notebooks, reports, and wiki provenance</li>
    </ul>
  </div>
</div>

<div class="source-footer">Source: reports/DATA_STORAGE_RETENTION_AUDIT_2026-09-03.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 16 — Updated Final Synthesis
      ──────────────────────────────────────────────────────── -->

# Updated Synthesis After the Sprint

<div class="grid grid-cols-3 gap-3 my-3">
  <div class="card text-center" style="border-color:rgba(52,211,153,0.5)">
    <div class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider mb-1">New Incumbent</div>
    <div class="text-2xl font-bold text-emerald-400">0.8882</div>
    <div class="text-[11px] text-slate-300 mt-0.5">AUROC · lower-back ensemble</div>
    <div class="text-[9px] text-slate-500 mt-0.5">Development-selected, 314 participants</div>
  </div>
  <div class="card text-center" style="border-color:rgba(167,139,250,0.5)">
    <div class="text-[10px] text-violet-400 font-bold uppercase tracking-wider mb-1">3-Channel Comparator Unchanged</div>
    <div class="text-2xl font-bold text-violet-400">0.914</div>
    <div class="text-[11px] text-slate-300 mt-0.5">AUROC · frozen RevalExo (n=17)</div>
    <div class="text-[9px] text-slate-500 mt-0.5">Still the higher-performance track</div>
  </div>
  <div class="card text-center" style="border-color:rgba(251,191,36,0.5)">
    <div class="text-[10px] text-amber-400 font-bold uppercase tracking-wider mb-1">Limiting Factor</div>
    <div class="text-lg font-bold text-amber-400 leading-tight mt-1">Cohort size</div>
    <div class="text-[11px] text-slate-300 mt-0.5">Not architecture — 11 rescue attempts all failed the same gate</div>
  </div>
</div>

<div class="card" style="border-color:rgba(56,189,248,0.4)">
  <h2>What this sprint actually proved</h2>
  <p class="text-sm text-slate-200 mt-1 leading-relaxed">Eighteen executed, leakage-safe experiments converge on one conclusion: <strong class="text-sky-300">the remaining error is explained by score overlap on a 314-participant development pool, not by model architecture, normalization, representation, or missing healthy-domain data.</strong> Every enrichment, synthesis, representation, and rescue attempt failed the same predefined non-inferiority gate. The lower-back ensemble is a genuine, evidence-gated improvement over plain ERM, but it is <strong class="text-amber-300">development-selected, not externally validated</strong>, and the 3-channel prototype remains the stronger externally-tested candidate.</p>
</div>

<div class="source-footer">Source: reports/MODEL_IMPROVEMENT_GATE_2026-09-03.md · reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md · reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 17 — Updated Recommended Next Steps
      ──────────────────────────────────────────────────────── -->

# Updated Recommended Next Steps

<div class="grid grid-cols-4 gap-2.5 my-3">
  <div class="card"><div class="text-emerald-400 font-bold text-[11px] uppercase tracking-wider mb-1">① Freeze &amp; Package</div><p class="text-xs text-slate-300">Lock the exact lower-back ensemble recipe (members, weights, threshold) — no further tuning on these 314 participants.</p></div>
  <div class="card"><div class="text-sky-400 font-bold text-[11px] uppercase tracking-wider mb-1">② One Frozen External Pass</div><p class="text-xs text-slate-300">Evaluate the packaged ensemble on RevalExo exactly once, under a pre-registered protocol, without retuning.</p></div>
  <div class="card"><div class="text-violet-400 font-bold text-[11px] uppercase tracking-wider mb-1">③ Recruit New Paired Cohort</div><p class="text-xs text-slate-300">Target ~257 healthy / ~222 stroke participants for a precise sensitivity/specificity interval — the single limiting requirement identified this sprint.</p></div>
  <div class="card"><div class="text-rose-400 font-bold text-[11px] uppercase tracking-wider mb-1">④ Non-Stroke Specificity</div><p class="text-xs text-slate-300">Acquire WearGait-PD or equivalent to test the 52.2% non-stroke false-positive rate against a genuine external cohort.</p></div>
</div>

<div class="grid grid-cols-2 gap-3 mt-1">
  <div class="card"><h3 class="text-slate-300">Closed for now</h3><ul class="text-xs text-slate-400 mt-1 space-y-0.5"><li>Architecture rotation on the existing 314 participants (canonical benchmark closed this)</li><li>Healthy-pool enrichment without source-conditional calibration</li><li>Synthetic data generation without a materially better realism gate</li></ul></div>
  <div class="card" style="border-color:rgba(245,158,11,0.35)"><h3 class="text-amber-300">Guardrails carried forward</h3><ul class="text-xs text-slate-400 mt-1 space-y-0.5"><li>RevalExo and NONAN stay frozen — never used for model selection</li><li>Every future experiment must pass the cross-dataset evidence-gate checklist</li><li>No claim of clinical readiness from development-only evidence</li></ul></div>
</div>

<div class="source-footer">Source: reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md · reports/EVIDENCE_GATE_CROSS_DATASET_IMU_2026-09-03.md · reports/BINARY_DATA_READINESS_AND_PUBLIC_RECRUITMENT_2026-09-01.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 18 — Updated Reproducibility Appendix
      ──────────────────────────────────────────────────────── -->

# Sprint Reproducibility Appendix

<div class="grid grid-cols-2 gap-3 my-2">
  <div>
    <h2>Key New Notebooks &amp; Scripts</h2>
    <table class="tiny-table">
      <thead><tr><th>File</th><th>Produces</th></tr></thead>
      <tbody>
        <tr><td class="text-emerald-300">29_evidence_gated_source_only_domain_generalization.ipynb</td><td>Admitted ensemble</td></tr>
        <tr><td class="text-emerald-300">30_fp_fn_and_test_set_credibility_audit.ipynb</td><td>Confusion counts + planning target</td></tr>
        <tr><td class="text-emerald-300">31_score_overlap_and_heterogeneous_rescue.ipynb</td><td>Threshold sweep + MiniROCKET fusion</td></tr>
        <tr><td class="text-emerald-300">32_participant_level_attention_mil.ipynb</td><td>MIL rejection</td></tr>
        <tr><td class="text-emerald-300">33_prior_method_code_alignment_audit.ipynb</td><td>Official-code trace</td></tr>
        <tr><td class="text-emerald-300">34_canonical_inceptiontime_minirocket_corrective_benchmark.ipynb</td><td>Final architecture gate</td></tr>
        <tr><td class="text-sky-300">scripts/benchmark_normalization_variants.py</td><td>Z-score vs. robust scaling</td></tr>
        <tr><td class="text-sky-300">scripts/evaluate_voisard_nonstroke_hard_negatives.py</td><td>138-cohort specificity test</td></tr>
      </tbody>
    </table>
  </div>
  <div>
    <h2>Key New Metrics Files</h2>
    <table class="tiny-table">
      <thead><tr><th>File</th><th>Key metric</th><th>Value</th></tr></thead>
      <tbody>
        <tr><td>evidence_gated_lower_back_dg_metrics.csv</td><td>Ensemble AUROC</td><td class="text-emerald-300 font-bold">0.8882</td></tr>
        <tr><td>full_expanded_lower_back_only_revalexo_metrics.csv</td><td>LB-only external AUROC</td><td class="text-rose-400">0.757</td></tr>
        <tr><td>voisard_nonstroke_hard_negative_summary.csv</td><td>Pooled non-stroke FP</td><td class="text-amber-300">52.2%</td></tr>
        <tr><td>normalization_variant_benchmark_repeated_seeds.csv</td><td>Robust vs. z-score Δ AUROC</td><td class="text-slate-300">+0.006 (n.s.)</td></tr>
        <tr><td>canonical_corrective_decision.json</td><td>Total errors, incumbent</td><td class="text-emerald-300">21.73</td></tr>
        <tr><td>participant_mil_metrics.csv</td><td>MIL total-error reduction</td><td class="text-rose-400">1.8% (needed 10%)</td></tr>
      </tbody>
    </table>
    <p class="text-[9px] text-slate-400 mt-1 leading-tight">
      <strong class="text-amber-400">Frozen cohorts untouched:</strong> RevalExo and NONAN were not loaded for training, tuning, or selection in any experiment this sprint.
    </p>
  </div>
</div>

<div class="source-footer">Source: wiki/log.md · reports/MODEL_IMPROVEMENT_GATE_2026-09-03.md · reports/CANONICAL_CORRECTIVE_BENCHMARK_2026-09-03.md · reports/TEST_SET_CREDIBILITY_AUDIT_2026-09-03.md · data/processed/evidence_gated_lower_back_dg_metrics.csv</div>
