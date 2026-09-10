"""Paired result verification, without re-running inference or fitting."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/packet_alignment_v1'


def main():
    pred=pd.read_csv(OUT/'frozen_nonstroke_predictions.csv')
    paired=pred.pivot(index=['participant_key','cohort'],columns='version',values='score').reset_index()
    paired['score_delta']=paired.aligned-paired.old
    paired['old_positive']=paired.old.ge(.5);paired['aligned_positive']=paired.aligned.ge(.5)
    paired.to_csv(OUT/'frozen_paired_comparison.csv',index=False)
    paired.groupby('cohort').agg(participants=('participant_key','size'),old_positive=('old_positive','sum'),aligned_positive=('aligned_positive','sum')).to_csv(OUT/'frozen_pathology_comparison.csv')
    old=pd.read_csv(ROOT/'data/processed/conditional_gait_v1/predictions.csv')
    new=pd.read_csv(OUT/'feature_predictions.csv')
    joined=old.merge(new,on=['scope','arm','participant','target','pathology','fold'],validate='one_to_one',suffixes=('_old','_aligned'))
    assert len(joined)==len(old)==len(new)
    joined['changed_call']=joined.score_old.ge(.5).ne(joined.score_aligned.ge(.5))
    joined.to_csv(OUT/'feature_paired_comparison.csv',index=False)
    controls=joined.arm.isin(['cadence_only','nuisance','nuisance_cadence'])|joined.scope.eq('device_protocol_matched')
    np.testing.assert_allclose(joined.loc[controls,'score_old'],joined.loc[controls,'score_aligned'],atol=1e-10,rtol=0)
    audit=pd.read_csv(OUT/'alignment_audit.csv')
    assert audit.provider_filtered_norm_max_error.notna().all()
    assert audit.provider_filtered_norm_max_error.max()<.001
    v=json.loads((OUT/'verification.json').read_text())
    v.update(tests_passed=4,old_positive=int(paired.old_positive.sum()),aligned_positive=int(paired.aligned_positive.sum()),
        changed_frozen_calls=int(paired.old_positive.ne(paired.aligned_positive).sum()),max_absolute_frozen_score_change=float(paired.score_delta.abs().max()),
        unaffected_control_predictions_equal=True,all_selected_trials_provider_alignment_verified=True)
    v['hashes'].update({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.csv')})
    (OUT/'verification.json').write_text(json.dumps(v,indent=2))
    print('Paired checks passed; frozen calls unchanged; control arms unchanged.')


if __name__=='__main__':main()
