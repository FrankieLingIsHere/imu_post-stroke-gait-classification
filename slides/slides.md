---
theme: seriph
layout: default
highlighter: shiki
lineNumbers: false
transition: slide-left
title: 3-Channel IMU Stroke Gait Classification
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
      SLIDE 1 — Title & Research Question
      ──────────────────────────────────────────────────────── -->
<div class="flex h-full flex-col justify-between">

<div>
<div class="flex items-center gap-2 mb-3">
  <span class="pill pill-amb">Research Prototype — Not Clinically Deployed</span>
</div>

# 3-Channel Wearable-IMU Stroke Gait Classification

<p class="text-slate-300 text-sm mt-1">Participant-level stroke vs. healthy gait discrimination from tri-sensor acceleration-magnitude windows</p>

<div class="grid grid-cols-3 gap-3 mt-5">
  <div class="p-3.5 rounded-xl bg-slate-800/70 border border-slate-700/80">
    <div class="text-[10px] text-sky-400 font-bold uppercase tracking-wider mb-1.5">Research Question</div>
    <p class="text-slate-200 text-xs">Can participant-level stroke ↔ healthy discrimination be learned from raw 3-channel IMU magnitude windows using deep and classical models?</p>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/70 border border-slate-700/80">
    <div class="text-[10px] text-sky-400 font-bold uppercase tracking-wider mb-1.5">3-Channel Input</div>
    <div class="flex flex-col gap-1.5 mt-1">
      <div class="flex items-center gap-1.5"><span class="pill pill-sky">LB</span><span class="text-xs text-slate-300">Lower Back · L5/Lumbar</span></div>
      <div class="flex items-center gap-1.5"><span class="pill pill-grn">LF</span><span class="text-xs text-slate-300">Left Foot · swing/clearance</span></div>
      <div class="flex items-center gap-1.5"><span class="pill pill-prp">RF</span><span class="text-xs text-slate-300">Right Foot · bilateral stance</span></div>
    </div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/70 border border-slate-700/80">
    <div class="text-[10px] text-sky-400 font-bold uppercase tracking-wider mb-1.5">Project Status</div>
    <ul class="text-xs text-slate-300 space-y-1">
      <li>✅ Research prototype — benchmarked</li>
      <li>✅ External validation (RevalExo, n=17)</li>
      <li>⚠️ Age/sex metadata gaps remain</li>
      <li>🚫 Not clinically validated or deployed</li>
    </ul>
  </div>
</div>
</div>

<div class="source-footer">Source: README.md · docs/DEEP_LEARNING_DEVELOPMENT_PLAN.md · docs/BASELINE_REQUIREMENTS_AUDIT.md</div>
</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 2 — Executive Summary
      ──────────────────────────────────────────────────────── -->

# Executive Summary

<div class="grid grid-cols-4 gap-2.5 my-3">
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/80 text-center">
    <div class="text-2xl font-bold text-sky-400">0.965</div>
    <div class="text-[11px] text-slate-400 mt-0.5">Internal OOF AUROC</div>
    <div class="text-[10px] text-slate-500 mt-0.5">Expanded · 314 participants</div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/80 text-center">
    <div class="text-2xl font-bold text-emerald-400">0.915</div>
    <div class="text-[11px] text-slate-400 mt-0.5">Internal Balanced Acc.</div>
    <div class="text-[10px] text-slate-500 mt-0.5">Expanded OOF · 126H / 188S</div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/80 text-center">
    <div class="text-2xl font-bold text-violet-400">0.914</div>
    <div class="text-[11px] text-slate-400 mt-0.5">External RevalExo AUROC</div>
    <div class="text-[10px] text-slate-500 mt-0.5">Locked · 17 participants</div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-amber-700/50 text-center">
    <div class="text-2xl font-bold text-amber-400">0.714</div>
    <div class="text-[11px] text-slate-400 mt-0.5">External Balanced Acc.</div>
    <div class="text-[10px] text-slate-500 mt-0.5">Small cohort — descriptive</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div class="p-3 bg-slate-800/40 border border-emerald-700/40 rounded-xl">
    <h3 class="text-emerald-400">✅ Current Strengths</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>Participant-disjoint 5-fold CV with fold-specific normalization</li>
      <li>Multi-source pooled training (Felius + Voisard + Sint)</li>
      <li>Paired bootstrap Sint gate passed (AUROC Δ = +0.044, CI [0.000, +0.171])</li>
      <li>Locked frozen external test (RevalExo) — no leakage</li>
      <li>Channel occlusion identifies lower-back as most influential</li>
    </ul>
  </div>
  <div class="p-3 bg-slate-800/40 border border-rose-700/40 rounded-xl">
    <h3 class="text-rose-400">⚠️ Key Limitations</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>RevalExo = 17 participants — underpowered for model selection</li>
      <li>No subject-level age/sex linkage across sources</li>
      <li>No direct gait-speed metadata (865 trials — all missing)</li>
      <li>Non-stroke clinical specificity unresolved</li>
      <li>No validated clinical decision threshold</li>
    </ul>
  </div>
</div>

<div class="source-footer">Source: data/processed/population_robustness_matrix.csv · reports/FULL_EXPANDED_PROTOTYPE_BENCHMARK.md · reports/SINT_SENSITIVITY_TRAINING.md · docs/BASELINE_REQUIREMENTS_AUDIT.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 3 — Clinical Motivation
      ──────────────────────────────────────────────────────── -->

# Clinical Motivation

<div class="grid grid-cols-2 gap-3.5 my-2">
  <div style="background: #161e2e; border: 1px solid #334155;" class="p-3 rounded-xl">
    <h2 class="text-sky-400 font-bold text-sm mb-1">Why Gait Classification Matters Post-Stroke</h2>
    <ul class="text-[11px] text-slate-200 space-y-1 mt-1 pl-3.5 list-disc">
      <li><strong class="text-sky-300">Prevalence:</strong> Stroke is a leading global cause of disability; gait impairment affects the vast majority of survivors.</li>
      <li><strong class="text-sky-300">Clinical Gap:</strong> Wearable IMUs enable continuous monitoring, but automated validated classifiers are lacking.</li>
      <li><strong class="text-sky-300">Specificity Challenge:</strong> Distinguishing stroke from healthy controls does NOT prove specificity against PD, MS, or COPD.</li>
      <li><strong class="text-sky-300">Asymmetric Gait:</strong> Hemiplegia causes bilateral asymmetry across lower-back and bilateral feet.</li>
    </ul>
  </div>

  <div style="background: #161e2e; border: 1px solid #334155;" class="p-3 rounded-xl">
    <h2 class="text-amber-400 font-bold text-sm mb-1">Known Confounders & Gaps</h2>
    <div class="space-y-1.5 mt-1 text-[10.5px]">
      <div style="background: #1e1b13; border: 1px solid #b45309;" class="p-1.5 rounded-lg">
        <span class="text-[10px] font-bold text-amber-400 uppercase">Age Distribution</span>
        <p class="text-slate-200 leading-tight mt-0.5">0 stroke cases in 18–39 band; 40–59 and 60+ have small cells (≤27 CVA). Healthy age range is wider.</p>
      </div>
      <div style="background: #1e1b13; border: 1px solid #b45309;" class="p-1.5 rounded-lg">
        <span class="text-[10px] font-bold text-amber-400 uppercase">Walking Speed</span>
        <p class="text-slate-200 leading-tight mt-0.5">All 865 primary-manifest trials lack recorded walking speed — speed independence is unresolved.</p>
      </div>
      <div style="background: #1e1b13; border: 1px solid #b45309;" class="p-1.5 rounded-lg">
        <span class="text-[10px] font-bold text-amber-400 uppercase">Severity & Walking Aids</span>
        <p class="text-slate-200 leading-tight mt-0.5">Fugl-Meyer, FAC scores, and assistive device metadata are unlinked across public datasets.</p>
      </div>
    </div>
  </div>
