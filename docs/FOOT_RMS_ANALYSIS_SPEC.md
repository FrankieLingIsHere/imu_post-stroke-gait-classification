# Specification: Foot RMS Cross-Dataset Generalization Analysis

**Target notebook:** `01_post_stroke_gait_baseline.ipynb`
**Purpose:** Close the single most predictable reviewer objection to the manuscript — that foot RMS was never entered into the cross-dataset generalization check that lower-back RMS passed, despite four of five healthy-reference datasets providing a usable foot or ankle channel.

---

## 0. Context (read before implementing)

The manuscript currently reports:

| Feature | Within Voisard | Within Felius | Pooled cross-dataset |
|---|---|---|---|
| Lower-back RMS | r = 0.566 (age-adj.) | corroborated | **r = 0.904** (5 datasets) / **r = 0.951** (3 genuine-trunk only) |
| Foot RMS | r = 0.719 (age-adj.) | r = 0.79 | **NOT COMPUTED** ← this task |

Foot RMS is *more* discriminative than lower-back RMS within both real stroke datasets, but has never been tested against the independent healthy-reference pool. The manuscript currently states this gap is due to the extraction pipeline not computing a foot RMS feature for the healthy-reference datasets, not due to data unavailability.

**Goal:** compute foot RMS for the healthy-reference datasets that support it, then run the identical participant-level pooled comparison already used for lower-back RMS.

---

## 1. Dataset eligibility

Determine foot/ankle channel availability from the actual data files, not from assumption. Expected (verify each):

| Dataset | Role | Expected foot/ankle channel | Include? |
|---|---|---|---|
| Voisard | stroke | bilateral foot | Yes — already computed |
| Felius | stroke | bilateral foot | Yes — already computed |
| DUO-GAIT | healthy ref | bilateral foot | Yes — genuine foot |
| Camargo | healthy ref | foot | Yes — genuine foot |
| GaitMotion | healthy ref | foot | Yes — genuine foot |
| MAREA | healthy ref | bilateral **ankle** | Yes — **flag as substitute** |
| OxWalk | healthy ref | hip, wrist only | **No** — exclude, no distal channel |

**Important:** MAREA provides ankle, not foot. Treat this exactly as the manuscript treats OxWalk's hip and GaitMotion's foot as *trunk* substitutes — i.e. include it in the main pooled figure but also report a substitute-free variant. If any dataset's channel turns out to differ from the table above, report that rather than forcing it into a category.

---

## 2. Feature computation requirements

Compute foot RMS using **exactly the same procedure already used for `lb_accel_rms`**, so the two are directly comparable. Locate that existing computation in the notebook and mirror it. Specifically:

1. **Unit conversion** — convert to `g` before computing, same as existing pipeline.
2. **Walking-span restriction** — restrict to the same straight-walking span used for the corrected lower-back RMS. Do **not** compute over the whole raw file (idle padding + u-turn included). This was a corrected defect in an earlier version; do not reintroduce it.
3. **Participant-level aggregation** — one row per participant, never per trial. Collapse repeated trials/visits per participant before any statistical test.
4. **Bilateral handling** — where a dataset provides both left and right foot, use the **same aggregation the existing Voisard/Felius foot RMS computation already uses** (check whether it averages, takes the affected side, or takes the max — then match it). Do not invent a new convention.
5. **Duplicate exclusion** — apply the same S001P duplicate-participant exclusion already applied elsewhere.

If any of these cannot be matched exactly for a given dataset, stop and report the mismatch rather than substituting an approximation.

---

## 3. Analyses to run

### 3.1 Primary pooled comparison
Pooled stroke (Voisard + Felius foot RMS) vs. pooled healthy reference (DUO-GAIT + Camargo + GaitMotion + MAREA).

Use the **same statistical procedure as the existing pooled trunk RMS test**:
- Mann-Whitney U test
- Rank-biserial correlation `r` as effect size
- 95% CI (match the existing method — bootstrap or analytic, whichever the notebook already uses)
- Report: `r`, 95% CI, `p`, `n_stroke`, `n_healthy`

