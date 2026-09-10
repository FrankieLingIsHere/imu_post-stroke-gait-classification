import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/classification'))
from benchmark_gait_frame import canonical

class FrameTests(unittest.TestCase):
    def test_proper_rotation_preserves_frame_and_norms(self):
        rng=np.random.default_rng(51)
        x=rng.normal(size=(8,200,6))*.1;x[:,:,0]+=1
        x[:,:,1]*=3
        q,_=np.linalg.qr(rng.normal(size=(3,3)))
        if np.linalg.det(q)<0:q[:,0]*=-1
        rotated=np.concatenate([x[:,:,:3]@q,x[:,:,3:]@q],axis=2)
        a,valid,_,_=canonical(x);b,valid2,_,_=canonical(rotated)
        self.assertTrue(valid.all() and valid2.all())
        np.testing.assert_allclose(a,b,atol=1e-6)
        np.testing.assert_allclose(np.linalg.norm(a[:,:,:3],axis=2),np.linalg.norm(x[:,:,:3],axis=2),atol=2e-7)
        np.testing.assert_allclose(np.linalg.norm(a[:,:,3:],axis=2),np.linalg.norm(x[:,:,3:],axis=2),atol=2e-7)

    def test_static_frame_unidentifiable(self):
        x=np.zeros((1,200,6));x[:,:,0]=1
        self.assertFalse(canonical(x)[1][0])

if __name__=='__main__':unittest.main()