</div>

<div class="source-footer">Source: docs/DEEP_LEARNING_DEVELOPMENT_PLAN.md · reports/SPEED_CONFOUND_AUDIT.md · data/processed/age_group_label_availability.csv</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 4 — Input Representation & Sensor Roles
      ──────────────────────────────────────────────────────── -->

# Input Representation & Sensor Roles

<div class="grid grid-cols-3 gap-3 my-3">
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-sky-700/50">
    <div class="flex items-center gap-2 mb-2">
      <span class="pill pill-sky text-sm">LB</span>
      <h3 class="text-sky-300">Lower Back (L5)</h3>
    </div>
    <ul class="text-xs text-slate-300 space-y-1">
      <li><strong class="text-slate-200">Signal:</strong> Trunk acceleration magnitude</li>
      <li><strong class="text-slate-200">Physiological role:</strong> Captures pelvic tilt, trunk stability, and lateral sway characteristic of hemiparetic gait</li>
      <li><strong class="text-slate-200">Occlusion rank:</strong> <span class="text-emerald-400 font-bold">#1</span> — Mean |ΔP| = <span class="text-emerald-300 font-semibold">0.188</span></li>
      <li><strong class="text-slate-200">Removal effect:</strong> Generally <em>reduces</em> stroke probability (mean signed Δ = +0.130)</li>
      <li class="text-amber-300 text-[10px] mt-1">⚠️ One fold only — cross-fold attribution pending</li>
    </ul>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-emerald-700/50">
    <div class="flex items-center gap-2 mb-2">
      <span class="pill pill-grn text-sm">LF</span>
      <h3 class="text-emerald-300">Left Foot</h3>
    </div>
    <ul class="text-xs text-slate-300 space-y-1">
      <li><strong class="text-slate-200">Signal:</strong> Foot acceleration magnitude</li>
      <li><strong class="text-slate-200">Physiological role:</strong> Foot clearance, swing timing, and push-off force on the paretic or non-paretic side</li>
      <li><strong class="text-slate-200">Occlusion rank:</strong> <span class="text-yellow-400 font-bold">#3</span> — Mean |ΔP| = <span class="text-yellow-300 font-semibold">0.090</span></li>
      <li><strong class="text-slate-200">Removal effect:</strong> Small mixed effect (mean signed Δ = +0.028)</li>
      <li class="text-amber-300 text-[10px] mt-1">⚠️ One fold only — cross-fold attribution pending</li>
    </ul>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-violet-700/50">
    <div class="flex items-center gap-2 mb-2">
      <span class="pill pill-prp text-sm">RF</span>
      <h3 class="text-violet-300">Right Foot</h3>
    </div>
    <ul class="text-xs text-slate-300 space-y-1">
      <li><strong class="text-slate-200">Signal:</strong> Foot acceleration magnitude</li>
      <li><strong class="text-slate-200">Physiological role:</strong> Bilateral stance asymmetry; complements left-foot signal for step-timing and loading differences</li>
      <li><strong class="text-slate-200">Occlusion rank:</strong> <span class="text-orange-400 font-bold">#2</span> — Mean |ΔP| = <span class="text-orange-300 font-semibold">0.104</span></li>
      <li><strong class="text-slate-200">Removal effect:</strong> Tends to <em>increase</em> stroke probability (mean signed Δ = −0.039)</li>
      <li class="text-amber-300 text-[10px] mt-1">⚠️ One fold only — cross-fold attribution pending</li>
    </ul>
  </div>
</div>

<div class="p-2.5 bg-slate-800/40 border border-slate-700/50 rounded-lg text-xs text-slate-400 mt-1">
  <strong class="text-slate-300">Representation contract:</strong> tri-axial accelerometer → per-sensor L2 magnitude → 3-channel tensor [LB, LF, RF] → 5-second windows @ 100 Hz → participant-level aggregated prediction. No fabricated channels for incompatible sources.
</div>

<div class="source-footer">Source: reports/INCEPTION_OCCLUSION_ANALYSIS.md · data/processed/inception_channel_occlusion_windows.csv · docs/DEEP_LEARNING_DEVELOPMENT_PLAN.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 5 — Data Sources & Dataset Roles
      ──────────────────────────────────────────────────────── -->

# Data Sources & Dataset Roles

<table class="my-2 tiny-table">
  <thead><tr>
    <th>Dataset</th><th>Role</th><th>N (H / S)</th><th>Age Range</th><th>Sex</th><th>IMU Compat.</th><th>Status / Decision</th>
  </tr></thead>
  <tbody>
    <tr>
      <td><strong class="text-sky-300">Felius 2024</strong></td>
      <td><span class="pill pill-sky">Core Training</span></td>
      <td>163 (34H / 129S)</td><td>Not linked</td><td>Incomplete</td><td>✅ LB/LF/RF</td>
      <td>Active development</td>
    </tr>
    <tr>
      <td><strong class="text-sky-300">Voisard 2025</strong></td>
      <td><span class="pill pill-sky">Core Training</span></td>
      <td>121 (72H / 49S)</td><td>18–90 (wider release)</td><td>Partial</td><td>✅ LB/LF/RF</td>
      <td>Active development</td>
    </tr>
    <tr>
      <td><strong class="text-emerald-300">Sint Maartenskliniek</strong></td>
      <td><span class="pill pill-grn">Sensitivity Training</span></td>
      <td>30 (20H / 10S)</td><td>Not linked</td><td>Not linked</td><td>✅ Xsens audited</td>
      <td>Gate passed — included</td>
    </tr>
    <tr>
      <td><strong class="text-violet-300">RevalExo</strong></td>
      <td><span class="pill pill-prp">External Eval (locked)</span></td>
      <td>17 (7H / 10S)</td><td>Cohort means only</td><td>Not linked</td><td>✅ Adapter validated</td>
      <td>Frozen — no fitting</td>
    </tr>
    <tr>
      <td><strong class="text-slate-300">Zhou Rehab</strong></td>
      <td><span class="pill pill-amb">Severity / Longitudinal</span></td>
      <td>10 (0H / 10S)</td><td>37–88</td><td>7M / 3F</td><td>⚠️ Different protocol</td>
      <td>Stroke-only auxiliary</td>
    </tr>
    <tr>
      <td><strong class="text-slate-300">Triaxial Healthy</strong></td>
      <td><span class="pill pill-amb">Healthy Domain Ref.</span></td>
      <td>60 (60H / 0S)</td><td>65–88</td><td>24/36 split</td><td>❌ No bilateral LB/LF/RF</td>
      <td>Domain analysis only</td>
    </tr>
    <tr>
      <td><strong class="text-rose-300">Mobilise-D CVS</strong></td>
      <td><span class="pill pill-red">Clinical Specificity</span></td>
      <td>2,315 (no stroke/HC)</td><td>21–96</td><td>~50/50</td><td>❌ Processed single-back DMO</td>
      <td>Stress-test only — not pooled</td>
    </tr>
    <tr>
      <td><strong class="text-slate-400">PiG</strong></td>
      <td><span class="pill" style="background:rgba(100,116,139,0.2);color:#94a3b8;border-color:rgba(100,116,139,0.3)">Biomech. Ref.</span></td>
      <td>188 (138H / 50S)</td><td>19–86</td><td>Mixed</td><td>❌ MotionCap / Force / EMG</td>
      <td>Literature ref. only</td>
    </tr>
  </tbody>
