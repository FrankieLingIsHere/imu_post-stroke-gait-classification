"""Known-answer checks for row-specific timing, not phone distance validation."""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from camera_imu_joint import integrate_gyro,project_rows,fit_joint_rotation_timing


class JointTests(unittest.TestCase):
    def test_gyro_rotation_integration(self):
        times=np.arange(0,2.001,.005)
        curve=integrate_gyro(times,np.tile([0,0,.3],(len(times),1)),np.zeros(3))
        self.assertAlmostEqual(curve(2).as_rotvec()[2],.6,places=9)

    def test_stillness_cannot_calibrate_three_axis_alignment(self):
        with self.assertRaisesRegex(ValueError,'excitation'):
            fit_joint_rotation_timing([{}]*40,np.arange(100)*.01,np.zeros((100,3)),np.eye(3),np.zeros(5),{})

    def test_clock_extrapolation_is_rejected(self):
        times=np.arange(0,2.001,.005)
        curve=integrate_gyro(times,np.tile([0,0,.3],(len(times),1)),np.zeros(3))
        with self.assertRaisesRegex(ValueError,'coverage'):
            project_rows({'times':np.array([3.]),'object':np.zeros((1,3))},np.zeros(10),np.zeros(3),curve,np.eye(3),np.zeros(5))

    def test_row_timing_recovers_known_rotation_and_offset(self):
        rng=np.random.default_rng(44);t=np.arange(0,10.005,.005)
        unbiased=np.column_stack([.4*np.sin(.9*t),.3*np.cos(1.3*t),.3*np.sin(1.7*t)])
        bias=np.array([.008,-.012,.005]);gyro=unbiased+bias
        Rci=Rotation.from_euler('xyz',[.2,-.3,.1]).as_matrix();offset=.035
        parameters=np.r_[Rotation.from_matrix(Rci).as_rotvec(),bias,offset,Rotation.from_matrix(Rci).as_rotvec()]
        curve=integrate_gyro(t,gyro,bias);K=np.array([[500.,0,320],[0,500.,240],[0,0,1]])
        points=np.array([[x*.02,y*.02,0.] for x in range(1,8) for y in range(1,6)])
        views=[]
        for timestamp in np.arange(1,7.5,.16):
            position=np.array([.07+.015*np.sin(timestamp),.05,-.65+.02*np.cos(timestamp)])
            v={'object':points,'times':np.full(len(points),timestamp+.03),'image':None}
            for _ in range(5):
                image=project_rows(v,parameters,position,curve,K,np.zeros(5))
                v['times']=timestamp+.015+np.clip(image[:,1]/479,0,1)*.032
            v['image']=project_rows(v,parameters,position,curve,K,np.zeros(5))+rng.normal(0,.1,(len(points),2))
            v['positionWorldCamera']=position.copy()
            v['rotationWorldCamera']=Rci@curve(float(np.mean(v['times'])+offset)).as_matrix()@Rci.T
            views.append(v)
        initial={'rotationImuToCamera':(Rotation.from_rotvec([.015,-.01,.01])*Rotation.from_matrix(Rci)).as_matrix(),
                 'gyroBiasRadS':bias+np.array([.001,-.001,.001]),'residualTimeOffsetSeconds':.025}
        result=fit_joint_rotation_timing(views,t,gyro,K,np.zeros(5),initial,max_evaluations=60)
        self.assertTrue(result['passed'],result)
        self.assertLess(abs(result['residualTimeOffsetSeconds']-offset),.006)
        self.assertLess(np.linalg.norm(np.asarray(result['rotationImuToCamera'])-Rci),.025)
        self.assertFalse(result['distanceReady'])

if __name__=='__main__':unittest.main(verbosity=2)
