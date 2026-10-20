import {Platform} from 'react-native';
import {requireOptionalNativeModule} from 'expo-modules-core';
import * as FileSystem from 'expo-file-system';
import {Camera} from 'expo-camera';
import {phoneDistanceProfile} from './onDeviceSetup';
import {phoneDistanceResult} from './phoneDistanceModel';
import {getSession,updateCameraDistance} from './store';
import {releaseInfo} from './releaseInfo';
import type {CalibrationCapture} from './cameraCalibration';
import {GAIT_DISTANCE_VERSION,distanceGeometry,distanceBindingKeys,validateGaitDistanceResult,type GaitCameraDistance} from './gaitDistanceModel';
import type {AssessmentProtocol} from './store';
export type LivePhoneDistance={initialized:boolean;integrity:boolean;positionStdMetres:number;receivedAt:number;walkProgress?:{usable:boolean;zone:string;complete:boolean;distanceMetres?:number;finishBootNs?:number}};
type Bridge={captureGaitDistance:(reference:string,release:string,id:string,protocol:string)=>Promise<CalibrationCapture>;gaitDistanceReady:()=>Promise<boolean>;beginGaitDistance:()=>Promise<void>;finishGaitDistance:(reason:string)=>Promise<void>;processGaitDistanceOnPhone?:(id:string)=>Promise<string>;stop:()=>Promise<void>;addListener?:(event:'distanceProgress',listener:(event:{sessionId:string;status:string})=>void)=>{remove:()=>void}};
export function gaitDistanceBridge():Bridge|null{
 if(Platform.OS!=='android')return null;
 const b=requireOptionalNativeModule<Bridge>('GaitCameraCalibration');
 return b&&['captureGaitDistance','gaitDistanceReady','beginGaitDistance','finishGaitDistance','stop'].every(k=>typeof (b as any)[k]==='function')?b:null;
}
export async function prepareGaitDistance(){
 if(!gaitDistanceBridge()?.processGaitDistanceOnPhone)throw new Error('Install the updated Android app to use camera distance.');
 const reference=await phoneDistanceProfile();if(!reference)throw new Error('Phone setup changed or has not completed. Set up this phone again.');
 const permission=await Camera.requestCameraPermissionsAsync();if(!permission.granted)throw new Error('Camera permission is needed for camera distance.');
 return reference;
}
const directory=()=>{if(!FileSystem.documentDirectory)throw new Error('Phone storage is unavailable.');return FileSystem.documentDirectory+'gait-camera-captures/';};
export const gaitDistanceArchive=(id:string)=>{if(!/^[a-zA-Z0-9_-]{1,160}$/.test(id))throw new Error('Invalid recording identifier.');return directory()+'gait-camera-'+id+'.zip';};
const pause=(ms:number)=>new Promise<void>(resolve=>setTimeout(resolve,ms));
const activeCaptures=new Set<string>();
function completedCapture(meta:any,a:GaitCameraDistance){return meta?.kind==='gait-camera-imu-distance-capture-v1'&&meta.sessionId===a.sessionId&&meta.captureId===a.captureId&&meta.protocol===a.protocol&&!meta.error&&meta.status==='completed'
 &&meta.diagnostics?.placementCompleted&&meta.diagnostics.walkEndedBootNs>meta.diagnostics.walkStartedBootNs&&distanceBindingKeys.every(k=>meta[k]===a.binding[k]);}
