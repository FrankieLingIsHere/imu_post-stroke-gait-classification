import * as Application from 'expo-application';
import * as Updates from 'expo-updates';

export function releaseInfo() {
  return {
    appVersion: Application.nativeApplicationVersion,
    buildNumber: Application.nativeBuildVersion,
    runtimeVersion: Updates.runtimeVersion ?? null,
    updateId: Updates.updateId ?? null,
    channel: Updates.channel ?? null,
    embedded: Updates.isEmbeddedLaunch,
  };
}
