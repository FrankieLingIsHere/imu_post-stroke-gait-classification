"""Fail-fast leakage audit for the formal multi-source benchmark."""
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1]
m=pd.read_csv(R/'data/processed/validated_window_metadata.csv'); splits=pd.read_csv(R/'data/interim/participant_splits.csv')
assert set(m.dataset_id.unique()) <= {'felius_2024','voisard_2025'}, 'unexpected binary source in validated metadata'
ext=pd.read_csv(R/'data/processed/revalexo_external_window_metadata.csv')
assert set(ext.subject).isdisjoint(set(m.participant_key)), 'external participant overlap'
for fold in sorted(splits.fold.unique()):
    s=splits[splits.fold.eq(fold)]; tr=set(s.loc[s.role.eq('training'),'participant_key']); va=set(s.loc[s.role.eq('validation'),'participant_key'])
    assert tr.isdisjoint(va), f'fold {fold}: participant overlap'
assert len(np.load(R/'data/processed/zenodo_benchmark_acceleration_magnitude_windows_float32.npy',mmap_mode='r'))==len(pd.read_csv(R/'data/processed/zenodo_benchmark_magnitude_metadata.csv'))
print('PASS: participant-disjoint folds, binary-source restriction, external exclusion, and Zenodo alignment')
