import unittest
import pandas as pd
from scripts.classification.adapt_eldernet_lower_back import split_calibration


class CalibrationSplitTest(unittest.TestCase):
    def test_small_groups_remain_disjoint_and_represented(self):
        data = pd.DataFrame({'participant':[f'p{i}' for i in range(18)],
                             'target':[0]*2+[1]*8+[2]*8})
        fit, cal = split_calibration(data, 1)
        self.assertFalse(set(fit.participant) & set(cal.participant))
        self.assertEqual(set(fit.participant) | set(cal.participant), set(data.participant))
        self.assertEqual(set(fit.target), {0,1,2})
        self.assertEqual(set(cal.target), {0,1,2})
        self.assertEqual(cal.target.value_counts().to_dict(), {1:2,2:2,0:1})
        _, repeated = split_calibration(data, 1)
        self.assertEqual(list(cal.participant), list(repeated.participant))


if __name__ == '__main__': unittest.main()
