// Compare a freshly computed source fingerprint with the recorded native release.
// A cached Gradle fingerprint is insufficient evidence of OTA compatibility.
const fs=require('node:fs');
const path=require('node:path');
const {createFingerprintAsync}=require('expo/fingerprint');
const root=path.resolve(__dirname,'..');
async function main(){
 const file=path.resolve(process.argv[2]??path.join(root,'releases/current-native.json'));
 const text=fs.readFileSync(file,'utf8').trim();
 const record=text.startsWith('{')?JSON.parse(text):{runtimeVersion:text};
 if(!/^[a-f0-9]{40}$/.test(record.runtimeVersion??''))throw Error('Missing or invalid recorded native runtime.');
 const app=JSON.parse(fs.readFileSync(path.join(root,'app.json'),'utf8')).expo;
 if(record.appVersion&&record.appVersion!==app.version||record.nativeVersionCode&&record.nativeVersionCode!==app.android.versionCode)
  throw Error('Recorded native release does not match app version/build.');
 const fingerprint=await createFingerprintAsync(root,{platforms:['android'],ignorePaths:['android/**/*','ios/**/*']});
 if(fingerprint.hash!==record.runtimeVersion)
  throw Error(`Native runtime mismatch: source ${fingerprint.hash}, recorded ${record.runtimeVersion}. Rebuild and verify the APK before publishing an update.`);
 console.log(`Native runtime verified: ${fingerprint.hash}`);
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
