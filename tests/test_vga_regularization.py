import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/classification'))
from benchmark_vga_regularization import rate,Adam
from keras import Variable,ops

class RegularizationTests(unittest.TestCase):
    def test_schedule_contrast(self):
        self.assertAlmostEqual(rate(0),.001)
        self.assertAlmostEqual(rate(0,True),.0002)
        self.assertAlmostEqual(rate(39),.00001)
        for epoch in range(4,40):self.assertEqual(rate(epoch),rate(epoch,True))
        self.assertTrue(all(rate(i+1)<=rate(i) for i in range(39)))

    def test_decoupled_decay_with_zero_gradient(self):
        for decay,expected in [(0.,1.),(.1,.999)]:
            w=Variable(np.array([1.],dtype='float32'))
            opt=Adam(learning_rate=.01,weight_decay=decay)
            opt.apply_gradients([(ops.zeros_like(w),w)])
            np.testing.assert_allclose(ops.convert_to_numpy(w),[expected],atol=1e-7)

if __name__=='__main__':unittest.main()