</table>

<div class="source-footer">Source: data/processed/demographic_clinical_population_coverage.csv · reports/PUBLIC_DATASET_ROLE_MATRIX.md · reports/NEW_DATASET_DEMOGRAPHIC_ROLE_MATRIX.html · reports/MOBILISE_D_CVS_COMPATIBILITY_AUDIT.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 6 — Preprocessing Pipeline
      ──────────────────────────────────────────────────────── -->

# Preprocessing Pipeline

<div class="grid grid-cols-5 gap-1.5 text-center text-[10px] my-3">
  <div style="background: #1e293b; border: 1px solid #334155;" class="p-2.5 rounded-lg">
    <span class="text-sky-400 font-bold block mb-0.5">01. Raw IMU</span>
    100Hz Acc/Gyro [LB, LF, RF]
  </div>
  <div style="background: #1e293b; border: 1px solid #334155;" class="p-2.5 rounded-lg">
    <span class="text-sky-400 font-bold block mb-0.5">02. Filter</span>
    Validation & 4th-Order Butterworth
  </div>
  <div style="background: #1e293b; border: 1px solid #334155;" class="p-2.5 rounded-lg">
    <span class="text-sky-400 font-bold block mb-0.5">03. Magnitude</span>
    L2 Vector Norm Per Sensor
  </div>
  <div style="background: #1e293b; border: 1px solid #334155;" class="p-2.5 rounded-lg">
    <span class="text-sky-400 font-bold block mb-0.5">04. Windows</span>
    5s (500 Samples) Fixed Segments
  </div>
  <div style="background: #1e293b; border: 1px solid #334155;" class="p-2.5 rounded-lg">
    <span class="text-sky-400 font-bold block mb-0.5">05. Group Split</span>
    Participant-Disjoint 5-Fold CV
  </div>
</div>

<div class="grid grid-cols-2 gap-3 mt-3">
  <div style="background: #1e293b; border: 1px solid rgba(16,185,129,0.4);" class="p-3 rounded-xl">
    <div class="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-1">Leakage Prevention</div>
    <p class="text-xs text-slate-200">Participant IDs never cross fold boundaries. Normalization stats fitted on training windows only. Window overlap never treated as independent subjects.</p>
  </div>
  <div style="background: #1e293b; border: 1px solid rgba(56,189,248,0.4);" class="p-3 rounded-xl">
    <div class="text-[11px] font-bold text-sky-400 uppercase tracking-wider mb-1">Aggregation Unit</div>
    <p class="text-xs text-slate-200">Window-level probabilities averaged per participant for a single score. All reported AUROC and balanced accuracy computed at the participant level.</p>
  </div>
</div>

<div class="source-footer">Source: notebooks/03_signal_preprocessing_and_windows.ipynb · docs/DEEP_LEARNING_DEVELOPMENT_PLAN.md § 3–4 · scripts/train_sint_sensitivity_inception.py</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 7 — Validation Design & Leakage Controls
      ──────────────────────────────────────────────────────── -->

# Validation Design & Leakage Controls

<div class="grid grid-cols-2 gap-4 my-3">
  <div class="space-y-2.5">
    <div class="p-3 bg-slate-800/50 border border-sky-700/40 rounded-xl">
      <h3 class="text-sky-300">Participant-Disjoint 5-Fold CV</h3>
      <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
        <li>StratifiedGroupKFold — group = participant ID</li>
        <li>All trials, visits, and windows from a participant stay in the same fold</li>
        <li>Expanded training: 63, 63, 63, 63, 62 held-out participants per fold</li>
        <li>Fold-specific normalization (mean/SD fitted on training windows only)</li>
      </ul>
    </div>
    <div class="p-3 bg-slate-800/50 border border-emerald-700/40 rounded-xl">
      <h3 class="text-emerald-300">Source / Class-Balanced Sampling</h3>
      <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
        <li>WeightedRandomSampler equalises source × label cells</li>
        <li>Prevents dominant source (Felius 163 pts) from overwhelming minority (Sint 30 pts)</li>
        <li>Applied only to training batches — not to validation</li>
      </ul>
    </div>
  </div>
  <div class="space-y-2.5">
    <div class="p-3 bg-slate-800/50 border border-violet-700/40 rounded-xl">
      <h3 class="text-violet-300">Frozen External Lock — RevalExo</h3>
      <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
        <li>17 participants excluded from ALL fitting, tuning, and architecture decisions</li>
        <li>Evaluated once per locked model — never used for thresholding or calibration</li>
        <li>Separate validated adapter maps RevalExo signals → LB/LF/RF magnitude tensor</li>
        <li>Sint external examination also kept blind before sensitivity training</li>
      </ul>
    </div>
    <div class="p-3 bg-slate-800/50 border border-rose-700/40 rounded-xl">
      <h3 class="text-rose-300">Anti-Leakage Checklist</h3>
      <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
        <li>❌ Windows from the same person in train AND val</li>
        <li>❌ Normalization computed on the full dataset</li>
        <li>❌ Threshold / calibration fitted on RevalExo</li>
        <li>❌ Overlapping windows treated as independent participants</li>
        <li>✅ All controls confirmed by audit scripts</li>
      </ul>
    </div>
  </div>
</div>

<div class="source-footer">Source: scripts/train_sint_sensitivity_inception.py · scripts/build_population_robustness_matrix.py · scripts/audit_no_leakage_formal_benchmark.py · reports/SINT_SENSITIVITY_TRAINING.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 8 — Model Comparison
      ──────────────────────────────────────────────────────── -->

# Model Comparison

