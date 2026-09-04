# Dataset coverage and permitted roles

| Dataset | Participants | Labels | Age metadata | Sensor compatibility | Permitted role |
|---|---:|---|---|---|---|
| Felius | 163 | Healthy/stroke | Incomplete public linkage | LB/LF/RF compatible | Primary supervised development |
| Voisard | 121 | Healthy/stroke | Healthy ages available; stroke age linkage incomplete | LB/LF/RF compatible | Primary supervised development |
| RevalExo | 17 | Healthy/stroke | Cohort means only | Adapter required | Frozen external test |
| Zenodo rehabilitation | 10 | Stroke only | Exact ages 37–88 | Converted to LB/LF/RF magnitudes | Auxiliary/domain/OOD only |
| DUO-Gait | 16 | Healthy only | Exact ages 21–35 | LF/SA; missing consistent RF | Healthy age-domain/OOD only |
| OxWalk | 39 | Healthy only | Coarse age bands | Hip/wrist only | Healthy age-domain/OOD only |
| MAREA | — | Healthy activity data | No local age table | Separate sensor format | Context/pretraining only |
| Camargo | — | Healthy locomotion data | No local age table | Separate sensor format | Context/pretraining only |

Healthy-only sources are not directly pooled into the binary model because their placements and protocols do not match the LB/LF/RF contract.
