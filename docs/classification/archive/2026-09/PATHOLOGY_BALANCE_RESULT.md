# Pathology balance: completed comparison

Executed 2026-09-09 under the [pre-fit protocol](../../PATHOLOGY_BALANCE.md).
Twenty-four fits completed with participant-disjoint inner folds and the existing
outer pathology holdouts. All 259 full-cohort and 144 matched-cohort rows retained.
Ten existing features reused, no acquisition or preprocessing changes.

| Scope / weighting | Stroke detected / 49 | Healthy FP | Neurological FP |
|---|---:|---:|---:|
| Full / current | 45 | 6/72 | 56/94 (59.6%) |
| Full / pathology-balanced | 44 | 7/72 | 52/94 (55.3%) |
| Matched / current | 44 | 5/19 | 47/76 (61.8%) |
| Matched / pathology-balanced | 44 | 5/19 | 48/76 (63.2%) |

All 44 orthopedic controls remained negative in both full-cohort arms. Consequently
the full-cohort *all-other* FPR changed from 56/138 (40.6%) to 52/138 (37.7%).
Do not confuse that denominator with the neurological-only denominator above.
Full CIPN positives changed 13/19 to 10/19, PD stayed 13/24 and RIL changed 30/51
to 29/51. Matched CIPN worsened 11/18 to 12/18, PD stayed 11/19 and RIL 25/39.

**Decision: do not replace stroke-phase-hr-v0.1.0.** The fixed replacement rule
failed in both scopes. The full-cohort reduction costs an additional missed stroke
and healthy false positive, and does not reproduce in the matched subset.
This particular weighting change is insufficient. It neither excludes other forms
of confounding nor proves that imbalance is the unique cause of the errors.
Do not rerun a weighting sweep from this result.

The comparison reuses development participants and historically inspected folds.
It is not a fresh external test. Inner folds are participant-disjoint but can share
pathology groups; outer non-stroke pathology holdouts remain enforced. Thresholds
are selected only from each outer training set's inner stroke predictions at a
90% target. The packaged full-fit threshold is not used for these metrics.

Artifacts: `data/processed/pathology_balance_v1/` contains the pre-fit source hashes,
inner and outer predictions, thresholds, outer training pathology-weight totals,
metrics, per-pathology counts and gate decision. The runner also checks cohort and
fold identity against the verified baseline. Two synthetic regression tests check
weight invariance to pathology-group duplication and fixed total class masses.

Reproduce with:

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe scripts/classification/compare_pathology_balance.py
```

The existing prototype remains available for feature-CSV research workflows.
Independent validation and sensor-only recovery of its annotation-assisted features
remain open. This result adds no new evidence for either capability.
