from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
base = ROOT / 'data' / 'raw' / 'mobilise_d_cvs' / 'clinical_data' / 'Clinical Data'
cohort_path = base / 'T1-T5-study-instances-Cohort Site-2026-06-05-10h09m34s.csv'
demo_path = base / 'T1-T5-study-instances-descriptives1.csv'
sensor_path = base / 'T1-T5-study-instances-sensors.csv'
out = ROOT / 'data' / 'processed' / 'mobilise_d_cvs_release_audit.csv'

cohort = pd.read_csv(cohort_path)
demo = pd.read_csv(demo_path)
sensor = pd.read_csv(sensor_path)

def unique_nonempty(s):
    return sorted({str(x).strip() for x in s.dropna() if str(x).strip()})

rows = []
for field in ['cohort ha', 'cohort hc', 'cohort pd', 'cohort ms', 'cohort pff', 'cohort copd', 'cohort chf']:
    vals = cohort[field].astype(str).str.strip().str.lower()
    ids = cohort.loc[vals.isin(['1', 'yes', 'y', 'true', 't']), 'participantid'].dropna().astype(str).unique()
    rows.append({'item': field, 'value': len(ids), 'detail': 'unique participant IDs'})

rows += [
    {'item': 'cohort_rows', 'value': len(cohort), 'detail': 'rows in cohort/site file'},
    {'item': 'cohort_unique_participants', 'value': cohort['participantid'].nunique(), 'detail': 'unique pseudonymised IDs'},
    {'item': 'demographic_rows', 'value': len(demo), 'detail': 'rows in descriptives1 file'},
    {'item': 'demographic_unique_participants', 'value': demo['participantid'].nunique(), 'detail': 'unique IDs'},
    {'item': 'age_nonmissing_rows', 'value': int(demo['age'].notna().sum()), 'detail': 'non-missing age values'},
    {'item': 'age_min', 'value': float(demo['age'].min()), 'detail': 'years'},
    {'item': 'age_max', 'value': float(demo['age'].max()), 'detail': 'years'},
    {'item': 'gender_nonmissing_rows', 'value': int(demo['gender'].notna().sum()), 'detail': 'non-missing gender values'},
    {'item': 'sensor_rows', 'value': len(sensor), 'detail': 'rows in sensor metadata file'},
    {'item': 'sensor_unique_participants', 'value': sensor['participantid'].nunique(), 'detail': 'unique IDs'},
    {'item': 'sensor_types', 'value': '|'.join(unique_nonempty(sensor['senstype'])), 'detail': 'reported sensor-type values'},
]

pd.DataFrame(rows).to_csv(out, index=False)
print(out)
print(pd.DataFrame(rows).to_string(index=False))
