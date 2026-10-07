import base64,unittest
import cv2
import numpy as np
from lens_framing import frame_outline

def image_frame(partial=False,blank=False):
    image=np.full((480,640),255,np.uint8)
    if not blank:
        board=cv2.aruco.CharucoBoard((9,7),1.,.75,cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100))
        target=board.generateImage((450,350));left=-100 if partial else 90
        visible_start=max(0,-left);image[60:410,max(0,left):left+450]=target[:,visible_start:]
    ok,data=cv2.imencode('.jpg',image);assert ok
    return base64.b64encode(data).decode()

class FramingChecks(unittest.TestCase):
    def test_real_detector_reports_centered_partial_and_absent_targets_without_admitting_calibration(self):
        whole=frame_outline(image_frame());partial=frame_outline(image_frame(partial=True));blank=frame_outline(image_frame(blank=True))
        self.assertEqual(len(whole['corners']),48);self.assertEqual(len(whole['outline']),4)
        self.assertGreater(len(partial['corners']),0);self.assertLess(len(partial['corners']),48)
        self.assertTrue(any(p[0]<0 for p in partial['outline']),'Projection shows clipping')
        self.assertEqual(blank['corners'],[]);self.assertEqual(blank['outline'],[])
        for result in [whole,partial,blank]:
            self.assertFalse(result['calibrationAuthority']);self.assertNotIn('jpeg',result)
            self.assertEqual((result['width'],result['height']),(640,480))
            self.assertTrue(all(0<=x<=1 and 0<=y<=1 for x,y in result['corners']))
    def test_bad_or_oversized_frames_are_rejected_without_coordinates(self):
        for value in ['broken','a'*1400001,base64.b64encode(b'not a jpeg').decode(),None]:
            with self.assertRaises((ValueError,OSError)):frame_outline(value)
        image=np.zeros((1500,1500),np.uint8);_,data=cv2.imencode('.jpg',image)
        with self.assertRaises(ValueError):frame_outline(base64.b64encode(data).decode())

if __name__=='__main__':unittest.main()
