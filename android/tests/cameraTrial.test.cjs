const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
function load(name,mocks={},cache={}){
 const file=path.resolve(__dirname,'../src',name+'.ts');if(cache[file])return cache[file].exports;
 const module={exports:{}};cache[file]=module;
 const code=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{esModuleInterop:true,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
 vm.runInNewContext(code,{module,exports:module.exports,Date,Math,performance,console,require:id=>id in mocks?mocks[id]:id.startsWith('.')?load(path.relative(path.resolve(__dirname,'../src'),path.resolve(path.dirname(file),id)),mocks,cache):require(id)});return module.exports;
}
const {CameraTrialCapture,newCameraTrial,validCameraTrial,cameraPlacementCue,cameraWalkCue}=load('cameraTrial');
const flush=()=>new Promise(r=>setImmediate(r));
function fixture(){
 let now=0,resolveVideo,rejectVideo;const spoken=[],stopped=[],done=[],errors=[],order=[];
 const engine={connect(){order.push('connect')},begin(){order.push('imu-begin')},disconnect(){},stop(reason){stopped.push(reason);return {source:'device',startedAt:'2026-10-06T00:00:00Z',streams:{accelerometer:[{x:1}],gyroscope:[{y:1}],magnetometer:[{z:1}]}}},recordingClock:{monotonicMs:0,startedAt:'2026-10-06T00:00:00Z'},allReceiving:true,baselineReady:true,motionStatus:{enough:true,upright:true,steady:true,context:'rest-or-quiet'},preserveSetupBaseline(){order.push('baseline')},candidateStepsAfter(since){this.pulseSince=since;return this.pulses??0}};
 const camera={recordAsync(){order.push('camera-request');return new Promise((r,j)=>{resolveVideo=r;rejectVideo=j;});},stopRecording(){order.push('camera-stop');}};
 const capture=new CameraTrialCapture({engine,camera,walkingSeconds:15,referenceDistanceM:3,now:()=>now,say:text=>new Promise((resolve,reject)=>spoken.push({text,resolve,reject})),onStage(){},onStopped:async(r,t)=>{order.push('raw-saved');},onDone:async(r,t,uri)=>{done.push({r,t,uri});},onError:e=>errors.push(e)});
 return {capture,engine,camera,spoken,stopped,done,errors,order,setNow:v=>now=v,video:uri=>resolveVideo({uri}),failVideo:e=>rejectVideo(e)};
}
async function ready(f){f.capture.start();assert.equal(f.spoken[0].text,cameraPlacementCue);f.spoken[0].resolve();await flush();f.setNow(6000);f.capture.tick();f.setNow(11000);f.capture.tick();assert.equal(f.capture.stage,'cue');assert.equal(f.spoken[1].text,cameraWalkCue);f.spoken[1].resolve();await flush();assert.equal(f.capture.stage,'waiting');}
test('Camera trial captures real sensor streams and video under one clock contract, without claiming frame sync',async()=>{
 const f=fixture();await ready(f);assert.deepEqual(f.order.slice(0,3),['connect','imu-begin','camera-request']);
 f.engine.motionStatus={enough:true,upright:true,steady:false,context:'movement'};f.engine.pulses=1;f.setNow(12000);f.capture.tick();assert.equal(f.capture.stage,'walking');
 f.engine.motionStatus={enough:true,upright:true,steady:true,context:'rest-or-quiet'};f.setNow(26999);f.capture.tick();assert.equal(f.stopped.length,0);
 f.setNow(27000);f.capture.tick();assert.deepEqual(f.stopped,['completed']);assert.ok(f.order.indexOf('raw-saved')<f.order.indexOf('camera-stop'));
 f.video('file://cache/result.mp4');await flush();assert.equal(f.done.length,1);const t=f.done[0].t;
 assert.equal(t.end,'duration');assert.equal(t.timing.vioReady,false);assert.equal(t.timing.actualVideoStartOffsetMs,null);assert.equal(t.timing.alignmentUncertaintyMs,null);
 assert.equal(validCameraTrial(t),true);assert.equal(f.done[0].r.streams.magnetometer.length,1);
});
test('Placement has no 20-second deadline; instructions must finish before the movement gate opens',async()=>{
 const f=fixture();f.capture.start();f.setNow(60000);f.capture.tick();assert.equal(f.capture.stage,'placing');assert.equal(f.stopped.length,0);
 f.spoken[0].resolve();await flush();f.capture.tick();f.setNow(65000);f.capture.tick();assert.equal(f.capture.stage,'cue');
 f.engine.pulses=2;f.engine.motionStatus={enough:true,upright:true,steady:false,context:'movement'};f.capture.tick();assert.equal(f.capture.stage,'cue');
 f.spoken[1].resolve();await flush();assert.equal(f.capture.stage,'waiting');assert.equal(f.capture.walkingRemaining,15);
});
test('Standing still, stale sensor coverage and possible handling cannot start the walking timer',async()=>{
 const f=fixture();await ready(f);f.engine.pulses=1;f.setNow(45000);f.capture.tick();assert.equal(f.capture.stage,'waiting');
 f.engine.motionStatus={enough:true,upright:true,steady:false,context:'possible-handling'};f.capture.tick();assert.equal(f.capture.stage,'waiting');
 f.engine.motionStatus.context='movement';f.engine.allReceiving=false;f.capture.tick();assert.equal(f.capture.stage,'waiting');
 f.engine.allReceiving=true;f.engine.pulses=0;f.capture.tick();assert.equal(f.capture.stage,'waiting');assert.equal(f.engine.pulseSince,11000);
});
test('Camera rejection saves partial raw data and marks video failure without inventing an attachment',async()=>{
 const f=fixture();f.capture.start();f.failVideo(new Error('camera unavailable'));await flush();assert.deepEqual(f.stopped,['interrupted']);assert.equal(f.done[0].uri,null);assert.equal(f.done[0].t.video.status,'failed');assert.equal(f.done[0].t.video.fileName,null);assert.match(f.done[0].t.video.error,/camera unavailable/);
});
test('Interruptions stop both sources once and await the real video result',async()=>{
 const f=fixture();f.capture.start();f.capture.finish('interrupted');f.capture.finish('user-stopped');assert.deepEqual(f.stopped,['interrupted']);assert.equal(f.done.length,0);
 f.video('file://cache/partial.mp4');await flush();assert.equal(f.done.length,1);assert.equal(f.done[0].t.end,'interrupted');assert.equal(f.order.filter(e=>e==='camera-stop').length,1);
});
test('Camera ending itself is not reported as completing the selected walking duration',async()=>{
 const f=fixture();await ready(f);f.video('file://cache/limited.mp4');await flush();assert.equal(f.done[0].t.end,'camera-ended');assert.deepEqual(f.stopped,['interrupted']);
});
test('Voice failure terminates partial capture without skipping into walking',async()=>{
 const f=fixture();f.capture.start();f.spoken[0].reject(new Error('no voice'));await flush();assert.equal(f.capture.stage,'finishing');assert.deepEqual(f.stopped,['interrupted']);assert.match(f.errors[0],/Voice guidance/);
});
test('Stop notification occurs before slow video finalization and only once',async()=>{
 const f=fixture(),notified=[];f.capture.options.onCaptureEnded=end=>notified.push(end);
 await ready(f);f.engine.motionStatus={enough:true,upright:true,steady:false,context:'movement'};f.engine.pulses=1;f.setNow(12000);f.capture.tick();
 f.setNow(27000);f.capture.tick();assert.deepEqual(notified,['duration']);assert.equal(f.done.length,0);assert.equal(f.capture.stage,'finishing');
 f.capture.finish('user-stopped');assert.equal(notified.length,1);f.video('file://cache/result.mp4');await flush();assert.equal(notified.length,1);
});
test('Intentional stop cancels pending guidance without reporting a false voice failure',async()=>{
 const f=fixture();f.capture.start();f.capture.finish('user-stopped');f.spoken[0].reject(new Error('cancelled'));await flush();assert.equal(f.errors.length,0);assert.deepEqual(f.stopped,['user-stopped']);
});
test('Camera metadata rejects path traversal, forged precise synchronization and invalid times',()=>{
 const g=newCameraTrial(30,3,'2026-10-06T00:00:00Z');assert.equal(validCameraTrial(g),true);
 for(const alter of [v=>v.video.fileName='../secret.mp4',v=>v.video.status='saved',v=>v.timing.vioReady=true,v=>v.timing.actualVideoStartOffsetMs=0,v=>v.referenceDistanceM=-3,v=>v.timing.events=[{type:'camera-request',elapsedMs:-1}]]){const copy=JSON.parse(JSON.stringify(g));alter(copy);assert.equal(validCameraTrial(copy),false);}
});
test('Camera route trial saves hands-free after four fresh quiet seconds following movement',async()=>{
 const f=fixture();await ready(f);f.engine.pulses=1;f.engine.motionStatus={enough:true,upright:true,steady:false,context:'movement'};f.setNow(12000);f.capture.tick();
 f.engine.motionStatus={enough:true,upright:true,steady:true,context:'rest-or-quiet'};f.setNow(13000);f.capture.tick();f.setNow(16999);f.capture.tick();assert.equal(f.stopped.length,0);
 f.setNow(17000);f.capture.tick();assert.deepEqual(f.stopped,['completed']);assert.equal(f.capture.trial.end,'quiet-stop');assert.equal(validCameraTrial(f.capture.trial),true);
});
test('Quiet timer resets for resumed movement or stale streams; no duration completion is invented',async()=>{
 const f=fixture();await ready(f);f.engine.pulses=1;f.engine.motionStatus={enough:true,upright:true,steady:false,context:'movement'};f.setNow(12000);f.capture.tick();
 f.engine.motionStatus={enough:true,upright:true,steady:true,context:'rest-or-quiet'};f.setNow(13000);f.capture.tick();f.engine.allReceiving=false;f.setNow(17000);f.capture.tick();assert.equal(f.stopped.length,0);
 f.engine.allReceiving=true;f.setNow(18000);f.capture.tick();f.engine.motionStatus.steady=false;f.engine.motionStatus.context='movement';f.setNow(21000);f.capture.tick();assert.equal(f.stopped.length,0);
 f.engine.motionStatus.steady=true;f.engine.motionStatus.context='rest-or-quiet';f.setNow(22000);f.capture.tick();f.setNow(26000);f.capture.tick();assert.equal(f.capture.trial.end,'quiet-stop');
});
test('Native video persistence moves durable bytes before session metadata, and retries reuse the same file',async()=>{
 const files=new Map(),saved=[],copied=[];
 const fileSystem={documentDirectory:'file://documents/',async makeDirectoryAsync(){},async getInfoAsync(p){return files.get(p)??{exists:false};},async moveAsync(v){copied.push(v);files.set(v.to,{exists:true,isDirectory:false,size:1024});}};
 const storage=load('cameraTrialStorage',{'expo-file-system':fileSystem,'expo-sharing':{},'./store':{async saveSession(s){saved.push(s);}},'./language':{translate:s=>s}});
 const session={id:'test-01',cameraTrial:newCameraTrial(30,null,'2026-10-06T00:00:00Z')};
 const result=await storage.saveCameraTrial(session,'file://cache/actual.mp4');assert.equal(result.cameraTrial.video.status,'saved');assert.equal(result.cameraTrial.video.fileName,'camera-test-01.mp4');assert.equal(await storage.cameraVideoAvailable(result),true);
 await storage.saveCameraTrial(session,'file://cache/actual.mp4');assert.equal(copied.length,1);assert.equal(saved.length,2);
 assert.throws(()=>storage.cameraFileName('../secret'));assert.equal(await storage.cameraVideoAvailable({...result,cameraTrial:{...result.cameraTrial,video:{status:'saved',fileName:'camera-other.mp4'}}}),false);
});
test('Empty video cannot be marked saved; an imported filename does not establish local availability',async()=>{
 const storage=load('cameraTrialStorage',{'expo-file-system':{documentDirectory:'file://docs/',async makeDirectoryAsync(){},async getInfoAsync(){return {exists:true,isDirectory:false,size:0};},async moveAsync(){}},'expo-sharing':{},'./store':{saveSession(){throw new Error('must not save empty video as success')}},'./language':{translate:s=>s}});
 const session={id:'test-01',cameraTrial:newCameraTrial(15,null,'2026-10-06T00:00:00Z')};await assert.rejects(storage.saveCameraTrial(session,'file://cache/empty.mp4'),/empty/);
});
