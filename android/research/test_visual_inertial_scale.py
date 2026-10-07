"""Synthetic known-answer recovery and degeneracy checks; no phone accuracy claim."""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from visual_inertial_scale import fit_metric_scale,screen_route


class ScaleTests(unittest.TestCase):
    def inputs(self):
        rng=np.random.default_rng(91);t=np.arange(0,20,.02)
        R=Rotation.from_euler('xyz',np.column_stack([.3*np.sin(t),.2*np.cos(1.3*t),.25*np.sin(.7*t)])).as_matrix()
        Rdd=np.gradient(np.gradient(R,.02,axis=0),.02,axis=0)
        pdd=np.column_stack([.6*np.sin(1.8*t),.7*np.cos(2.1*t),.5*np.sin(2.8*t)])
        scale=2.7;bias=np.array([.08,-.03,.05]);gravity=np.array([0.,0.,-9.80665]);lever=np.array([.02,-.01,.015])
        world=scale*pdd-Rdd@lever-gravity
        force=np.einsum('nji,nj->ni',R,world)+bias+rng.normal(0,.01,(len(t),3))
        return pdd,R,Rdd,force,scale

    def test_known_metric_scale_without_route_distance(self):
        p,R,Rdd,f,scale=self.inputs();out=fit_metric_scale(p,R,Rdd,f)
        self.assertEqual(out['status'],'scale-candidate',out)
        self.assertLess(abs(out['metresPerMapUnit']-scale),.015)
        self.assertFalse(out['distanceReady'])

    def test_stillness_or_constant_speed_cannot_identify_distance(self):
        p,R,Rdd,f,_=self.inputs();out=fit_metric_scale(np.zeros_like(p),R,Rdd,f)
        self.assertEqual(out['status'],'rejected')
        self.assertNotIn('metresPerMapUnit',out)

    def test_inconsistent_visual_motion_is_rejected(self):
        p,R,Rdd,f,_=self.inputs();out=fit_metric_scale(p[::-1],R,Rdd,f)
        self.assertEqual(out['status'],'rejected',out)

    def test_missing_samples_are_not_filled(self):
        p,R,Rdd,f,_=self.inputs();p[3,0]=np.nan
        with self.assertRaisesRegex(ValueError,'Nonfinite'):fit_metric_scale(p,R,Rdd,f)

    def test_route_connector_uses_camera_poses_and_si_imu(self):
        t=np.arange(0,16.001,.02);scale=2.7
        R=Rotation.from_euler('xyz',np.column_stack([.3*np.sin(.7*t),.2*np.cos(.9*t),.25*np.sin(.6*t)])).as_matrix()
        positions=np.column_stack([.2*t+.3*np.sin(.8*t),.2*np.cos(1.1*t),.15*np.sin(1.3*t)])
        pdd=np.column_stack([-.3*.8**2*np.sin(.8*t),-.2*1.1**2*np.cos(1.1*t),-.15*1.3**2*np.sin(1.3*t)])
        Rdd=np.gradient(np.gradient(R,.02,axis=0),.02,axis=0)
        bias=np.array([.02,-.01,.03]);lever=np.array([.01,-.01,.02]);gravity=np.array([0.,0.,-9.80665])
        force=np.einsum('nji,nj->ni',R,scale*pdd-Rdd@lever-gravity)+bias
        gyro=Rotation.from_matrix(R[:-1].transpose(0,2,1)@R[1:]).as_rotvec()/.02
        gyro=np.vstack([gyro,gyro[-1]])
        out=screen_route({'times':t,'positionsMap':positions,'rotationsCameraWorld':R.transpose(0,2,1)},
                         t,gyro,t,force,np.eye(3),0.)
        self.assertEqual(out['status'],'scale-candidate',out)
        self.assertLess(abs(out['metresPerMapUnit']-scale),.15)
        self.assertGreater(out['experimentalHorizontalCameraPathMetres'],1.)
        self.assertFalse(out['distanceReady'])


if __name__=='__main__':unittest.main(verbosity=2)
