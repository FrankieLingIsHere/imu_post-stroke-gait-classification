# MiniROCKET readiness

## Configuration formalised

The existing architecture-comparison notebook now saves, per fold:

- fitted `MiniRocketMultivariate` transformer;
- fitted `RidgeClassifier`;
- training-fold normalization mean and standard deviation;
- fold and seed metadata;
- input channel order (`LB`, `LF`, `RF`), five-second window length, and transformed feature count.

The intended configuration remains 2,000 kernels, maximum 16 dilations per kernel, seed 42, Ridge `alpha=1.0`, participant/class sample weighting, and participant-level aggregation.

## Execution status

The native Windows notebook remains blocked by Windows Application Control when Numba loads its compiled `_typeconv` extension. The MiniROCKET-only export was therefore executed in the available WSL Python environment, using the same project data, participant folds, normalization, kernel settings and Ridge configuration. All five fold artifacts were generated successfully.

The native Windows execution issue is an environment limitation, not a model result. The certified artifacts are valid for the documented MiniROCKET pipeline; the historical metrics were not overwritten.

## Required resolution

For native Windows continuation, repair the Application Control restriction so both of the following succeed in a clean kernel:

```python
from sktime.transformations.panel.rocket import MiniRocketMultivariate
import numba
```

Then execute `notebooks/archive/14_architecture_comparison.ipynb`, verify five `minirocket_ridge_fold_*_seed_42.joblib` files, and record their hashes before using MiniROCKET for external adaptation or final model selection.
