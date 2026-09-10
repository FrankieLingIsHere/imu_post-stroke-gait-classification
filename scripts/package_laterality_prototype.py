"""Package the user-authorized lower-gate research prototype, not a validated release."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from scipy.io import loadmat
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from run_conditional_gait_comparison import sha
from models.prototype_laterality import features


def main():
    source=ROOT/'data/processed/tvs_optical_laterality_v1'
    out=ROOT/'models/prototypes/tvs-contact-laterality-v0.1.0';out.mkdir(parents=True,exist_ok=True)
    data=pd.read_csv(source/'features.csv');metrics=pd.read_csv(source/'exploratory_metrics.csv')
    counts=pd.read_csv(source/'trial_coverage.csv').groupby('cohort')[['expected','usable']].sum()
    assert metrics['mean'].ge(.85).all() and (counts.usable/counts.expected).ge(.85).all()
    cols=[f'f{k}' for k in range(9)]
    side_counts=data.groupby(['participant','side']).size()
    assert side_counts.groupby(level=0).size().eq(2).all()
    w=np.array([.5/side_counts.loc[(r.participant,r.side)] for r in data.itertuples()]);w*=len(data)/w.sum()
    model=make_pipeline(MinMaxScaler(),SVC(C=1,kernel='linear'))
    model.fit(data[cols],data.side,svc__sample_weight=w)
    artifact=dict(task='contact_laterality',sampling_hz=100,frame='TVS SU.LowerBack native XYZ',model=model)
    path=out/'model.joblib';joblib.dump(artifact,path)
    # Verify extraction and serialized inference against one existing input trial.
    first=data.iloc[0];manifest=json.loads((source/'manifest.json').read_text())
    raw=loadmat(manifest[first.participant]['path'],simplify_cells=True)['data']
    tm,task,trial=first.trial.split('/');gyro=raw[tm][task][trial]['SU']['LowerBack']['Gyr']
    example=data[data.participant.eq(first.participant)&data.trial.eq(first.trial)]
    contacts=example.ic.to_numpy(int);x=features(gyro,contacts)
    np.testing.assert_allclose(x,example[cols],rtol=1e-10,atol=1e-12)
    loaded=joblib.load(path);np.testing.assert_array_equal(loaded['model'].predict(x),model.predict(example[cols]))
    examples=out/'examples';examples.mkdir(exist_ok=True)
    np.save(examples/'example_gyro.npy',gyro);np.save(examples/'example_contacts.npy',contacts)
    result=dict(status='research_prototype',policy='85% cohort macro accuracy and 85% declared-contact coverage; post-result user-authorized policy',
                previous_strict_gate='failed; historical result unchanged',task='left/right at supplied contacts; not stroke diagnosis',
                training_participants=int(data.participant.nunique()),training_contacts=len(data),
                evaluation='earlier participant-disjoint exploratory CV, not full-fit training accuracy',
                accuracy=metrics.set_index('cohort')['mean'].to_dict(),coverage=(counts.usable/counts.expected).to_dict(),
                checkpoint_sha256=sha(path),input_sha256=sha(source/'features.csv'),code_sha256=sha(Path(__file__)),
                inference_code_sha256=sha(ROOT/'models/prototype_laterality.py'),roundtrip_and_feature_parity='passed')
    (out/'manifest.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
