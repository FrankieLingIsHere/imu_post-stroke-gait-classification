import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/classification'))
from finalize_vga_screen import strict_threshold

class ThresholdTests(unittest.TestCase):
    def test_float32_boundary_excluded_and_budget_respected(self):
        for n in [5,7,10,12,20]:
            x=np.linspace(.1,.9,n,dtype='float32');cut=x[int(np.ceil(.9*n))-1]
            t=strict_threshold(x)
            self.assertFalse(pd.Series([cut],dtype='float32').ge(t).iloc[0])
            self.assertLessEqual(pd.Series(x).ge(t).sum(),int(np.floor(.1*n)))

    def test_ties_and_invalid(self):
        x=np.repeat(np.float32(.5),12)
        self.assertEqual(pd.Series(x).ge(strict_threshold(x)).sum(),0)
        for bad in [[],[np.nan]]:
            with self.assertRaises(ValueError):strict_threshold(bad)

if __name__=='__main__':unittest.main()
