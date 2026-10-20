// Consolidate executed evidence; never convert software fixtures into physical validation.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'android/dist');
const read=p=>JSON.parse(fs.readFileSync(path.join(base,p),'utf8').replace(/^\uFEFF/,''));
const software=read('sandbox-checks/verification.json'),native=read('acceptance/native-recordings/verification-summary.json'),exportReport=read('acceptance/export-roundtrip/report.json');
assert.equal(software.passed,true);assert.equal(native.passed,true);assert.equal(native.checks.length,5);assert.ok(exportReport.checks.every(c=>c.passed));
const reference=read('acceptance/native-recordings/2026-10-10T14-00-27-784Z-67fcebbd.json');
const imports=[];for(const format of ['json','csv']){
 const actual=read('acceptance/export-roundtrip/native-'+format+'-import.json');
 assert.equal(actual.id,'EMU-six-'+format+'-import');assert.equal(actual.participantId,reference.participantId);
 for(const name of ['accelerometer','gyroscope','magnetometer'])assert.deepEqual(actual.recording.streams[name],reference.recording.streams[name]);
 imports.push({format,passed:true,everyRawSampleUnchanged:true,id:actual.id});
}
const form=read('emulator-lab/worker-form/saved-native.json').assessment.gaitAssessment;
assert.equal(Object.keys(form.ratings).length,31);assert.equal(form.assessor,'EMU-RATER-NOT-CLINICAL');
const selected=fs.readFileSync(path.join(base,'acceptance/export-roundtrip/native-selected.csv'),'utf8');
const ids=[...new Set(selected.split(/\r?\n/).slice(1).filter(Boolean).map(row=>row.split(',')[0]))];assert.equal(ids.length,1);
const log=name=>fs.readFileSync(path.join(base,'sandbox-checks',name+'.log'),'utf8');
const componentTests=Number(log('app-components').match(/tests (\d+)/)?.[1]),browserChecks=Number(log('browser-flows').match(/(\d+) passed/)?.[1]);
const nativeJavaAssertions=[...log('native-contracts').matchAll(/PASS: (\d+) (?:Java|native|guided|measured)/g)].reduce((sum,m)=>sum+Number(m[1]),0);
assert.ok(componentTests>0&&browserChecks>0&&nativeJavaAssertions>0);
const elderReplay=read('acceptance/elder-audio-flow.json');assert.equal(elderReplay.checks.length,4);assert.ok(elderReplay.checks.every(c=>c.passed));
const report={createdAt:new Date().toISOString(),passed:true,physicalPhoneUsed:false,simulatedSensorInputs:true,allPhysicalFeaturesValidated:false,nativeDistanceEnabledCaptureValidated:false,distanceAccuracyValidated:false,audibleSpeechValidated:false,clinicalValidation:false,patientDataGenerated:false,
 elderlyExperience:{olderAdultUsabilityStudy:false,audioReplay:elderReplay,nativeRecordingFlowEvidencePredatesVoiceCueChange:true,latestNativeChecks:['small-screen settings','visible import progress','JSON/CSV review opening']},
 software:{report:'android/dist/sandbox-checks/verification.json',steps:software.steps,componentTests,nativeJavaAssertions,browserChecks,integratedRecordingScenarios:8},
 native:{report:'android/dist/acceptance/native-recordings/verification-summary.json',checks:native.checks,voiceEnabled:false,phoneDistanceEnabled:false},
 importRoundTrips:imports,workerForm:{ratings:31,persistenceVerified:true,clinicalObservations:false,artifact:'android/dist/emulator-lab/worker-form/saved-native.json'},
 selectedExport:{ids,selectedCount:1,bytes:Buffer.byteLength(selected),sentToRecipient:false},finalEmulatorApk:read('emulator-lab/emulator-apk.json'),
 usabilityFollowUp:fs.existsSync(path.join(base,'acceptance/usability-summary.json'))?read('acceptance/usability-summary.json'):null,
 procedures:['tools/mobile/APP_ACCEPTANCE.md','tools/mobile/scenarios/research-recording.json','tools/mobile/clinical-scenarios.cjs','tools/mobile/scenarios/six-minute-imports.json','tools/mobile/worker-form.cjs','tools/mobile/scenarios/selected-export-storage.json'],
 uiEvidenceDirectory:'android/dist/emulator-lab/interactions',limitations:['Camera-enabled phone setup and live VIO are not validated by the fixed emulator camera.','Tracked 10MWT boundaries pass controlled replay, not physical distance validation.','Native clinical flows used voice-off practice mode; heard TTS remains a physical check.','OEM sensors, background restrictions and lower-back bag placement require physical checks.']};
fs.writeFileSync(path.join(base,'acceptance/verification.json'),JSON.stringify(report,null,2));console.log('Acceptance manifest passed: android/dist/acceptance/verification.json');
