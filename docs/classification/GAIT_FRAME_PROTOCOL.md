# Waveform-frame gait CNN protocol

Locked before fitting, 2026-09-09. Custom measurement-frame experiment, not an
anatomical AP/ML calibration or a claimed root-cause correction. No new datasets.

For each filtered/resampled stride, estimate vertical from mean acceleration.
Project acceleration onto the horizontal plane and find its dominant eigenvector.
Fix its sign using the largest absolute horizontal projection in time. Complete
a right-handed basis by cross product. Apply this same proper rotation to acc and
gyro. This preserves six channels in g and rad/s. Frame is per-stride and may be
unstable for nearly equal eigenvalues; retain eigenvalue gap and gravity magnitude
as quality diagnostics only, not classifier inputs. No diagnosis, side, age,
external target labels or performance-selected axis permutations. Exact ties or
zero-motion frames are unidentifiable; flag/exclude and report coverage. This
removes absolute heading information, not physical placement effects. Mean walking
acceleration is an approximate gravity direction, not verified static calibration.

Compare magnitude and frame6 with the existing three outer participant/pathology
folds, identical fitting/validation/calibration participant identities, weights,
threshold90% calibration stroke sensitivity, and mean trial/participant aggregation.
Actual upstream CNN unchanged. Two recipes only: upstream lr.02/max25/patience3/
LR patience2 floor.001; conservative lr.001/max40/patience8/LR patience3 floor.00001.
Both restore best validation weights, batch32. Select recipe by minimum weighted
validation loss for each arm/fold/seed, never test/calibration/DUO-GAIT performance.
Three seeds42,137,202:36 fits. No refit. Save both recipe histories/weights and
selected predictions. Full259 and matched144 scopes, all seeds, fixed.5 and
calibration thresholds. Improvement requires >=5pp neurological FPR reduction
with no extra stroke misses or healthy FP versus selected magnitude, in both
scopes for every seed. Report tradeoffs even when gate fails.

After selection, frozen DUO-GAIT inference on all four conditions using existing
v2 event eligibility/timestamp intervals; native128Hz10Hz filter, same200-point
resampling. Acc already g; gyro deg/s converted rad/s. Source and physical gyro
scale support recorded in existing calibration evidence. No gyro bias adjustment
added to either source. Frame constructed identically after resampling. Never
select recipe/frame from external outcomes. DUO-GAIT is reused healthy-only stress
data, not independent positive validation. Prior native6 results are contextual,
not the controlled effect of frame normalization alone because optimization differs.
