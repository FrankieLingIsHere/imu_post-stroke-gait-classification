import unittest
from unittest.mock import patch
import numpy as np
from models.input_validity import screen_windows,predict_windows_with_validity


class InputValidityTests(unittest.TestCase):
    def test_mixed_inputs_only_eligible_windows_reach_model(self):
        x=np.ones((3,500,1),dtype='float32');x[1,2,0]=np.nan;x[2,:,0]+=np.sin(np.arange(500))*.1
        with patch('models.input_validity.validate_bundle'),patch('models.input_validity.predict_windows',return_value=np.array([.8])) as predict:
            rows=predict_windows_with_validity({},x)
        self.assertEqual(predict.call_args.args[1].shape,(1,500,1))
        np.testing.assert_array_equal(predict.call_args.args[1][0],x[2])
        self.assertEqual([r['stroke_score'] for r in rows],[None,None,.8])
        self.assertEqual([r['reason'] for r in rows],['constant_magnitude','nonfinite_signal',None])

    def test_all_invalid_has_no_inference_or_fake_negative(self):
        with patch('models.input_validity.validate_bundle'),patch('models.input_validity.predict_windows') as predict:
            rows=predict_windows_with_validity({},np.ones((2,500,1)))
        predict.assert_not_called();self.assertTrue(all(r['stroke_score'] is None for r in rows))

    def test_shape_rejected_and_small_variation_not_arbitrarily_thresholded(self):
        with self.assertRaises(ValueError):screen_windows(np.ones((2,500,3)))
        x=np.ones((1,500,1),dtype='float32');x[0,2,0]+=1e-5
        self.assertTrue(screen_windows(x)[1][0])


if __name__=='__main__':unittest.main()
