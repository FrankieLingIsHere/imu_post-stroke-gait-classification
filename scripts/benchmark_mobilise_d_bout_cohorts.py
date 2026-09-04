from pathlib import Path
import json
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import balanced_accuracy_score, f1_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
files = sorted((ROOT / 'data/raw/mobilise_d_cvs/walking_bout_dmo/extracted').rglob('*.csv'))
main = ROOT / 'data/raw/mobilise_d_cvs/main_datasets/Main datasets for analysis/CSV files/All_cohorts_dataset.csv'
out = ROOT / 'data/processed'
report = ROOT / 'reports/MOBILISE_D_BOUT_COHORT_BENCHMARK.md'
raw_features = ['duration','numberstrides','averagecadence','turn_number_so','averagestridespeed','averagestridelength','averagestrideduration','averagestepduration_so']
pieces = []
for f in files:
    use = ['participantid'] + raw_features
    for chunk in pd.read_csv(f, usecols=lambda c: c in use, chunksize=200000, low_memory=False):
        for c in raw_features: chunk[c] = pd.to_numeric(chunk[c], errors='coerce')
        pieces.append(chunk)
bouts = pd.concat(pieces, ignore_index=True)
agg = {c: ['median','mean'] for c in raw_features}
participant = bouts.groupby('participantid').agg(agg)
participant.columns = [f'{a}_{b}' for a,b in participant.columns]
participant['bout_count'] = bouts.groupby('participantid').size()
participant = participant.reset_index()
cohort = pd.read_csv(main, usecols=['participantid','cohort'], low_memory=False).drop_duplicates('participantid')
participant = participant.merge(cohort, on='participantid', how='inner')
participant = participant[participant['cohort'].isin(['COPD','MS','PD','PFF'])].copy()
features = [c for c in participant.columns if c not in ['participantid','cohort']]
X, y = participant[features], participant['cohort']
labels = sorted(y.unique())
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
model = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(max_iter=3000, class_weight='balanced', random_state=42))
pred = cross_val_predict(model, X, y, cv=cv, method='predict')
metrics = {'bouts': int(len(bouts)), 'participants': int(len(participant)), 'features_used': len(features), 'missingness_mean': float(X.isna().mean().mean()), 'balanced_accuracy': float(balanced_accuracy_score(y,pred)), 'macro_f1': float(f1_score(y,pred,average='macro')), 'labels': labels, 'confusion_matrix_rows_true_cols_pred': confusion_matrix(y,pred,labels=labels).tolist()}
(out/'mobilise_d_bout_cohort_benchmark_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
pd.DataFrame({'participantid':participant['participantid'],'true_cohort':y,'predicted_cohort':pred,'bout_count':participant['bout_count']}).to_csv(out/'mobilise_d_bout_cohort_predictions.csv',index=False)
report.write_text(f'''# Mobilise-D walking-bout cohort benchmark

## Protocol

- Five visit-level bout files were combined.
- Bouts were aggregated to one participant vector using median and mean statistics; bout count was retained as a feature.
- Repeated visits and bouts were therefore not treated as independent subjects.
- Five-fold participant-level stratified validation used imputation, standardisation, and class-balanced logistic regression.

## Result

- Walking bouts processed: {metrics['bouts']}
- Participants: {metrics['participants']}
- Features used: {metrics['features_used']}
- Mean missingness before imputation: {metrics['missingness_mean']:.1%}
- Balanced accuracy: {metrics['balanced_accuracy']:.3f}
- Macro-F1: {metrics['macro_f1']:.3f}
- Cohorts: {', '.join(metrics['labels'])}

This remains a clinical-cohort separability experiment, not stroke detection. The representation is processed single-back DMO and must not be pooled into the bilateral raw-IMU classifier.
''',encoding='utf-8')
print(json.dumps(metrics,indent=2))
