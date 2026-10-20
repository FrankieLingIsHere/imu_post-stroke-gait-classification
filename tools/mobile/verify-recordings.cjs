// Read only the disposable emulator's owned files; preserve evidence before cleanup.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'android/dist/acceptance/native-recordings');fs.mkdirSync(out,{recursive:true});
const adb=path.join(root,'android/dist/native-distance-tools/android-sdk/platform-tools/adb.exe');
const names=execFileSync(adb,['-s','emulator-5560','shell','ls','/data/data/com.gaitsteps.app/files/recordings'],{encoding:'utf8'}).trim().split(/\r?\n/);
for(const name of names){if(!/^[a-zA-Z0-9_-]+\.json$/.test(name))throw Error('Unexpected emulator recording filename');execFileSync(adb,['-s','emulator-5560','pull','/data/data/com.gaitsteps.app/files/recordings/'+name,path.join(out,name)],{stdio:'inherit'});}
const records=names.map(n=>JSON.parse(fs.readFileSync(path.join(out,n),'utf8'))).sort((a,b)=>b.date.localeCompare(a.date));
const checks=[];
for(const protocol of ['research-walk','10mwt','tug','2mwt','6mwt']){
 const s=records.find(s=>s.assessmentSetup?.protocol===protocol);assert.ok(s,'Missing saved native '+protocol);
 assert.equal(s.isPractice,true);assert.equal(s.participantLabel,'EMU-SYNTHETIC-NOT-PATIENT');assert.equal(s.recording?.stopReason,'completed');assert.equal(s.assessment?.completed,false);
 const counts=Object.fromEntries(Object.entries(s.recording.streams).map(([name,v])=>[name,v.length]));assert.equal(Object.keys(counts).length,3);assert.ok(Object.values(counts).every(n=>n>0));
 if(protocol!=='research-walk'){
  assert.equal(s.protocolExecution?.protocol,protocol);assert.equal(s.protocolExecution.clinicalOutcomeVerified,false);
  assert.equal(s.protocolExecution.end,['2mwt','6mwt'].includes(protocol)?'duration':'auto-stop-estimate');
  if(protocol==='2mwt'||protocol==='6mwt'){const seconds=protocol==='2mwt'?120:360;assert.ok(s.protocolExecution.elapsedFromGoSeconds>=seconds);assert.ok(s.protocolExecution.elapsedFromGoSeconds<seconds+2);}
 }
 checks.push({protocol,id:s.id,passed:true,stopReason:s.recording.stopReason,counts,quality:s.quality,execution:s.protocolExecution??null,personalReference:s.recording.baseline?.postureReference??null});
}
const report={createdAt:new Date().toISOString(),passed:true,physicalPhoneUsed:false,simulatedSensorInputs:true,distanceEnabled:false,distanceAccuracyValidated:false,audibleSpeechValidated:false,clinicalValidation:false,checks};
fs.writeFileSync(path.join(out,'verification-summary.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
