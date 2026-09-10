import unittest
import numpy as np
from src.features.directional_hr import stride_log_hr,trial_hr


class HRTest(unittest.TestCase):
    def test_known_ratio_and_sign_offset_scale(self):
        t=np.arange(128)/128
        x=2*np.sin(2*np.pi*t)+np.sin(4*np.pi*t)
        self.assertAlmostEqual(stride_log_hr(x),np.log(3))
        self.assertAlmostEqual(stride_log_hr(-4*x+10),np.log(3))

    def test_missing_flat_short(self):
        for x in [np.zeros(100),np.ones(30),np.full(100,np.nan)]:
            self.assertTrue(np.isnan(stride_log_hr(x)))

    def test_turns_missing_and_bounds(self):
        t=np.arange(1000)/100;y=2*np.sin(2*np.pi*t)+np.sin(4*np.pi*t)
        l=[[i-40,i] for i in range(100,1000,100)]
        r=[[i+10,i+50] for i in range(100,900,100)]
        a=trial_hr(y,l,r,[400,600]);b=trial_hr(y,l,r,[1100,1200])
        self.assertLess(a['valid_strides'],b['valid_strides'])
        self.assertGreater(trial_hr(y[:200],l,r,[1100,1200])['invalid_strides'],0)


if __name__=='__main__':unittest.main()
