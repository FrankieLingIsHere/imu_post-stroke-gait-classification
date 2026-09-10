import unittest

import numpy as np
import pandas as pd

from src.features.lower_back_events import COLS, detect_lower_back_events, match_events


class EventAdapterTests(unittest.TestCase):
    def test_one_to_one_matching_and_tolerance(self):
        r=match_events([100,200],[99,101,215,400],15)
        self.assertEqual((r['tp'],r['fp'],r['fn']),(2,2,0))
        self.assertEqual(r['residuals'],[-1,15])
        self.assertEqual(match_events([100],[116],15)['tp'],0)

    def test_matching_cardinality_against_dynamic_programming(self):
        rng=np.random.default_rng(3)
        for _ in range(100):
            a=np.sort(rng.choice(100,8,replace=False));b=np.sort(rng.choice(100,9,replace=False))
            dp=np.zeros((len(a)+1,len(b)+1),dtype=int)
            for i in range(1,len(a)+1):
                for j in range(1,len(b)+1):
                    dp[i,j]=max(dp[i-1,j],dp[i,j-1],dp[i-1,j-1]+int(abs(a[i-1]-b[j-1])<=7))
            self.assertEqual(match_events(a,b,7)['tp'],dp[-1,-1])

    def test_invalid_and_constant_signals_have_no_measurement(self):
        d=pd.DataFrame(np.zeros((500,6)),columns=COLS);d.acc_x=9.80665
        self.assertEqual(detect_lower_back_events(d,100)['status'],'constant_magnitude')
        d.loc[4,'acc_x']=np.nan
        self.assertEqual(detect_lower_back_events(d,100)['status'],'invalid_acceleration')

    def test_gyro_is_not_a_detector_input(self):
        d=pd.DataFrame(np.zeros((2000,6)),columns=COLS)
        d.acc_x=9.80665+2*np.sin(2*np.pi*2*np.arange(len(d))/100)
        a=detect_lower_back_events(d,100,known_gait=True)
        d[COLS[3:]]=np.random.default_rng(4).normal(size=(len(d),3))*100
        b=detect_lower_back_events(d,100,known_gait=True)
        self.assertGreater(len(a['events']),10)
        self.assertEqual(a,b)


if __name__=='__main__':unittest.main()
