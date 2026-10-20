/** Pure admission contract shared by the app and offline replay. */
import {REFERENCE_TRACKING_METHOD,validateReferenceTrackingProfile} from './referenceTrackingProfile';

export const PHONE_SETUP_METHOD='openvins-self-calibration-v1';
export const PHONE_SETUP_COMMIT='69488123ed9362dd44b6f28e7f4680abbff1442b';
const keys=['installationId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','capturePipeline','opticalSetup'];
export function validateOnDeviceProfile(p:any,binding:any){
 if(p?.method===REFERENCE_TRACKING_METHOD)return validateReferenceTrackingProfile(p,binding);
 const fail=()=>{throw new Error('Phone setup changed or has not completed. Set up this phone again.');};
 if(p?.schemaVersion!==1||p.kind!=='phone-on-device-camera-imu-profile-v1'||p.method!==PHONE_SETUP_METHOD||p.upstreamCommit!==PHONE_SETUP_COMMIT
  ||p.computerUsed!==false||p.groundTruthDistanceUsed!==false||p.independentDistanceValidation!==false||p.numericalCalibrationReady!==true||p.stableTailAccepted!==true
  ||!/^[a-f0-9]{64}$/.test(p.sourceSha256??'')||!binding?.installationId||keys.some(k=>p.binding?.[k]!==binding[k])
  ||binding.width!==640||binding.height!==480||binding.capturePipeline!=='native-camera-imu-v3'||binding.opticalSetup!=='waist-bag-window'
  ||binding.imageAxes!=='native-sensor-unrotated-unmirrored'||binding.stabilizationRequested!=='off'||![0,90,180,270].includes(binding.sensorOrientationDegrees))return fail();
 const r=p.fit,k=r?.cameraValues,e=r?.imuToCamera,s=r?.calibrationStd,m=r?.axisMotionRadians;
 if(r?.initialized!==true||r.integrity!==true||r.numericalCalibrationReady!==true||!Number.isInteger(r.updates)||r.updates<200||!Number.isFinite(r.positionStdMetres)||r.positionStdMetres<0||r.positionStdMetres>=.15
  ||[[k,8],[e,7],[s,15],[m,3]].some(([a,n])=>!Array.isArray(a)||a.length!==n||a.some((x:any)=>typeof x!=='number'||!Number.isFinite(x)))
  ||k[0]<150||k[0]>1600||k[1]<150||k[1]>1600||k[2]<160||k[2]>480||k[3]<120||k[3]>360||k.slice(4).some((v:number)=>Math.abs(v)>1)
  ||Math.abs(e.slice(0,4).reduce((a:number,b:number)=>a+b*b,0)-1)>1e-5||Math.hypot(...e.slice(4))>.25
  ||s.some((v:number)=>v<0)||s[0]/k[0]>=.04||s[1]/k[1]>=.04||Math.max(s[2],s[3])>=6||Math.max(...s.slice(8,11))>=.035||Math.max(...s.slice(11,14))>=.015||s[14]>=.003
  ||m.some((v:number)=>v<.5)||!Number.isFinite(r.timeOffsetSeconds)||Math.abs(r.timeOffsetSeconds)>.15||!Number.isFinite(r.readoutSeconds)||r.readoutSeconds<0||r.readoutSeconds>.1)return fail();
 return p;
}
