import unittest
import numpy as np
import pandas as pd
from src.data.voisard_aligned import align_packets


def frame(t,v):
    return pd.DataFrame(dict(PacketCounter=t,Acc_X=v,Acc_Y=v,Acc_Z=v))


class AlignmentTests(unittest.TestCase):
    def test_shared_origin_and_interior_interpolation(self):
        a=align_packets(frame([101,103,104],[1,3,4]),100)
        self.assertTrue(np.isnan(a[0]).all())
        np.testing.assert_allclose(a[1:,0],[1,2,3,4])

    def test_rollover_with_missing_packet(self):
        a=align_packets(frame([65534,65535,1],[0,1,3]),65534)
        np.testing.assert_allclose(a[:,0],[0,1,2,3])

    def test_large_gap_and_bad_counter_do_not_get_hidden(self):
        a=align_packets(frame([0,152],[0,1]),0)
        self.assertTrue(np.isnan(a[1:152]).all())
        with self.assertRaises(ValueError):align_packets(frame([1,1],[0,1]),1)
        with self.assertRaises(ValueError):align_packets(frame([10,5],[0,1]),0)

    def test_gap_free_values_preserved_despite_float_noise(self):
        f=frame([0,1,2.000000000000001],[9,8,7])
        np.testing.assert_array_equal(align_packets(f,0),f[['Acc_X','Acc_Y','Acc_Z']].to_numpy())


if __name__=='__main__':unittest.main()
