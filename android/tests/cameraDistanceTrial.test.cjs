const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
function api(storage={}){const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(__dirname,'../src/cameraDistanceTrial.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,{module,exports:module.exports,require:id=>id==='react-native'?{Platform:{OS:'web'}}:storage});return module.exports;}
function fixture(){const binding={installationId:'phone-one',captureId:'calibration-123',cameraId:'1',width:640,height:480,imageAxes:'native-sensor-unrotated-unmirrored',sensorOrientationDegrees:270,stabilizationRequested:'off'};return {capture:{metadata:JSON.stringify({...binding,status:'completed'})},profile:{schemaVersion:1,kind:'phone-camera-distance-research-profile-v1',binding,lens:{cameraMatrix:[[500,0,320],[0,500,240],[0,0,1]],distortion:[0,0,0,0,0],heldOutP90Pixels:.2},rotationTiming:{passed:true,rotationImuToCamera:[[1,0,0],[0,1,0],[0,0,1]],residualTimeOffsetSeconds:-.03,gyroBiasRadS:[0,0,0]},distanceReady:false,fullCalibrationReady:false,independentDistanceValidation:false}};}
test('A rotation-only research profile never becomes full clinical calibration',()=>{const {profile,capture}=fixture();assert.equal(api().validateDistanceResearchProfile(profile,capture).fullCalibrationReady,false);assert.equal(api().distanceBridge(),null);});
test('New pipeline optics binding and blocked metric state cannot be bypassed by old distance fields',()=>{
 const {profile,capture}=fixture();capture.metadata=JSON.stringify({...JSON.parse(capture.metadata),capturePipeline:'native-camera-imu-v2',opticalSetup:'waist-bag-window'});
 assert.throws(()=>api().validateDistanceResearchProfile(profile,capture));Object.assign(profile.binding,{capturePipeline:'native-camera-imu-v2',opticalSetup:'waist-bag-window'});assert.equal(api().validateDistanceResearchProfile(profile,capture),profile);
 const metadata={status:'quiet-stop',diagnostics:{status:'experimental-estimate',distanceReady:false,independentDistanceValidation:false,placementCompleted:true,experimentalHorizontalCameraPathMetres:3,metricReadiness:{status:'blocked'}}};
 assert.equal(api().distanceTrialSummary({metadata:JSON.stringify(metadata)}).metres,null);
});
test('Research profile rejects wrong phone, bad geometry, reflection and claimed readiness',()=>{
 for(const mutate of [p=>p.binding.installationId='other',p=>p.binding.width=800,p=>p.fullCalibrationReady=true,p=>p.distanceReady=true,p=>p.rotationTiming.passed=false,p=>p.rotationTiming.rotationImuToCamera[0][0]=-1,p=>p.lens.distortion=[NaN],p=>p.rotationTiming.residualTimeOffsetSeconds=1,p=>p.rotationTiming.gyroBiasRadS=['0',0,0]]){
  const {profile,capture}=fixture();mutate(profile);assert.throws(()=>api().validateDistanceResearchProfile(profile,capture));
 }
});
test('Interrupted or failed trials cannot display a metric result, even with a forged distance field',()=>{
 const metadata={status:'quiet-stop',diagnostics:{status:'experimental-estimate',distanceReady:false,independentDistanceValidation:false,placementCompleted:true,experimentalHorizontalCameraPathMetres:3.1}};
 const a=api();assert.equal(a.distanceTrialSummary({metadata:JSON.stringify(metadata)}).metres,3.1);
 for(const status of ['interrupted','user-stopped','error'])assert.equal(a.distanceTrialSummary({metadata:JSON.stringify({...metadata,status})}).available,false);
 for(const mutate of [d=>d.status='rejected',d=>d.distanceReady=true,d=>d.independentDistanceValidation=true,d=>d.placementCompleted=false,d=>d.experimentalHorizontalCameraPathMetres=-2]){
  const v=JSON.parse(JSON.stringify(metadata));mutate(v.diagnostics);assert.equal(a.distanceTrialSummary({metadata:JSON.stringify(v)}).available,false);
 }
});
test('Native ZIP aliases persist without self-copy, and recovery retains interrupted status',async()=>{
 const root='file:///data/files/camera-distance-trials/',files=new Map(),copies=[];const canonical=p=>p.replace(/^file:\/+/, '/');
 const meta={kind:'front-camera-distance-research-v1',captureId:'distance-trial-123',distanceReady:false,status:'interrupted',error:'Camera disconnected'};
 files.set(canonical(root+'distance-trial-123.zip'),'zip');files.set(canonical(root+'distance-trial-123/manifest.json'),JSON.stringify(meta));
 const storage={documentDirectory:'file:///data/files/',makeDirectoryAsync:async()=>{},getInfoAsync:async p=>p===root?{exists:true,isDirectory:true}:files.has(canonical(p))?{exists:true,isDirectory:false,size:files.get(canonical(p)).length}:{exists:false},readAsStringAsync:async p=>{if(!files.has(canonical(p)))throw Error('missing');return files.get(canonical(p));},writeAsStringAsync:async(p,v)=>files.set(canonical(p),v),readDirectoryAsync:async()=>['distance-trial-123.zip'],copyAsync:async v=>copies.push(v)};
 const a=api(storage),saved=await a.retainDistanceTrial({uri:(root+'distance-trial-123.zip').replace('file:///','file:/'),metadata:JSON.stringify(meta),error:meta.error});
 assert.equal(saved.uri,root+'distance-trial-123.zip');assert.equal(copies.length,0);const recovered=await a.latestDistanceTrial();assert.equal(JSON.parse(recovered.metadata).status,'interrupted');
});
const React=require('react'),renderer=require('react-test-renderer'),flush=()=>new Promise(r=>setImmediate(r));
function screenFixture(withProfile=true){
 const spoken=[],calls=[],events={},native={captureDistance:async()=>{calls.push('capture');return await new Promise(r=>native.resolve=r);},beginDistance:async()=>calls.push('begin'),stop:async()=>calls.push('stop'),addListener:(_,fn)=>{events.progress=fn;return {remove(){}};}};
 const component=p=>React.createElement('Body',{},p.children),mocks={react:React,'react-native':{AppState:{addEventListener:(_,fn)=>{events.app=fn;return {remove(){}};}},BackHandler:{addEventListener:()=>({remove(){}})},Image:'Image',View:'View'},'expo-camera':{useCameraPermissions:()=>[{granted:true},async()=>({granted:true})]},'expo-keep-awake':{useKeepAwake(){}},'expo-document-picker':{},'expo-file-system':{},'expo-sharing':{},'../components/Screen':{Screen:p=>React.createElement('Screen',{},p.children,p.actions),Body:component,ui:{}},'../components/BigButton':p=>React.createElement('Button',p),'../i18n':{Text:component,t:s=>s},'../audio':{speakQueued:(s,o)=>{spoken.push({s,o});return Promise.resolve();},stopSpeaking:()=>{for(const v of spoken)if(!v.done){v.done=true;v.o.onStopped?.();}}},'../releaseInfo':{releaseInfo:()=>({appVersion:'0.3.3',buildNumber:'10',runtimeVersion:'fixture-only',updateId:null})},'../cameraCalibration':{latestCalibrationCapture:async()=>null},'../cameraDistanceTrial':{distanceBridge:()=>native,loadDistanceResearchProfile:async()=>withProfile?fixture().profile:null,latestDistanceTrial:async()=>null,distanceTrialSummary:()=>null,retainDistanceTrial:async s=>s}};
 const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(__dirname,'../src/screens/CameraDistanceTrialScreen.tsx'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true}}).outputText,{module,exports:module.exports,require:id=>mocks[id],console});
 let tree;renderer.act(()=>tree=renderer.create(React.createElement(module.exports.default,{navigation:{goBack(){}}})));
 return {tree,spoken,calls,events,native,finishVoice(index){spoken[index].done=true;spoken[index].o.onDone();},start(){const start=tree.root.findAllByType('Button').find(v=>v.props.label==='Start camera distance trial');renderer.act(()=>start.props.onPress());}};
}
test('Native trial starts only after prep speech; begin waits for the complete cue and repeated progress cannot duplicate it',async()=>{
 const f=screenFixture();await renderer.act(async()=>await flush());f.start();await renderer.act(async()=>await flush());assert.equal(f.calls.length,0);
 await renderer.act(async()=>{f.finishVoice(0);await flush();});assert.deepEqual(f.calls,['capture']);
 await renderer.act(async()=>{f.events.progress({phase:'cue',imageUri:'file:///frame.jpg'});f.events.progress({phase:'cue',imageUri:'file:///frame.jpg'});await flush();});
 assert.equal(f.spoken.length,2);assert.equal(f.calls.includes('begin'),false);
 await renderer.act(async()=>{f.finishVoice(1);await flush();});assert.deepEqual(f.calls,['capture','begin']);renderer.act(()=>f.tree.unmount());
});
test('Backgrounding during preparation cannot start native capture after cancelled speech',async()=>{
 const f=screenFixture();await renderer.act(async()=>await flush());f.start();await renderer.act(async()=>await flush());
 await renderer.act(async()=>{f.events.app('background');await flush();});assert.equal(f.calls.includes('capture'),false);assert.equal(f.calls.includes('stop'),true);renderer.act(()=>f.tree.unmount());
});
test('Normal completion saves the capture and waits for the finish voice before re-enabling Start',async()=>{
 const f=screenFixture();await renderer.act(async()=>await flush());f.start();await renderer.act(async()=>await flush());
 await renderer.act(async()=>{f.finishVoice(0);await flush();});
 await renderer.act(async()=>{f.events.progress({phase:'cue',imageUri:'file:///frame.jpg'});await flush();});
 await renderer.act(async()=>{f.finishVoice(1);await flush();});
 await renderer.act(async()=>{f.native.resolve({uri:'file:///native/distance-trial-123.zip',metadata:JSON.stringify({captureId:'distance-trial-123',kind:'front-camera-distance-research-v1',distanceReady:false}),error:null});await flush();});
 assert.equal(f.spoken.length,3);assert.equal(f.spoken[2].s,'Finished. You can take the phone out.');
 assert.equal(f.tree.root.findAllByType('Button').some(v=>v.props.label==='Start camera distance trial'),false);
 await renderer.act(async()=>{f.finishVoice(2);await flush();});
 assert.equal(f.tree.root.findAllByType('Button').some(v=>v.props.label==='Start camera distance trial'),true);
 assert.equal(f.tree.root.findAllByType('Button').some(v=>v.props.label==='Export distance trial'),true);renderer.act(()=>f.tree.unmount());
});

test('Missing research profile presents import first and cannot initiate distance capture',async()=>{
 const f=screenFixture(false);await renderer.act(async()=>await flush());
 assert.equal(f.tree.root.findAllByType('Button').some(v=>v.props.label==='Start camera distance trial'),false);
 assert.equal(f.tree.root.findAllByType('Button').some(v=>v.props.label==='Import phone research profile'),true);
 assert.equal(f.spoken.length,0);assert.equal(f.calls.length,0);renderer.act(()=>f.tree.unmount());
});