<div class="grid grid-cols-2 gap-4 my-2">
  <div>
    <h2>Internal 5-Fold (Felius + Voisard)</h2>
    <table>
      <thead><tr><th>Model</th><th>AUROC</th><th>Bal. Acc.</th><th>F1</th></tr></thead>
      <tbody>
        <tr>
          <td><span class="pill pill-sky">MiniROCKET + Ridge</span></td>
          <td class="text-emerald-300 font-bold">0.972</td>
          <td class="text-emerald-300 font-bold">0.936</td>
          <td class="text-emerald-300 font-bold">0.956</td>
        </tr>
        <tr>
          <td><span class="pill pill-prp">Inception CNN</span></td>
          <td>0.962</td><td>0.873</td><td>0.879</td>
        </tr>
        <tr>
          <td><span class="pill" style="background:rgba(100,116,139,0.2);color:#94a3b8;border-color:rgba(100,116,139,0.3)">Compact CNN</span></td>
          <td>0.973</td><td>0.857</td><td>0.845</td>
        </tr>
      </tbody>
    </table>
    <div class="p-2 bg-amber-900/20 border border-amber-700/30 rounded-lg mt-2 text-[11px] text-amber-300">
      ⚠️ MiniROCKET internal advantage is consistent, but the external comparison (17 participants) cannot confirm superiority.
    </div>
  </div>
  <div>
    <h2>Frozen RevalExo External (n=17)</h2>
    <table>
      <thead><tr><th>Model</th><th>AUROC</th><th>Brier</th><th>95% CI (AUROC Δ vs. Inception)</th></tr></thead>
      <tbody>
        <tr>
          <td><span class="pill pill-sky">MiniROCKET</span></td>
          <td>0.886</td><td class="text-rose-300">0.214</td>
          <td class="text-slate-400">−0.129 to +0.167</td>
        </tr>
        <tr>
          <td><span class="pill pill-prp">Inception CNN</span></td>
          <td>0.871</td><td class="text-emerald-300 font-bold">0.185</td>
          <td class="text-slate-400">—</td>
        </tr>
        <tr>
          <td><span class="pill pill-grn">Expanded Inception</span></td>
          <td class="text-emerald-300 font-bold">0.914</td><td>0.161</td>
          <td class="text-slate-400">—</td>
        </tr>
      </tbody>
    </table>
    <div class="p-2 bg-rose-900/20 border border-rose-700/30 rounded-lg mt-2 text-[11px] text-rose-300">
      🚫 Do NOT declare a winner. Paired bootstrap CI −0.129 to +0.167 — interval straddles zero. Keep both as co-primary candidates.
    </div>
  </div>
</div>

<div class="p-2 bg-slate-800/40 border border-slate-700/40 rounded-lg text-[11px] text-slate-400 mt-1">
  <strong class="text-slate-300">Calibration:</strong> Inception internal pooled Brier = 0.120 (ECE-10 = 0.182). MiniROCKET calibrated internal Brier = 0.060 (separate calibration run — not directly comparable to external Brier).
</div>

<div class="source-footer">Source: data/processed/architecture_comparison_summary.csv · data/processed/minirocket_calibration_summary.csv · reports/REVISED_MODEL_SELECTION_GATE.md · data/processed/pooled_inception_calibration.csv</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 9 — Expanded Pooled Training (Sint)
      ──────────────────────────────────────────────────────── -->

# Expanded Pooled Training — Sint Maartenskliniek

<div class="grid grid-cols-3 gap-3 my-3">
  <div class="p-3 rounded-xl bg-slate-800/80 border border-slate-700 text-center">
    <div class="text-2xl font-bold text-sky-400">0.966</div>
    <div class="text-[11px] text-slate-300 mt-0.5">Mean Internal AUROC</div>
    <div class="text-[10px] text-slate-400 mt-0.5">5-fold · Felius+Voisard+Sint</div>
  </div>
  <div class="p-3 rounded-xl bg-slate-800/80 border border-slate-700 text-center">
    <div class="text-2xl font-bold text-emerald-400">0.904</div>
    <div class="text-[11px] text-slate-300 mt-0.5">Mean Balanced Accuracy</div>
    <div class="text-[10px] text-slate-400 mt-0.5">Internal expanded OOF</div>
  </div>
  <div class="p-3 rounded-xl bg-slate-800/80 border border-violet-700/60 text-center">
    <div class="text-2xl font-bold text-violet-400">0.914</div>
    <div class="text-[11px] text-slate-300 mt-0.5">RevalExo AUROC (expanded)</div>
    <div class="text-[10px] text-slate-400 mt-0.5">vs. 0.871 original Inception</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div class="p-3 bg-slate-800/70 border border-sky-700/40 rounded-xl">
    <h3 class="text-sky-300">Why Sint Was Evaluated</h3>
    <ul class="text-xs text-slate-200 mt-1 space-y-0.5">
      <li>30 participants (20 healthy / 10 stroke) with audited Xsens → LB/LF/RF mapping</li>
      <li>First used as a blind external examination (AUROC 0.915, Brier 0.097)</li>
      <li>Then tested in a sensitivity experiment before unlocking RevalExo gate</li>
    </ul>
  </div>
  <div class="p-3 bg-slate-800/70 border border-emerald-700/40 rounded-xl">
    <h3 class="text-emerald-300">Paired RevalExo Bootstrap Gate</h3>
    <table>
      <thead><tr><th>Metric</th><th>Delta (Expanded − Original)</th><th>95% CI</th></tr></thead>
      <tbody>
        <tr><td>AUROC Δ</td><td class="text-emerald-300 font-semibold">+0.044</td><td>[0.000, +0.171]</td></tr>
        <tr><td>Brier Δ</td><td class="text-emerald-300 font-semibold">−0.022</td><td>[−0.040, −0.002]</td></tr>
      </tbody>
    </table>
    <div style="background: #0f172a; border: 1px solid #eab308; color: #fef08a;" class="p-2 mt-2 rounded text-[11px]">
      ✅ <strong>Decision Gate Passed:</strong> Brier CI excludes zero. Sint retained as training candidate. No clinical superiority claim (n=17 only).
    </div>
  </div>
</div>

<div class="source-footer">Source: data/processed/sint_sensitivity_inception_metrics.csv · data/processed/sint_revalexo_bootstrap_gate.csv · reports/SINT_SENSITIVITY_TRAINING.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 10 — External Robustness (RevalExo)
      ──────────────────────────────────────────────────────── -->

# External Robustness — Locked RevalExo Evaluation

