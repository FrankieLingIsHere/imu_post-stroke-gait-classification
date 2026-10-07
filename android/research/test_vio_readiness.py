import copy
import unittest
from vio_readiness import assess_readiness


class ReadinessChecks(unittest.TestCase):
    def fixture(self):
        calibration={k:True for k in ('geometryVerified','measuredWhiteNoiseVerified','biasRandomWalkVerified','deviceAndOpticsMatched')}
        rows=[{'timeSeconds':i*.1,'initialized':True,'resetCount':0,'trackedFeatures':30,
               'translationCameraToImuMetres':[.02,0,0],'rotationCameraToImuQuaternionWxyz':[1,0,0,0],
               'velocityMetresPerSecond':[.5,0,0],'accelBias':[.01,0,0],'gyroBias':[.001,0,0],
               'timeOffsetSeconds':.005,'gravityNorm':9.80665} for i in range(25)]
        return rows,calibration

    def test_complete_stable_engineering_fixture_not_clinical(self):
        rows,c=self.fixture();r=assess_readiness(rows,c)
        self.assertTrue(r['researchTrackingReady']);self.assertFalse(r['clinicalReady']);self.assertFalse(r['distanceReady'])

    def test_initialized_without_calibration_or_full_state_never_ready(self):
        rows,c=self.fixture()
        self.assertFalse(assess_readiness(rows,{})['researchTrackingReady'])
        c['geometryVerified']='false'
        self.assertFalse(assess_readiness(rows,c)['researchTrackingReady'])
        del rows[0]['translationCameraToImuMetres']
        self.assertIn('complete-vector-state-telemetry-required',assess_readiness(rows,c)['reasons'])

    def test_reset_gap_impossible_state_and_short_window(self):
        rows,c=self.fixture()
        for key,value in [('resetCount',1),('initialized',False),('velocityMetresPerSecond',[23,0,0]),('translationCameraToImuMetres',[8,0,0])]:
            changed=copy.deepcopy(rows);changed[-1][key]=value
            self.assertFalse(assess_readiness(changed,c)['researchTrackingReady'])
        self.assertFalse(assess_readiness(rows[-10:],c)['researchTrackingReady'])
        self.assertFalse(assess_readiness(rows[:10]+rows[13:],c)['researchTrackingReady'])

    def test_equal_lever_arm_norm_does_not_hide_direction_drift(self):
        rows,c=self.fixture();rows[-1]['translationCameraToImuMetres']=[0,.02,0]
        self.assertIn('camera-imu-calibration-still-changing',assess_readiness(rows,c)['reasons'])

    def test_quaternion_sign_is_not_rotation_drift(self):
        rows,c=self.fixture();rows[-1]['rotationCameraToImuQuaternionWxyz']=[-1,0,0,0]
        self.assertTrue(assess_readiness(rows,c)['researchTrackingReady'])


if __name__=='__main__':unittest.main()
