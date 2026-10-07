import {Platform} from 'react-native';
import * as FileSystem from 'expo-file-system';
export type CalibrationCapture={uri:string;metadata:string;error:string|null};
export interface CalibrationBridge{
 capture():Promise<CalibrationCapture>;stop():Promise<void>;
 captureWithOptics?(setup:'waist-bag-window'|'clear-lens'):Promise<CalibrationCapture>;
 captureNoise?():Promise<CalibrationCapture>;
 captureGuidedLens?(setup:'waist-bag-window'|'clear-lens'):Promise<CalibrationCapture>;
 phoneCalibrationInfo?():Promise<string>;
 digitalCalibrationBoard?():Promise<string>;
 captureAlignment?(setup:'waist-bag-window'|'clear-lens'):Promise<CalibrationCapture>;
 beginAlignmentMovement?():Promise<void>;
 addListener(event:'progress',listener:(event:{elapsedSeconds:number;frames:number;imageUri:string;phase:'still'|'move'|'noise'|'lens'|'alignment-still'|'alignment-cue'|'alignment-move';lens?:string|null})=>void):{remove():void};
}
export function calibrationBridge():CalibrationBridge|null{
 if(Platform.OS!=='android')return null;
 return require('expo-modules-core').requireOptionalNativeModule('GaitCameraCalibration');
}
function calibrationDirectory(){
 if(!FileSystem.documentDirectory)throw new Error('Phone storage is unavailable.');
 return FileSystem.documentDirectory+'camera-calibration/';
}
// Java File.toURI emits file:/...; Expo emits file:///... for the same file.
function localPath(uri:string){return decodeURIComponent(uri.replace(/^file:\/+/, '/'));}

export function validateLensReport(report:any,binding:any){
 const fail=()=>{throw new Error('Lens parameters do not match this camera setup.');};
 if(report?.schemaVersion!==1||report.kind!=='phone-camera-lens-calibration-v1'||report.method!=='opencv-zhang-2000'
  ||report.status!=='lens-candidate'||report.lensReady!==true||report.fullCalibrationReady!==false||report.distanceReady!==false
  ||report.independentDistanceValidation!==false||!Array.isArray(report.errors)||report.errors.length||!Number.isInteger(report.acceptedViews)||report.acceptedViews<24)return fail();
 const keys=['installationId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','focusRequestedDioptres','capturePipeline','opticalSetup'];
 if(!binding?.installationId||!['waist-bag-window','clear-lens'].includes(binding.opticalSetup)||keys.some(k=>report.binding?.[k]!==binding[k]))return fail();
 const K=report.lens?.cameraMatrix,D=report.lens?.distortion;
 if(!Array.isArray(K)||K.length!==3||K.some((r:any)=>!Array.isArray(r)||r.length!==3||r.some((v:any)=>typeof v!=='number'||!Number.isFinite(v)))
  ||K[0][0]<=0||K[1][1]<=0||Math.abs(K[2][2]-1)>1e-6||!Array.isArray(D)||D.length!==5||D.some((v:any)=>typeof v!=='number'||!Number.isFinite(v))
  ||report.lens.model!=='opencv-pinhole-radtan5'||!Number.isFinite(report.lens.heldOutP90Pixels)||report.lens.heldOutP90Pixels>1.5
  ||!Number.isFinite(report.lens.focalSubsetDriftFraction)||report.lens.focalSubsetDriftFraction>.05
  ||!Number.isFinite(report.lens.principalSubsetDriftFraction)||report.lens.principalSubsetDriftFraction>.02)return fail();
 return report;
}
export async function currentLensReport(binding:any){
 const path=calibrationDirectory()+'lens.json';if(!(await FileSystem.getInfoAsync(path)).exists)return null;
 try{return validateLensReport(JSON.parse(await FileSystem.readAsStringAsync(path)),binding);}catch{return null;}
}
export async function recoverLensReport(capture:CalibrationCapture){
 const meta=JSON.parse(capture.metadata);
 if(meta.status!=='completed'||meta.error||meta.captureMode!=='guided-lens-zhang')return null;
 return validateLensReport(meta.lensCalibration,meta);
}
async function nonemptyFile(uri:string){
 const info=await FileSystem.getInfoAsync(uri);
 return info.exists&&!info.isDirectory&&info.size>0;
}
export async function retainCalibrationCapture(value:CalibrationCapture){
 const metadata=JSON.parse(value.metadata);
 if(!/^calibration-\d+$/.test(metadata.captureId)||!value.uri.startsWith('file:'))throw new Error('Invalid calibration capture.');
 const dir=calibrationDirectory();await FileSystem.makeDirectoryAsync(dir,{intermediates:true});
 const uri=dir+metadata.captureId+'.zip';
 if(!await nonemptyFile(value.uri))throw new Error('Calibration ZIP is missing or empty.');
 if(localPath(value.uri)!==localPath(uri))await FileSystem.copyAsync({from:value.uri,to:uri});
 if(!await nonemptyFile(uri))throw new Error('Calibration ZIP is missing or empty.');
 const record={...value,uri};const index=metadata.captureMode==='guided-lens-zhang'?'latest-lens.json':metadata.captureMode==='targetless-alignment'?'latest-alignment.json':'latest.json';
 await FileSystem.writeAsStringAsync(dir+index,JSON.stringify(record));return record;
}
export function validateCalibrationReport(report:any,capture:CalibrationCapture){
 const meta=JSON.parse(capture.metadata);
 if(report?.schemaVersion!==1||report.kind!=='phone-camera-imu-calibration-v1'||report.status!=='geometry-candidate'
  ||report.distanceReady!==false||report.independentDistanceValidation!==false||report.errors?.length!==0
  ||!report.cameraImuRotationTiming?.passed||!report.translationAcceleration?.passed)
  throw new Error('This calibration report did not pass processing.');
 const keys=['installationId','captureId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested'];
 if(meta.capturePipeline)keys.push('capturePipeline','opticalSetup');
 if(meta.status!=='completed'||!meta.installationId||keys.some(k=>report.binding?.[k]!==meta[k]))
  throw new Error('This report belongs to another phone or camera setup.');
 const K=report.lens?.cameraMatrix;
 if(!Array.isArray(K)||K.length!==3||K.some((r:any)=>!Array.isArray(r)||r.length!==3||r.some((v:any)=>typeof v!=='number'||!Number.isFinite(v)))
  ||K[0][0]<=0||K[1][1]<=0||Math.abs(K[2][2]-1)>1e-6
  ||!Number.isFinite(report.lens?.heldOutP90Pixels)||report.lens.heldOutP90Pixels>1.5)
  throw new Error('This calibration report did not pass processing.');
 return report;
}

