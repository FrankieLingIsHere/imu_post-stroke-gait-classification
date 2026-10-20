// W3C Appium smoke test. Every device operation is locked to our virtual device.
const fs=require('node:fs'),path=require('node:path'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'android/dist/emulator-lab');
const argv=process.argv.slice(2),argument=(key,fallback)=>{const i=argv.indexOf(key);return i>=0?argv[i+1]:fallback;};
const serial='emulator-5560',pkg=argument('--package','com.gaitsteps.app'),apk=argument('--apk','');
const adb=path.join(root,'android/dist/native-distance-tools/android-sdk/platform-tools/adb.exe');
fs.mkdirSync(out,{recursive:true});
const report={startedAt:new Date().toISOString(),physicalPhoneUsed:false,emulatorSerial:serial,package:pkg,
  apk,steps:[],passed:false,clinicalValidation:false,distanceAccuracyValidated:false,audibleSpeechValidated:false};
const save=()=>fs.writeFileSync(path.join(out,'interaction-report.json'),JSON.stringify(report,null,2)+'\n');
const device=(...args)=>execFileSync(adb,['-s',serial,...args],{encoding:'utf8',timeout:45000});
let session;
async function api(method,route,body){
 const response=await fetch('http://127.0.0.1:4725'+route,{method,headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(120000)});
 const value=await response.json();if(!response.ok||value.value?.error)throw new Error(JSON.stringify(value.value));return value.value;
}
const call=(method,route,body)=>api(method,'/session/'+session+route,body);
const literal=value=>value.includes("'")?'"'+value+'"':"'"+value+"'";
async function element(label,editable=false){
 const selector=`//*[${editable?"@class='android.widget.EditText' and ":""}(@text=${literal(label)} or @content-desc=${literal(label)})]`;
 const result=await call('POST','/elements',{using:'xpath',value:selector});
 if(!result.length)throw new Error(`UI reply missing: ${label}`);
 return result[0]['element-6066-11e4-a52e-4f735466cecf'];
}
async function click(label){await call('POST','/element/'+await element(label)+'/click',{});}
async function checkpoint(name){
 const source=await call('GET','/source');fs.writeFileSync(path.join(out,name+'.xml'),source);
 const picture=await call('GET','/screenshot');fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(picture,'base64'));
 return source;
}
async function step(name,operation){
 const entry={name,passed:false};report.steps.push(entry);save();
 try{const reply=await operation();entry.passed=true;if(reply!==undefined)entry.reply=reply;await checkpoint(name);console.log('PASS: '+name);}
 catch(error){entry.error=error.message;await checkpoint(name+'-failed').catch(()=>{});throw error;}
 finally{save();}
}
async function main(){
 if(!apk||!fs.existsSync(apk))throw new Error('Pass --apk with the built APK.');
 device('get-state');
 // noReset intentionally preserves virtual-device records, but Appium also skips
 // installation in that mode. Explicitly upgrade first so we never test stale code.
 report.installReply=device('install','-r',path.resolve(apk)).trim();
 if(!report.installReply.includes('Success'))throw new Error('APK installation did not succeed.');
 report.installedPackage=device('shell','dumpsys','package',pkg).split('\n').filter(line=>/primaryCpuAbi|versionCode=|versionName=/.test(line)).map(line=>line.trim());
 if(!report.installedPackage.some(line=>line.includes('primaryCpuAbi=x86_64')))throw new Error('Use a verified x86_64 APK in this emulator lab.');
 device('shell','am','force-stop',pkg);
 report.androidVersion=device('shell','getprop','ro.build.version.release').trim();
 report.abis=device('shell','getprop','ro.product.cpu.abilist').trim();save();
 const value=await api('POST','/session',{capabilities:{alwaysMatch:{platformName:'Android',
  'appium:automationName':'UiAutomator2','appium:udid':serial,'appium:app':path.resolve(apk),
  'appium:appPackage':pkg,'appium:appActivity':'.MainActivity','appium:noReset':true,
  'appium:autoGrantPermissions':false,'appium:enforceAppInstall':true,'appium:newCommandTimeout':180,
  'appium:adbExecTimeout':90000,'appium:uiautomator2ServerInstallTimeout':90000},firstMatch:[{}]}});
 session=value.sessionId;
 await call('POST','/timeouts',{implicit:12000});
 await step('01-home',async()=>{await element('Start a walk');return 'Actual installed APK home is accessible.';});
 await step('02-recordings',async()=>{await click('My recordings');return 'Recording history opens.';});
 device('shell','input','keyevent','4');
 await step('03-participants',async()=>{await click('Participants and profiles');await element('Add participant');return 'Participant management opens.';});
 device('shell','input','keyevent','4');
 await step('04-dashboard',async()=>{await click('Tools and help');await click('Progress dashboard');return 'Dashboard opens from Tools and help.';});
 device('shell','input','keyevent','4');
 await step('05-prepare',async()=>{await click('Start a walk');const motion=await call('POST','/elements',{using:'accessibility id',value:'Record motion only'});if(motion.length)await click('Record motion only');await element('Continue');await element('Automatic study ID');return 'Preparation opens with an automatic ID; motion-only choice explicitly bypasses camera distance.';});
 await step('06-intake-gate',async()=>{await click('Continue');await element('Enter an age from 1 to 120.');return 'Missing age is rejected; a study ID does not need typing.';});
 await step('06b-keyboard-and-age-gate',async()=>{
  await click('Age in years');
  await call('POST','/element/'+await element('Age in years',true)+'/value',{text:'0'});
  const keyboard=await call('GET','/appium/device/is_keyboard_shown');
  if(keyboard){await checkpoint('06b-keyboard-visible');device('shell','input','keyevent','4');}
  await click('Continue');await element('Enter an age from 1 to 120.');
  return 'Real Android text entry works; missing age is rejected.';
 });
 device('shell','input','keyevent','4');
 await step('07-background-resume',async()=>{device('shell','input','keyevent','3');await call('POST','/execute/sync',{script:'mobile: activateApp',args:[{appId:pkg}]});await element('Start a walk');return 'APK resumes from Android Home.';});
 await step('08-research-menu',async()=>{await click('Tools and help');await element('Set up this phone');return 'Native phone setup entry is visible.';});
 await step('09-phone-setup',async()=>{await click('Set up this phone');await element('Start phone setup');return 'Native setup screen opens without starting capture.';});
 await step('09b-setup-return',async()=>{await click('Back');await element('Start a walk');return 'Setup returns safely without starting a capture.';});
 await step('10-virtual-sensors',async()=>device('emu','sensor','status'));
 report.passed=true;report.completedAt=new Date().toISOString();save();
 console.log('Emulator UI smoke checks passed. '+path.join(out,'interaction-report.json'));
}
main().catch(error=>{report.error=error.message;save();console.error(error.message);process.exitCode=1;}).finally(async()=>{
 if(session)await call('DELETE','').catch(()=>{});
 try{fs.writeFileSync(path.join(out,'logcat.txt'),device('logcat','-d','-t','1500'));}catch{}
});
