import unittest
import numpy as np
from scripts.audit_voisard_gyro_axes import best_mapping


class GyroMappingTest(unittest.TestCase):
    def test_signed_permutation_scale(self):
        x=np.random.default_rng(7).normal(size=(200,3))
        y=x[:,[2,0,1]]*[-2,2,-2]+[.2,-.3,4]
        r=best_mapping(x,y)
        self.assertEqual(r['mapping'],'-Z +X -Y')
        self.assertAlmostEqual(r['scale'],2)
        self.assertLess(r['scaled_rmse'],1e-12)
        self.assertAlmostEqual(r['offset_z'],4)

    def test_identity(self):
        x=np.random.default_rng(9).normal(size=(100,3))
        r=best_mapping(x,x)
        self.assertEqual(r['mapping'],'+X +Y +Z')
        self.assertAlmostEqual(r['rmse'],0)


if __name__=='__main__':unittest.main()
