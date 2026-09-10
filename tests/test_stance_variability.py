import unittest
import numpy as np
from src.features.stance_variability import stance_cv
from src.features.bilateral_phase import extract_phase


class StanceVariabilityTest(unittest.TestCase):
    def test_side_and_bout_mean_differences_are_not_variability(self):
        result=stance_cv([[[.5]*5,[.8]*5],[[1.]*5,[1.6]*5]])
        self.assertAlmostEqual(result['stance_duration_cv'],0)

    def test_known_variability_and_side_invariance(self):
        a=[.4,.5,.6,.7,.8]; b=[.6]*5
        x=stance_cv([[a,b]])['stance_duration_cv']
        self.assertAlmostEqual(x,np.std(a,ddof=1)/np.mean(a)/2)
        self.assertAlmostEqual(x,stance_cv([[b,a]])['stance_duration_cv'])

    def test_coverage_and_invalid(self):
        self.assertTrue(np.isnan(stance_cv([[[.5]*4,[.6]*5]])['stance_duration_cv']))
        with self.assertRaises(ValueError):
            stance_cv([[[-1]*5,[.6]*5]])

    def test_optional_extraction_preserves_previous_results(self):
        l=[[i-.4,i] for i in range(1,10)]; r=[[i+.1,i+.5] for i in range(1,10)]
        old=extract_phase(l,r,[20,21],1)
        new=extract_phase(l,r,[20,21],1,return_stances=True)
        self.assertEqual(old,{k:v for k,v in new.items() if k!='stance_segments'})
        self.assertAlmostEqual(stance_cv(new['stance_segments'])['stance_duration_cv'],0)


if __name__=='__main__':
    unittest.main()
