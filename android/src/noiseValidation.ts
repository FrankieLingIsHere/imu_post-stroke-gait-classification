import * as FileSystem from 'expo-file-system';
import type {CalibrationCapture} from './cameraCalibration';
import {calibrationComputer} from './referenceCalibration';
import {researchRequest} from './distanceValidation';

export function validateNoiseResult(result:any,meta:any){
 if(result?.schemaVersion!==1||result.kind!=='phone-imu-noise-report-v1'||result.biasRandomWalkReady!==false||result.fullCalibrationReady!==false||result.distanceReady!==false
  ||!['rejected','review-required','white-noise-candidate'].includes(result.status)||!Array.isArray(result.errors)||!/^[a-f0-9]{64}$/.test(result.sourceSha256??'')
  ||['installationId','captureId','capturePipeline'].some(k=>result.binding?.[k]!==meta[k])||JSON.stringify(result.binding?.device)!==JSON.stringify(meta.device)
  ||result.whiteNoiseCandidateReady!==(result.status==='white-noise-candidate'))throw new Error('The sensor noise result did not pass import checks.');
 return result;
}
export async function checkNoiseCapture(capture:CalibrationCapture,cancelled:()=>boolean){
 const computer=await calibrationComputer();if(!computer)throw new Error('Connect the calibration computer first.');
 const meta=JSON.parse(capture.metadata);if(meta.kind!=='phone-imu-noise-capture-v1'||meta.status!=='completed'||meta.error||!/^imu-noise-\d+$/.test(meta.captureId))throw new Error('A completed stationary sensor capture is needed.');
 const health=await researchRequest(computer,'/api/health');if(health.distanceValidationVersion!==2)throw new Error('Restart the updated computer helper before testing distance.');
 const response=await FileSystem.uploadAsync(computer.url+'/api/noise-captures',capture.uri,{httpMethod:'POST',uploadType:FileSystem.FileSystemUploadType.BINARY_CONTENT,headers:{Authorization:'Bearer '+computer.token,'Content-Type':'application/zip'}});
 if(response.status!==202)throw new Error('Could not send the sensor capture. It is saved on this phone.');
 const job=JSON.parse(response.body);if(!/^[0-9a-f]{24}$/.test(job.id??''))throw new Error('The sensor noise result did not pass import checks.');
 const began=Date.now();while(!cancelled()){
  const row=await researchRequest(computer,'/api/jobs/'+job.id);if(cancelled())return null;
  if(row.status==='completed'){
   const result=validateNoiseResult(row.result,meta);await FileSystem.writeAsStringAsync(FileSystem.documentDirectory+'camera-imu-noise/'+meta.captureId+'-report.json',JSON.stringify(result));if(result.whiteNoiseCandidateReady){await FileSystem.makeDirectoryAsync(FileSystem.documentDirectory+'camera-calibration/',{intermediates:true});await FileSystem.writeAsStringAsync(FileSystem.documentDirectory+'camera-calibration/noise.json',JSON.stringify(result));}return result;
  }
  if(row.status==='failed'||Date.now()-began>120000)throw new Error('Sensor noise processing did not finish. Retry the saved capture.');
  await new Promise<void>(resolve=>setTimeout(resolve,1000));
 }return null;
}
