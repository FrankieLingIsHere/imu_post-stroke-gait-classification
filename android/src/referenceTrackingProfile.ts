/** Reuse a same-phone reference as a tracking seed. This is not self-calibration or clinical validation. */
export const REFERENCE_TRACKING_METHOD='ikalibr-reference-reuse-v2';
const keys=['installationId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','opticalSetup'];
const base='ulong2/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c';
const fail=()=>{throw new Error('Saved reference does not match this phone or camera setup.');};
function finite(a:any,n:number):number[]{if(!Array.isArray(a)||a.length!==n||a.some(x=>typeof x!=='number'||!Number.isFinite(x)))return fail();return a;}
function parameter(p:any,section:string,key:string,topic:string){const a=p?.[section]?.[key];if(!Array.isArray(a))return fail();const rows=a.filter((r:any)=>r.key===topic);if(rows.length!==1)return fail();return rows[0].value;}
export function referenceTrackingFit(r:any,binding:any){
 const s=r?.software,b=r?.binding,l=r?.lensProfile;
 const verified=s?.image===base||s?.image==='sha256:e6b2e0e5dd4e88831560e1d3d3012d69673c00f2e58f0c6b0c85e3ba610f1b91'&&s.executableSha256==='b01cdfb24f098e6be0a35ead8b55932f6899cd892c07d4c1ac09738ae690b429'&&s.baseImage===base&&['cpu','cuda'].includes(s.experimentalBackend);
 if(r?.schemaVersion!==1||r.kind!=='phone-reference-camera-imu-calibration-v1'||r.method!=='ikalibr-tro-2025'||r.status!=='reference-solved-review-required'
  ||r.cameraImuCandidateReady!==false||r.fullCalibrationReady!==false||r.distanceReady!==false||r.independentDistanceValidation!==false||!Array.isArray(r.reviewRequired)||!r.reviewRequired.length
  ||!verified||!/^[a-f0-9]{64}$/.test(s?.executableSha256??'')||!/^[a-f0-9]{64}$/.test(r.sourceSha256??'')
  ||!binding?.installationId||keys.some(k=>b?.[k]!==binding[k])||b.capturePipeline!=='native-camera-imu-v2'||binding.capturePipeline!=='native-camera-imu-v3'
  ||binding.width!==640||binding.height!==480||binding.imageAxes!=='native-sensor-unrotated-unmirrored'||binding.opticalSetup!=='waist-bag-window'||binding.stabilizationRequested!=='off'
  ||![0,90,180,270].includes(binding.sensorOrientationDegrees)||l?.method!=='opencv-zhang-2000'||l.lensReady!==true||keys.some(k=>l.binding?.[k]!==b[k])||l.binding.capturePipeline!==b.capturePipeline)return fail();
 const lens=l.lens,m=lens?.cameraMatrix;if(!Array.isArray(m)||m.length!==3)return fail();m.forEach((row:any)=>finite(row,3));
 const d=finite(lens.distortion,5),k=[m[0][0],m[1][1],m[0][2],m[1][2],...d.slice(0,4)];
 if(lens.model!=='opencv-pinhole-radtan5'||m[0][1]!==0||m[1][0]!==0||m[2][0]!==0||m[2][1]!==0||m[2][2]!==1||k[0]<150||k[0]>1600||k[1]<150||k[1]>1600||k[2]<160||k[2]>480||k[3]<120||k[3]>360||d.some(v=>Math.abs(v)>1))return fail();
 const p=r.upstreamParameters?.CalibParam,q=parameter(p,'EXTRI','SO3_CmToBr','/gaittrace/camera'),t=parameter(p,'EXTRI','POS_CmInBr','/gaittrace/camera');
 const [x,y,z,w]=finite([q.qx,q.qy,q.qz,q.qw],4),v=finite([t.r0c0,t.r1c0,t.r2c0],3);
 if(Math.abs(x*x+y*y+z*z+w*w-1)>1e-5||Math.hypot(...v)>.25)return fail();
 const iq=parameter(p,'EXTRI','SO3_BiToBr','/gaittrace/imu'),it=parameter(p,'EXTRI','POS_BiInBr','/gaittrace/imu');
 finite([iq.qx,iq.qy,iq.qz,iq.qw,it.r0c0,it.r1c0,it.r2c0],7);
 const imuTime=parameter(p,'TEMPORAL','TO_BiToBr','/gaittrace/imu');
 if(!Number.isFinite(imuTime)||Math.max(Math.abs(iq.qx),Math.abs(iq.qy),Math.abs(iq.qz),Math.abs(iq.qw-1),Math.abs(it.r0c0),Math.abs(it.r1c0),Math.abs(it.r2c0),Math.abs(imuTime))>1e-8)return fail();
 const td=parameter(p,'TEMPORAL','TO_CmToBr','/gaittrace/camera'),rs=parameter(p,'TEMPORAL','RS_READOUT','/gaittrace/camera');
 if(!Number.isFinite(td)||Math.abs(td)>.15||!Number.isFinite(rs)||rs<0||rs>.1)return fail();
 // Hamilton camera->IMU equals JPL IMU->camera quaternion; camera-frame translation is -R^T p.
 const R=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]];
 return {cameraValues:k,fixedLensK3:d[4],imuToCamera:[x,y,z,w,...[0,1,2].map(i=>-R.reduce((sum,row,j)=>sum+row[i]*v[j],0))],timeOffsetSeconds:td,readoutSeconds:rs};
}
export function validateReferenceTrackingProfile(p:any,binding:any){
 if(p?.schemaVersion!==1||p.kind!=='phone-on-device-camera-imu-profile-v1'||p.method!==REFERENCE_TRACKING_METHOD||p.upstreamCommit!=='69488123ed9362dd44b6f28e7f4680abbff1442b'
  ||p.computerUsed!==true||p.groundTruthDistanceUsed!==false||p.independentDistanceValidation!==false||p.numericalCalibrationReady!==false||p.trackingSeedReady!==true
  ||p.geometryConversion!=='radtan5-fixed-k3-v2'||p.sourceSha256!==p.sourceReference?.sourceSha256||[...keys,'capturePipeline'].some(k=>p.binding?.[k]!==binding?.[k]))return fail();
 const fit=referenceTrackingFit(p.sourceReference,binding);
 for(const key of ['cameraValues','imuToCamera'] as const){const a=finite(p.fit?.[key],fit[key].length);if(a.some((v,i)=>Math.abs(v-fit[key][i])>1e-10))return fail();}
 if(p.fit?.timeOffsetSeconds!==fit.timeOffsetSeconds||p.fit?.readoutSeconds!==fit.readoutSeconds||p.fit?.fixedLensK3!==fit.fixedLensK3)return fail();
 return p;
}
