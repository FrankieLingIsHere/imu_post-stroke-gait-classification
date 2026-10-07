"""Display-only ChArUco framing; never a calibration solver or admission gate.

Phone JPEGs are decoded in memory and discarded. Return corner positions only,
so the computer does not display a second copy of the coded calibration target.
"""
import base64,io
import cv2
import numpy as np
from PIL import Image

def frame_outline(jpeg):
    if not isinstance(jpeg,str) or len(jpeg)>1400000:raise ValueError('Invalid preview.')
    data=base64.b64decode(jpeg,validate=True)
    if len(data)>1024**2:raise ValueError('Invalid preview.')
    with Image.open(io.BytesIO(data)) as header:
        width,height=header.size
        if header.format!='JPEG' or not 0<width<=1920 or not 0<height<=1920 or width*height>1280*960:
            raise ValueError('Invalid preview dimensions.')
    gray=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_GRAYSCALE)
    if gray is None:raise ValueError('Invalid preview.')
    board=cv2.aruco.CharucoBoard((9,7),1.,.75,cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100))
    corners,ids,_,_=cv2.aruco.CharucoDetector(board).detectBoard(gray)
    points=[] if ids is None else corners.reshape(-1,2)
    points=np.asarray(points,dtype=np.float32).reshape(-1,2)
    if not np.isfinite(points).all():raise ValueError('Invalid preview detections.')
    outline=[]
    if len(points)>=4:
        objects=board.getChessboardCorners()[ids.ravel(),:2]
        matrix,_=cv2.findHomography(objects,points,cv2.RANSAC,3.)
        if matrix is not None:
            projected=cv2.perspectiveTransform(np.float32([[[0,0],[9,0],[9,7],[0,7]]]),matrix).reshape(-1,2)
            # Bound speculative projection from a poorly conditioned partial view.
            if np.isfinite(projected).all() and np.max(np.abs(projected))<=max(width,height)*4:
                outline=(projected/[width,height]).tolist()
    return {'width':width,'height':height,'corners':(points/[width,height]).tolist(),'outline':outline,
            'kind':'display-only-charuco-framing','calibrationAuthority':False}
