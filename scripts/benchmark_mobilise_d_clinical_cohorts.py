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
src = ROOT / 'data/raw/mobilise_d_cvs/main_datasets/Main datasets for analysis/CSV files/All_cohorts_dataset.csv'
out = ROOT / 'data/processed'
report = ROOT / 'reports/MOBILISE_D_CLINICAL_COHORT_BENCHMARK.md'
df = pd.read_csv(src)
features = ['ws_1030_avg_w','ws_30_avg_w','ws_30_p90_w','ws_30_var_w','ws_10_p90_w','strlen_1030_avg_w','cadence_30_avg_w','strdur_30_avg_w','wb_all_sum_w','walkdur_all_sum_w','wbsteps_all_sum_w','wbdur_all_avg_w','wbdur_all_p90_w','wbdur_all_var_w','cadence_all_avg_w','strdur_all_avg_w','cadence_all_var_w','strdur_all_var_w','n_days_w','best_6mwd_distance','tugtime','total_sppb_score']
features = [f for f in features if f in df.columns]
df = df[df['cohort'].isin(['COPD','MS','PD','PFF'])].copy()
df[features] = df[features].apply(pd.to_numeric, errors='coerce')
participant = df.groupby('participantid', as_index=False).agg({**{f:'median' for f in features}, 'cohort':'first'})
X, y = participant[features], participant['cohort']
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
model = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(max_iter=3000, class_weight='balanced', multi_class='multinomial', random_state=42))
pred = cross_val_predict(model, X, y, cv=cv, method='predict')
labels = sorted(y.unique())
metrics = {'participants': int(len(participant)), 'features_used': len(features), 'missingness_mean': float(X.isna().mean().mean()), 'balanced_accuracy': float(balanced_accuracy_score(y, pred)), 'macro_f1': float(f1_score(y, pred, average='macro')), 'labels': labels, 'confusion_matrix_rows_true_cols_pred': confusion_matrix(y, pred, labels=labels).tolist()}
(out / 'mobilise_d_clinical_cohort_benchmark_metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
pd.DataFrame({'participantid': participant['participantid'], 'true_cohort': y, 'predicted_cohort': pred}).to_csv(out / 'mobilise_d_clinical_cohort_predictions.csv', index=False)
report.write_text(f'''# Mobilise-D clinical-cohort benchmark

This is a separate validity experiment. Mobilise-D CVS contains no stroke and no healthy-control cohort, so it cannot directly evaluate the current stroke-versus-healthy classifier. It tests whether participant-level digital mobility outcomes distinguish the four clinical cohorts.

## Protocol

- One median feature vector per participant; repeated visits are not independent samples.
- Five-fold participant-level stratified cross-validation.
- Median imputation, standardisation, and class-balanced multinomial logistic regression.
- No Mobilise-D data is added to the raw bilateral-IMU training set.

## Result

- Participants: {metrics['participants']}
- Features used: {metrics['features_used']}
- Mean feature missingness before imputation: {metrics['missingness_mean']:.1%}
- Balanced accuracy: {metrics['balanced_accuracy']:.3f}
- Macro-F1: {metrics['macro_f1']:.3f}
- Cohorts: {', '.join(metrics['labels'])}

This result measures cohort separability, not stroke detection. A strong result supports Mobilise-D as a clinical-population stress-test resource, but a separate stroke-versus-healthy evaluation dataset remains necessary.
''', encoding='utf-8')
print(json.dumps(metrics, indent=2))
