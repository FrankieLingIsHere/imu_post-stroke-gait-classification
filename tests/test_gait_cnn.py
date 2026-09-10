import contextlib
import io
import unittest
import numpy as np
import pandas as pd
from scripts.classification.benchmark_gait_cnn import cycle_bounds, weights, upstream_builder


class GaitCNNTests(unittest.TestCase):
    def test_cycle_boundaries(self):
        m = dict(leftGaitEvents=[[0, 20], [80, 120], [180, 220], [280, 320]],
                 uturnBoundaries=[150, 250])
        self.assertEqual(cycle_bounds(m), ([(20, 120)], 0))
        m['leftGaitEvents'] = [[0, 20], [10, 120]]
        self.assertEqual(cycle_bounds(m), ([], 1))

    def test_balanced_people_and_trials(self):
        p = pd.DataFrame(dict(participant=['a', 'b', 'c', 'd'], target=[0, 1, 1, 2]))
        m = pd.DataFrame(dict(participant=['a', 'b', 'b', 'b', 'c', 'd'],
                              trial=['a1', 'b1', 'b1', 'b2', 'c1', 'd1']))
        w = weights(m, p)
        np.testing.assert_allclose(pd.Series(w).groupby(m.participant).sum(), [1.5]*4)
        self.assertAlmostEqual(w[1]+w[2], w[3])

    def test_upstream_forward_matches_numpy(self):
        rng = np.random.default_rng(19)
        for channels in [1, 6, 12, 18]:
            with contextlib.redirect_stdout(io.StringIO()):
                model = upstream_builder()(dict(use_wandb=False, n_filters=32, n_layers=1,
                    initial_lr=.02, evaluation_metric='AUC'), 200, channels)
            x = rng.normal(size=(2, 200, channels)).astype('float32')
            kernel, bias, dense, intercept = model.get_weights()
            conv = np.stack([np.einsum('btc,tco->bo', x[:, i:i+5], kernel)+bias
                             for i in range(196)], axis=1)
            logits = np.maximum(conv, 0).max(axis=1) @ dense + intercept
            expected = np.exp(logits-logits.max(axis=1, keepdims=True))
            expected /= expected.sum(axis=1, keepdims=True)
            np.testing.assert_allclose(model.predict(x, verbose=0), expected, atol=2e-6)
            self.assertEqual(model.count_params(), 32*(5*channels+1)+66)


if __name__ == '__main__':
    unittest.main()
