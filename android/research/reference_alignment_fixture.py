"""Image/IMU control for exercising the published executable, never phone data.
The themed notebook owns orchestration, saved results and interpretation.
"""
import io,json,zipfile
from pathlib import Path
import cv2
import numpy as np
from scipy.spatial.transform import Rotation

def write_alignment_control(destination):
    rng=np.random.default_rng(71026)
    dt=.005;t=np.arange(0,60,dt);active=np.maximum(t-10,0)
    ramp=np.minimum(active/3,1);ramp=ramp*ramp*(3-2*ramp)
    angles=np.column_stack([.22*np.sin(.8*active),.24*np.sin(.63*active),.16*np.sin(1.03*active)])*ramp[:,None]
    R=Rotation.from_euler('xyz',angles).as_matrix()
    p=np.column_stack([.8*np.sin(.55*active),.45*np.sin(.79*active),.25*np.sin(.92*active)])*ramp[:,None]
    lever=np.array([.025,.018,.012]);camera_position=p+R@lever
    accel=np.einsum('nji,nj->ni',R,np.gradient(np.gradient(p,dt,axis=0),dt,axis=0)-[0,0,-9.80665])
    gyro=Rotation.from_matrix(R[:-1].transpose(0,2,1)@R[1:]).as_rotvec()/dt;gyro=np.vstack([gyro,gyro[-1]])
    K=np.array([[420.,0,320.],[0,420.,240.],[0,0,1.]])
    binding={'installationId':'synthetic-reference-control','captureId':'synthetic-lens-control','cameraId':'front-control','width':640,'height':480,'imageAxes':'native-camera-unmirrored','sensorOrientationDegrees':0,'stabilizationRequested':'off','capturePipeline':'camera2-native-frames-v2','opticalSetup':'clear-lens'}
    lens={'schemaVersion':1,'kind':'phone-camera-lens-calibration-v1','method':'opencv-zhang-2000','binding':binding,'lensReady':True,'distanceReady':False,'lens':{'cameraMatrix':K.tolist(),'distortion':[0.,0.,0.,0.,0.]},'source':'synthetic-known-answer'}
    meta={**binding,'captureId':'synthetic-alignment-control','kind':'phone-camera-imu-alignment-capture-v1','status':'completed','timestampSource':'realtime','alignmentMovementStartedBootNs':110000000000,'units':{'accelerometer':'m/s2','gyroscope':'rad/s','magnetometer':'uT'},'lensProfile':lens,'source':'synthetic-known-answer-not-phone-or-gait-data'}
    # Fixed textured patches at several depths give SfM real correspondence and
    # parallax, rather than injecting poses into the reference engine.
    patches=[]
    for i in range(220):
        center=np.array([rng.uniform(-3,3),rng.uniform(-2.1,2.1),rng.uniform(2.1,5.2)])
        half=rng.uniform(.065,.12);corners=center+np.array([[-half,-half,0],[half,-half,0],[half,half,0],[-half,half,0]])
        texture=rng.integers(30,240,(8,8),dtype=np.uint8);texture=cv2.resize(texture,(48,48),interpolation=cv2.INTER_NEAREST)
        patches.append((center[2],corners,texture))
    patches.sort(reverse=True,key=lambda x:x[0]);source=np.float32([[0,0],[47,0],[47,47],[0,47]])
    frames=[];results=[];imu=[]
    for i,v in enumerate(t):
        ns=100000000000+round(v*1e9)
        for name,value in [('accelerometer',accel[i]),('gyroscope',gyro[i])]:
            imu.append({'sensor':name,'timestampNs':ns,'x':float(value[0]),'y':float(value[1]),'z':float(value[2])})
        if i%4==0:imu.append({'sensor':'magnetometer','timestampNs':ns,'x':25.,'y':0.,'z':-40.})
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for i in range(0,len(t),20):
            img=np.full((480,640),18,np.uint8)
            for _,corners,texture in patches:
                pts=(corners-camera_position[i])@R[i];xy=pts[:,:2]/pts[:,2:]*[420,420]+[320,240]
                if np.any(pts[:,2]<.1) or np.max(xy[:,0])<0 or np.min(xy[:,0])>=640 or np.max(xy[:,1])<0 or np.min(xy[:,1])>=480:continue
                H=cv2.getPerspectiveTransform(source,xy.astype(np.float32));warped=cv2.warpPerspective(texture,H,(640,480));mask=cv2.warpPerspective(np.full((48,48),255,np.uint8),H,(640,480));img[mask>0]=warped[mask>0]
            ns=100000000000+round(t[i]*1e9);name=f'frames/frame-{i:06d}.jpg'
            z.writestr(name,cv2.imencode('.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,92])[1].tobytes())
            frames.append({'file':name,'timestampNs':ns});results.append({'timestampNs':ns,'exposureNs':0,'rollingShutterSkewNs':0})
        z.writestr('manifest.json',json.dumps(meta))
        for name,rows in [('frames.ndjson',frames),('capture-results.ndjson',results),('imu.ndjson',imu)]:z.writestr(name,'\n'.join(json.dumps(r) for r in rows))
    expected={'source':meta['source'],'T_camera_in_imu_m':lever.tolist(),'rotation_camera_in_imu_xyzw':[0,0,0,1],'time_offset_s':0.,'readout_s':0.,'frameRateHz':10.,'frames':len(frames),'durationSeconds':60.}
    destination.with_suffix('.expected.json').write_text(json.dumps(expected,indent=2))
    return expected
