import {Platform} from 'react-native';
import * as FileSystem from 'expo-file-system';
import type {CalibrationCapture} from './cameraCalibration';
export type DistanceProgress={elapsedSeconds:number;frames:number;imageUri:string;phase:'placing'|'cue'|'waiting'|'walking';tracking?:string|null};
export interface DistanceBridge{
 captureDistance(profile:string|null,release:string):Promise<CalibrationCapture>;beginDistance():Promise<void>;stop():Promise<void>;
 addListener(event:'progress',listener:(event:DistanceProgress)=>void):{remove():void};
}
export function distanceBridge():DistanceBridge|null{
 if(Platform.OS!=='android')return null;
 const bridge=require('expo-modules-core').requireOptionalNativeModule('GaitCameraCalibration');
 return typeof bridge?.captureDistance==='function'?bridge:null;
}
const directory=()=>{if(!FileSystem.documentDirectory)throw new Error('Phone storage is unavailable.');return FileSystem.documentDirectory+'camera-distance-trials/';};
const profilePath=()=>directory()+'profile.json';
export function validateDistanceResearchProfile(profile:any,capture:CalibrationCapture){
 const meta=JSON.parse(capture.metadata),binding=profile?.binding;
 const keys=['installationId','captureId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested'];
 if(meta.capturePipeline)keys.push('capturePipeline','opticalSetup');
 if(profile?.schemaVersion!==1||profile.kind!=='phone-camera-distance-research-profile-v1'||profile.distanceReady!==false
  ||profile.fullCalibrationReady!==false||profile.independentDistanceValidation!==false||profile.rotationTiming?.passed!==true
  ||meta.status!=='completed'||!meta.installationId||keys.some(k=>binding?.[k]!==meta[k]))throw new Error('This research profile does not match this phone.');
 const K=profile.lens?.cameraMatrix,R=profile.rotationTiming?.rotationImuToCamera;
 const matrix=(m:any)=>Array.isArray(m)&&m.length===3&&m.every((r:any)=>Array.isArray(r)&&r.length===3&&r.every((v:any)=>typeof v==='number'&&Number.isFinite(v)));
 if(!matrix(K)||!matrix(R)||K[0][0]<=0||K[1][1]<=0||Math.abs(K[2][2]-1)>1e-6
  ||!Array.isArray(profile.lens.distortion)||![4,5,8,12,14].includes(profile.lens.distortion.length)
  ||!profile.lens.distortion.every((v:any)=>typeof v==='number'&&Number.isFinite(v))
  ||!Number.isFinite(profile.lens.heldOutP90Pixels)||profile.lens.heldOutP90Pixels>1.5
  ||!Number.isFinite(profile.rotationTiming.residualTimeOffsetSeconds)||Math.abs(profile.rotationTiming.residualTimeOffsetSeconds)>.15
  ||!Array.isArray(profile.rotationTiming.gyroBiasRadS)||profile.rotationTiming.gyroBiasRadS.length!==3
  ||!profile.rotationTiming.gyroBiasRadS.every((v:any)=>Number.isFinite(v)&&Math.abs(v)<.2))throw new Error('Invalid research profile.');
 for(let i=0;i<3;i++)for(let j=0;j<3;j++)if(Math.abs(R[i].reduce((s:number,v:number,k:number)=>s+v*R[j][k],0)-(i===j?1:0))>1e-3)throw new Error('Invalid research profile.');
 const det=R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])-R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])+R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0]);
 if(det<.999)throw new Error('Invalid research profile.');
 return profile;
}
export async function saveDistanceResearchProfile(profile:any,capture:CalibrationCapture){
 validateDistanceResearchProfile(profile,capture);await FileSystem.makeDirectoryAsync(directory(),{intermediates:true});await FileSystem.writeAsStringAsync(profilePath(),JSON.stringify(profile));
}
export async function loadDistanceResearchProfile(capture:CalibrationCapture|null){
 if(!capture||!(await FileSystem.getInfoAsync(profilePath())).exists)return null;
 try{return validateDistanceResearchProfile(JSON.parse(await FileSystem.readAsStringAsync(profilePath())),capture);}catch{return null;}
}
export async function retainDistanceTrial(record:CalibrationCapture){
 const meta=JSON.parse(record.metadata);
 if(!/^distance-trial-\d+$/.test(meta.captureId)||meta.kind!=='front-camera-distance-research-v1'||meta.distanceReady!==false)throw new Error('Invalid distance trial.');
 const target=directory()+meta.captureId+'.zip';const info=await FileSystem.getInfoAsync(record.uri);
 if(!info.exists||info.isDirectory||info.size===0)throw new Error('Distance trial file is missing.');
 const canonical=(uri:string)=>decodeURIComponent(uri.replace(/^file:\/+/, '/'));
 await FileSystem.makeDirectoryAsync(directory(),{intermediates:true});
 if(canonical(target)!==canonical(record.uri))await FileSystem.copyAsync({from:record.uri,to:target});
 const saved={...record,uri:target};await FileSystem.writeAsStringAsync(directory()+'latest.json',JSON.stringify(saved));return saved;
}
export async function latestDistanceTrial():Promise<CalibrationCapture|null>{
 const dir=directory();if(!(await FileSystem.getInfoAsync(dir)).exists)return null;
 // Recover after process death or an interrupted index write, preserving native status.
 const names=(await FileSystem.readDirectoryAsync(dir)).filter(v=>/^distance-trial-\d+\.zip$/.test(v)).sort((a,b)=>Number(b.slice(15,-4))-Number(a.slice(15,-4)));
 for(const file of names){try{
  const uri=dir+file,info=await FileSystem.getInfoAsync(uri);if(!info.exists||info.isDirectory||!info.size)continue;
  const metadata=await FileSystem.readAsStringAsync(dir+file.slice(0,-4)+'/manifest.json');const meta=JSON.parse(metadata);
  if(meta.kind==='front-camera-distance-research-v1'&&meta.captureId===file.slice(0,-4)&&meta.distanceReady===false)return {uri,metadata,error:meta.error??null};
 }catch{/* Preserve other captures and try the next native ZIP. */}}
 return null;
}
export function distanceTrialSummary(record:CalibrationCapture|null){
 if(!record)return null;const meta=JSON.parse(record.metadata),d=meta.diagnostics;
 const valid=d?.status==='experimental-estimate'&&d.distanceReady===false&&d.independentDistanceValidation===false
  &&(!d.metricReadiness||d.metricReadiness.status==='ready')
  &&['quiet-stop','walk-time-limit','time-limit'].includes(meta.status)&&d.placementCompleted===true
  &&typeof d.experimentalHorizontalCameraPathMetres==='number'&&Number.isFinite(d.experimentalHorizontalCameraPathMetres)&&d.experimentalHorizontalCameraPathMetres>=0;
 return {available:valid,metres:valid?d.experimentalHorizontalCameraPathMetres:null,reason:d?.metricReadiness?.status==='blocked'?'Calibration and live tracking are not ready yet.':d?.reason??'tracking-error',diagnostics:d};
}
