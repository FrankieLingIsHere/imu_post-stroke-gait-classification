import unittest

import numpy as np
import pandas as pd

from scripts.run_conditional_gait_comparison import run_cv, score_metrics, NUISANCE, GAIT


class ConditionalComparisonTests(unittest.TestCase):
    def fixture(self):
        rng = np.random.default_rng(8)
        rows = []
        for fold in range(3):
            for target in range(3):
                for i in range(3):
                    row = dict(participant=f'{fold}-{target}-{i}', target=target,
                               fold=fold, pathology=f'other{fold}' if target == 2 else str(target))
                    row.update({c: float(rng.normal()) for c in set(NUISANCE + GAIT)})
                    rows.append(row)
        return pd.DataFrame(rows)

    def test_heldout_labels_do_not_change_their_predictions(self):
        data = self.fixture()
        a = run_cv(data, 'test')
        changed = data.copy()
        mask = changed.fold.eq(0) & changed.target.lt(2)
        changed.loc[mask, 'target'] = 1 - changed.loc[mask, 'target']
        b = run_cv(changed, 'test')
        np.testing.assert_allclose(a.loc[a.fold.eq(0), 'score'], b.loc[b.fold.eq(0), 'score'])

    def test_missing_feature_keeps_participant(self):
        data = self.fixture()
        data.loc[0, GAIT] = np.nan
        result = run_cv(data, 'test')
        self.assertEqual(result.participant.nunique(), len(data))
        self.assertTrue(np.isfinite(result.score).all())

    def test_specificity_is_healthy_only_and_other_fpr_separate(self):
        f = pd.DataFrame({'target': [0, 0, 1, 1, 2, 2], 'score': [.1, .7, .8, .9, .6, .8]})
        m = score_metrics(f)
        self.assertEqual(m['healthy_specificity'], .5)
        self.assertEqual(m['sensitivity'], 1.)
        self.assertEqual(m['other_fpr'], 1.)


if __name__ == '__main__':
    unittest.main()
