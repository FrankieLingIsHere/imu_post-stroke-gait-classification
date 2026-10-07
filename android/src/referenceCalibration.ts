import * as FileSystem from 'expo-file-system';
import type {CalibrationCapture} from './cameraCalibration';

export type CalibrationComputer={kind:'gaittrace-local-calibration-pair-v1';url:string;token:string};
const directory=()=>{if(!FileSystem.documentDirectory)throw new Error('Phone storage is unavailable.');return FileSystem.documentDirectory+'camera-calibration/';};
export function validateCalibrationComputer(value:any):CalibrationComputer{
 const fail=()=>{throw new Error('Scan the setup code shown by your calibration computer.');};
 if(value?.kind!=='gaittrace-local-calibration-pair-v1'||typeof value.url!=='string'||!/^http:\/\/(\d{1,3}\.){3}\d{1,3}:\d{2,5}$/.test(value.url)||!/[0-9a-f]{64}/.test(value.token??'')||value.token.length!==64)return fail();
 const u=new URL(value.url),n=u.hostname.split('.').map(Number),port=Number(u.port);
 if(n.some(v=>v>255)||port<1024||port>65535||!(n[0]===10||n[0]===192&&n[1]===168||n[0]===172&&n[1]>=16&&n[1]<=31))return fail();
 return value;
}
async function read(name:string){const path=directory()+name;if(!(await FileSystem.getInfoAsync(path)).exists)return null;try{return JSON.parse(await FileSystem.readAsStringAsync(path));}catch{return null;}}
async function save(name:string,value:any){await FileSystem.makeDirectoryAsync(directory(),{intermediates:true});await FileSystem.writeAsStringAsync(directory()+name,JSON.stringify(value));}
export async function calibrationComputer(){try{return validateCalibrationComputer(await read('computer.json'));}catch{return null;}}
async function request(computer:CalibrationComputer,path:string){
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);
 try{const r=await fetch(computer.url+path,{headers:{Authorization:'Bearer '+computer.token},signal:controller.signal});if(!r.ok)throw new Error('Could not connect to the calibration computer.');return await r.json();}
 finally{clearTimeout(timeout);}
}
export async function connectCalibrationComputer(code:string){
 let value;try{value=JSON.parse(code);}catch{throw new Error('Scan the setup code shown by your calibration computer.');}
 const computer=validateCalibrationComputer(value),health=await request(computer,'/api/health');
 if(health.kind!=='gaittrace-local-calibration-service-v1'||health.method!=='ikalibr-tro-2025'||health.distanceReady!==false)throw new Error('This computer is not running the calibration processor.');
 await save('computer.json',computer);return computer;
}
export async function showComputerBoard(computer:CalibrationComputer,html:string,mode:'computer'|'tablet'='computer'){
 const png=html.match(/src="data:image\/png;base64,([A-Za-z0-9+/=]+)"/)?.[1];if(!png)throw new Error('Could not generate digital board');
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);
 try{const response=await fetch(computer.url+'/api/board',{method:'POST',headers:{Authorization:'Bearer '+computer.token,'Content-Type':'application/json'},body:JSON.stringify({png,mode}),signal:controller.signal});
 if(!response.ok)throw new Error('Could not connect to the calibration computer.');}finally{clearTimeout(timeout);}
}
export type LensFeedback={acceptedViews:number;hint:string;status:'checking'|'completed'|'stopped'|'failed'};
/** Optional display feedback only. Coalesce updates; never block or influence calibration. */
export function createLensFeedback(computer:CalibrationComputer){
 let latest:{value:LensFeedback;imageUri?:string}|null=null,closed=false,busy=false,lastStart=0,timer:ReturnType<typeof setTimeout>|undefined,controller:AbortController|undefined;
 async function flush(){
  timer=undefined;if(closed||busy||!latest)return;
  const delay=1000-(Date.now()-lastStart);if(delay>0){timer=setTimeout(()=>void flush(),delay);return;}
  const update=latest;latest=null;busy=true;lastStart=Date.now();controller=new AbortController();const timeout=setTimeout(()=>controller?.abort(),3000);
  try{
   let jpeg:string|undefined;
   if(update.imageUri?.startsWith('file:')){try{const encoded=await FileSystem.readAsStringAsync(update.imageUri,{encoding:FileSystem.EncodingType.Base64});if(encoded.length<=1400000)jpeg=encoded;}catch{/* Display metadata still works if a preview file is unavailable. */}}
   if(closed||controller.signal.aborted)return;
   await fetch(computer.url+'/api/lens-progress',{method:'POST',headers:{Authorization:'Bearer '+computer.token,'Content-Type':'application/json'},body:JSON.stringify({...update.value,...(jpeg?{jpeg}:{})}),signal:controller.signal});
  }
  catch{/* A lost computer display must not discard a phone's lens capture. */}
  finally{clearTimeout(timeout);busy=false;if(latest&&!closed)void flush();}
 }
 return {send(value:LensFeedback,imageUri?:string){if(closed)return;latest={value,imageUri};if(!busy&&!timer)void flush();},close(){closed=true;latest=null;clearTimeout(timer);controller?.abort();}};
}
export function validateReferenceCalibration(report:any,binding:any){
 const keys=['installationId','captureId','cameraId','width','height','imageAxes','sensorOrientationDegrees','stabilizationRequested','capturePipeline','opticalSetup'];
 if(report?.schemaVersion!==1||report.kind!=='phone-reference-camera-imu-calibration-v1'||report.method!=='ikalibr-tro-2025'
  ||report.status!=='reference-solved-review-required'||report.cameraImuCandidateReady!==false||report.fullCalibrationReady!==false||report.distanceReady!==false
  ||report.independentDistanceValidation!==false||!binding.installationId||keys.some(k=>report.binding?.[k]!==binding[k])
  ||!report.upstreamParameters?.CalibParam||!Array.isArray(report.reviewRequired)||!report.reviewRequired.length
  ||!/^ulong2\/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c$/.test(report.software?.image??'')
  ||!/^[0-9a-f]{64}$/.test(report.software?.executableSha256??'')||!/^[0-9a-f]{64}$/.test(report.sourceSha256??''))throw new Error('The reference result did not pass import checks.');
 return report;
}
export async function submitAlignment(computer:CalibrationComputer,capture:CalibrationCapture){
 validateCalibrationComputer(computer);const meta=JSON.parse(capture.metadata);
 if(meta.kind!=='phone-camera-imu-alignment-capture-v1'||meta.status!=='completed'||meta.error)throw new Error('A completed sensor-alignment capture is needed.');
 const response=await FileSystem.uploadAsync(computer.url+'/api/captures',capture.uri,{httpMethod:'POST',uploadType:FileSystem.FileSystemUploadType.BINARY_CONTENT,headers:{Authorization:'Bearer '+computer.token,'Content-Type':'application/zip'}});
 if(response.status!==202)throw new Error('Could not transfer calibration to the computer. Your capture is saved.');
 const job=JSON.parse(response.body);if(!/^[0-9a-f]{24}$/.test(job.id??''))throw new Error('The reference result did not pass import checks.');
 await save('pending-reference.json',{id:job.id,binding:meta});return job.id;
}
export async function pendingReference(){return read('pending-reference.json');}
export async function savedReference(lens:any){
 const report=await read('reference.json');if(!report||!lens)return null;
 try{validateReferenceCalibration(report,report.binding);
  if(report.lensProfile?.binding?.captureId!==lens.binding?.captureId)return null;
  for(const key of ['installationId','cameraId','width','height','capturePipeline','opticalSetup'])if(report.binding[key]!==lens.binding[key])return null;
  return report;
 }catch{return null;}
}
export async function pollReference(computer:CalibrationComputer,cancelled:()=>boolean){
 const pending=await pendingReference();if(!pending||!/^[0-9a-f]{24}$/.test(pending.id))throw new Error('No calibration processing is waiting.');
 const began=Date.now();
 while(!cancelled()){
  const job=await request(computer,'/api/jobs/'+pending.id);
  if(cancelled())return null;
  if(job.status==='completed'){
   const result=validateReferenceCalibration(job.result,pending.binding);await save('reference.json',result);await FileSystem.deleteAsync(directory()+'pending-reference.json',{idempotent:true});return result;
  }
  if(job.status==='failed')throw new Error('Reference processing could not complete. The capture is kept for review.');
  if(job.status!=='processing'||Date.now()-began>3600000)throw new Error('Calibration processing is unavailable. Your capture is saved.');
  await new Promise<void>(resolve=>setTimeout(resolve,2000));
 }
 return null;
}
