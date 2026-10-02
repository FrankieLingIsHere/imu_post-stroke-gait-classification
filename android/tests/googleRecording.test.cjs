// Injected API contracts. These checks do not establish Android/device accuracy.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function load(name, mocks = {}) {
  const file = path.resolve(__dirname,'../src',name+'.ts');
  const module = {exports:{}};
  const code = ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
  vm.runInNewContext(code,{module,exports:module.exports,Date,Math,console,
    setTimeout:(fn,ms)=>setTimeout(fn,ms===2000?0:ms),clearTimeout,setInterval,clearInterval,
    require:id=>id in mocks?mocks[id]:id.startsWith('.')?load(id.slice(2),mocks):require(id)});
  return module.exports;
}
const {summarizeGoogleRecords,GoogleRecordingCapture} = load('googleRecording');
const point = (kind,value,startUnixMs=1000,endUnixMs=11000)=>({kind,value,startUnixMs,endUnixMs,firstReceivedAtUnixMs:13000});
test('No Google records means unknown distance, not a fabricated zero',()=>{
  const r=summarizeGoogleRecords(1000,11000,[],[],[]);
  assert.equal(r.distanceM,null);assert.equal(r.steps,null);assert.equal(r.meanSpeedMps,null);
  assert.equal(r.status,'no-records');assert.equal(r.clinicallyValidated,false);assert.equal(r.controlsTestEnd,false);
});
test('Repeated polls are deduplicated; OS-reported zero is preserved',()=>{
  const r=summarizeGoogleRecords(1000,11000,[point('distance',0),point('distance',0),point('steps',0)],[],[]);
  assert.equal(r.distanceM,0);assert.equal(r.steps,0);assert.equal(r.status,'records-received');assert.equal(r.meanSpeedMps,0);
});
test('Boundary-straddling, invalid and overlapping records cannot inflate test distance',()=>{
  const observations=[point('distance',2,500,2000),point('distance',4,2000,6000),point('distance',5,5000,7000),point('distance',NaN),point('steps',1.5)];
  const r=summarizeGoogleRecords(1000,11000,observations,[],[]);
  assert.equal(r.distanceM,4);assert.equal(r.boundaryRecordsExcluded,1);assert.equal(r.invalidRecordsExcluded,2);assert.equal(r.overlappingRecordsExcluded,1);
  assert.equal(r.meanSpeedMps,null);assert.equal(r.status,'partial');assert.equal(r.observations.length,5);
});
test('Sparse records withhold full-test speed even if both data types exist',()=>{
  const r=summarizeGoogleRecords(1000,11000,[point('distance',1,1000,2000),point('steps',2,1000,2000)],[],[]);
  assert.equal(r.distanceCoverageFraction,0.1);assert.equal(r.meanSpeedMps,null);assert.equal(r.status,'partial');
});
test('Capture reads a fixed Go-to-finish window, retains arrival evidence and releases subscriptions',async()=>{
  const calls=[];let unsubscribed=0;
  const bridge={async subscribe(){},async unsubscribe(){unsubscribed++},async readData(start,end){calls.push([start,end]);return {receivedAtUnixMs:13000,points:[point('distance',10),point('steps',20)]}}};
  const capture=new GoogleRecordingCapture(bridge,()=>12000);
  await capture.prepare();capture.begin(1000);
  const r=await capture.finish(11000);
  assert.equal(calls.length,2);assert.ok(calls.every(([start,end])=>start===1000&&end===11000));
  assert.equal(r.distanceM,10);assert.equal(r.steps,20);assert.equal(r.observations.length,2);
  assert.equal(r.observations[0].firstReceivedAtUnixMs,13000);assert.equal(r.polls.length,2);
  assert.equal(r.subscriptionCleanup,'complete');assert.equal(unsubscribed,1);
});
test('API failure does not turn into a distance reading; cleanup failure is saved',async()=>{
  const capture=new GoogleRecordingCapture({async subscribe(){throw Error('API unavailable')},async unsubscribe(){throw Error('cleanup failed')}},()=>12000);
  await capture.prepare();capture.begin(1000);const r=await capture.finish(11000);
  assert.equal(r.status,'error');assert.equal(r.distanceM,null);assert.equal(r.subscriptionCleanup,'failed');assert.equal(r.errors.length,2);
});
test('Cancelling during subscription cleans up a subscription that arrives late',async()=>{
  let resolveSubscribe,unsubscribed=0;
  const capture=new GoogleRecordingCapture({subscribe:()=>new Promise(r=>resolveSubscribe=r),async unsubscribe(){unsubscribed++}});
  const preparation=capture.prepare();await capture.cancel();resolveSubscribe();await preparation;
  await new Promise(resolve=>setImmediate(resolve));assert.ok(unsubscribed>=2);
});
test('Older APK and denied activity permission produce an actionable setup message',async()=>{
  const native={available:true,permissionGranted:false};
  const core={requireOptionalNativeModule:()=>null};
  const permissions={PERMISSIONS:{ACTIVITY_RECOGNITION:'activity'},RESULTS:{GRANTED:'granted'},async request(){return 'denied'}};
  const api=load('googleRecordingBridge',{'react-native':{Platform:{OS:'android'},PermissionsAndroid:permissions},'expo-modules-core':core});
  await assert.rejects(api.checkGoogleRecordingPermission(),/new Android APK/);
  core.requireOptionalNativeModule=()=>({async availability(){return native}});
  await assert.rejects(api.checkGoogleRecordingPermission(),/Activity permission was not granted/);
});
test('Google summaries reach both CSV exports and detailed observations remain in JSON',()=>{
  const exporting=load('exportData');
  const recording={schemaVersion:2,source:'device',platform:'android',startedAt:new Date(1000).toISOString(),elapsedSeconds:10,requestedHz:{accelerometer:100,gyroscope:100,magnetometer:50},guidanceEvents:[],streams:{accelerometer:[{x:0,y:0,z:1,elapsedMs:0,receivedAtUnixMs:1000,sensorTimestampSeconds:1}],gyroscope:[],magnetometer:[]}};
  recording.googleRecording=summarizeGoogleRecords(1000,11000,[point('distance',10),point('steps',20)],[],[],'complete');
  const session={id:'google-test',recording,duration:10,isPractice:false,windows:[]};
  for(const csv of [exporting.exportCSV(session),exporting.exportFeatureCSV(session)]){
    const rows=csv.trim().split(/\r?\n/).map(row=>row.slice(1,-1).split('","'));
    assert.ok(rows[0].includes('google_distance_m'));assert.ok(rows.length>1);
    for(const row of rows.slice(1)){assert.equal(row.length,rows[0].length);assert.equal(row[rows[0].indexOf('google_distance_m')],'10');}
  }
  assert.equal(JSON.parse(exporting.exportJSON(session)).session.recording.googleRecording.observations.length,2);
});
test('All Google-facing UI and setup failure messages have Malay and Chinese translations',()=>{
  const {messages}=load('translations');
  for(const key of Object.keys(messages).filter(k=>/Google|Activity permission was not granted/.test(k)))
    assert.ok(messages[key].length===2&&messages[key].every(v=>v.trim()),key);
});
test('JSON review preserves the optional Google summary and rejects malformed numeric fields',()=>{
  const {parseReviewRecording}=load('reviewRecording');
  const summary=summarizeGoogleRecords(1000,11000,[point('distance',10),point('steps',20)],[],[],'complete');
  const session={id:'google-review',date:new Date(1000).toISOString(),duration:10,isPractice:false,windows:[],recording:{source:'device',schemaVersion:2,elapsedSeconds:10,stopReason:'completed',guidanceEvents:[],streams:{accelerometer:[],gyroscope:[],magnetometer:[]},requestedHz:{accelerometer:100,gyroscope:100,magnetometer:50},googleRecording:summary}};
  const payload={source:'device',exportSchemaVersion:3,session};
  assert.equal(parseReviewRecording(JSON.stringify(payload)).recording.googleRecording.distanceM,10);
  session.recording.googleRecording.distanceM='10';
  assert.throws(()=>parseReviewRecording(JSON.stringify(payload)),/valid Gait Steps/);
  delete session.recording.googleRecording;
  assert.ok(parseReviewRecording(JSON.stringify(payload)),'Older exports remain supported');
});