export class GaitDistanceCapture{
 attachment:GaitCameraDistance;
 live:LivePhoneDistance|undefined;
 private listener:{remove:()=>void}|undefined;
 private lastLiveTime=-Infinity;
 private bridge:Bridge;private task:Promise<void>;private failed=false;private cancelled=false;
 constructor(id:string,protocol:AssessmentProtocol,reference:any){
  const b=gaitDistanceBridge();if(!b)throw new Error('Install the updated Android app to use camera distance.');this.bridge=b;
  this.attachment={version:GAIT_DISTANCE_VERSION,sessionId:id,captureId:'gait-camera-'+id,protocol,status:'capturing',referenceSha256:reference.sourceSha256,binding:reference.binding,distanceM:null,meanSpeedMps:null,intervalSeconds:null,reason:'capture-pending'};
  if(reference.kind==='phone-on-device-camera-imu-profile-v1')this.listener=b.addListener?.('distanceProgress',event=>{
   if(event.sessionId!==id||this.cancelled)return;
   try{const value=JSON.parse(event.status);if(typeof value.initialized!=='boolean'||typeof value.integrity!=='boolean'||!Number.isFinite(value.positionStdMetres)||value.positionStdMetres<0||!Number.isFinite(value.state?.imu_time_s)||value.state.imu_time_s<=this.lastLiveTime)return;
    const w=value.walkProgress;
    if(w&&(typeof w.usable!=='boolean'||typeof w.complete!=='boolean'||typeof w.zone!=='string'||w.complete&&(!w.usable||w.targetMetres!==12||w.boundarySource!=='on-device-estimated-trajectory-crossing'||!Number.isFinite(w.finishBootNs)||!Number.isFinite(w.startBootNs)||w.finishBootNs<=w.startBootNs||w.finishBootNs>value.state.imu_time_s*1e9+1000)))return;
    this.lastLiveTime=value.state.imu_time_s;
    this.live={...value,receivedAt:Date.now()};
   }catch{/* A malformed update never supplies a finish event. */}
  });
  activeCaptures.add(id);
  this.task=b.captureGaitDistance(JSON.stringify(reference),JSON.stringify(releaseInfo()),id,protocol).then(async capture=>{
   const meta=JSON.parse(capture.metadata);
   if(this.failed||capture.error||!completedCapture(meta,this.attachment))throw new Error('Camera capture was incomplete. Motion data is kept.');
   const target=gaitDistanceArchive(id);
   // Native capture already owns this canonical path; avoid self-copying.
   if(capture.uri.replace(/^file:\/+/, '/')!==target.replace(/^file:\/+/, '/'))await FileSystem.copyAsync({from:capture.uri,to:target});
   this.attachment={...this.attachment,status:'saved',reason:'waiting-for-phone-processing'};
  }).catch(()=>{this.failed=true;this.attachment={...this.attachment,status:'unavailable',reason:'capture-failed'};}).finally(()=>{activeCaptures.delete(id);this.listener?.remove();});
 }
 async ready(){const deadline=Date.now()+15000;while(Date.now()<deadline&&!this.failed&&!this.cancelled){if(await this.bridge.gaitDistanceReady())return;await pause(100);}throw new Error('Phone tracking could not start. Return to phone setup.');}
 begin(){if(this.failed||this.cancelled)return;void this.bridge.beginGaitDistance().catch(()=>{this.failed=true;void this.bridge.stop();});}
 finish(reason:string){if(this.cancelled)return;void this.bridge.finishGaitDistance(reason).catch(()=>{this.failed=true;void this.bridge.stop();});}
 async finished(){await this.task;return this.attachment;}
 async attach(){await this.task;if(this.cancelled)return;const kept=await updateCameraDistance(this.attachment.sessionId,this.attachment);if(!kept){await this.remove();return;}if(this.attachment.status==='saved')void processGaitDistance(this.attachment.sessionId).catch(()=>{});}
 async remove(){await FileSystem.deleteAsync(gaitDistanceArchive(this.attachment.sessionId),{idempotent:true});await FileSystem.deleteAsync(directory()+this.attachment.captureId,{idempotent:true});}
 async cancel(){this.cancelled=true;await this.bridge.stop().catch(()=>{});await this.task;await this.remove();}
}
const processing=new Map<string,Promise<void>>();
let processingTail:Promise<void>=Promise.resolve();
/** Each recording owns its job. Closing a screen never loses the saved archive/job. */
export function processGaitDistance(sessionId:string):Promise<void>{
 const existing=processing.get(sessionId);if(existing)return existing;
 const task=processingTail.catch(()=>{}).then(()=>processSaved(sessionId)).finally(()=>processing.delete(sessionId));
 processingTail=task;processing.set(sessionId,task);return task;
}
async function processSaved(id:string){
 if(Platform.OS!=='android')return;
 const session=await getSession(id);let a=session?.cameraDistance;if(!a||a.status==='complete')return;
 if(a.status==='capturing'){
  if(activeCaptures.has(id))return;
  let valid=false;
  try{const manifest=JSON.parse(await FileSystem.readAsStringAsync(directory()+a.captureId+'/manifest.json'));valid=completedCapture(manifest,a)&&(await FileSystem.getInfoAsync(gaitDistanceArchive(id))).exists;}catch{}
  a={...a,status:valid?'saved':'unavailable',reason:valid?'waiting-for-phone-processing':'capture-failed'};
  if(!await updateCameraDistance(id,a)||!valid)return;
 }
 if(a.status==='unavailable'&&!a.result)return;
 const bridge=gaitDistanceBridge();
 if(!bridge?.processGaitDistanceOnPhone)throw new Error('Install the updated Android app to use phone-only distance.');
 try{
  if(!(await FileSystem.getInfoAsync(gaitDistanceArchive(id))).exists)throw new Error('The camera archive is missing. Motion data is kept.');
  a={...a,status:'processing',jobId:undefined,reason:'phone-processing'};
  if(!await updateCameraDistance(id,a))return;
  const raw=JSON.parse(await bridge.processGaitDistanceOnPhone(id));
  const result=validateGaitDistanceResult(phoneDistanceResult(raw,a),a);
  await updateCameraDistance(id,{...a,result,status:result.fullRouteCovered?'complete':'unavailable',distanceM:result.completeRouteEstimateMetres,meanSpeedMps:result.meanSpeedMps,intervalSeconds:result.intervalSeconds,reason:result.reason});
 }catch(error){
  await updateCameraDistance(id,{...a,status:'saved',jobId:undefined,reason:'phone-processing-retry'});
  throw new Error('Phone distance processing could not finish. Your recording is saved; retry on this phone.');
 }
}
