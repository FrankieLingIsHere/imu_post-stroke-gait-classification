import unittest
import numpy as np
from scripts.run_gyro_laterality import gyro_features


class GyroTest(unittest.TestCase):
    def test_feature_shape_and_sign(self):
        t=np.arange(300)/100;x=np.c_[np.sin(2*np.pi*t),np.cos(2*np.pi*t)]
        a=gyro_features(x,[70,150,200]);self.assertEqual(a.shape,(3,6))
        np.testing.assert_allclose(gyro_features(-x,[70,150,200]),-a)

    def test_duplicate_outside_and_nonfinite(self):
        for x,ic in [(np.zeros((100,2)),[2,2]),(np.zeros((100,2)),[100]),(np.full((100,2),np.nan),[5])]:
            with self.assertRaises(ValueError):gyro_features(x,ic)


if __name__=='__main__':unittest.main()
