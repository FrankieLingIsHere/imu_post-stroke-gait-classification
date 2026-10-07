"""Numerical and admission checks, not a physical walking-distance validation."""
import tempfile
import unittest
import zipfile
import json
from pathlib import Path
import numpy as np
import cv2
from scipy.spatial.transform import Rotation
from camera_calibration import board, write_board, fit_gyro_alignment, fit_accel_geometry, point_reprojection_rms, process_bundle, camera_observation_time_seconds


class CalibrationTests(unittest.TestCase):
    def test_hardware_time_uses_feature_row_and_exposure(self):
        result={'exposureNs':20_000_000,'rollingShutterSkewNs':32_000_000}
        frame={'timestampNs':2_000_000_000,'arrivalBootNs':9_000_000_000,'meanFeatureRow':479}
        self.assertAlmostEqual(camera_observation_time_seconds(frame,result,1_000_000_000,0,480),1.042)
        frame['meanFeatureRow']=0
        self.assertAlmostEqual(camera_observation_time_seconds(frame,result,1_000_000_000,0,480),1.010)
        with self.assertRaisesRegex(ValueError,'metadata missing'):
            camera_observation_time_seconds(frame,{},1_000_000_000,0,480)

    def test_projection_shape_aliases_compare_corresponding_points(self):
        observed=np.array([[10.,20.],[30.,40.],[50.,60.]])
        self.assertEqual(point_reprojection_rms(observed[:,None,:],observed),0.)
        self.assertAlmostEqual(point_reprojection_rms((observed+.2)[:,None,:],observed),.2)
        with self.assertRaisesRegex(ValueError,'correspondence mismatch'):
            point_reprojection_rms(observed[:1],observed)

    def test_printed_board_detects_expected_corners(self):
        image = board().generateImage((1800, 1400), marginSize=30)
        corners, ids, _, _ = cv2.aruco.CharucoDetector(board()).detectBoard(image)
        self.assertEqual(len(ids), 48)
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(write_board(directory).exists())

    def test_recovers_rotation_bias_and_offset_from_synthetic_motion(self):
        # Integrate camera-local rates. Inject a separate clock offset and IMU-axis rotation.
        dt=.0025; t=np.arange(0,16,dt)
        rates=np.column_stack([.5*np.sin(.9*t),.4*np.cos(1.3*t),.3*np.sin(1.7*t+.2)])
        rotations=[np.eye(3)]
        for rate in rates[:-1]: rotations.append(rotations[-1]@Rotation.from_rotvec(rate*dt).as_matrix())
        rotation=Rotation.from_euler('xyz',[.2,-.3,.1]).as_matrix()
        bias=np.array([.014,-.009,.005]);offset=.035
        gyro=np.column_stack([np.interp(t-offset,t,rates[:,k]) for k in range(3)])@rotation+bias
        indices=np.arange(0,len(t),27)
        result=fit_gyro_alignment(t[indices],np.asarray(rotations)[indices],t,gyro)
        self.assertTrue(result['passed'],result)
        self.assertLess(abs(result['residualTimeOffsetSeconds']-offset),.004)
        self.assertLess(np.linalg.norm(np.asarray(result['rotationImuToCamera'])-rotation),.004)
        self.assertLess(np.linalg.norm(np.asarray(result['gyroBiasRadS'])-bias),.002)

    def test_stillness_is_not_calibration(self):
        t=np.arange(0,10,.05)
        with self.assertRaisesRegex(ValueError,'excite three axes'):
            fit_gyro_alignment(t,np.tile(np.eye(3),(len(t),1,1)),t,np.zeros((len(t),3)))

    def test_acceleration_geometry_recovers_known_coefficients(self):
        rng=np.random.default_rng(8);count=300
        Q=Rotation.random(count,random_state=rng).as_matrix()
        rdd=rng.normal(size=(count,3,3));pdd=rng.normal(size=(count,3))
        lever=np.array([.04,-.025,.01]);bias=np.array([.05,-.03,.02]);gravity=np.array([0,0,9.80665])
        world=pdd+np.einsum('nij,j->ni',rdd,lever)+Q@bias+gravity
        accel=np.einsum('nji,nj->ni',Q,world)
        result=fit_accel_geometry(pdd,rdd,Q,accel)
        self.assertTrue(result['passed'],result)
        np.testing.assert_allclose(result['cameraToImuInCameraM'],lever,atol=1e-9)
        np.testing.assert_allclose(result['accelerometerBiasMps2'],bias,atol=1e-9)

    def test_unobservable_translation_is_rejected(self):
        result=fit_accel_geometry(np.zeros((100,3)),np.zeros((100,3,3)),np.tile(np.eye(3),(100,1,1)),np.tile([0,0,9.80665],(100,1)))
        self.assertFalse(result['passed'])

    def test_interrupted_capture_never_activates_distance(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'capture.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('manifest.json',json.dumps({'schemaVersion':1,'status':'interrupted','error':None}))
            report=process_bundle(path,Path(directory)/'result')
            self.assertEqual(report['status'],'rejected')
            self.assertFalse(report['distanceReady'])
            self.assertFalse(report['independentDistanceValidation'])
            self.assertTrue(report['errors'])

    def test_unsafe_archive_is_rejected_without_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'capture.zip'
            with zipfile.ZipFile(path,'w') as z: z.writestr('../unsafe','test')
            report=process_bundle(path,Path(directory)/'result')
            self.assertEqual(report['status'],'rejected')
            self.assertIn('Unsafe',report['errors'][0])


if __name__=='__main__': unittest.main(verbosity=2)
