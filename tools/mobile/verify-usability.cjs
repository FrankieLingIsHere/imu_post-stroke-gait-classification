// Verify current-APK interaction evidence, retaining every incomplete/failed attempt.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'android/dist');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const apk=read(path.join(base,'emulator-lab/emulator-apk.json'));
const folders=fs.readdirSync(path.join(base,'emulator-lab/interactions')).sort().reverse();
const checks=[];
for(const name of ['returning-participant','usability-review','small-screen-settings','result-worker-review','collector-navigation','compact-review-export','list-layout-review','audio-control-layout']){
 const controls=read(path.join(__dirname,'scenarios',name+'.json'));
 const match=folders.find(folder=>{
  const dir=path.join(base,'emulator-lab/interactions',folder),file=path.join(dir,'replies.json');
  if(!fs.existsSync(file)||fs.existsSync(path.join(dir,'failure.json')))return false;
  const result=read(file);
  return result.serial==='emulator-5560'&&result.installedApkSha256===apk.sha256&&result.physicalPhoneUsed===false&&result.replies.length===controls.length&&
   Date.parse(result.replies[0].at)>=Date.parse(apk.builtAt)&&result.replies.every((r,i)=>r.passed&&JSON.stringify(r.command)===JSON.stringify(controls[i]));
 });
 assert.ok(match,'No complete current-APK interaction evidence for '+name);
 checks.push({scenario:name,passed:true,steps:controls.length,evidence:'android/dist/emulator-lab/interactions/'+match});
}
const report={createdAt:new Date().toISOString(),passed:true,apk,checks,physicalPhoneUsed:false,
 audibleSpeechValidated:false,olderAdultUsabilityStudy:false,distanceAccuracyValidated:false,
 limits:['An IMU-only stop remains provisional, even after its warning and resume grace.','JSON parsing and final persistence are atomic; cancellation is available during reads and CSV validation.','Long review content and worker fields scroll; recording-detail tabs scroll with content on small or enlarged-text screens and remain fixed on roomy screens.'],
 failuresRetained:true};
fs.writeFileSync(path.join(base,'acceptance/usability-summary.json'),JSON.stringify(report,null,2));
console.log('Current emulator usability checks passed; steps and screenshots retained.');
