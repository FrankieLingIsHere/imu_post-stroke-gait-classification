import type {AssessmentProtocol} from './store';
export const GAIT_DISTANCE_VERSION='gait-camera-distance-v1';
export const distanceBindingKeys=['installationId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','capturePipeline','opticalSetup'] as const;
export type GaitCameraDistance={
 version:typeof GAIT_DISTANCE_VERSION;sessionId:string;captureId:string;protocol:AssessmentProtocol;
 status:'capturing'|'saved'|'processing'|'complete'|'unavailable';referenceSha256:string;
 binding:Record<string,unknown>;jobId?:string;result?:Record<string,any>;
 distanceM:number|null;meanSpeedMps:number|null;intervalSeconds:number|null;reason:string;
};
export function distanceGeometry(protocol:AssessmentProtocol){return ['10mwt','research-walk'].includes(protocol)?'straight':'with-turns';}
export function validateGaitDistanceResult(result:any,pending:GaitCameraDistance){
 const live=result?.method==='openvins-on-device-live-v1';
 if(result?.schemaVersion!==1||result.kind!=='gait-camera-distance-result-v1'||!['vins-mono-offline-reference-v1','vins-mono-on-device-v1','openvins-on-device-live-v1'].includes(result.method)
  ||result.sessionId!==pending.sessionId||result.captureId!==pending.captureId||result.protocol!==pending.protocol
  ||result.referenceCalibrationSha256!==pending.referenceSha256||! /^[0-9a-f]{64}$/.test(result.sourceSha256??'')
  ||distanceBindingKeys.some(k=>result.binding?.[k]!==pending.binding[k])
  ||result.distanceReady!==false||result.independentDistanceValidation!==false||result.groundTruthUsedToSetScale!==false||result.clinicalOutcomeVerified!==false
  ||result.referenceDistanceMetres!==null||result.errorMetres!==null||result.errorPercent!==null
  ||result.speedScope!=='whole-protocol-capture-including-rests'||result.routeGeometry!==distanceGeometry(pending.protocol)
  ||(live?(result.software?.processing?.live!==true||result.software?.processing?.rollingShutterCorrection!=='measured-midpoint-gyro-rotational-row-compensation-v1'||result.software?.openvinsCommit!=='69488123ed9362dd44b6f28e7f4680abbff1442b'):result.software?.processing?.fixedTimeRowCorrection!==true)||result.software?.processing?.quietInitializationRequired!==true
  ||!['not-initialized','tracking-integrity-failed','partial-route','experimental-complete-route','standing-drift','boundary-unavailable','route-geometry-mismatch'].includes(result.reason)
  ||result.fullRouteCovered!==(result.reason==='experimental-complete-route')||result.fullRouteCovered!==(result.completeRouteEstimateMetres!==null))throw new Error('The camera distance result does not match this recording.');
 for(const k of ['experimentalSegmentMetres','completeRouteEstimateMetres','meanSpeedMps','intervalSeconds'])if(result[k]!==null&&(!Number.isFinite(result[k])||result[k]<0))throw new Error('Invalid camera distance result.');
 if(result.fullRouteCovered&&(!Number.isFinite(result.intervalSeconds)||!Number.isFinite(result.meanSpeedMps)||result.intervalSeconds<=0||result.intervalSeconds>600||Math.abs(result.meanSpeedMps-result.completeRouteEstimateMetres/result.intervalSeconds)>1e-6))throw new Error('Invalid camera distance interval.');
 if(!result.fullRouteCovered&&result.meanSpeedMps!==null)throw new Error('Partial tracking cannot supply a whole-walk speed.');
 if(pending.protocol==='10mwt'){
  const z=result.testOutcome;
  if(!z||!['experimental','unavailable'].includes(z.status)||z.clinicalOutcomeVerified!==false||z.boundarySource!=='estimated-trajectory-crossings'||z.accelerationMetres!==1||z.timedDistanceMetres!==10||z.decelerationMetres!==1)throw new Error('Invalid 10MWT zones.');
  if(z.status==='experimental'&&(!result.fullRouteCovered||result.completeRouteEstimateMetres<12||!Number.isFinite(z.timedZoneSeconds)||z.timedZoneSeconds<=0||!Number.isFinite(z.startOffsetSeconds)||z.startOffsetSeconds<0||!Number.isFinite(z.endOffsetSeconds)||z.endOffsetSeconds>result.intervalSeconds+.2||Math.abs(z.endOffsetSeconds-z.startOffsetSeconds-z.timedZoneSeconds)>1e-6||!Number.isFinite(z.speedMps)||Math.abs(z.speedMps-10/z.timedZoneSeconds)>1e-6))throw new Error('Invalid 10MWT zone estimate.');
  if(z.status==='unavailable'&&[z.timedZoneSeconds,z.speedMps,z.startOffsetSeconds,z.endOffsetSeconds].some(v=>v!==null))throw new Error('Invalid 10MWT zone estimate.');
 }else if(result.testOutcome!==null)throw new Error('Invalid protocol outcome.');
 return result;
}
export function validGaitCameraDistance(value:any,sessionId:string,protocol:AssessmentProtocol):value is GaitCameraDistance{
 try{
  if(!value||value.version!==GAIT_DISTANCE_VERSION||value.sessionId!==sessionId||value.captureId!=='gait-camera-'+sessionId||! /^[a-zA-Z0-9_-]{1,160}$/.test(sessionId)
   ||value.protocol!==protocol||!['capturing','saved','processing','complete','unavailable'].includes(value.status)||! /^[0-9a-f]{64}$/.test(value.referenceSha256??'')||!value.binding
   ||(value.jobId!==undefined&&! /^[0-9a-f]{24}$/.test(value.jobId))||typeof value.reason!=='string'||value.reason.length>512
   ||typeof value.binding.installationId!=='string'||typeof value.binding.cameraId!=='string'||!Number.isInteger(value.binding.width)||!Number.isInteger(value.binding.height)
   ||value.binding.width<=0||value.binding.height<=0||!['native-camera-imu-v2','native-camera-imu-v3'].includes(value.binding.capturePipeline)||value.binding.imageAxes!=='native-sensor-unrotated-unmirrored'||value.binding.stabilizationRequested!=='off'
   ||![0,90,180,270].includes(value.binding.sensorOrientationDegrees)||!['waist-bag-window','clear-lens'].includes(value.binding.opticalSetup))return false;
  if(value.result){validateGaitDistanceResult(value.result,value);if(value.distanceM!==value.result.completeRouteEstimateMetres||value.meanSpeedMps!==value.result.meanSpeedMps||value.intervalSeconds!==value.result.intervalSeconds||value.reason!==value.result.reason)return false;}
  if(value.status==='complete')return !!value.result&&value.result.fullRouteCovered===true;
  return value.distanceM===null&&value.meanSpeedMps===null;
 }catch{return false;}
}
/** Do not silently substitute a height estimate when camera tracking was selected but failed. */
export function cameraDistanceOutcome(attachment:GaitCameraDistance){
 const z=attachment.protocol==='10mwt'?attachment.result?.testOutcome:null;
 return {distanceM:attachment.distanceM,meanSpeedMps:attachment.protocol==='10mwt'?(z?.status==='experimental'?z.speedMps:null):attachment.meanSpeedMps,status:attachment.status==='complete'?'experimental-camera-imu':'unavailable',method:attachment.result?.method??'vins-mono-on-device-v1',reason:attachment.reason,speedScope:attachment.protocol==='10mwt'?'estimated-central-10m-zone':'whole-protocol-capture-including-rests',clinicalOutcomeVerified:false};
}
