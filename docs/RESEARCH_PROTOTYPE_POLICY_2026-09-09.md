# Research prototype policy and dataset roles

User direction: prioritize a working research prototype and permit lower gates.
Validation gates and their historical failures remain unchanged. Prototype acceptance
is an explicit, post-result engineering decision, not independent validation.

For the TVS contact-laterality prototype, use >=85% participant-macro side accuracy
and >=85% declared optical-contact coverage in each available cohort. The corrected
results meet this policy: HA 87.46% accuracy/86.45% coverage, PD 87.34%/85.45%.
The full-data prototype is fitted on 32 participants/1,645 usable contacts.
The quoted accuracy is earlier participant-held-out exploratory CV, not training
accuracy of the packaged full fit. Partial-reference coverage exclusions remain
explicit. Never erase the initial denominator bug or original failed gate.

This prototype assigns left/right to supplied contacts using native TVS lower-back
gyro XYZ at 100Hz. It does not detect contacts, classify stroke or establish a
Voisard frame correction. No direct application to an unverified other-device frame.
Frozen stroke v0.2.0 remains the existing executable stroke research model. Its
false positives remain material; prototype status does not remove those errors.

## Where the datasets are used

| Dataset | Current role |
|---|---|
| Felius | Existing healthy/stroke development source for the frozen stroke model. Not deleted or superseded by TVS. |
| Voisard | Existing stroke development source plus healthy/other-pathology specificity experiments; phase, HR and gyro work used its selected 259 participants. |
| Sint Maartenskliniek | Existing healthy/stroke development source after its historical external experiment. Cannot now be described as untouched validation for the expanded model. |
| RevalExo | Previously evaluated paired external cohort, retained in the evidence history; repeatedly inspected, not fresh validation for another tuned model. |
| TVS | Separate healthy/PD specificity and measurement track. 40 metadata, 36 raw participants in the acquisition ledger; this optical prototype uses 32 local laboratory participants (30 cohort files plus two schema samples), not all TVS files. No stroke cohort in this local scope. |
| Healthy-only sources including NONAN and other gait datasets | Healthy-domain, pretraining, feature or specificity roles according to their existing source-specific decisions. Not automatically poolable with stroke data or optical event labels. |

Source roles are documented in CLASSIFICATION_EVIDENCE_MAP.md and the wiki dataset
pages. No acquisition deletion or new download occurred. Different experiments
use different compatible subsets; the 32-person optical experiment does not replace
the 314-person three-source stroke development history.

## Executable artifact

Local trusted model: `models/prototypes/tvs-contact-laterality-v0.1.0/model.joblib`.
Manifest records hash, source, prototype policy and contract. Only load trusted
local joblib artifacts. CLI accepts gyro NPY plus supplied zero-based IC indices.

```powershell
& C:/Users/frank/.venv-cu130/Scripts/python.exe -m models.prototype_laterality --model models/prototypes/tvs-contact-laterality-v0.1.0/model.joblib --gyro models/prototypes/tvs-contact-laterality-v0.1.0/examples/example_gyro.npy --contacts models/prototypes/tvs-contact-laterality-v0.1.0/examples/example_contacts.npy --output models/prototypes/tvs-contact-laterality-v0.1.0/examples/example_predictions.csv
```

Feature parity against the saved experiment, serialized prediction parity and
real-input CLI smoke execution passed. The example is an implementation check on
a training-source trial, not validation. Acquisition unchanged, full prototype
fit/package complete, exploratory evaluation reused, independent validation open.
