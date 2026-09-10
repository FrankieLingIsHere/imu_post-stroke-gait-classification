"""Verify clinical-label and specificity-calibration provenance."""
from benchmark_vga_screen import *

def main():
    s=pd.read_csv(OUT/'selection.csv');h=pd.read_csv(OUT/'histories.csv');people=pd.read_csv(OUT/'people.csv')
    p=pd.read_csv(OUT/'predictions.csv');c=pd.read_csv(OUT/'calibration.csv');e=pd.read_csv(OUT/'external_predictions.csv')
    ledger=pd.read_csv(OUT/'label_coverage.csv');labels=pd.read_csv(OUT/'first_session_labels.csv');split=pd.read_csv(OLD/'splits.csv')
    assert len(people)==248 and people.target.eq(0).sum()==84 and people.target.eq(1).sum()==164
    assert len(ledger)==259 and (~ledger.eligible).sum()==11
    assert (people.target==people.vga.gt(0)).all()
    ss=split[split.participant.isin(people.participant)].rename(columns={'target':'legacy_diagnosis_target'})
    ss=ss.merge(people[['participant','target','vga']],on='participant',validate='many_to_one')
    ss.to_csv(OUT/'screening_splits.csv',index=False)
    assert len(s)==9 and h.run.nunique()==18 and np.isfinite(h[['loss','val_loss']]).all().all()
    assert len(p)==248*3 and not p.duplicated(['participant','seed']).any()
    assert len(e)==16*4*9 and not e.duplicated(['participant','condition','seed','outer_fold']).any()
    checks=[]
    for r in s.itertuples():
        losses=h[h.run.str.startswith(f'{r.arm}_fold{r.fold}_seed{r.seed}_')].groupby('run').val_loss.min()
        assert np.isclose(losses[r.run],losses.min()) and np.isclose(losses.min(),r.val_loss)
        for run in losses.index:assert (OUT/'checkpoints'/f'{run}.weights.h5').exists()
        cc=c[(c.outer_fold==r.fold)&(c.seed==r.seed)];normal=cc[cc.target.eq(0)]
        threshold=normal.threshold.iloc[0];ordered=np.sort(normal.score);cut=ordered[int(np.ceil(.9*len(ordered)))-1]
        assert np.isclose(threshold,cut,atol=1e-7,rtol=0)
        assert normal.positive.sum()<=np.floor(.1*len(normal)+1e-8)
        test=p[(p.outer_fold==r.fold)&(p.seed==r.seed)]
        expected=set(split[(split.outer_fold==r.fold)&split.role.eq('test')].participant)&set(people.participant)
        assert set(test.participant)==expected and not set(cc.participant)&expected
        for table in [test,e[(e.outer_fold==r.fold)&e.seed.eq(r.seed)]]:assert np.allclose(table.threshold,threshold)
        checks.append(dict(fold=r.fold,seed=r.seed,normal_n=len(normal),normal_alerts=int(normal.positive.sum()),threshold=threshold))
    for f in ['manifest.json','metadata_hashes.json','external_hashes.json']:
        for path,digest in json.loads((OUT/f).read_text()).items():assert sha(ROOT/path)==digest,path
    pd.DataFrame(checks).to_csv(OUT/'calibration_resolution.csv',index=False)
    result=dict(fits=18,selected_models=9,eligible_people=248,unknown_people=11,label_checks=True,selection_checks=True,threshold_checks=True,source_checks=True)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
