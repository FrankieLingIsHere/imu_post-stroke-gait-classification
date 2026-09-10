"""Label-free physical checks; no test-side labels choose a correction."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_conditional_gait_comparison import sha
OUT=ROOT/'data/processed/gyro_calibration_evidence_v1'


def main():
    OUT.mkdir(exist_ok=True)
    selected_path=ROOT/'data/processed/bilateral_phase_v1/trial_features.csv'
    mapping_path=ROOT/'data/processed/gyro_axis_v1/gyro_axis_audit.csv'
    selected=pd.read_csv(selected_path);mappings=pd.read_csv(mapping_path).set_index('trial')
    paths={p.stem.removesuffix('_meta'):p for p in (ROOT/'data/raw/voisard_2025/data').glob('*/*/*/*/*_meta.json')}
    (OUT/'manifest.json').write_text(json.dumps({str(p):sha(p) for p in [Path(__file__),selected_path,mapping_path]},indent=2))
    rows=[]
    for r in selected.itertuples():
        p=paths[r.trial];m=json.loads(p.read_text(encoding='utf-8'))
        source=p.parent/f'{r.trial}_processed_data.txt'
        columns=[s+'_'+v+'_'+axis for s in ['LB','HE'] for v in ['Acc','Gyr'] for axis in 'XYZ']
        data=pd.read_csv(source,sep='\t',usecols=columns)
        start,end=map(int,m['uturnBoundaries']);fs=float(m['freq'])
        row=dict(participant=r.participant,trial=r.trial,sensor=m['sensor'],session=m.get('session'),days=m.get('daysSinceFirstSession'),protocol=m.get('protocol'),source_sha256=sha(source))
        for sensor in ['LB','HE']:
            acc=data[[f'{sensor}_Acc_{a}' for a in 'XYZ']].to_numpy()
            gyro=data[[f'{sensor}_Gyr_{a}' for a in 'XYZ']].to_numpy()
            n=min(200,len(data));initial=gyro[:n]
            row[sensor+'_initial_gyro_mean_norm']=float(np.linalg.norm(np.mean(initial,axis=0))) if np.isfinite(initial).all() else np.nan
            row[sensor+'_initial_gyro_rms']=float(np.sqrt(np.mean(initial**2))) if np.isfinite(initial).all() else np.nan
            if 0<=start<end<len(data) and np.isfinite(gyro[start:end+1]).all() and np.isfinite(acc[:n]).all():
                vertical=np.mean(acc[:n],axis=0)
                norm=np.linalg.norm(vertical)
                if norm<=1e-12:
                    row[sensor+'_turn_vertical_integral']=np.nan
                    continue
                vertical/=norm
                row[sensor+'_turn_vertical_integral']=float(np.trapezoid(gyro[start:end+1]@vertical,dx=1/fs))
                row[sensor+'_turn_x_integral']=float(np.trapezoid(gyro[start:end+1,0],dx=1/fs))
            else:row[sensor+'_turn_vertical_integral']=np.nan
        match=mappings.loc[r.trial]
        if match.status=='compared':
            raw=pd.read_csv(p.parent/f'{r.trial}_raw_data_LB.txt',sep='\t',nrows=200,usecols=['Gyr_X','Gyr_Y','Gyr_Z']).to_numpy()
            # Native first 200 rows are a proxy if packets are missing, not exact shared-clock 2s.
            signs=np.array([1 if x[0]=='+' else -1 for x in match.mapping.split()])
            perm=['XYZ'.index(x[1]) for x in match.mapping.split()]
            expected=-np.mean(raw[:,perm]*signs,axis=0)
            offsets=match[['offset_x','offset_y','offset_z']].to_numpy(float)
            row['initial_bias_offset_residual']=float(np.linalg.norm(expected-offsets))
        rows.append(row)
    frame=pd.DataFrame(rows);frame.to_csv(OUT/'physical_checks.csv',index=False)
    frame['turn_abs']=frame.LB_turn_vertical_integral.abs()
    frame['head_back_same_turn_sign']=np.sign(frame.LB_turn_vertical_integral)==np.sign(frame.HE_turn_vertical_integral)
    summary=frame.groupby('sensor')[['turn_abs','LB_initial_gyro_mean_norm','initial_bias_offset_residual']].agg(['count','median','min','max'])
    summary.to_csv(OUT/'summary.csv');print(summary.to_string())
    pair_ids=pd.read_csv(ROOT/'data/processed/gyro_axis_v1/within_participant_device_comparison.csv').participant
    frame[frame.participant.isin(pair_ids)].to_csv(OUT/'paired_device_trial_metadata.csv',index=False)
    valid=frame.dropna(subset=['LB_turn_vertical_integral','HE_turn_vertical_integral'])
    print('Head/back turn sign agreement',valid.groupby('sensor').head_back_same_turn_sign.agg(['count','mean']).to_string())


if __name__=='__main__':main()
