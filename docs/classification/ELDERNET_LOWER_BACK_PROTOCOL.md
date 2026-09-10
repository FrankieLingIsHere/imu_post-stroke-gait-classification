# ElderNet lower-back transfer: locked first experiment

Locked 2026-09-09 before fitting. Test a frozen pretrained encoder plus a newly
trained stroke head against the identical frozen randomly initialized encoder
plus the same trained head. This is a linear-probe transfer experiment, not
end-to-end fine-tuning. One initialization seed (20260909), no parameter sweep.

Use all previously selected Voisard trials and genuine raw lower-back XYZ in g,
packet-aligned with the existing loader. Never duplicate magnitude into XYZ.
Use supplied straight-walking event bounds, never join across turns. Cut complete
10-second windows, 5-second stride, and resample each using polyphase anti-aliasing
100 to 30 Hz. No padding/stretching of short bouts. Keep missing participants in
the coverage ledger by diagnosis, report metrics only on available participants.
This can preferentially retain slower walkers; no whole-cohort performance claim.

Use the pinned ElderNet gait-speed backbone and 128-dimensional FC representation,
discard its speed regressor. Freeze all parameters and batch-normalization state.
Average window embeddings within each trial, then trials within each participant.
Same input, pooling and head for both arms. No nuisance or diagnosis inputs.

Head: training-only StandardScaler and LogisticRegression C=1, max_iter=3000,
healthy/stroke/other total training masses .25/.50/.25. Existing three outer folds,
whole non-stroke pathology holdouts, inner three target-stratified participant
folds seed 20260909. Select threshold only from inner stroke OOF scores to target
90% sensitivity. Run full available and existing matched available scopes.
Abort a scope if any outer or inner training split lacks a target group.

Report TP/FN, healthy/other/neurological FP, AUROC, coverage and paired prediction
changes. Candidate is promising only if both scopes reduce neurological FPR by
at least 5 percentage points with no extra stroke misses or healthy false
positives relative to random features. Single-seed developmental evidence cannot
promote a release. Existing feature-model results on the same available people
are descriptive contextual comparisons, not identical-input baselines.

TVS was an ElderNet fine-tuning source; do not use it as an independent test.
This is within-Voisard participant/pathology transfer, not cross-source stroke
validation. Upstream pretraining provenance is reported, not independently audited.
