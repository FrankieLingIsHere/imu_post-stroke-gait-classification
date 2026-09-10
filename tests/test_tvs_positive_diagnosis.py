import unittest
import numpy as np
from scripts.diagnose_tvs_positive_calls import transform


class DiagnosticTransformsTests(unittest.TestCase):
    def test_order_probes_preserve_values(self):
        x=np.random.default_rng(7).normal(1,.2,(2,500,1)).astype('float32')
        for name in ('time_shuffle','time_reverse'):
            np.testing.assert_array_equal(np.sort(transform(x,name),axis=1),np.sort(x,axis=1))

    def test_dynamic_gain_keeps_mean(self):
        x=np.random.default_rng(7).normal(1,.2,(2,500,1)).astype('float32')
        y=transform(x,'half_dynamic_amplitude')
        np.testing.assert_allclose(y.mean(1),x.mean(1),atol=2e-7)
        np.testing.assert_allclose(y.std(1),x.std(1)/2,atol=2e-7)

    def test_spectral_probe_removes_high_frequency_preserves_dc(self):
        t=np.arange(500)/100
        x=(1+.2*np.sin(2*np.pi*2*t)+.1*np.sin(2*np.pi*20*t))[None,:,None].astype('float32')
        y=transform(x,'keep_below_5hz')
        expected=(1+.2*np.sin(2*np.pi*2*t))[None,:,None]
        np.testing.assert_allclose(y,expected,atol=2e-7)


if __name__=='__main__':unittest.main()
