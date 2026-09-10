import unittest
import numpy as np
import pandas as pd
from models.prototype_stroke_features import FEATURES,validate,predict_frame


class Dummy:
    def predict_proba(self,x):return np.tile([.3,.7],(len(x),1))


class ContractTest(unittest.TestCase):
    def frame(self):
        return pd.DataFrame([dict(participant='a',**dict(zip(FEATURES,[50.,0.,10.,100.,.2,.2,.2,.4,.2,1.])))])
    def test_unknown_rows_and_missing_age(self):
        f=self.frame();f.loc[0,'age']=np.nan
        self.assertEqual(predict_frame(f,Dummy(),.5).iloc[0].decision,'research_positive')
        f.loc[0,'cadence']=np.inf
        r=predict_frame(f,Dummy(),.5).iloc[0]
        self.assertEqual(r.decision,'unknown');self.assertTrue(np.isnan(r.score))
    def test_duplicates_missing_schema_and_text(self):
        f=self.frame()
        with self.assertRaises(ValueError):validate(pd.concat([f,f],ignore_index=True))
        with self.assertRaises(ValueError):validate(f.drop(columns='ml_log_hr'))
        f['age']='unknown';self.assertNotEqual(validate(f)[1].iloc[0],'ok')
    def test_labels_do_not_enter_features(self):
        f=self.frame();f['target']=1;f['pathology']='stroke'
        self.assertEqual(list(validate(f)[0].columns),FEATURES)


if __name__=='__main__':unittest.main()
