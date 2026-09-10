import unittest
import numpy as np
import pandas as pd
import torch
from scripts.train_differential_gait_candidate import make_model,stroke_scores,make_folds,participant_batch


class DifferentialTests(unittest.TestCase):
    def test_identical_initial_backbone_and_correct_stroke_class(self):
        a=make_model('binary_exposure',42);b=make_model('three_class',42)
        for key,value in a.features.state_dict().items():torch.testing.assert_close(value,b.features.state_dict()[key],rtol=0,atol=0)
        scores=stroke_scores(torch.tensor([[0.,100.,0.],[0.,0.,100.]]),'three_class')
        self.assertGreater(scores[0].item(),.99);self.assertLess(scores[1].item(),.01)

    def fixture(self):
        rows=[]
        for target in (0,1):
            for i in range(6):rows.append(dict(participant=f'{target}-{i}',target=target,pathology=str(target)))
        for pathology in ('ACL','CIPN','HOA','KOA','PD','RIL'):
            for i in range(2):rows.append(dict(participant=f'{pathology}-{i}',target=2,pathology=pathology))
        return pd.DataFrame(rows)

    def test_whole_people_and_pathologies_held_out(self):
        m=self.fixture();f=make_folds(pd.concat([m,m],ignore_index=True))
        self.assertEqual(len(f),len(m));self.assertFalse(f.participant.duplicated().any())
        self.assertTrue(f[f.target==2].groupby('pathology').fold.nunique().eq(1).all())
        for fold in range(3):self.assertEqual(set(f[f.fold==fold].target),{0,1,2})

    def test_batch_excludes_test_people_and_balances_targets(self):
        m=self.fixture();train=pd.Series(True,index=m.index);train.iloc[0]=False
        indices=participant_batch(m,train,np.random.default_rng(42))
        self.assertNotIn(0,indices)
        self.assertEqual(m.iloc[indices].target.value_counts().to_dict(),{0:32,1:32,2:32})


if __name__=='__main__':unittest.main()