<div class="grid grid-cols-4 gap-2 my-3">
  <div class="p-3 rounded-xl bg-slate-800/80 border border-slate-700 text-center">
    <div class="text-2xl font-bold text-violet-400">17</div>
    <div class="text-[11px] text-slate-300 mt-0.5">Total Participants</div>
    <div class="text-[10px] text-slate-400">7 Healthy · 10 Stroke</div>
  </div>
  <div class="p-3 rounded-xl bg-slate-800/80 border border-slate-700 text-center">
    <div class="text-2xl font-bold text-sky-400">0.914</div>
    <div class="text-[11px] text-slate-300 mt-0.5">Expanded AUROC</div>
    <div class="text-[10px] text-slate-400">Participant-level</div>
  </div>
  <div class="p-3 rounded-xl bg-slate-800/80 border border-slate-700 text-center">
    <div class="text-2xl font-bold text-amber-400">0.161</div>
    <div class="text-[11px] text-slate-300 mt-0.5">Brier Score</div>
    <div class="text-[10px] text-slate-400">Descriptive — not clinical</div>
  </div>
  <div class="p-3 rounded-xl bg-slate-800/80 border border-rose-700/50 text-center">
    <div class="text-2xl font-bold text-rose-400">4/7</div>
    <div class="text-[11px] text-slate-300 mt-0.5">Healthy False Positives</div>
    <div class="text-[10px] text-slate-400">at descriptive 0.5 cutoff</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div>
    <h2>Confusion Matrix — Expanded Inception (0.5 cutoff)</h2>
    <div class="grid grid-cols-3 gap-1.5 text-center text-xs max-w-xs mt-2">
      <div class="p-1.5 bg-slate-800 rounded"></div>
      <div class="p-1.5 bg-slate-800 font-semibold text-slate-300">Pred: Healthy</div>
      <div class="p-1.5 bg-slate-800 font-semibold text-slate-300">Pred: Stroke</div>
      <div class="p-1.5 bg-slate-800 font-semibold text-slate-300">True: Healthy</div>
      <div class="p-1.5 bg-emerald-500/20 border border-emerald-500/40 rounded font-bold text-emerald-300">TN: 3</div>
      <div class="p-1.5 bg-rose-500/20 border border-rose-500/30 rounded text-rose-300">FP: 4</div>
      <div class="p-1.5 bg-slate-800 font-semibold text-slate-300">True: Stroke</div>
      <div class="p-1.5 bg-rose-500/20 border border-rose-500/30 rounded text-rose-300">FN: 0</div>
      <div class="p-1.5 bg-emerald-500/20 border border-emerald-500/40 rounded font-bold text-emerald-300">TP: 10</div>
    </div>
    <p class="text-[10px] text-slate-400 mt-1">All 10 stroke participants correctly classified. 4/7 healthy = false positive.</p>
  </div>
  <div class="space-y-2">
    <div style="background: #1e293b; border: 1px solid rgba(244,63,94,0.4);" class="p-2.5 rounded-lg">
      <span class="text-[10px] font-bold text-rose-400 uppercase">False Positive Pattern</span>
      <p class="text-xs text-slate-300 mt-0.5">4 healthy subjects predicted as stroke (probabilities: 0.52–0.76). Likely older/slower walkers without individual-age confirmation.</p>
    </div>
    <div style="background: #0f172a; border: 1px solid #eab308; color: #fef08a;" class="p-2.5 rounded-lg">
      <span class="text-[10px] font-bold uppercase tracking-wider block mb-0.5">Confidence Limitation</span>
      <p class="text-xs text-amber-200">n=17 is insufficient for calibrated thresholding, subgroup analysis, or clinical validation. Treat as site/device robustness stress-test only.</p>
    </div>
  </div>
</div>

<div class="source-footer">Source: data/processed/full_expanded_prototype_revalexo_metrics.csv · data/processed/revalexo_external_error_analysis.csv</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 11 — Population Robustness
      ──────────────────────────────────────────────────────── -->

# Population Robustness Matrix

<table class="my-2 tiny-table">
  <thead><tr>
    <th>Scope / Population</th><th>N</th><th>Healthy</th><th>Stroke</th><th>AUROC</th><th>Brier</th><th>Bal. Acc.</th><th>Evidence Type</th>
  </tr></thead>
  <tbody>
    <tr class="text-emerald-100">
      <td><strong>Expanded Internal OOF</strong></td><td>314</td><td>126</td><td>188</td>
      <td class="text-emerald-300 font-bold">0.965</td><td>0.069</td><td class="text-emerald-300 font-bold">0.915</td>
      <td><span class="pill pill-sky">OOF — internal</span></td>
    </tr>
    <tr>
      <td>↳ Felius 2024</td><td>163</td><td>34</td><td>129</td><td>0.925</td><td>0.083</td><td>0.884</td>
      <td><span class="pill pill-sky">OOF — source slice</span></td>
    </tr>
    <tr>
      <td>↳ Sint Maartenskliniek</td><td>30</td><td>20</td><td>10</td><td>0.945</td><td>0.050</td><td>0.950</td>
      <td><span class="pill pill-sky">OOF — source slice</span></td>
    </tr>
    <tr>
      <td>↳ Voisard 2025</td><td>121</td><td>72</td><td>49</td><td>0.983</td><td>0.054</td><td>0.914</td>
      <td><span class="pill pill-sky">OOF — source slice</span></td>
    </tr>
    <tr class="text-violet-100">
      <td><strong>RevalExo External (locked)</strong></td><td>17</td><td>7</td><td>10</td>
      <td class="text-violet-300 font-bold">0.914</td><td class="text-amber-300">0.161</td><td class="text-amber-300">0.714</td>
      <td><span class="pill pill-prp">Independent external</span></td>
    </tr>
  </tbody>
</table>

<div class="grid grid-cols-3 gap-2.5 mt-2">
  <div class="p-2.5 bg-slate-800/50 border border-slate-700/40 rounded-lg">
    <span class="text-[10px] font-bold text-sky-400 uppercase">Source Diversity</span>
    <p class="text-xs text-slate-400 mt-0.5">3 sources, multiple sites and devices. Internal performance consistent across sources.</p>
  </div>
  <div class="p-2.5 bg-amber-900/20 border border-amber-700/30 rounded-lg">
    <span class="text-[10px] font-bold text-amber-400 uppercase">Demographic Diversity ≠ Source Diversity</span>
    <p class="text-xs text-slate-400 mt-0.5">No linked age/sex for most participants. Age-stratified and sex-stratified results are NOT available.</p>
  </div>
  <div class="p-2.5 bg-rose-900/20 border border-rose-700/30 rounded-lg">
    <span class="text-[10px] font-bold text-rose-400 uppercase">Non-Stroke Specificity Gap</span>
    <p class="text-xs text-slate-400 mt-0.5">Current training population = stroke + healthy only. No test against PD, MS, COPD, fracture.</p>
  </div>
</div>

<div class="source-footer">Source: data/processed/population_robustness_matrix.csv · reports/POPULATION_ROBUSTNESS_MATRIX.html · reports/DEMOGRAPHIC_CLINICAL_POPULATION_COVERAGE.html</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 12 — Demographic Subgroup Gate
      ──────────────────────────────────────────────────────── -->

# Demographic Subgroup Gate

<div class="grid grid-cols-[1.1fr_0.9fr] gap-3.5 my-2 items-start">
  <div>
    <h2>Age-Band Coverage (Binary Labels Only)</h2>
    <table class="w-full">
      <thead><tr><th>Age Band</th><th>CVA (Stroke)</th><th>HS (Healthy)</th><th>Stroke AUROC</th><th>Status</th></tr></thead>
      <tbody>
        <tr>
          <td class="font-medium">18–39 (Young)</td>
          <td class="text-rose-400 font-bold">0</td>
          <td class="text-emerald-300">43</td>
          <td class="text-slate-400">N/A</td>
          <td><span class="pill pill-red">❌ Cannot estimate</span></td>
        </tr>
        <tr>
          <td class="font-medium">40–59 (Middle)</td>
          <td class="text-amber-300">27</td>
          <td class="text-amber-300">15</td>
          <td class="text-amber-300 font-semibold">0.953 (exploratory)</td>
          <td><span class="pill pill-amb">⚠️ Small / imbalanced</span></td>
        </tr>
        <tr>
          <td class="font-medium">60+ (Older)</td>
          <td class="text-amber-300">22</td>
          <td class="text-amber-300">15</td>
          <td class="text-amber-300 font-semibold">0.913 (exploratory)</td>
          <td><span class="pill pill-amb">⚠️ Small / imbalanced</span></td>
        </tr>
      </tbody>
    </table>
    <div style="background: #161e2e; border: 1px solid #334155;" class="p-2 rounded-lg mt-2 text-[10.5px]">
      <strong class="text-sky-300">Required Next Data:</strong> ≥20–30 participants per class per band. Mandatory next step is verifying subject-level age/sex linkage across sources.
    </div>
  </div>

  <div class="space-y-2">
    <div style="background: #201217; border: 1px solid #be123c;" class="p-2.5 rounded-xl">
      <h3 class="text-rose-400 font-bold text-xs">🚫 Critical Gap: Young Stroke</h3>
      <p class="text-[11px] text-slate-200 mt-0.5 leading-snug">Zero stroke participants aged 18–39. 43 healthy subjects in this band creates severe age confounding — the model has never seen young stroke gait.</p>
    </div>
    <div style="background: #1e1b13; border: 1px solid #b45309;" class="p-2.5 rounded-xl">
      <h3 class="text-amber-400 font-bold text-xs">⚠️ Fairness Claim Blocked</h3>
      <p class="text-[11px] text-slate-200 mt-0.5 leading-snug"><strong>Age-generalisation & fairness claims are NOT supported.</strong> Sex linkage is also incomplete. Current results reflect exploratory confound analyses only.</p>
    </div>
  </div>
