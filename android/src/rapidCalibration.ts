import * as FileSystem from 'expo-file-system';
import {calibrationBridge,validateLearnedLensSeed,type CalibrationCapture} from './cameraCalibration';
import {validateReferenceCalibration,validateCalibrationComputer,type CalibrationComputer} from './referenceCalibration';
import {researchRequest} from './distanceValidation';

export const RAPID_REVISION='geocalib-five-view-ikalibr-enrollment-v1';
const directory=()=>{if(!FileSystem.documentDirectory)throw new Error('Phone storage is unavailable.');return FileSystem.documentDirectory+'camera-calibration/';};
async function read(name:string){try{return JSON.parse(await FileSystem.readAsStringAsync(directory()+name));}catch{return null;}}
async function save(name:string,value:any){await FileSystem.makeDirectoryAsync(directory(),{intermediates:true});await FileSystem.writeAsStringAsync(directory()+name,JSON.stringify(value));}
export async function pendingRapid(){return read('pending-rapid.json');}
export async function latestRapid():Promise<CalibrationCapture|null>{
 const value=await read('latest-rapid.json');if(!value)return null;
 try{const meta=JSON.parse(value.metadata);
  if(!/^calibration-\d+$/.test(meta.captureId)||meta.kind!=='phone-rapid-camera-imu-capture-v1'||value.uri.replace(/^file:\/+/, '/')!==(directory()+meta.captureId+'.zip').replace(/^file:\/+/, '/'))return null;
  const file=await FileSystem.getInfoAsync(value.uri);return file.exists&&!file.isDirectory&&file.size>0?value:null;
 }catch{return null;}
}
export function validateRapidResult(result:any,binding:any){
 validateReferenceCalibration(result,binding);validateLearnedLensSeed(result.lensProfile,binding);
 const e=result.enrollment,x=result.trainingExample;
 if(e?.method!==RAPID_REVISION||e.experimental!==true||e.neuralWeightsUpdated!==false||e.shortScanGuaranteed!==false||e.computerUsedOnce!==true||e.ordinaryTestsRunOnPhone!==true
  ||result.lensProfile.binding.captureId!==binding.captureId||x?.kind!=='few-shot-camera-calibration-example-v1'||x.sourceSha256!==result.sourceSha256||x.independentValidation!==false||x.labelSource!=='ikalibr-candidate-not-independent-truth')throw new Error('Quick calibration did not pass import checks.');
 validateRapidGeometry(result.upstreamParameters.CalibParam);
 const refined=rapidRefinedLens(result.upstreamParameters.CalibParam);
 const supplied=result.enrollment.refinedLensCandidate;
 if(!supplied||JSON.stringify(supplied.cameraMatrix)!==JSON.stringify(refined.cameraMatrix)||JSON.stringify(supplied.distortion)!==JSON.stringify(refined.distortion)||supplied.origin!=='ikalibr-refined-candidate'||supplied.independentLensValidation!==false)throw new Error('Quick calibration did not pass import checks.');
 return result;
}
export function rapidRefinedLens(p:any){
 const fail=()=>{throw new Error('Quick calibration did not pass import checks.');};
 const rows=p?.INTRI?.Camera;if(!Array.isArray(rows))return fail();const cameras=rows.filter((r:any)=>r.key==='/gaittrace/camera');if(cameras.length!==1)return fail();
 const c=cameras[0].value?.ptr_wrapper?.data,f=c?.focal_length,v=c?.principal_point,d=c?.disto_param;
 if(!Array.isArray(f)||f.length!==2||!Array.isArray(v)||v.length!==2||!Array.isArray(d)||d.length!==5||[...f,...v,...d].some(x=>!Number.isFinite(x))||f.some(x=>x<150||x>1600)||v[0]<160||v[0]>480||v[1]<120||v[1]>360||d.some(x=>Math.abs(x)>5)||c.img_width!==640||c.img_height!==480)return fail();
 return {cameraMatrix:[[f[0],0,v[0]],[0,f[1],v[1]],[0,0,1]],distortion:[d[0],d[1],d[3],d[4],d[2]]};
}
export function validateRapidGeometry(p:any){
 const fail=()=>{throw new Error('Quick calibration did not pass import checks.');};
 function item(section:string,key:string,topic:string){const rows=p?.[section]?.[key];if(!Array.isArray(rows))return fail();const matches=rows.filter((r:any)=>r.key===topic);if(matches.length!==1)return fail();return matches[0].value;}
 const q=item('EXTRI','SO3_CmToBr','/gaittrace/camera'),pos=item('EXTRI','POS_CmInBr','/gaittrace/camera');
 const quaternion=['qx','qy','qz','qw'].map(k=>q?.[k]),translation=['r0c0','r1c0','r2c0'].map(k=>pos?.[k]);
 const td=item('TEMPORAL','TO_CmToBr','/gaittrace/camera'),rs=item('TEMPORAL','RS_READOUT','/gaittrace/camera');
 if([...quaternion,...translation,td,rs].some(v=>!Number.isFinite(v))||Math.abs(quaternion.reduce((s,v)=>s+v*v,0)-1)>1e-5||Math.hypot(...translation)>.25||Math.abs(td)>.15||rs<0||rs>.1)return fail();
 const iq=item('EXTRI','SO3_BiToBr','/gaittrace/imu'),ip=item('EXTRI','POS_BiInBr','/gaittrace/imu'),it=item('TEMPORAL','TO_BiToBr','/gaittrace/imu');
 if(['qx','qy','qz','qw'].some(k=>!Number.isFinite(iq?.[k])||Math.abs(iq[k]-(k==='qw'?1:0))>1e-8)||['r0c0','r1c0','r2c0'].some(k=>!Number.isFinite(ip?.[k])||Math.abs(ip[k])>1e-8)||!Number.isFinite(it)||Math.abs(it)>1e-8)return fail();
}
export async function rapidReady(computer:CalibrationComputer){
 const health=await researchRequest(computer,'/api/health');if(health.rapidEnrollmentVersion!==1||health.rapidEnrollmentAvailable!==true)throw new Error('Restart the computer helper for quick calibration.');
}
export async function submitRapid(computer:CalibrationComputer,capture:CalibrationCapture){
 validateCalibrationComputer(computer);await rapidReady(computer);const meta=JSON.parse(capture.metadata);
 if(meta.kind!=='phone-rapid-camera-imu-capture-v1'||meta.status!=='completed'||meta.error||!/^calibration-\d+$/.test(meta.captureId)||!(meta.alignmentMovementStartedBootNs>0))throw new Error('Capture incomplete. Your previous profile is kept.');
 const response=await FileSystem.uploadAsync(computer.url+'/api/rapid-captures',capture.uri,{httpMethod:'POST',uploadType:FileSystem.FileSystemUploadType.BINARY_CONTENT,headers:{Authorization:'Bearer '+computer.token,'Content-Type':'application/zip'}});
 if(response.status!==202)throw new Error('Could not send the capture. It is saved on this phone.');
 const job=JSON.parse(response.body);if(!/^[a-f0-9]{24}$/.test(job.id??''))throw new Error('Quick calibration did not pass import checks.');
 await save('pending-rapid.json',{id:job.id,binding:meta});
}
export async function pollRapid(computer:CalibrationComputer,cancelled:()=>boolean){
 const pending=await pendingRapid();if(!pending||!/^[a-f0-9]{24}$/.test(pending.id))throw new Error('No quick calibration is waiting.');
 const began=Date.now();while(!cancelled()){
  const job=await researchRequest(computer,'/api/jobs/'+pending.id);if(cancelled())return null;
  if(job.status==='completed'){
   const result=validateRapidResult(job.result,pending.binding);await save('rapid-result.json',result);
   await FileSystem.deleteAsync(directory()+'pending-rapid.json',{idempotent:true});return result;
  }
  if(job.status==='failed')throw new Error(rapidFailureMessage(job.retryReason));
  if(job.status!=='processing'||Date.now()-began>3600000)throw new Error('Processing unavailable. Your previous profile is kept.');
  await new Promise<void>(resolve=>setTimeout(resolve,2000));
 }return null;
}
export function rapidFailureMessage(reason:string){
 if(reason==='clear-scene-views-needed')return 'Retry in a brighter room with furniture in view.';
 if(reason==='more-varied-motion-needed')return 'Retry with gentle loops and tilts in all directions.';
 if(reason==='view-estimates-disagree')return 'The views disagree. Retry with clearer scene views.';
 return 'Processing could not finish. Export this attempt for review.';
}
export async function savedRapidResult(){return read('rapid-result.json');}
export async function activateRapid(result:any,binding:any){
 validateRapidResult(result,binding);
 const path=directory()+'rapid-profile.json',temp=path+'.tmp';
 await FileSystem.writeAsStringAsync(temp,JSON.stringify(result));
 await FileSystem.moveAsync({from:temp,to:path});
}
export async function exportRapid(result:any){
 validateRapidResult(result,result.binding);
 const b=calibrationBridge();if(!b?.exportRapidEnrollment)throw new Error('Install the updated Android app for quick calibration.');
 return b.exportRapidEnrollment(result.binding.captureId,JSON.stringify(result));
}
