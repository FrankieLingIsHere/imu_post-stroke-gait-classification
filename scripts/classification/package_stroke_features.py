"""Package a full-development model, keeping prototype threshold provenance explicit."""
from pathlib import Path
import sys,json
import pandas as pd
import numpy as np
import joblib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from models.prototype_stroke_features import FEATURES,predict_frame
from run_stance_variability import fit_model
from run_phase_nested_threshold import sensitivity_threshold
from run_conditional_gait_comparison import sha


def main():
    source=ROOT/'data/processed/directional_hr_v1'
    output=ROOT/'models/prototypes/stroke-phase-hr-v0.1.0';output.mkdir(parents=True,exist_ok=True)
    examples=output/'examples';examples.mkdir(exist_ok=True)
    people=pd.read_csv(source/'participants_main.csv')
    scores=pd.read_csv(source/'predictions.csv')
    scores=scores[scores.variant.eq('main')&scores.scope.eq('all_selected')&scores.arm.eq('nuisance_cadence_phase_hr')]
    assert len(people)==259 and scores.participant.nunique()==259
    assert set(scores.participant)==set(people.participant)
    # All development labels are available for this full-development prototype.
    # This new operating point has no untouched evaluation and is not the earlier nested result.
    threshold=sensitivity_threshold(scores.loc[scores.target.eq(1),'score'],.9)
    model=fit_model(people,FEATURES);checkpoint=output/'model.joblib';joblib.dump(model,checkpoint)
    batch=people[['participant']+FEATURES]
    example=pd.concat([batch.iloc[:3],batch.iloc[[0]].assign(participant='example_invalid',cadence=-1)])
    example.to_csv(examples/'participants.csv',index=False)
    loaded=joblib.load(checkpoint)
    np.testing.assert_allclose(model.predict_proba(batch[FEATURES]),loaded.predict_proba(batch[FEATURES]),rtol=0,atol=0)
    result=predict_frame(example,loaded,threshold);assert result.iloc[-1].decision=='unknown'
    result.to_csv(examples/'predictions.csv',index=False)
    manifest=dict(task='stroke_feature_research',status='research_prototype',features=FEATURES,training_participants=259,
        populations={'healthy':72,'stroke':49,'other_pathology':138},threshold=threshold,
        threshold_provenance='90% empirical stroke sensitivity target from existing full-scope participant OOF development scores; selected after those results were inspected; not independently evaluated',
        historical_evaluation='Prior nested thresholds: full 45/49 stroke, 6/72 healthy FP, 56/138 other FP. Separately fitted matched scope: 44/49, 5/19, 47/76. Neither is validation of this full-data artifact/threshold.',
        contract='One participant row; reference-assisted phase features and nominal lower-back Y log HR; same extraction as directional_hr_v1; age only may be missing; no autonomous raw IMU inference',
        checkpoint_sha256=sha(checkpoint),input_sha256=sha(source/'participants_main.csv'),threshold_source_sha256=sha(source/'predictions.csv'),
        builder_sha256=sha(Path(__file__)),inference_sha256=sha(ROOT/'models/prototype_stroke_features.py'),serialization_parity='passed')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    # Report already executed OOF comparisons, never in-sample accuracy of packaged model.
    metrics=pd.read_csv(source/'metrics.csv')
    metrics=metrics[metrics.variant.eq('main')&metrics.rule.eq('nested')&metrics.arm.isin(['nuisance_cadence','nuisance_cadence_phase','nuisance_cadence_phase_hr'])]
    metrics.to_csv(examples/'historical_oof_comparison.csv',index=False)
    print(json.dumps({'package':str(output),'threshold':threshold,'training_participants':259,'new_validation':False}))


if __name__=='__main__':main()