</div>

<div class="source-footer">Source: data/processed/age_group_label_availability.csv · reports/DEMOGRAPHIC_SUBGROUP_VALIDATION_GATE.html · data/processed/age_stratified_gait_results.csv</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 13 — Mobilise-D Clinical Specificity
      ──────────────────────────────────────────────────────── -->

# Mobilise-D Clinical Specificity Stress-Test

<div class="grid grid-cols-3 gap-3 my-3">
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-rose-700/40 text-center">
    <div class="text-2xl font-bold text-rose-400">2,315</div>
    <div class="text-[11px] text-slate-400 mt-0.5">Participants (visit-level)</div>
    <div class="text-[10px] text-slate-500 mt-0.5">COPD · MS · PD · PFF</div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-sky-700/40 text-center">
    <div class="text-2xl font-bold text-sky-400">0.713</div>
    <div class="text-[11px] text-slate-400 mt-0.5">Visit-Level Balanced Acc.</div>
    <div class="text-[10px] text-slate-500 mt-0.5">22 DMO features · 5-fold CV</div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-emerald-700/40 text-center">
    <div class="text-2xl font-bold text-emerald-400">0.717</div>
    <div class="text-[11px] text-slate-400 mt-0.5">Bout-Level Balanced Acc.</div>
    <div class="text-[10px] text-slate-500 mt-0.5">16M bouts · 17 features</div>
  </div>
</div>

<div class="grid grid-cols-2 gap-3">
  <div class="p-3 bg-slate-800/50 border border-rose-700/30 rounded-xl">
    <h3 class="text-rose-300">Why NOT Pooled Into Training</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>CVS release contains <strong>processed digital mobility outcomes (DMO)</strong> from a single back-worn sensor — NOT raw bilateral LB/LF/RF windows</li>
      <li>No stroke or healthy-control cohort exists in CVS</li>
      <li>No representation-matching experiment has been performed</li>
      <li>Pooling would require fabricating missing bilateral channels</li>
    </ul>
  </div>
  <div class="p-3 bg-slate-800/50 border border-sky-700/30 rounded-xl">
    <h3 class="text-sky-300">Value as Stress-Test Resource</h3>
    <ul class="text-xs text-slate-300 mt-1 space-y-0.5">
      <li>Clinical DMO features (walking speed, cadence, stride length) distinguish COPD/MS/PD/PFF cohorts with ~0.71 balanced accuracy</li>
      <li>Bout-level vs. visit-level difference is small (+0.004) — no new training pathway justified</li>
      <li>Demonstrates that non-stroke clinical populations produce measurably different mobility signatures</li>
      <li>Required for <em>future</em> false-positive specificity testing before clinical deployment</li>
    </ul>
  </div>
</div>

<div class="source-footer">Source: data/processed/mobilise_d_clinical_cohort_benchmark_metrics.json · data/processed/mobilise_d_bout_cohort_benchmark_metrics.json · reports/MOBILISE_D_CLINICAL_COHORT_BENCHMARK.md · reports/MOBILISE_D_CVS_COMPATIBILITY_AUDIT.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 14 — Failure Analysis & Diagnostics
      ──────────────────────────────────────────────────────── -->

# Failure Analysis & Explainability

<div class="grid grid-cols-2 gap-3 mt-1">
  <!-- Top Left: Error Table -->
  <div style="background: #161e2e; border: 1px solid #334155;" class="p-2 rounded-xl">
    <h3 class="text-sky-300 text-xs font-bold mb-0.5">Per-Dataset Error Breakdown (Internal)</h3>
    <table class="tiny-table" style="width: 100%;">
      <thead>
        <tr><th>Model</th><th>Dataset</th><th>Sens.</th><th>Spec.</th><th>FP</th><th>FN</th></tr>
      </thead>
      <tbody>
        <tr><td>Inception</td><td>Felius</td><td>0.837</td><td>0.853</td><td>5</td><td>21</td></tr>
        <tr><td>Inception</td><td>Voisard</td><td>0.776</td><td>0.958</td><td>3</td><td>11</td></tr>
        <tr><td>MiniROCKET</td><td>Felius</td><td class="text-emerald-300 font-bold">0.984</td><td>0.824</td><td>6</td><td class="text-emerald-300 font-bold">2</td></tr>
        <tr><td>MiniROCKET</td><td>Voisard</td><td class="text-emerald-300 font-bold">0.918</td><td>0.944</td><td>4</td><td class="text-emerald-300 font-bold">4</td></tr>
      </tbody>
    </table>
    <p class="text-[8.5px] text-slate-400 mt-0.5">0.5 cutoff is descriptive only. Speed metadata missing for error stratification.</p>
  </div>

  <!-- Top Right: Occlusion Table -->
  <div style="background: #161e2e; border: 1px solid #334155;" class="p-2 rounded-xl">
    <h3 class="text-violet-300 text-xs font-bold mb-0.5">Channel Occlusion (Fold-0 Only)</h3>
    <table class="tiny-table" style="width: 100%;">
      <thead>
        <tr><th>Channel</th><th>Mean |ΔP|</th><th>Signed Δ</th><th>Rank</th></tr>
      </thead>
      <tbody>
        <tr><td><span class="pill pill-sky">LB</span> Lower Back</td><td class="text-emerald-300 font-bold">0.188</td><td>+0.130</td><td>🥇 1st</td></tr>
        <tr><td><span class="pill pill-prp">RF</span> Right Foot</td><td>0.104</td><td>−0.039</td><td>🥈 2nd</td></tr>
        <tr><td><span class="pill pill-grn">LF</span> Left Foot</td><td>0.090</td><td>+0.028</td><td>🥉 3rd</td></tr>
      </tbody>
    </table>
    <p class="text-[8.5px] text-amber-300 mt-0.5">⚠️ Single fold only. Cross-fold temporal attribution pending.</p>
  </div>
</div>

