import { Platform, PermissionsAndroid } from 'react-native';
import type { GoogleRecordingBridge } from './googleRecording';

export function googleRecordingBridge(): GoogleRecordingBridge | null {
  if (Platform.OS !== 'android') return null;
  // Optional lookup keeps older APKs and Expo Go usable without the native module.
  const { requireOptionalNativeModule } = require('expo-modules-core');
  return requireOptionalNativeModule('GaitGoogleRecording') as GoogleRecordingBridge | null;
}
export async function checkGoogleRecordingPermission(): Promise<void> {
  const bridge = googleRecordingBridge();
  if (!bridge) throw new Error('Google distance test needs the new Android APK. Turn it off to continue.');
  const status = await bridge.availability();
  if (!status.available) throw new Error('Google Play services cannot provide distance on this phone. Turn off the Google distance test to continue.');
  if (!status.permissionGranted) {
    const granted = await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.ACTIVITY_RECOGNITION);
    if (granted !== PermissionsAndroid.RESULTS.GRANTED)
      throw new Error('Activity permission was not granted. Turn off the Google distance test to continue.');
  }
}
