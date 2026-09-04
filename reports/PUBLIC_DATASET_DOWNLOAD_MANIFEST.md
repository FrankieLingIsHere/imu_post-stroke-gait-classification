# Public dataset download manifest

Downloads started on 2026-08-25 using resumable `aria2c` transfers. Existing datasets were not duplicated.

| Dataset | Local target | Archive | Size | Status | Intended role |
|---|---|---:|---:|---|---|
| Sint Maartenskliniek | `data/raw/sint_maartenskliniek/` | `IMU_GaitAnalysis-1.1.0.zip` | 2.59 GB | Complete + extracted; MD5 verified | External examination, then sensitivity-training candidate |
| Triaxial accelerometer | `data/raw/triaxial_accelerometer/` | `triaxial_accelerometer_data.zip` | 0.54 GB | Complete + extracted | Healthy sensor/domain robustness |
| Zhou rehabilitation | `data/raw/zenodo_stroke_rehab/` | Already present | — | Complete | Stroke-only longitudinal/robustness analysis |
| Felius, Voisard, RevalExo, DUO-GAIT, OxWalk, MAREA, Camargo, GaitMotion | Existing project folders | Already present | — | Complete | Existing roles retained |
| Mobilise-D | Not downloaded | 60+ GB across groups | — | Deferred | Download only selected group after schema/role audit |

Progress logs:

- `reports/download_sint_maartenskliniek.log`
- `reports/download_triaxial.log`
