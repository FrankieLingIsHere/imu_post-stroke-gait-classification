import unittest
import pandas as pd
import numpy as np
from scripts.classification.compare_pathology_balance import weights_for


class PathologyWeightsTest(unittest.TestCase):
    def test_fixed_class_masses(self):
        frame = pd.DataFrame({'target': [0, 1, 1, 2, 2, 2],
                              'pathology': ['healthy', 'stroke', 'stroke', 'A', 'B', 'B']})
        weight = weights_for(frame) / len(frame)
        np.testing.assert_allclose(weight.groupby(frame.target).sum(), [.25, .5, .25])
        self.assertAlmostEqual(weight[frame.pathology.eq('A')].sum(), .125)
        self.assertAlmostEqual(weight[frame.pathology.eq('B')].sum(), .125)

    def test_duplication_preserves_group_mass(self):
        frame = pd.DataFrame({'target': [0, 1, 2, 2],
                              'pathology': ['healthy', 'stroke', 'A', 'B']})
        duplicated = pd.concat([frame, frame[frame.pathology.eq('B')]], ignore_index=True)
        a = (weights_for(frame) / len(frame)).groupby(frame.pathology).sum()
        b = (weights_for(duplicated) / len(duplicated)).groupby(duplicated.pathology).sum()
        np.testing.assert_allclose(a.sort_index(), b.sort_index())


if __name__ == '__main__':
    unittest.main()
