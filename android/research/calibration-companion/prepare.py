"""Convert device measurements to upstream iKalibr inputs. No calibration math.
Runs inside the pinned reference image; raw ZIP is retained unchanged.
"""
import hashlib,json,zipfile
from pathlib import Path
import numpy as np
import yaml,rosbag,rospy
from sensor_msgs.msg import Imu,CompressedImage,MagneticField

ROOT=Path('/data');SOURCE=ROOT/'input.zip'
def rows(z,name):return [json.loads(r) for r in z.read(name).decode().splitlines() if r.strip()]
def fail(reason):raise ValueError(reason)

with zipfile.ZipFile(SOURCE) as z:
    if sum(i.file_size for i in z.infolist())>350*1024**2:fail('Capture is too large to process.')
    meta=json.loads(z.read('manifest.json'))
    if meta.get('kind')!='phone-camera-imu-alignment-capture-v1' or meta.get('status')!='completed' or meta.get('error'):fail('A completed sensor-alignment capture is needed.')
    if meta.get('timestampSource')!='realtime' or meta.get('units')!={'accelerometer':'m/s2','gyroscope':'rad/s','magnetometer':'uT'}:fail('The capture clocks or sensor units are not supported.')
    lens=meta.get('lensProfile',{})
    if lens.get('method')!='opencv-zhang-2000' or lens.get('lensReady') is not True or lens.get('distanceReady') is not False:fail('A matching lens calibration is needed.')
    keys=['installationId','cameraId','width','height','imageAxes','sensorOrientationDegrees','capturePipeline','opticalSetup']
    if any(lens.get('binding',{}).get(k)!=meta.get(k) for k in keys):fail('Lens parameters do not match this camera setup.')
    frames=rows(z,'frames.ndjson');results={r['timestampNs']:r for r in rows(z,'capture-results.ndjson')};imu=rows(z,'imu.ndjson')
    origin=int(meta.get('alignmentMovementStartedBootNs',0))
    if not origin:fail('Calibration guidance did not finish.')
    groups={s:[r for r in imu if r['sensor']==s] for s in ['accelerometer','gyroscope','magnetometer']}
    for name,data in groups.items():
        t=np.array([r['timestampNs'] for r in data],dtype=np.int64);v=np.array([[r[k] for k in ['x','y','z']] for r in data])
        if len(t)<100 or np.any(np.diff(t)<=0) or not np.isfinite(v).all():fail('Sensor readings are missing or invalid.')
        if np.max(np.diff(t))/1e9>(.15 if name=='magnetometer' else .025):fail('Sensor timing had a gap.')
        if name in ['accelerometer','gyroscope']:
            active=v[t>=origin]
            if len(active)<100 or np.min(np.linalg.eigvalsh(np.cov(active.T)))<(1e-4 if name=='gyroscope' else .001):fail('More varied movement is needed for sensor alignment.')
    times=np.array([f['timestampNs'] for f in frames],dtype=np.int64)
    if len(times)<300 or np.any(np.diff(times)<=0) or np.max(np.diff(times))/1e9>.2 or (times[-1]-origin)/1e9<40:fail('Not enough continuous camera frames were saved.')
    K=np.array(lens['lens']['cameraMatrix']);D=lens['lens']['distortion']
    intrinsics={'Intrinsics':{'polymorphic_id':2147483649,'polymorphic_name':'pinhole_brown_t2','ptr_wrapper':{'id':2147483649,'data':{
        'img_width':meta['width'],'img_height':meta['height'],'focal_length':[float(K[0,0]),float(K[1,1])],
        'principal_point':[float(K[0,2]),float(K[1,2])],'disto_param':[D[0],D[1],D[4],D[2],D[3]]}}}}
    # Upstream OutputDataFormat also controls intrinsic-file deserialization.
    # Keep input/output archives consistently JSON; config itself remains YAML.
    (ROOT/'camera.json').write_text(json.dumps(intrinsics))
    imu_template=Path('/home/iKalibr/install/share/ikalibr/config/imu-intri.yaml')
    (ROOT/'imu.json').write_text(json.dumps(yaml.safe_load(imu_template.read_text())))
    template=Path('/home/iKalibr/install/share/ikalibr/config/ikalibr-config.yaml')
    config=yaml.safe_load(template.read_text());c=config['Configor'];stream=c['DataStream']
    stream['IMUTopics']=[{'key':'/gaittrace/imu','value':{'Type':'SENSOR_IMU','Intrinsics':'/data/imu.json','AcceWeight':1.,'GyroWeight':1.}}]
    stream['CameraTopics']=[{'key':'/gaittrace/camera','value':{'Type':'SENSOR_IMAGE_COMP_RS_MID','Intrinsics':'/data/camera.json','Weight':50.,'TrackLengthMin':10,'ScaleSplineType':'LIN_POS_SPLINE'}}]
    for key in ['RadarTopics','LiDARTopics','RGBDTopics','EventTopics']:stream[key]=[]
    stream.update(ReferIMU='/gaittrace/imu',BagPath='/data/capture.bag',BeginTime=-1.,Duration=-1.,OutputPath='/data/output')
    c['Prior'].update(GravityNorm=9.80665,SpatTempPrioriPath='',OptTemporalParams=True,TimeOffsetPadding=.1,ReadoutTimePadding=.04)
    c['Preference'].update(UseCudaInSolving=False,Outputs=['ParamInEachIter','VisualReprojErrors','AlignedInertialMes'],OutputDataFormat='JSON',ThreadsToUse=2)
    (ROOT/'config.yaml').write_text(yaml.safe_dump(config,sort_keys=False));(ROOT/'output').mkdir(exist_ok=True)
    accel=groups['accelerometer'];at=np.array([r['timestampNs'] for r in accel],dtype=np.int64);av=np.array([[r[k] for k in ['x','y','z']] for r in accel])
    # Interpolate acceleration only to measured gyro timestamps with close real
    # bracketing readings. Raw streams and all original sensor clocks stay in ZIP.
    def stamp(ns):return rospy.Time(int(ns)//10**9,int(ns)%10**9)
    with rosbag.Bag(str(ROOT/'capture.bag'),'w') as bag:
        for row in groups['gyroscope']:
            ts=row['timestampNs'];j=np.searchsorted(at,ts)
            if j==0 or j==len(at):continue
            if at[j]-at[j-1]>25000000:fail('Acceleration and gyroscope timing cannot be paired.')
            a=av[j-1]+(av[j]-av[j-1])*float(ts-at[j-1])/float(at[j]-at[j-1])
            msg=Imu();msg.header.stamp=stamp(ts);msg.header.frame_id='phone_imu';msg.orientation_covariance[0]=-1
            msg.angular_velocity.x,msg.angular_velocity.y,msg.angular_velocity.z=[row[k] for k in ['x','y','z']]
            msg.linear_acceleration.x,msg.linear_acceleration.y,msg.linear_acceleration.z=[float(v) for v in a]
            bag.write('/gaittrace/imu',msg,msg.header.stamp)
        for f in frames:
            r=results.get(f['timestampNs']);name=f['file']
            if not r or r.get('exposureNs') is None or r.get('rollingShutterSkewNs') is None:fail('Camera timing data was unavailable.')
            if not name.startswith('frames/') or '..' in name or not name.endswith('.jpg'):fail('Invalid camera frame path.')
            ts=int(f['timestampNs']+r['exposureNs']/2+r['rollingShutterSkewNs']/2)
            msg=CompressedImage();msg.header.stamp=stamp(ts);msg.header.frame_id='phone_front_camera';msg.format='jpeg';msg.data=z.read(name)
            bag.write('/gaittrace/camera',msg,msg.header.stamp)
        for row in groups['magnetometer']:
            msg=MagneticField();msg.header.stamp=stamp(row['timestampNs'])
            msg.magnetic_field.x,msg.magnetic_field.y,msg.magnetic_field.z=[row[k]*1e-6 for k in ['x','y','z']]
            bag.write('/gaittrace/magnetometer',msg,msg.header.stamp)
    (ROOT/'provenance.json').write_text(json.dumps({'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'metadata':meta,
        'cameraClockConvention':'exposure-and-readout-midpoint; upstream RS_MID','imuConversion':'acceleration interpolated at real gyro timestamps','magnetometerUse':'retained; not an iKalibr input',
        'noiseWeights':'equal provisional IMU weights; not a verified long-term noise model','imageRateHz':float(1e9/np.median(np.diff(times)))},indent=2))