### 3.2 Substitute-free variant
Same test, healthy reference restricted to **genuine foot channels only** (DUO-GAIT, Camargo, GaitMotion — excluding MAREA's ankle).

This mirrors the existing trunk-only restricted analysis (r = 0.951, n_healthy = 58) and is required for symmetry: the manuscript must not apply a stricter evidentiary standard to trunk than to foot.

### 3.3 Per-dataset breakdown
Foot RMS in pooled stroke vs. **each individual healthy dataset separately**. Report `r` and `p` for each.

The manuscript claims lower-back RMS is "significant against every individual healthy dataset with no exception." The same claim must be checkable for foot RMS.

### 3.4 Healthy-reference medians
Report median foot RMS and SD per healthy dataset, plus `n`, plus pooled stroke median.

This mirrors the existing per-dataset trunk medians disclosure (DUO-GAIT 1.06 g, MAREA 1.12 g, etc.) that discloses between-dataset spread.

### 3.5 Re-run FDR correction
Family 4 (pooled cross-dataset comparison) currently contains 6 features and is corrected via `scipy`'s `false_discovery_control` / Benjamini-Hochberg.

**Add foot RMS as a 7th feature and re-run the correction for that family.** Report updated q-values for all 7. Confirm explicitly whether any feature's significance status changes as a result.

---

## 4. Required output format

Print a single consolidated block containing:

```
=== FOOT RMS CROSS-DATASET GENERALIZATION ===

[3.1] Primary pooled (4 healthy datasets, incl. MAREA ankle substitute)
  r = ...  95% CI [..., ...]  p = ...  n_stroke = ...  n_healthy = ...

[3.2] Substitute-free (3 genuine-foot datasets only)
  r = ...  95% CI [..., ...]  p = ...  n_stroke = ...  n_healthy = ...

[3.3] Per-dataset breakdown (pooled stroke vs. each healthy dataset)
  DUO-GAIT    r = ...  p = ...  n_healthy = ...
  Camargo     r = ...  p = ...  n_healthy = ...
  GaitMotion  r = ...  p = ...  n_healthy = ...
  MAREA       r = ...  p = ...  n_healthy = ...   [ankle substitute]

[3.4] Healthy-reference medians (foot RMS, g)
  DUO-GAIT    median = ...  SD = ...  n = ...
  Camargo     median = ...  SD = ...  n = ...
  GaitMotion  median = ...  SD = ...  n = ...
  MAREA       median = ...  SD = ...  n = ...   [ankle substitute]
  Pooled stroke median = ...

[3.5] FDR re-run, Family 4 (now 7 features)
  feature                 p = ...      q = ...   significant_after_FDR = ...
  ... (all 7)
  Any feature flips significant -> non-significant: ...
  Any feature flips non-significant -> significant: ...

[SANITY] Comparison to existing trunk RMS figures
  trunk RMS pooled (5 ds):        r = 0.904
  trunk RMS genuine-channel (3):  r = 0.951
  foot RMS pooled (4 ds):         r = ...
  foot RMS genuine-channel (3):   r = ...
```

---

## 5. Constraints and cautions

- **Do not modify any existing cell's output or existing computed values.** Add new cells. The manuscript already cites the existing figures; silently changing them would break traceability.
- **Do not train any classifier.** The manuscript explicitly states this strand is scoped to feature validation, not classifier development. Adding classification would contradict a claim now made in the Abstract, Introduction, Section 3.8, and Conclusion.
- **Report failures rather than working around them.** If a dataset's foot channel is unusable (missing, corrupt, wrong orientation, unresolvable units), report that explicitly and exclude it with a stated reason. An honest `n = 3 datasets` is publishable; a silently patched `n = 4` is not.
- **Flag any result that contradicts the manuscript.** If foot RMS does *not* generalize, that is a legitimate and useful finding — it would establish trunk's advantage rather than leaving it open. Do not tune the analysis toward the expected answer.
- **Add a markdown cell** above the new code documenting: date added, purpose, and which manuscript claim it addresses (Section 4.2.5 / 4.2.6 foot-vs-trunk scope asymmetry).

---

## 6. What happens after

Send the full printed output block back. It will be written into:
- **Section 4.2.5** — the foot-vs-trunk scope comparison (currently states foot was not cross-validated)
- **Section 4.2.6** — pooled generalization results table and narrative
- **Section 3.8** — updated FDR family 4 description (6 → 7 features, updated q-values)
- **Figure 5, Panel A** — add foot RMS as an additional row
- **Abstract and Conclusion** — the foot-vs-trunk framing, which currently says the two "differ in scope rather than identifying a winner"

Depending on the result, the manuscript's placement conclusion may change substantively in either direction. Both outcomes are publishable; the current gap is not.