export async function retainNoiseCapture(value:CalibrationCapture){
 const meta=JSON.parse(value.metadata);
 if(meta.kind!=='phone-imu-noise-capture-v1'||!/^imu-noise-\d+$/.test(meta.captureId)||!value.uri.startsWith('file:')||meta.distanceReady!==false)throw new Error('Invalid sensor noise capture.');
 if(!FileSystem.documentDirectory)throw new Error('Phone storage is unavailable.');
 const dir=FileSystem.documentDirectory+'camera-imu-noise/';await FileSystem.makeDirectoryAsync(dir,{intermediates:true});
 const uri=dir+meta.captureId+'.zip';
 if(!await nonemptyFile(value.uri))throw new Error('Calibration ZIP is missing or empty.');
 if(localPath(value.uri)!==localPath(uri))await FileSystem.copyAsync({from:value.uri,to:uri});
 const record={...value,uri};await FileSystem.writeAsStringAsync(dir+'latest.json',JSON.stringify(record));return record;
}
export async function latestNoiseCapture():Promise<CalibrationCapture|null>{
 if(!FileSystem.documentDirectory)return null;
 const dir=FileSystem.documentDirectory+'camera-imu-noise/';
 if(!(await FileSystem.getInfoAsync(dir)).exists)return null;
 const names=(await FileSystem.readDirectoryAsync(dir)).filter(n=>/^imu-noise-\d+\.zip$/.test(n)).sort((a,b)=>Number(b.slice(10,-4))-Number(a.slice(10,-4)));
 for(const name of names){try{
  if(!await nonemptyFile(dir+name))continue;
  const metadata=await FileSystem.readAsStringAsync(dir+name.slice(0,-4)+'/manifest.json');const m=JSON.parse(metadata);
  if(m.kind==='phone-imu-noise-capture-v1'&&m.captureId===name.slice(0,-4)&&m.distanceReady===false)return {uri:dir+name,metadata,error:m.error??null};
 }catch{/* Preserve captures and inspect the next durable manifest. */}}
 return null;
}
export async function retainCalibrationReport(report:any,capture:CalibrationCapture){
 validateCalibrationReport(report,capture);
 await FileSystem.writeAsStringAsync(FileSystem.documentDirectory+'camera-calibration/geometry.json',JSON.stringify(report));
}
export async function hasCalibrationGeometry(capture:CalibrationCapture){
 const path=FileSystem.documentDirectory+'camera-calibration/geometry.json';
 if(!(await FileSystem.getInfoAsync(path)).exists)return false;
 try{validateCalibrationReport(JSON.parse(await FileSystem.readAsStringAsync(path)),capture);return true;}catch{return false;}
}
export async function latestCalibrationCapture():Promise<CalibrationCapture|null>{
 const dir=calibrationDirectory(),path=dir+'latest.json';
 if(!(await FileSystem.getInfoAsync(dir)).exists)return null;
 let latest:CalibrationCapture|null=null;
 try{if((await FileSystem.getInfoAsync(path)).exists){
  const record=JSON.parse(await FileSystem.readAsStringAsync(path));
  const meta=JSON.parse(record.metadata);
  if(/^calibration-\d+$/.test(meta.captureId)&&localPath(record.uri)===localPath(dir+meta.captureId+'.zip')&&await nonemptyFile(record.uri))latest=record;
 }}catch{/* A native manifest can recover an unindexed capture. */}
 const names=(await FileSystem.readDirectoryAsync(dir)).filter(n=>/^calibration-\d+\.zip$/.test(n))
  .sort((a,b)=>Number(b.slice(12,-4))-Number(a.slice(12,-4)));
 const latestId=latest?JSON.parse(latest.metadata).captureId:null;
 for(const name of names){
  const id=name.slice(0,-4);if(id===latestId)return latest;
  let record:CalibrationCapture;
  try{
   if(!await nonemptyFile(dir+name))continue;
   const metadata=await FileSystem.readAsStringAsync(dir+id+'/manifest.json');
   const meta=JSON.parse(metadata);
   if(meta.schemaVersion!==1||meta.captureId!==id||['guided-lens-zhang','targetless-alignment'].includes(meta.captureMode))continue;
   record={uri:dir+name,metadata,error:typeof meta.error==='string'?meta.error:null};
  }catch{continue;}
  // The native ZIP is already in durable storage. Recover its index without copying it.
  await FileSystem.writeAsStringAsync(path,JSON.stringify(record));return record;
 }
 return latest;
}