<!-- Bottom Row: The Two Diagnosis Cards -->
<div class="grid grid-cols-2 gap-3 mt-2">
  <div style="background: #201217; border: 1px solid #be123c;" class="p-2 rounded-xl">
    <h3 class="text-rose-400 text-xs font-bold mb-0.5">RevalExo False Positive Pattern</h3>
    <p class="text-[10px] text-slate-200 leading-snug">4/7 healthy classified as stroke (prob: 0.52–0.76). Likely older/slower walkers without individual-age confirmation.</p>
  </div>

  <div style="background: #1e1b13; border: 1px solid #b45309;" class="p-2 rounded-xl">
    <h3 class="text-amber-400 text-xs font-bold mb-0.5">Domain Shift & Speed Confound</h3>
    <p class="text-[10px] text-slate-200 leading-snug">CNN sensitivity drops in Voisard vs. Felius; MiniROCKET is more balanced. Missing trial speed prevents speed-stratified validation.</p>
  </div>
</div>

<div class="source-footer">Source: reports/PARTICIPANT_ERROR_ANALYSIS.md · reports/INCEPTION_OCCLUSION_ANALYSIS.md · data/processed/revalexo_external_error_analysis.csv</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 15 — Research Sufficiency vs. Gaps
      ──────────────────────────────────────────────────────── -->

# Research Sufficiency vs. Clinical Deployment Gaps

<div class="grid grid-cols-2 gap-3 my-2">
  <div style="background: #1e293b; border: 1px solid rgba(16,185,129,0.4);" class="p-3 rounded-xl">
    <h2 class="text-emerald-400 font-bold text-sm mb-1">✅ Sufficient for Research Prototype</h2>
    <div class="space-y-1 text-xs">
      <div><span class="font-bold text-emerald-300">✓ Binary stroke/healthy discrimination</span><span class="text-slate-300 text-[10.5px] block">AUROC 0.965 internal · 0.914 external (RevalExo)</span></div>
      <div><span class="font-bold text-emerald-300">✓ Leakage-controlled validation</span><span class="text-slate-300 text-[10.5px] block">GroupKFold · fold-specific normalization · locked external test</span></div>
      <div><span class="font-bold text-emerald-300">✓ Multi-source wearable-IMU benchmark</span><span class="text-slate-300 text-[10.5px] block">Felius + Voisard + Sint (n=314) with site diversity</span></div>
      <div><span class="font-bold text-emerald-300">✓ Locked external test</span><span class="text-slate-300 text-[10.5px] block">Independent RevalExo site · paired bootstrap gate</span></div>
      <div><span class="font-bold text-emerald-300">✓ Non-stroke clinical stress testing</span><span class="text-slate-300 text-[10.5px] block">2,315 Mobilise-D cohort participants</span></div>
    </div>
  </div>

  <div style="background: #1e293b; border: 1px solid rgba(244,63,94,0.4);" class="p-3 rounded-xl">
    <h2 class="text-rose-400 font-bold text-sm mb-1">🚫 Gaps Blocking Clinical Deployment</h2>
    <div class="space-y-1 text-xs">
      <div><span class="font-bold text-rose-300">✗ No validated decision threshold</span><span class="text-slate-300 text-[10.5px] block">0.5 cutoff is descriptive only — no prospective trial</span></div>
      <div><span class="font-bold text-rose-300">✗ Subgroup fairness unresolved</span><span class="text-slate-300 text-[10.5px] block">No stroke participants aged 18–39; metadata incomplete</span></div>
      <div><span class="font-bold text-rose-300">✗ Non-stroke specificity untested</span><span class="text-slate-300 text-[10.5px] block">Never evaluated against PD, MS, COPD, or fracture gait</span></div>
      <div><span class="font-bold text-rose-300">✗ Speed independence unconfirmed</span><span class="text-slate-300 text-[10.5px] block">865 trials with missing speed — potential confounder</span></div>
      <div><span class="font-bold text-rose-300">✗ External sample underpowered</span><span class="text-slate-300 text-[10.5px] block">n=17 is too small to declare architecture superiority</span></div>
    </div>
  </div>
</div>

<div class="source-footer">Source: docs/BASELINE_REQUIREMENTS_AUDIT.md · reports/DATA_SUFFICIENCY_AND_PUBLIC_SOURCE_REVIEW.html · reports/REVISED_MODEL_SELECTION_GATE.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 16 — Final Synthesis
      ──────────────────────────────────────────────────────── -->

# Final Synthesis

<div class="grid grid-cols-3 gap-3 my-3">
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-sky-700/60 text-center">
    <div class="text-[10px] text-sky-400 font-bold uppercase tracking-wider mb-1">Best Internal Result</div>
    <div class="text-3xl font-bold text-sky-400">0.965</div>
    <div class="text-[11px] text-slate-300 mt-0.5">AUROC · 314 participants</div>
    <div class="text-[10px] text-slate-500 mt-0.5">Expanded Inception · OOF</div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-violet-700/60 text-center">
    <div class="text-[10px] text-violet-400 font-bold uppercase tracking-wider mb-1">Best External Result</div>
    <div class="text-3xl font-bold text-violet-400">0.914</div>
    <div class="text-[11px] text-slate-300 mt-0.5">AUROC · 17 participants (locked)</div>
    <div class="text-[10px] text-slate-500 mt-0.5">RevalExo · Brier = 0.161</div>
  </div>
  <div class="p-3.5 rounded-xl bg-slate-800/60 border border-amber-700/50 text-center">
    <div class="text-[10px] text-amber-400 font-bold uppercase tracking-wider mb-1">Key Limitation</div>
    <div class="text-xl font-bold text-amber-400 leading-tight mt-1">n=17</div>
    <div class="text-[11px] text-slate-300 mt-0.5">External cohort — too small for model selection, clinical validation, or age/sex subgroups</div>
  </div>
</div>

<div class="p-4 bg-slate-800/50 border border-sky-700/40 rounded-xl">
  <h2>Verified Research Claim</h2>
  <p class="text-sm text-slate-200 mt-1 leading-relaxed">
    "The current system is a <strong class="text-sky-300">promising research prototype</strong> for participant-level stroke-versus-healthy gait discrimination across multiple public wearable-IMU sources (Felius + Voisard + Sint; AUROC 0.965 internal). An independent external stress-test on RevalExo (n=17) yields AUROC 0.914. <strong class="text-amber-300">Age-stratified, sex-stratified, non-stroke clinical specificity, and clinical deployment evidence remain incomplete.</strong> Both Inception and MiniROCKET are co-primary candidates — no winner is declared."
  </p>
</div>

<div class="grid grid-cols-2 gap-3 mt-2">
  <div class="p-2.5 bg-emerald-900/15 border border-emerald-700/30 rounded-lg text-xs text-slate-300">
    <strong class="text-emerald-400">What can be published now:</strong> Methodology, internal benchmark, external RevalExo result, limitations, and roadmap.
  </div>
  <div class="p-2.5 bg-rose-900/15 border border-rose-700/30 rounded-lg text-xs text-slate-300">
    <strong class="text-rose-400">What must NOT be claimed:</strong> Clinical readiness, age fairness, superiority of either model, or speed independence.
  </div>
</div>

<div class="source-footer">Source: data/processed/population_robustness_matrix.csv · reports/FULL_EXPANDED_PROTOTYPE_BENCHMARK.md · reports/REVISED_MODEL_SELECTION_GATE.md · docs/BASELINE_REQUIREMENTS_AUDIT.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 17 — Recommended Next Steps
      ──────────────────────────────────────────────────────── -->

# Recommended Next Steps

