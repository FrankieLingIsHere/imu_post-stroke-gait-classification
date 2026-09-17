# Research prototypes

Start here for executable experimental models. Frozen release checkpoints remain
in `../checkpoints/`. Prototype acceptance does not replace validation evidence.

**Clone contents:** this repository publishes source, manifests and saved research evidence. Locally fitted `model.joblib` files, checkpoints and generated examples are intentionally ignored. The packaged/CLI-verified states below describe local verification; inference will not run from a fresh clone until the matching trusted artifacts and required data are supplied or reproduced. Installing Python dependencies alone does not recreate weights.

| Package | Task | Inputs | State |
|---|---|---|---|
| `tvs-contact-laterality-v0.1.0/` | Assign left/right to supplied contacts | Native TVS lower-back gyro XYZ, 100Hz, zero-based contact indices | Packaged and CLI verified; exploratory side accuracy HA 87.46%, PD 87.34% |
| `stroke-phase-hr-v0.1.0/` | Stroke-versus-non-stroke research classification | Participant covariates and annotation-assisted gait features | Packaged, feature/CLI verified; full-development threshold has no independent validation |

The laterality package is not an end-to-end stroke classifier. Its model and
manifest live at the package root; example inputs/outputs live in `examples/`.

Current stroke entry point: `python -m models.predict_lower_back` with the frozen
v0.2.0 checkpoint. See [models README](../README.md).

Next-work order and dataset roles: [classification workspace guide](../../docs/classification/README.md).
Policy and laterality CLI: [prototype policy](../../docs/RESEARCH_PROTOTYPE_POLICY_2026-09-09.md).
