// Injected browser events verify contracts; these are not physical sensor trials.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
function load(name,globals={},mocks={},cache={}) {
 const file=path.resolve(__dirname,'../src',name+'.ts');if(cache[file])return cache[file].exports;
 const module={exports:{}};cache[file]=module;
 const code=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,esModuleInterop:true}}).outputText;
 vm.runInNewContext(code,{module,exports:module.exports,console,Date,Math,performance,setTimeout,clearTimeout,...globals,require:id=>id==='./releaseInfo'?{releaseInfo:()=>({appVersion:'test',buildNumber:'0',runtimeVersion:null,updateId:null,channel:null,embedded:true})}:id in mocks?mocks[id]:id.startsWith('.')?load(path.relative(path.resolve(__dirname,'../src'),path.resolve(path.dirname(file),id)),globals,mocks,cache):require(id)});return module.exports;
}
function rig(missing) {
 let now=0;const instances={},timers=new Map();let id=0;
 const globals={isSecureContext:true,performance:{now:()=>now},setTimeout:fn=>{timers.set(++id,fn);return id},clearTimeout:i=>timers.delete(i)};
 for(const name of ['Accelerometer','Gyroscope','Magnetometer'])if(name!==missing)globals[name]=class {
  constructor(options){this.options=options;this.listeners={};instances[name]=this;this.stopped=false;}
  addEventListener(t,f){this.listeners[t]=f}removeEventListener(t){delete this.listeners[t]}start(){}stop(){this.stopped=true}
 };
 const api=load('browserSensors',globals);
 return {api,globals,instances,setTime:t=>now=t,emit(name,t,axes=[0,9.80665,0]){now=t;const s=instances[name];if(!s||s.stopped)return;[s.x,s.y,s.z]=axes;s.timestamp=t;s.listeners.reading?.()},finish(){now=3000;for(const fn of [...timers.values()])fn()},feed(rate=50){for(let t=0;t<3000;t+=1000/rate)for(const n of Object.keys(instances))this.emit(n,t)}};
}
test('Browser check requires measured readings from all three sensors and stops every subscription',async()=>{
 const r=rig(),promise=r.api.checkBrowserSensors();r.feed();r.finish();const result=await promise;
 assert.equal(result.ready,true);for(const v of Object.values(result.sensors)){assert.equal(v.count,150);assert.ok(Math.abs(v.hz-50)<1e-8)}
 for(const s of Object.values(r.instances)){assert.equal(s.stopped,true);assert.equal(s.options.referenceFrame,'device')}
});
test('Hardware presence, missing magnetometer, slow streams and permission errors never pass',async()=>{
 for(const mode of ['empty','missing','slow','denied','stale']){
  const r=rig(mode==='missing'?'Magnetometer':undefined),p=r.api.checkBrowserSensors();
  if(mode!=='empty'&&mode!=='stale')r.feed(mode==='slow'?10:50);
  if(mode==='stale')for(let t=0;t<1000;t+=20)for(const n of Object.keys(r.instances))r.emit(n,t);
  if(mode==='denied')r.instances.Gyroscope.listeners.error();
  r.finish();assert.equal((await p).ready,false,mode);
 }
});
test('Unit conversion preserves axes, gravity, gyro/magnetic units and sensor timestamp provenance',()=>{
 const r=rig(),events=[];
 const a=r.api.subscribeBrowserSensor('accelerometer',v=>events.push(v));r.emit('Accelerometer',1250,[9.80665,-19.6133,0]);
 assert.equal(events[0].x,1);assert.equal(events[0].y,-2);assert.equal(events[0].timestamp,1.25);
 r.api.subscribeBrowserSensor('gyroscope',v=>events.push(v));r.emit('Gyroscope',1270,[1,2,3]);assert.equal(events[1].z,3);
 r.api.subscribeBrowserSensor('magnetometer',v=>events.push(v));r.emit('Magnetometer',1300,[20,30,40]);assert.equal(events[2].z,40);a.remove();
});
test('Invalid/null axes or nonmonotonic timestamps terminate the browser stream without invented samples',()=>{
 for(const axes of [[null,1,2],[NaN,1,2],[Infinity,1,2]]){
  const r=rig();let count=0,failed=0;r.api.subscribeBrowserSensor('accelerometer',()=>count++,()=>failed++);r.emit('Accelerometer',100,axes);assert.equal(count,0);assert.equal(failed,1);assert.equal(r.instances.Accelerometer.stopped,true);
 }
 const r=rig();let count=0;r.api.subscribeBrowserSensor('gyroscope',()=>count++);r.emit('Gyroscope',100);r.emit('Gyroscope',100);assert.equal(count,1);assert.equal(r.instances.Gyroscope.stopped,true);
});
test('Cancelled check stops all sensors and cannot report readiness',async()=>{
 const r=rig(),controller=new AbortController(),p=r.api.checkBrowserSensors(controller.signal);r.feed();controller.abort();assert.equal((await p).ready,false);assert.ok(Object.values(r.instances).every(s=>s.stopped));
});
test('Browser recorder and every export identify the acquisition path; browser storage retains capture in memory',async()=>{
 const r=rig();r.globals.navigator={userAgent:'test-browser'};
 const {SensorRecorder}=load('sensors',r.globals,{'expo-sensors':{},'react-native':{Platform:{OS:'web',Version:'test'}}});
 const engine=new SensorRecorder({guidanceEnabled:false,voiceEnabled:false},()=>{});engine.connect();engine.begin();r.emit('Accelerometer',100);r.emit('Gyroscope',100);r.emit('Magnetometer',100);r.setTime(200);const recording=engine.stop('user-stopped');
 assert.equal(recording.platform,'web');assert.equal(recording.acquisition.api,'generic-sensor-api-v1');assert.match(recording.timestampBasis,/browser/);assert.equal(recording.streams.accelerometer[0].y,1);
 const session={id:'browser',date:recording.startedAt,isPractice:true,duration:10,windows:[],recording};
 const store=load('store.web'),exports=load('exportData');await store.saveSession(session);assert.equal((await store.getSession('browser')).recording,recording);
 for(const text of [exports.exportJSON(session),exports.exportCSV(session),exports.exportFeatureCSV(session)]){assert.match(text,/generic-sensor-api-v1/);assert.match(text,/browser/)}
 const parsed=load('reviewRecording').parseReviewRecording(exports.exportJSON(session));assert.equal(parsed.recording.platform,'web');
});