<div class="grid grid-cols-4 gap-2.5 my-3">
  <div class="p-3 bg-slate-800/70 border border-sky-700/50 rounded-xl">
    <div class="text-sky-400 font-bold text-[11px] uppercase tracking-wider mb-1">① Lock Baseline</div>
    <p class="text-xs text-slate-300">Freeze current expanded Inception checkpoint + MiniROCKET as co-primary candidates. Log exact hashes. No further model changes without new external evidence.</p>
  </div>
  <div class="p-3 bg-slate-800/70 border border-emerald-700/50 rounded-xl">
    <div class="text-emerald-400 font-bold text-[11px] uppercase tracking-wider mb-1">② Link Demographics</div>
    <p class="text-xs text-slate-300">Obtain subject-level age and sex for Felius, Voisard, Sint. Verify linkage against existing participant IDs. Enable age-stratified exploratory analysis.</p>
  </div>
  <div class="p-3 bg-slate-800/70 border border-violet-700/50 rounded-xl">
    <div class="text-violet-400 font-bold text-[11px] uppercase tracking-wider mb-1">③ Audit MIMU 85/97</div>
    <p class="text-xs text-slate-300">Audit the 85-stroke / 97-healthy wearable-MIMU dataset as a potential age-labelled independent cohort. Verify channel compatibility before pooling or evaluation.</p>
  </div>
  <div class="p-3 bg-slate-800/70 border border-rose-700/50 rounded-xl">
    <div class="text-rose-400 font-bold text-[11px] uppercase tracking-wider mb-1">④ Non-Stroke Specificity</div>
    <p class="text-xs text-slate-300">Apply frozen model to Mobilise-D-compatible cohort after representation audit. Measure false-positive rate against PD/MS/COPD/fracture — required for any clinical claim.</p>
  </div>
</div>

<div class="grid grid-cols-2 gap-3 mt-1">
  <div class="p-3 bg-slate-800/40 border border-slate-700/40 rounded-xl">
    <h3 class="text-slate-300">Additional Priorities (Ordered)</h3>
    <ol class="text-xs text-slate-400 mt-1 space-y-0.5 list-decimal list-inside">
      <li>Complete cross-fold temporal channel occlusion for Inception</li>
      <li>Improve external calibration — ECE-10 currently 0.182 (pooled internal)</li>
      <li>Obtain walking-speed metadata or perform cadence-stratified analysis</li>
      <li>Pre-specify equivalence margin for model-selection design (e.g., ±0.03 AUROC)</li>
      <li>Only then: package for clinical prototype evaluation</li>
    </ol>
  </div>
  <div class="p-3 bg-slate-800/40 border border-amber-700/30 rounded-xl">
    <h3 class="text-amber-300">Data Acquisition Guardrails</h3>
    <ul class="text-xs text-slate-400 mt-1 space-y-0.5">
      <li>❌ Do NOT pool Mobilise-D, PiG, or Triaxial without channel-compatibility verification</li>
      <li>❌ Do NOT assign synthetic stroke labels to healthy-only datasets</li>
      <li>❌ Do NOT use RevalExo for any fitting, threshold, or calibration decision</li>
      <li>✅ Any new source must pass blind external audit before sensitivity training</li>
    </ul>
  </div>
</div>

<div class="source-footer">Source: docs/BASELINE_REQUIREMENTS_AUDIT.md · reports/PUBLIC_DATASET_ROLE_MATRIX.md · reports/DATA_SUFFICIENCY_AND_PUBLIC_SOURCE_REVIEW.html · reports/MOBILISE_D_CVS_COMPATIBILITY_AUDIT.md</div>

---

<!--  ──────────────────────────────────────────────────────────
      SLIDE 18 — Reproducibility Appendix
      ──────────────────────────────────────────────────────── -->

# Reproducibility Appendix

<div class="grid grid-cols-2 gap-4 my-0.5">
  <div>
    <h2>Key Artefacts</h2>
    <table class="tiny-table" style="width: 100%;">
      <thead>
        <tr><th style="width: 18%;">Type</th><th style="width: 54%;">Path / Filename</th><th style="width: 28%;">Produces</th></tr>
      </thead>
      <tbody>
        <tr><td>Script</td><td class="text-sky-300">train_sint_sensitivity.py</td><td>Sint fold weights</td></tr>
        <tr><td>Script</td><td class="text-sky-300">train_full_expanded.py</td><td>Full prototype</td></tr>
        <tr><td>Script</td><td class="text-sky-300">benchmark_full_expanded.py</td><td>RevalExo metrics</td></tr>
        <tr><td>Script</td><td class="text-sky-300">build_population_matrix.py</td><td>Robustness matrix</td></tr>
        <tr><td>Script</td><td class="text-sky-300">benchmark_mobilise_d.py</td><td>Mobilise-D DMO</td></tr>
        <tr><td>Notebook</td><td class="text-emerald-300">08_robust_pooled_training.ipynb</td><td>Internal benchmark</td></tr>
        <tr><td>Notebook</td><td class="text-emerald-300">26_frozen_external_revalexo.ipynb</td><td>Locked eval</td></tr>
        <tr><td>Notebook</td><td class="text-emerald-300">28_revalexo_error_analysis.ipynb</td><td>Domain shift</td></tr>
      </tbody>
    </table>
  </div>

  <div>
    <h2>Key Executed Metrics</h2>
    <table class="tiny-table" style="width: 100%;">
      <thead>
        <tr><th style="width: 52%;">Metric File</th><th style="width: 32%;">Key Metric</th><th style="width: 16%;">Value</th></tr>
      </thead>
      <tbody>
        <tr><td>population_robustness_matrix.csv</td><td>Expanded OOF AUROC</td><td class="text-emerald-300 font-bold">0.965</td></tr>
        <tr><td>full_expanded_revalexo_metrics.csv</td><td>RevalExo AUROC</td><td class="text-violet-300 font-bold">0.914</td></tr>
        <tr><td>sint_revalexo_bootstrap_gate.csv</td><td>AUROC Δ 95% CI</td><td class="text-amber-300">[0.00, +0.17]</td></tr>
        <tr><td>architecture_comparison.csv</td><td>MiniROCKET AUROC</td><td class="text-sky-300 font-bold">0.972</td></tr>
        <tr><td>mobilise_d_clinical_cohorts.json</td><td>Clinical Bal. Acc.</td><td class="text-sky-300">0.713</td></tr>
        <tr><td>age_group_availability.csv</td><td>CVA Age 18–39</td><td class="text-rose-400 font-bold">0</td></tr>
        <tr><td>INCEPTION_OCCLUSION_ANALYSIS.md</td><td>LB Mean |ΔP|</td><td class="text-sky-300">0.188</td></tr>
        <tr><td>pooled_inception_calibration.csv</td><td>Pooled Brier</td><td class="text-amber-300">0.120</td></tr>
      </tbody>
    </table>
    <p class="text-[9px] text-slate-400 mt-1 leading-tight">
      <strong class="text-amber-400">Model weights:</strong> <code>full_expanded_inception_prototype_seed_42.pt</code> · <code>minirocket_ridge_fold_*_seed_42.joblib</code>
    </p>
  </div>
</div>

<div class="source-footer">Source: all files listed above · see reports/REVISED_MODEL_SELECTION_GATE.md and docs/BASELINE_REQUIREMENTS_AUDIT.md</div>
