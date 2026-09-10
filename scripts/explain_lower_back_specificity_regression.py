"""Three-step decision analysis from saved predictions; no fitting or threshold search."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
from scipy.stats import binomtest, spearmanr

ROOT = Path(__file__).resolve().parents[1]
P = ROOT/'data/processed'


def main():
    current_path=P/'lower_back_v020_nonstroke_stress_participants.csv'
    old_path=P/'voisard_nonstroke_hard_negative_participant_predictions.csv'
    window_path=P/'lower_back_v020_nonstroke_stress_windows.csv'
    out=P/'lower_back_specificity_regression_decision.json'
    if out.exists():
        raise FileExistsError('Read the existing analysis instead of repeating it')
    a=pd.read_csv(current_path)
    b=pd.read_csv(old_path)
    m=a.merge(b[['participant_key','cohort','mean_stroke_probability']],on=['participant_key','cohort'],validate='one_to_one')
    assert len(m)==len(a)==len(b)==138
    m['old_positive']=m.mean_stroke_probability.ge(.5)
    m['new_positive']=m.probability.ge(.5)
    m['new_error']=m.new_positive & ~m.old_positive
    m['corrected_error']=~m.new_positive & m.old_positive
    changed=m[m.new_positive.ne(m.old_positive)]
    new=int(m.new_error.sum()); corrected=int(m.corrected_error.sum())
    pathology=m.groupby('cohort').agg(n=('participant_key','size'),new_errors=('new_error','sum'),corrected_errors=('corrected_error','sum'),old_positive=('old_positive','sum'),new_positive=('new_positive','sum'))
    # Prespecified descriptive strata, with missing age kept explicitly.
    m['age_band']=pd.cut(m.age,[-np.inf,39,59,74,np.inf],labels=['under40','40to59','60to74','75plus']).astype('string').fillna('missing')
    age=m.groupby('age_band').agg(n=('participant_key','size'),positive=('new_positive','sum'),new_errors=('new_error','sum'),corrected_errors=('corrected_error','sum'))
    # Trial weighting is a diagnostic only, never adopted as a new decision rule.
    w=pd.read_csv(window_path)
    trial=w.groupby(['participant_key','trial_id']).probability.mean().groupby('participant_key').mean()
    m['equal_trial_probability']=m.participant_key.map(trial)
    assert m.equal_trial_probability.notna().all()
    shifts=int(m.equal_trial_probability.ge(.5).ne(m.new_positive).sum())
    correlations={}
    for name in ['age','windows']:
        d=m[[name,'probability']].dropna()
        r=spearmanr(d[name],d.probability)
        correlations[name]={'n':len(d),'spearman_rho':float(r.statistic)}
    result=dict(
        purpose='descriptive paired specificity diagnosis, not independent validation',
        step1=dict(matched_participants=len(m),new_errors=new,corrected_errors=corrected,
                   persistent_positive=int((m.new_positive&m.old_positive).sum()),
                   persistent_negative=int((~m.new_positive&~m.old_positive).sum()),
                   discordant_exact_two_sided_p=binomtest(new,len(changed),.5).pvalue),
        step2=dict(descriptive_correlations=correlations,age_missing=int(m.age.isna().sum()),
                   equal_trial_weighting_classification_changes=shifts,
                   equal_trial_weighting_positive_count=int(m.equal_trial_probability.ge(.5).sum())),
        step3=dict(stroke_specificity_claim='not_supported',
                   threshold_or_pooling_change_admitted=False,
                   reason='Non-stroke-only analysis cannot establish preserved stroke sensitivity; models differ in more than sensor count',
                   next_intervention='A separately specified differential-gait training task with clinically identified non-stroke negatives and independent paired validation; do not recycle the inspected cohort as a final test'),
        input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [current_path,old_path,window_path]})
    pathology.to_csv(P/'lower_back_specificity_regression_pathology.csv')
    age.to_csv(P/'lower_back_specificity_regression_age.csv')
    m.to_csv(P/'lower_back_specificity_regression_matched.csv',index=False)
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2));print(pathology.to_string());print(age.to_string())


if __name__=='__main__':
    main()
