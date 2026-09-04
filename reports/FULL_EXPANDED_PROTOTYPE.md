# Full expanded prototype checkpoint

The inclusion gate supported retaining Sint Maartenskliniek as a prototype training source. A full expanded Inception checkpoint was therefore trained on:

- Felius + Voisard + Sint Maartenskliniek;
- 314 participants;
- 22,506 healthy/stroke windows;
- the established 5-second, 100-Hz, `LB/LF/RF` acceleration-magnitude contract;
- source/class-balanced sampling;
- normalization fitted on the complete development pool for this prototype checkpoint;
- GPU training, seed 42, 15 epochs.

Checkpoint: `data/processed/full_expanded_inception_prototype_seed_42.pt`.

This is the current prototype artifact. It is not a clinical release model: the operating threshold, deployment calibration, subgroup robustness, and external validation limitations still need to be documented around it. RevalExo was not used during fitting.
