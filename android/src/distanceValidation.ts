import * as FileSystem from 'expo-file-system';
import {calibrationBridge,currentLensReport,type CalibrationCapture} from './cameraCalibration';
import {validateCalibrationComputer,savedReference,type CalibrationComputer} from './referenceCalibration';

const directory=()=>{if(!FileSystem.documentDirectory)throw new Error('Phone storage is unavailable.');return FileSystem.documentDirectory+'camera-distance-trials/';};
async function read(name:string){const path=directory()+name;if(!(await FileSystem.getInfoAsync(path)).exists)return null;return JSON.parse(await FileSystem.readAsStringAsync(path));}
async function save(name:string,value:any){await FileSystem.makeDirectoryAsync(directory(),{intermediates:true});await FileSystem.writeAsStringAsync(directory()+name,JSON.stringify(value));}
const keys=['installationId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','capturePipeline','opticalSetup'];
export async function distanceReference(){
 const info=await calibrationBridge()?.phoneCalibrationInfo?.();if(!info)return null;
 const lens=await currentLensReport({...JSON.parse(info),opticalSetup:'waist-bag-window'});return savedReference(lens);
}
export async function researchRequest(computer:CalibrationComputer,path:string){
 validateCalibrationComputer(computer);const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
 try{const response=await fetch(computer.url+path,{headers:{Authorization:'Bearer '+computer.token},signal:controller.signal});if(!response.ok)throw new Error('Could not connect to the calibration computer.');return await response.json();}
 finally{clearTimeout(timer);}
}
export async function distanceComputerReady(computer:CalibrationComputer){const health=await researchRequest(computer,'/api/health');if(health.distanceValidationVersion!==2)throw new Error('Restart the updated computer helper before testing distance.');const engine=await researchRequest(computer,'/api/distance-health');if(engine.available!==true)throw new Error('The computer distance engine is not ready.');}
export async function distanceResultFile(capture:CalibrationCapture){const id=JSON.parse(capture.metadata).captureId;if(!/^distance-trial-\d+$/.test(id))throw new Error('Invalid distance trial.');return directory()+id+'-validation.json';}
export function validateDistanceResult(result:any,pending:any){
 if(result?.schemaVersion!==1||result.kind!=='phone-distance-validation-result-v1'||result.method!=='vins-mono-offline-reference-v1'
  ||result.distanceReady!==false||result.independentDistanceValidation!==false||result.groundTruthUsedToSetScale!==false
  ||result.captureId!==pending.captureId||result.referenceCalibrationSha256!==pending.referenceSha256
  ||keys.some(k=>result.binding?.[k]!==pending.binding?.[k])||result.referenceDistanceMetres!==pending.referenceMetres
  ||result.routeGeometry!==(pending.routeGeometry??'straight')
  ||!['not-initialized','tracking-integrity-failed','partial-route','experimental-complete-route','standing-drift','boundary-unavailable','route-geometry-mismatch'].includes(result.reason)
  ||!/^[0-9a-f]{64}$/.test(result.sourceSha256??''))throw new Error('The distance result did not pass import checks.');
 for(const key of ['experimentalSegmentMetres','completeRouteEstimateMetres'])if(result[key]!==null&&(typeof result[key]!=='number'||!Number.isFinite(result[key])||result[key]<0))throw new Error('The distance result did not pass import checks.');
 if(result.fullRouteCovered!== (result.completeRouteEstimateMetres!==null)||result.fullRouteCovered!== (result.reason==='experimental-complete-route'))throw new Error('The distance result did not pass import checks.');
 if(result.fullRouteCovered&&(typeof result.errorMetres!=='number'||!Number.isFinite(result.errorMetres)||Math.abs(result.errorMetres-(result.completeRouteEstimateMetres-result.referenceDistanceMetres))>1e-6))throw new Error('The distance result did not pass import checks.');
 return result;
}
export async function retainValidationRoute(capture:CalibrationCapture,referenceMetres:number,routeGeometry='straight'){
 const meta=JSON.parse(capture.metadata);if(!/^distance-trial-\d+$/.test(meta.captureId)||![2,3,5].includes(referenceMetres))throw new Error('Invalid distance trial.');
 if(!['straight','with-turns'].includes(routeGeometry))throw new Error('Invalid distance trial.');
 await save(meta.captureId+'-route.json',{referenceMetres,routeGeometry});
}
export async function validationGeometry(capture:CalibrationCapture|null){if(!capture)return 'straight';const id=JSON.parse(capture.metadata).captureId;if(!/^distance-trial-\d+$/.test(id))return 'straight';return (await read(id+'-route.json'))?.routeGeometry==='with-turns'?'with-turns':'straight';}
export async function validationRoute(capture:CalibrationCapture|null){
 if(!capture)return 3;const meta=JSON.parse(capture.metadata);if(!/^distance-trial-\d+$/.test(meta.captureId))return 3;
 const row=await read(meta.captureId+'-route.json');return [2,3,5].includes(row?.referenceMetres)?row.referenceMetres:3;
}
export async function pendingDistanceValidation(){return read('pending-validation.json');}
export async function savedDistanceValidation(capture:CalibrationCapture|null){
 if(!capture)return null;const meta=JSON.parse(capture.metadata);if(!/^distance-trial-\d+$/.test(meta.captureId))return null;
 const record=await read(meta.captureId+'-validation.json');if(!record)return null;
 return validateDistanceResult(record.result,{...record.pending,captureId:meta.captureId,binding:meta});
}
export async function submitDistanceValidation(computer:CalibrationComputer,capture:CalibrationCapture,reference:any,referenceMetres:number,routeGeometry='straight'){
 await distanceComputerReady(computer);const meta=JSON.parse(capture.metadata);
 if(!['straight','with-turns'].includes(routeGeometry)||![2,3,5].includes(referenceMetres)||!/^distance-trial-\d+$/.test(meta.captureId)||meta.kind!=='front-camera-distance-research-v1'
  ||meta.error||!['quiet-stop','walk-time-limit','time-limit'].includes(meta.status)||!meta.diagnostics?.placementCompleted
  ||keys.some(k=>meta[k]!==reference.binding?.[k]))throw new Error('A completed distance walk is needed.');
 const response=await FileSystem.uploadAsync(computer.url+'/api/distance-captures',capture.uri,{httpMethod:'POST',uploadType:FileSystem.FileSystemUploadType.BINARY_CONTENT,headers:{Authorization:'Bearer '+computer.token,'Content-Type':'application/zip','X-GaitTrace-Reference-Metres':String(referenceMetres),'X-GaitTrace-Route-Geometry':routeGeometry}});
 if(response.status!==202)throw new Error('Could not send the walk. It is saved on this phone.');
 const job=JSON.parse(response.body);if(!/^[0-9a-f]{24}$/.test(job.id??''))throw new Error('The distance result did not pass import checks.');
 await save('pending-validation.json',{id:job.id,captureId:meta.captureId,binding:meta,referenceSha256:reference.sourceSha256,referenceMetres,routeGeometry});
}
export async function pollDistanceValidation(computer:CalibrationComputer,cancelled:()=>boolean){
 const pending=await pendingDistanceValidation();if(!pending||!/^[0-9a-f]{24}$/.test(pending.id))throw new Error('No distance processing is waiting.');
 const began=Date.now();while(!cancelled()){
  const job=await researchRequest(computer,'/api/jobs/'+pending.id);if(cancelled())return null;
  if(job.status==='completed'){const result=validateDistanceResult(job.result,pending);await save(pending.captureId+'-validation.json',{pending,result});await FileSystem.deleteAsync(directory()+'pending-validation.json',{idempotent:true});return result;}
  if(job.status==='failed')throw new Error('Distance processing could not complete. Your walk is saved; retry processing.');
  if(job.status!=='processing'||Date.now()-began>1200000)throw new Error('Distance processing is still pending. Resume when the computer is ready.');
  await new Promise<void>(resolve=>setTimeout(resolve,2000));
 }return null;
}
