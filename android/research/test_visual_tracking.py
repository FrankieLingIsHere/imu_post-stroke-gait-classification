import unittest
import cv2
import numpy as np
from visual_tracking import initialize_map,locate_camera,track_native_frames


class TrackingTests(unittest.TestCase):
    def test_camera_gap_does_not_reset_map_and_continue_distance(self):
        image=np.random.default_rng(13).integers(0,256,(480,640),dtype=np.uint8)
        with self.assertRaisesRegex(ValueError,'clock gap'):
            track_native_frames([(0.,image),(.5,image)],np.eye(3),np.zeros(5))

    def test_one_map_preserves_relative_translation_scale(self):
        rng=np.random.default_rng(72)
        X=np.column_stack([rng.uniform(-2,2,150),rng.uniform(-1.5,1.5,150),rng.uniform(4,9,150)])
        K=np.array([[500.,0,320],[0,500.,240],[0,0,1.]])
        def project(position):return cv2.projectPoints(X,np.zeros(3),-np.asarray(position,dtype=float),K,np.zeros(5))[0].reshape(-1,2)
        result=initialize_map(project([0,0,0]),project([.6,0,0]),K,np.zeros(5))
        # Corresponding second-view pixels identify which triangulated landmarks survived.
        indices=[np.argmin(np.linalg.norm(project([.6,0,0])-p,axis=1)) for p in result['secondPixels']]
        _,position,_,_=locate_camera(result['pointsMap'],project([1.2,.12,0])[indices],K,np.zeros(5))
        self.assertLess(np.linalg.norm(position-np.array([2.,.2,0.])),.01)
        self.assertFalse(result['distanceReady'])

    def test_pure_rotation_does_not_establish_distance_scale(self):
        rng=np.random.default_rng(81);K=np.array([[500.,0,320],[0,500.,240],[0,0,1.]])
        X=np.column_stack([rng.uniform(-2,2,120),rng.uniform(-1,1,120),rng.uniform(4,8,120)])
        first=cv2.projectPoints(X,np.zeros(3),np.zeros(3),K,np.zeros(5))[0].reshape(-1,2)
        second=cv2.projectPoints(X,np.array([0,.15,0]),np.zeros(3),K,np.zeros(5))[0].reshape(-1,2)
        with self.assertRaises(ValueError):initialize_map(first,second,K,np.zeros(5))


if __name__=='__main__':unittest.main(verbosity=2)
