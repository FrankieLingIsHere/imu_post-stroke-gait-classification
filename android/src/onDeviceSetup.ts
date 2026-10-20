import {calibrationBridge} from './cameraCalibration';
import {Camera} from 'expo-camera';

import {validateOnDeviceProfile} from './onDeviceProfile';
export {PHONE_SETUP_METHOD,PHONE_SETUP_COMMIT,validateOnDeviceProfile} from './onDeviceProfile';

export async function phoneDistanceProfile(){
 const b=calibrationBridge();if(!b?.onDeviceProfile||!b.phoneCalibrationInfo)return null;
 const info={...JSON.parse(await b.phoneCalibrationInfo()),capturePipeline:'native-camera-imu-v3',opticalSetup:'waist-bag-window'};
 const text=await b.onDeviceProfile();
 if(text){try{return validateOnDeviceProfile(JSON.parse(text),info);}catch{/* A failed candidate must not erase a compatible older reference. */}}
 if(b.referenceTrackingProfile){try{const saved=await b.referenceTrackingProfile();if(saved)return validateOnDeviceProfile(JSON.parse(saved),info);}catch{/* Missing or incompatible reference stays unavailable. */}}
 return null;
}
export async function phoneSetupPermission(){
 const b=calibrationBridge();
 if(!b?.captureOnDeviceSetup||!b.completeOnDeviceSetup||!b.beginAlignmentMovement)throw new Error('Install the updated Android app for on-phone setup.');
 const permission=await Camera.getCameraPermissionsAsync();
 if(!permission.granted&&!(await Camera.requestCameraPermissionsAsync()).granted)throw new Error('Camera permission is needed for on-phone setup.');
 return b;
}
export async function completePhoneSetup(captureId:string){
 if(!/^calibration-\d+$/.test(captureId))throw new Error('Phone setup could not finish. Your previous setup is kept.');
 const b=calibrationBridge();if(!b?.completeOnDeviceSetup||!b.phoneCalibrationInfo)throw new Error('Install the updated Android app for on-phone setup.');
 const p=JSON.parse(await b.completeOnDeviceSetup(captureId));
 return validateOnDeviceProfile(p,{...JSON.parse(await b.phoneCalibrationInfo()),capturePipeline:'native-camera-imu-v3',opticalSetup:'waist-bag-window'});
}
