const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
const React=require('react'),{create,act}=require('react-test-renderer');
// Optional evidence replay: native states must come from the separately installed
// Android JNI lab. Only React host controls, speech callbacks and bridge delivery
// are substituted; the fit/profile values are not hand-written fixtures.
if(process.env.GAITTRACE_ANDROID_SETUP_PROOF){
 const directory=path.resolve(process.env.GAITTRACE_ANDROID_SETUP_PROOF);
 const verification=JSON.parse(fs.readFileSync(path.join(directory,'verification.json'),'utf8'));
 assert.equal(verification.kind,'android-jni-setup-proof-suite');
 for(const result of verification.cases)test('Android numerical evidence through actual setup screen: '+result.caseName,async()=>{
  assert.equal(result.kind,'android-production-jni-calibration-control');
  assert.equal(result.syntheticInput,true);
  const raw=fs.readFileSync(path.join(directory,result.caseName,'states.ndjson'));
  assert.equal(require('node:crypto').createHash('sha256').update(raw).digest('hex'),result.statesSha256);
  const states=raw.toString('utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
  const h=await setupHarness({profileForSave:result.savedProfile});let voice=0,cued=false;
  const finishVoices=async()=>{while(voice<h.voices.length){const index=voice++;await act(async()=>h.voices[index].done());}};
  await beginCalibration(h);await finishVoices();assert.equal(h.captures.length,1);
  const first=states[0]?.timestampSeconds??100;
  for(const state of states){
   const elapsed=state.timestampSeconds-first;
   if(!cued&&result.baselineAccepted&&elapsed>=result.fixtureSpecification.quietSeconds){
    cued=true;await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:elapsed,setupTracking:JSON.stringify(state)}));await finishVoices();
   }
   await act(async()=>h.progress({phase:cued?'alignment-move':'alignment-still',elapsedSeconds:elapsed,setupTracking:JSON.stringify(state),setupSettled:false}));
   await finishVoices();assert.ok(h.button('Cancel'),'A slow or missing view must not terminate the screen');
   assert.equal(h.counts().save,0);assert.equal(h.button('Try again'),undefined);
  }
  if(result.accepted){
   await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:result.completionSeconds,setupTracking:JSON.stringify(result.lastState),setupSettled:true}));
   assert.equal(load('phoneSetupGuidance').phoneSetupFeedback(JSON.stringify(result.lastState),true,true).fitReady,true);
   const a=load('onDeviceSetup',{'./cameraCalibration':{calibrationBridge:()=>null},'expo-camera':{}});
   a.validateOnDeviceProfile(result.savedProfile,result.savedProfile.binding);
   await act(async()=>h.captures[0]({metadata:JSON.stringify({captureId:result.savedProfile.sourceCaptureId,status:'completed'})}));
   await finishVoices();assert.equal(h.counts().save,1);assert.equal(h.button('Continue').props.disabled,false);
   await act(async()=>h.button('Continue').props.onPress());assert.equal(h.counts().back,1);
  }else{
   // The fixture ended, not the production capture. Leave it pending until the
   // user explicitly cancels; never manufacture a completion promise.
   assert.ok(h.button('Cancel'));await act(async()=>h.button('Cancel').props.onPress());assert.equal(h.counts().save,0);
  }
  await h.unmount();
 });
}
function load(name,mocks={},cache={}){
 let file=path.resolve(__dirname,'../src',name);if(!fs.existsSync(file))file+=fs.existsSync(file+'.ts')?'.ts':'.tsx';
 if(cache[file])return cache[file].exports;const module={exports:{}};cache[file]=module;
 vm.runInNewContext(ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{esModuleInterop:true,module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React}}).outputText,
 {module,exports:module.exports,console,setTimeout,clearTimeout,Date,Map,Set,require:id=>id in mocks?mocks[id]:id.startsWith('.')?load(path.resolve(path.dirname(file),id),mocks,cache):require(id)});
 return module.exports;
}
// Deliberately synthetic validator fixture, never represented as sensor capture.
function profile(){const binding={installationId:'fixture-phone',cameraId:'1',width:640,height:480,imageAxes:'native-sensor-unrotated-unmirrored',sensorOrientationDegrees:270,stabilizationRequested:'off',capturePipeline:'native-camera-imu-v3',opticalSetup:'waist-bag-window'};
 return {schemaVersion:1,kind:'phone-on-device-camera-imu-profile-v1',method:'openvins-self-calibration-v1',upstreamCommit:'69488123ed9362dd44b6f28e7f4680abbff1442b',computerUsed:false,groundTruthDistanceUsed:false,independentDistanceValidation:false,numericalCalibrationReady:true,stableTailAccepted:true,sourceSha256:'a'.repeat(64),binding,
 fit:{positionStdMetres:.02,initialized:true,integrity:true,numericalCalibrationReady:true,updates:500,cameraValues:[400,400,320,240,0,0,0,0],imuToCamera:[0,0,0,1,0,0,0],calibrationStd:[2,2,1,1,.01,.01,.001,.001,.01,.01,.01,.005,.005,.005,.0005],axisMotionRadians:[1,1,1],timeOffsetSeconds:.04,readoutSeconds:.02}};
}
async function beginPreviewCapture(tree){
 await act(async()=>tree.root.findByType('CameraView').props.onCameraReady());
 await act(async()=>tree.root.findAllByType('Button').find(n=>n.props.label==='Start calibration').props.onPress());
}
async function beginCalibration(h,label='Start phone setup'){
 await act(async()=>h.button(label).props.onPress());await beginPreviewCapture(h.tree);
}
test('Phone profile requires actual convergence contract and matching hardware, without computer or known-distance scale',async()=>{
 const p=profile();let current={...p.binding};const bridge={onDeviceProfile:async()=>JSON.stringify(p),phoneCalibrationInfo:async()=>JSON.stringify(current)};
 const a=load('onDeviceSetup',{'./cameraCalibration':{calibrationBridge:()=>bridge},'expo-camera':{}});
 assert.equal(a.validateOnDeviceProfile(p,p.binding),p);assert.equal((await a.phoneDistanceProfile()).method,p.method);
 for(const change of [p=>p.computerUsed=true,p=>p.groundTruthDistanceUsed=true,p=>p.fit.axisMotionRadians=[0,0,0],p=>p.fit.calibrationStd[0]=-1,p=>p.fit.calibrationStd[14]=.02,p=>p.fit.cameraValues[0]=NaN,p=>p.stableTailAccepted=false,p=>p.fit.updates=1]){
  const q=structuredClone(p);change(q);assert.throws(()=>a.validateOnDeviceProfile(q,p.binding));
 }
 current.cameraId='2';assert.equal(await a.phoneDistanceProfile(),null);
});
test('Actual phone setup screen completes each spoken instruction before capture or motion; saves locally with no transfer',async()=>{
 const node=name=>props=>React.createElement(name,props,props.children);let progress,captureResolve,voiceResolve,captureCount=0,motionCount=0,saveCount=0,back=0;
 const bridge={addListener(_e,fn){progress=fn;return{remove(){}};},captureOnDeviceSetup(){captureCount++;return new Promise(r=>captureResolve=r);},async beginAlignmentMovement(){motionCount++;},async stop(){}};
 const mocks={'react-native':{AppState:{addEventListener(){return{remove(){}};}},BackHandler:{addEventListener(){return{remove(){}};}},ActivityIndicator:node('Spinner'),View:node('View'),Image:node('Image')},'expo-camera':{CameraView:node('CameraView')},'expo-keep-awake':{useKeepAwake(){}},
 '../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../i18n':{Text:node('Text'),t:s=>s},'../components/BigButton':{default:node('Button'),__esModule:true},
 '../audio':{speakQueued(_text,options){return new Promise(r=>voiceResolve=()=>{options.onDone();r();});},stopSpeaking(){}},'../cameraCalibration':{calibrationBridge:()=>bridge},'../onDeviceSetup':{phoneDistanceProfile:async()=>null,phoneSetupPermission:async()=>bridge,completePhoneSetup:async id=>{assert.equal(id,'calibration-123');saveCount++;return profile();}}};
 let tree;await act(async()=>{tree=create(React.createElement(load('screens/PhoneSetupScreen',mocks).default,{navigation:{goBack(){back++;}}}));});
 const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);
 await act(async()=>{button('Start phone setup').props.onPress();});await beginPreviewCapture(tree);assert.equal(captureCount,0);
 await act(async()=>voiceResolve());assert.equal(captureCount,1);
 await act(async()=>progress({phase:'alignment-cue',elapsedSeconds:10}));assert.equal(motionCount,0);
 await act(async()=>voiceResolve());assert.equal(motionCount,1);
 await act(async()=>progress({phase:'alignment-cue',elapsedSeconds:11}));assert.equal(motionCount,1);
 await act(async()=>captureResolve({metadata:JSON.stringify({captureId:'calibration-123',status:'completed'}),error:null}));assert.equal(saveCount,1);
 await act(async()=>voiceResolve());assert.ok(button('Continue'));await act(async()=>button('Continue').props.onPress());assert.equal(back,1);
 await act(async()=>tree.unmount());
});
test('Interrupted phone capture never calls profile saving',async()=>{
 const node=name=>p=>React.createElement(name,p,p.children);let progress,resolve,voice,save=0;
 const b={addListener(_e,fn){progress=fn;return{remove(){}};},captureOnDeviceSetup:()=>new Promise(r=>resolve=r),stop:async()=>{}};
 const mocks={'react-native':{AppState:{addEventListener(){return{remove(){}};}},BackHandler:{addEventListener(){return{remove(){}};}},ActivityIndicator:node('Spinner'),View:node('View'),Image:node('Image')},'expo-camera':{CameraView:node('CameraView')},'expo-keep-awake':{useKeepAwake(){}},'../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../i18n':{Text:node('Text'),t:s=>s},'../components/BigButton':{default:node('Button'),__esModule:true},'../audio':{speakQueued:(_text,options)=>new Promise(r=>voice=()=>{options.onDone();r();}),stopSpeaking(){}},'../cameraCalibration':{calibrationBridge:()=>b},'../onDeviceSetup':{phoneDistanceProfile:async()=>null,phoneSetupPermission:async()=>b,completePhoneSetup:async()=>save++}};
 let tree;await act(async()=>tree=create(React.createElement(load('screens/PhoneSetupScreen',mocks).default,{navigation:{goBack(){}}})));
 await act(async()=>{tree.root.findAllByType('Button').find(n=>n.props.label==='Start phone setup').props.onPress();});await beginPreviewCapture(tree);await act(async()=>voice());
 await act(async()=>resolve({metadata:JSON.stringify({status:'interrupted'}),error:'failed'}));assert.equal(save,0);assert.ok(tree.root.findAllByType('Button').some(n=>n.props.label==='Try again'));await act(async()=>tree.unmount());
});
// Render the actual screen; only the hardware and speech boundaries are substituted.
async function setupHarness({saved=null,deferStop=false,deferPermission=false,failStop=false,profileForSave=null}={}){
 const node=name=>p=>React.createElement(name,p,p.children),voices=[],captures=[];let progress,background,hardwareBack,stopResolve,permissionResolve,save=0,movement=0,back=0,stopCount=0;
 const b={addListener(_e,fn){progress=fn;return{remove(){}};},captureOnDeviceSetup:()=>new Promise(r=>captures.push(r)),beginAlignmentMovement:async()=>movement++,stop:()=>{stopCount++;return failStop?Promise.reject(new Error('native stop failed')):deferStop?new Promise(r=>stopResolve=r):Promise.resolve();}};
 const mocks={'react-native':{AppState:{addEventListener(_e,fn){background=fn;return{remove(){}};}},BackHandler:{addEventListener(_e,fn){hardwareBack=fn;return{remove(){}};}},ActivityIndicator:node('Spinner'),View:node('View'),Image:node('Image')},'expo-camera':{CameraView:node('CameraView')},'expo-keep-awake':{useKeepAwake(){}},'../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../i18n':{Text:node('Text'),t:s=>s},'../components/BigButton':{default:node('Button'),__esModule:true},'../audio':{speakQueued:(text,options)=>new Promise(r=>voices.push({text,done(){options.onDone();r();},fail(){r();}})),stopSpeaking(){}},'../cameraCalibration':{calibrationBridge:()=>b},'../onDeviceSetup':{phoneDistanceProfile:async()=>saved,phoneSetupPermission:()=>deferPermission?new Promise(r=>permissionResolve=()=>r(b)):Promise.resolve(b),completePhoneSetup:async()=>{save++;return profileForSave??profile();}}};
 let tree;await act(async()=>tree=create(React.createElement(load('screens/PhoneSetupScreen',mocks).default,{navigation:{goBack(){back++;}}})));
 return {tree,voices,captures,button:label=>tree.root.findAllByType('Button').find(n=>n.props.label===label),progress:e=>progress(e),background:()=>background('background'),foreground:()=>background('active'),hardwareBack:()=>hardwareBack(),finishStop:()=>stopResolve(),finishPermission:()=>permissionResolve(),counts:()=>({save,movement,back,stopCount}),unmount:()=>act(async()=>tree.unmount())};
}
test('A failed initial spoken cue cannot start camera capture',async()=>{
 const h=await setupHarness();await beginCalibration(h);await act(async()=>h.voices[0].fail());
 assert.equal(h.captures.length,0);assert.ok(h.button('Start calibration'));assert.ok(h.tree.root.findAllByType('Text').some(n=>n.props.children==='The voice instruction could not finish. Check your phone voice and try again.'));await h.unmount();
});
test('A failed movement cue stops capture and never saves or begins movement',async()=>{
 const h=await setupHarness();await beginCalibration(h);await act(async()=>h.voices[0].done());
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:10}));await act(async()=>h.voices[1].fail());
 assert.deepEqual(h.counts(),{save:0,movement:0,back:0,stopCount:1});assert.ok(h.button('Try again'));
 await act(async()=>h.captures[0]({metadata:JSON.stringify({captureId:'old',status:'completed'})}));assert.equal(h.counts().save,0);await h.unmount();
});
test('Interrupted capture waits for native stop, and late completion cannot change the retry',async()=>{
 const h=await setupHarness({deferStop:true});await beginCalibration(h);await act(async()=>h.voices[0].done());
 await act(async()=>h.background());assert.ok(h.button('Stopping phone capture...'));assert.equal(h.button('Try again'),undefined);assert.equal(h.hardwareBack(),true);
 await act(async()=>h.finishStop());await act(async()=>h.foreground());await beginCalibration(h,'Try again');await act(async()=>h.voices[1].done());assert.equal(h.captures.length,2);
 await act(async()=>h.captures[0]({metadata:JSON.stringify({captureId:'old',status:'completed'})}));assert.equal(h.counts().save,0);assert.ok(h.button('Cancel'));
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:10}));await act(async()=>h.voices[2].done());assert.equal(h.counts().movement,1);
 await act(async()=>h.captures[1]({metadata:JSON.stringify({captureId:'new',status:'completed'})}));assert.equal(h.counts().save,1);assert.equal(h.button('Continue').props.disabled,true);
 await act(async()=>h.voices[3].done());assert.equal(h.button('Continue').props.disabled,false);await h.unmount();
});
test('Permission completing after cancellation cannot play an obsolete instruction',async()=>{
 const h=await setupHarness({deferPermission:true});await act(async()=>{h.button('Start phone setup').props.onPress();});await act(async()=>h.hardwareBack());await act(async()=>h.finishPermission());assert.equal(h.voices.length,0);assert.equal(h.captures.length,0);await h.unmount();
});
test('Android permission pause waits for foreground and the complete spoken cue before native capture',async()=>{
 const h=await setupHarness({deferPermission:true});await act(async()=>{h.button('Start phone setup').props.onPress();});
 await act(async()=>h.background());assert.equal(h.counts().stopCount,0);assert.ok(h.button('Cancel'));
 await act(async()=>h.finishPermission());assert.equal(h.voices.length,0);assert.equal(h.captures.length,0);
 await act(async()=>h.foreground());assert.equal(h.voices.length,0);assert.ok(h.button('Start calibration'));await beginPreviewCapture(h.tree);assert.equal(h.voices.length,1);assert.equal(h.captures.length,0);
 await act(async()=>h.voices[0].done());assert.equal(h.captures.length,1);
 // Once permissions are finished, actually leaving the capture still stops it.
 await act(async()=>h.background());assert.equal(h.counts().stopCount,1);assert.ok(h.button('Try again'));await h.unmount();
});
test('Cancellation while awaiting return from the permission dialog prevents capture on resume',async()=>{
 const h=await setupHarness({deferPermission:true});await act(async()=>{h.button('Start phone setup').props.onPress();});await act(async()=>h.background());await act(async()=>h.finishPermission());
 await act(async()=>h.button('Cancel').props.onPress());await act(async()=>h.foreground());assert.equal(h.counts().back,1);assert.equal(h.voices.length,0);assert.equal(h.captures.length,0);await h.unmount();
});
test('Phone setup reuses an existing camera grant and rejects a refused first-use request',async()=>{
 let requests=0,granted=true;
 const bridge={captureOnDeviceSetup(){},completeOnDeviceSetup(){},beginAlignmentMovement(){}};
 const a=load('onDeviceSetup',{'./cameraCalibration':{calibrationBridge:()=>bridge},'expo-camera':{Camera:{getCameraPermissionsAsync:async()=>({granted}),requestCameraPermissionsAsync:async()=>{requests++;return {granted:false};}}}});
 assert.equal(await a.phoneSetupPermission(),bridge);assert.equal(requests,0);
 granted=false;await assert.rejects(a.phoneSetupPermission(),/Camera permission is needed/);assert.equal(requests,1);
});
test('A failed native stop blocks another capture until the app is reopened',async()=>{
 const h=await setupHarness({failStop:true});await beginCalibration(h);await act(async()=>h.voices[0].done());await act(async()=>h.background());
 assert.equal(h.button('Try again').props.disabled,true);await act(async()=>h.button('Try again').props.onPress());assert.equal(h.captures.length,1);assert.equal(h.voices.length,1);await h.unmount();
});
test('A matching saved phone profile is reused without repeating capture',async()=>{
 const h=await setupHarness({saved:profile()});assert.ok(h.button('Set up this phone again'));await act(async()=>h.button('Use saved phone setup').props.onPress());assert.equal(h.counts().back,1);assert.equal(h.captures.length,0);assert.equal(h.voices.length,0);await h.unmount();
});
// Invented numeric contract fixture only; this is not a recorded calibration.
function referenceFixture(){
 const b={...profile().binding,capturePipeline:'native-camera-imu-v2'},camera='/gaittrace/camera',imu='/gaittrace/imu';
 const pairs=(key,value)=>[{key,value}];
 return {schemaVersion:1,kind:'phone-reference-camera-imu-calibration-v1',method:'ikalibr-tro-2025',status:'reference-solved-review-required',sourceSha256:'c'.repeat(64),binding:b,
 cameraImuCandidateReady:false,fullCalibrationReady:false,distanceReady:false,independentDistanceValidation:false,reviewRequired:['Physical accuracy unverified'],
 software:{image:'ulong2/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c',executableSha256:'d'.repeat(64)},
 lensProfile:{method:'opencv-zhang-2000',lensReady:true,binding:b,lens:{model:'opencv-pinhole-radtan5',cameraMatrix:[[400,0,320],[0,400,240],[0,0,1]],distortion:[0,0,0,0,.1]}},
 upstreamParameters:{CalibParam:{EXTRI:{SO3_CmToBr:pairs(camera,{qx:0,qy:0,qz:Math.SQRT1_2,qw:Math.SQRT1_2}),POS_CmInBr:pairs(camera,{r0c0:.02,r1c0:.03,r2c0:.01}),SO3_BiToBr:pairs(imu,{qx:0,qy:0,qz:0,qw:1}),POS_BiInBr:pairs(imu,{r0c0:0,r1c0:0,r2c0:0})},TEMPORAL:{TO_CmToBr:pairs(camera,.002),RS_READOUT:pairs(camera,.03),TO_BiToBr:pairs(imu,0)}}}};
}
test('Saved computer reference reuses matching geometry without claiming self-calibration or clinical validation',async()=>{
 const r=referenceFixture(),binding=profile().binding;
 const module=load('referenceTrackingProfile');const fit=module.referenceTrackingFit(r,binding);
 assert.equal(fit.fixedLensK3,.1);
 assert.ok(Math.abs(fit.imuToCamera[4]+.03)<1e-10);assert.ok(Math.abs(fit.imuToCamera[5]-.02)<1e-10);
 const p={schemaVersion:1,kind:'phone-on-device-camera-imu-profile-v1',method:module.REFERENCE_TRACKING_METHOD,upstreamCommit:profile().upstreamCommit,binding,sourceReference:r,sourceSha256:r.sourceSha256,fit,
 computerUsed:true,groundTruthDistanceUsed:false,independentDistanceValidation:false,numericalCalibrationReady:false,trackingSeedReady:true,geometryConversion:'radtan5-fixed-k3-v2'};
 const b={onDeviceProfile:async()=>null,referenceTrackingProfile:async()=>JSON.stringify(p),phoneCalibrationInfo:async()=>JSON.stringify(binding)};
 const a=load('onDeviceSetup',{'./cameraCalibration':{calibrationBridge:()=>b},'expo-camera':{}});
 assert.equal((await a.phoneDistanceProfile()).method,p.method);assert.equal(a.validateOnDeviceProfile(p,binding),p);
 for(const change of [q=>q.fit.imuToCamera[4]=.2,q=>q.computerUsed=false,q=>q.numericalCalibrationReady=true,q=>q.sourceReference.distanceReady=true,q=>q.sourceReference.binding.cameraId='2',q=>q.sourceReference.lensProfile.binding.width=800,q=>q.sourceReference.software.image='unverified',q=>q.sourceReference.reviewRequired='invalid',q=>q.sourceReference.upstreamParameters.CalibParam.TEMPORAL.TO_BiToBr[0].value='0',q=>q.method=profile().method]){
  const q=structuredClone(p);change(q);assert.throws(()=>a.validateOnDeviceProfile(q,binding));
 }
 for(const change of [q=>q.fit.fixedLensK3=0,q=>delete q.fit.fixedLensK3,q=>q.geometryConversion='radtan5-to-radtan4-k3-omitted-v1']){
  const q=structuredClone(p);change(q);assert.throws(()=>a.validateOnDeviceProfile(q,binding));
 }
 b.onDeviceProfile=async()=>JSON.stringify(profile());assert.equal((await a.phoneDistanceProfile()).method,profile().method);
 b.onDeviceProfile=async()=>JSON.stringify({...profile(),stableTailAccepted:false});assert.equal((await a.phoneDistanceProfile()).method,p.method);
 b.referenceTrackingProfile=async()=>{throw new Error('Missing reference');};assert.equal(await a.phoneDistanceProfile(),null);
});
test('Live result interpolates the saved finish between real adjacent poses, and refuses gaps',()=>{
 const model=load('phoneDistanceModel'),p=profile(),pending={sessionId:'sample',captureId:'gait-camera-sample',protocol:'10mwt',referenceSha256:p.sourceSha256,binding:p.binding};
 const states=Array.from({length:347},(_,i)=>{const t=i/20;return {imu_time_s:t,initialized:1,px:Math.max(0,Math.min(12.2,t-1)),py:0,pz:0,vx:1,vy:0,vz:0,ba_norm:.01,bg_norm:.001,tic_norm:.04,g_norm:9.80665,rotation_change_deg:0,reboot:0,position_std_m:.02};});
 const end=13.025;for(const s of states)s.px=Math.max(0,Math.min(12.1,s.imu_time_s-1.025));const raw={manifest:{...p.binding,sessionId:pending.sessionId,captureId:pending.captureId,protocol:pending.protocol,diagnostics:{walkStartedBootNs:1e9,walkEndedBootNs:end*1e9,tenMetreBoundaries:{version:'ten-metre-boundaries-v1',usable:true,startBootNs:1e9,timedStartBootNs:2.025e9,timedEndBootNs:12.025e9,finishBootNs:end*1e9,origin:[0,0],axis:[1,0]},endBoundarySource:'on-device-estimated-12m-crossing'}},reference:p,states,processingLocation:'phone',processingRevision:'android-openvins-live-v1',captureEndSeconds:17.3,sourceSha256:'b'.repeat(64)};
 const result=model.phoneDistanceResult(raw,pending);assert.ok(Math.abs(result.completeRouteEstimateMetres-12)<1e-8);assert.equal(result.testOutcome.speedMps,1);assert.equal(result.clinicalOutcomeVerified,false);
 const gap={...raw,states:states.filter(s=>s.imu_time_s<12.9||s.imu_time_s>13.2)};assert.equal(model.phoneDistanceResult(gap,pending).reason,'tracking-integrity-failed');
});
test('Every new setup caption and speech cue has Malay and Chinese text',()=>{
 const messages=load('translations').messages,s=fs.readFileSync(path.join(__dirname,'../src/screens/PhoneSetupScreen.tsx'),'utf8');
 for(const m of s.matchAll(/<Body>([^<{]+)<\/Body>|label="([^"{]+)"|(?:speakQueued|sayComplete)\('([^']+)'/g)){const key=m[1]??m[2]??m[3];assert.ok(messages[key],key);for(const v of messages[key]){assert.ok(v.trim());assert.notEqual(v,key);}}
});

test('Setup guidance names missing requirements without treating movement count as a ready fit',()=>{
 const g=load('phoneSetupGuidance');
 for(const raw of [null,'broken','{}'])assert.equal(g.phoneSetupFeedback(raw,false).hint,g.setupViewInstruction);
 const state={initialized:true,integrity:true,axisMotionRadians:[.6,.1,.1],numericalCalibrationReady:false};
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true).hint,g.setupTiltInstruction);
 state.axisMotionRadians=[.6,.6,.1];assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true).hint,g.setupTurnInstruction);
 state.axisMotionRadians=[.6,.6,.6];let f=g.phoneSetupFeedback(JSON.stringify(state),true);assert.equal(f.movementReady,true);assert.equal(f.fitReady,false);assert.equal(f.hint,g.setupFitInstruction);
 state.numericalCalibrationReady=true;assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,false).fitReady,false);
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,true).fitReady,true);
 state.integrity=false;assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,true).fitReady,false);
 for(const angles of [[.6,-1,.6],[.6,null,.6],[.6],[.6,'1',.6]]){state.integrity=true;state.axisMotionRadians=angles;assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,true).movementReady,false);}
 const messages=load('translations').messages;
 for(const value of Object.values(g).filter(v=>typeof v==='string')){assert.equal(messages[value]?.length,2,value);for(const translated of messages[value])assert.ok(translated&&translated!==value);}
 for(const key of [g.setupViewInstruction,g.setupWaitingMessage,g.setupNodInstruction,g.setupTurnInstruction,g.setupFitInstruction,g.setupLostInstruction,'Room tracking','Movement coverage','Stable camera and sensor fit','Live front camera view','Waiting','Complete'])assert.equal(messages[key]?.length,2,key);
});

test('Slow setup and missing direction keep one capture open, with a live view and non-overlapping spoken help',async()=>{
 const h=await setupHarness();await beginCalibration(h);await act(async()=>h.voices[0].done());
 const state={initialized:true,integrity:true,axisMotionRadians:[.6,.6,.1],numericalCalibrationReady:false};
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:130,setupTracking:JSON.stringify(state)}));
 assert.equal(h.counts().movement,0);await act(async()=>h.voices[1].done());assert.equal(h.counts().movement,1);
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:160,setupTracking:JSON.stringify(state),imageUri:'file:/tmp/view.jpg'}));
 assert.equal(h.voices.length,3);assert.match(h.voices[2].text,/steering wheel/);
 assert.equal(h.tree.root.findByType('Image').props.source.uri,'file:///tmp/view.jpg');
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:600,setupTracking:JSON.stringify(state)}));
 assert.equal(h.voices.length,3);assert.equal(h.captures.length,1);assert.equal(h.counts().save,0);assert.ok(h.button('Cancel'));assert.equal(h.button('Try again'),undefined);
 await act(async()=>h.voices[2].done());
 state.axisMotionRadians=[.6,.6,.6];state.numericalCalibrationReady=true;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:601,setupTracking:JSON.stringify(state),setupSettled:true}));
 assert.equal(h.voices.length,4);assert.equal(h.voices[3].text,'Rotation movement complete.');
 await act(async()=>h.captures[0]({metadata:JSON.stringify({captureId:'calibration-123',status:'completed'}),error:null}));
 assert.equal(h.counts().save,0);await act(async()=>h.voices[3].done());assert.equal(h.counts().save,1);await act(async()=>h.voices[4].done());assert.ok(h.button('Continue'));await h.unmount();
});

test('Front-camera beginner setup guides one movement at a time after the previous instruction completes',async()=>{
 const h=await setupHarness(),g=load('phoneSetupGuidance');
 await beginCalibration(h);
 assert.match(h.voices[0].text,/Rest the bagged phone securely/);assert.match(h.voices[0].text,/Keep it still/);
 await act(async()=>h.voices[0].done());
 const s={initialized:true,integrity:true,axisMotionRadians:[0,0,0],numericalCalibrationReady:false};
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:10,setupTracking:JSON.stringify(s)}));
 assert.equal(h.voices[1].text,g.setupMovementInstruction);await act(async()=>h.voices[1].done());
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:11,setupTracking:JSON.stringify(s)}));
 assert.equal(h.voices[2].text,g.setupNodInstruction);
 s.axisMotionRadians[0]=.6;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:15,setupTracking:JSON.stringify(s)}));assert.equal(h.voices.length,3);
 await act(async()=>h.voices[2].done());
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:16,setupTracking:JSON.stringify(s)}));assert.equal(h.voices[3].text,g.setupNodComplete);
 assert.equal(h.voices.length,4);await act(async()=>h.voices[3].done());assert.equal(h.voices[4].text,g.setupTiltInstruction);
 s.axisMotionRadians[1]=.6;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:20,setupTracking:JSON.stringify(s)}));assert.equal(h.voices.length,5);
 await act(async()=>h.voices[4].done());
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:21,setupTracking:JSON.stringify(s)}));assert.equal(h.voices[5].text,g.setupTiltComplete);
 await act(async()=>h.voices[5].done());assert.equal(h.voices[6].text,g.setupTurnInstruction);
 await act(async()=>h.voices[6].done());
 s.axisMotionRadians[2]=.6;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:24,setupTracking:JSON.stringify(s)}));assert.equal(h.voices[7].text,g.setupTurnComplete);
 await act(async()=>h.voices[7].done());assert.equal(h.voices[8].text,g.setupMovementsComplete);
 await act(async()=>h.voices[8].done());assert.equal(h.voices[9].text,g.setupFitInstruction);await act(async()=>h.voices[9].done());await h.unmount();
});


test('Framing preview opens before voice or calibration; failed speech returns to framing without false retained-capture text',async()=>{
 const h=await setupHarness();await act(async()=>h.button('Start phone setup').props.onPress());
 assert.ok(h.tree.root.findByType('CameraView'));assert.equal(h.voices.length,0);assert.equal(h.captures.length,0);assert.equal(h.button('Start calibration').props.disabled,true);
 await beginPreviewCapture(h.tree);await act(async()=>h.voices[0].fail());
 assert.equal(h.captures.length,0);assert.ok(h.tree.root.findByType('CameraView'));
 const body=h.tree.root.findAllByType('Body').map(n=>n.props.children);
 assert.ok(body.includes('Calibration has not been saved.'));assert.ok(!body.includes('This attempt was kept for review.'));assert.ok(!body.includes('Your saved phone setup is still available.'));await h.unmount();
});
test('Voice sample failure stays outside calibration and Back remains available',async()=>{
 const h=await setupHarness();await act(async()=>h.button('Start phone setup').props.onPress());await act(async()=>h.button('Play voice sample').props.onPress());
 assert.equal(h.captures.length,0);assert.ok(h.button('Back'));assert.equal(h.button('Back').props.disabled,undefined);
 await act(async()=>h.voices[0].fail());assert.ok(h.tree.root.findByType('CameraView'));assert.equal(h.captures.length,0);await h.unmount();
});

test('A failed movement confirmation stops safely and cannot save a completed native fit',async()=>{
 const h=await setupHarness(),g=load('phoneSetupGuidance');await beginCalibration(h);await act(async()=>h.voices[0].done());
 const s={initialized:true,integrity:true,axisMotionRadians:[0,0,0],numericalCalibrationReady:false};
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:10,setupTracking:JSON.stringify(s)}));await act(async()=>h.voices[1].done());
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:11,setupTracking:JSON.stringify(s)}));await act(async()=>h.voices[2].done());
 s.axisMotionRadians[0]=.6;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:15,setupTracking:JSON.stringify(s)}));assert.equal(h.voices[3].text,g.setupNodComplete);
 await act(async()=>h.voices[3].fail());assert.ok(h.button('Try again'));assert.equal(h.counts().save,0);
 await act(async()=>h.captures[0]({metadata:JSON.stringify({captureId:'late',status:'completed'}),error:null}));assert.equal(h.counts().save,0);assert.equal(h.button('Continue'),undefined);await h.unmount();
});

test('Native completion during speech still acknowledges the requested movement before saving',async()=>{
 const h=await setupHarness(),g=load('phoneSetupGuidance');await beginCalibration(h);await act(async()=>h.voices[0].done());
 const s={initialized:true,integrity:true,axisMotionRadians:[.6,.6,0],numericalCalibrationReady:false};
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:10,setupTracking:JSON.stringify(s)}));await act(async()=>h.voices[1].done());
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:11,setupTracking:JSON.stringify(s)}));assert.equal(h.voices[2].text,g.setupTurnInstruction);
 s.axisMotionRadians[2]=.6;s.numericalCalibrationReady=true;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:20,setupTracking:JSON.stringify(s),setupSettled:true}));assert.equal(h.voices.length,3);
 await act(async()=>h.captures[0]({metadata:JSON.stringify({captureId:'calibration-123',status:'completed'}),error:null}));assert.equal(h.counts().save,0);
 await act(async()=>h.voices[2].done());assert.equal(h.voices[3].text,g.setupTurnComplete);assert.equal(h.counts().save,0);
 await act(async()=>h.voices[3].done());assert.equal(h.counts().save,1);await act(async()=>h.voices[4].done());await h.unmount();
});

test('Guidance maps screen edges to measured sensor axes for portrait and naturally landscape devices',()=>{
 const g=load('phoneSetupGuidance');
 for(const rotation of [0,90,180,270]){
  const top=rotation===90||rotation===270?1:0,side=1-top;
  const state={initialized:true,integrity:true,displayRotationDegrees:rotation,axisMotionRadians:[0,0,0]};
  assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true).hint,g.setupNodInstruction);
  // Rotating the other edge cannot fulfil the requested top-edge movement.
  state.axisMotionRadians[side]=.6;assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true).hint,g.setupNodInstruction);
  state.axisMotionRadians[side]=0;state.axisMotionRadians[top]=.6;
  assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true).hint,g.setupTiltInstruction);
  state.axisMotionRadians[side]=.6;assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true).hint,g.setupTurnInstruction);
 }
});


test('Final-check guidance identifies measured uncertainty, required time and stable-tail waiting separately',()=>{
 const g=load('phoneSetupGuidance');
 const state={initialized:true,integrity:true,axisMotionRadians:[1,1,1],numericalCalibrationReady:false,positionStdMetres:.05,cameraValues:[400,400,320,240,0,0,0,0],calibrationStd:Array(15).fill(.001)};
 const feedback=()=>g.phoneSetupFeedback(JSON.stringify(state),true,false);
 state.calibrationStd[2]=8;assert.equal(feedback().hint,g.setupOpticsInstruction);
 state.calibrationStd[2]=.001;state.calibrationStd[11]=.03;assert.equal(feedback().hint,g.setupAlignmentInstruction);
 state.calibrationStd[11]=.001;state.calibrationStd[14]=.01;assert.equal(feedback().hint,g.setupTimingInstruction);
 state.calibrationStd[14]=.001;state.positionStdMetres=.2;assert.equal(feedback().hint,g.setupPositionInstruction);
 state.positionStdMetres=.05;state.numericalCalibrationReady=true;
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,false,12000).hint,g.setupDurationInstruction);
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,false,0).hint,g.setupStableInstruction);
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,false,0).fitReady,false);
});

test('Stuck final check announces coverage once, names the changing blocker and never saves from elapsed time',async()=>{
 const h=await setupHarness(),g=load('phoneSetupGuidance');await beginCalibration(h);await act(async()=>h.voices[0].done());
 const state={initialized:true,integrity:true,axisMotionRadians:[1,1,1],numericalCalibrationReady:false,positionStdMetres:.05,cameraValues:[400,400,320,240,0,0,0,0],calibrationStd:Array(15).fill(.001)};
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:10,setupTracking:JSON.stringify(state)}));await act(async()=>h.voices[1].done());
 state.calibrationStd[11]=.03;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:12,setupTracking:JSON.stringify(state)}));assert.equal(h.voices[2].text,g.setupMovementsComplete);await act(async()=>h.voices[2].done());assert.equal(h.voices[3].text,g.setupAlignmentInstruction);await act(async()=>h.voices[3].done());
 let finished=4;
 for(const elapsed of [20,40,75,140,300]){
  await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:elapsed,setupTracking:JSON.stringify(state)}));
  while(finished<h.voices.length){const i=finished++;await act(async()=>h.voices[i].done());}
 }
 assert.equal(h.voices.filter(v=>v.text===g.setupMovementsComplete).length,1);assert.equal(h.voices.filter(v=>v.text===g.setupLongWaitInstruction).length,1);assert.equal(h.counts().save,0);assert.equal(h.captures.length,1);assert.ok(h.button('Cancel'));
 state.calibrationStd[11]=.001;state.calibrationStd[14]=.01;
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:310,setupTracking:JSON.stringify(state)}));assert.equal(h.voices.at(-1).text,g.setupTimingInstruction);
 await act(async()=>h.voices.at(-1).done());assert.equal(h.counts().save,0);await h.unmount();
});


test('Stable numerical fit does not display final completion before native movement duration ends',()=>{
 const g=load('phoneSetupGuidance'),state={initialized:true,integrity:true,axisMotionRadians:[1,1,1],numericalCalibrationReady:true};
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,true,12000).fitReady,false);
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,true,12000).hint,g.setupDurationInstruction);
 assert.equal(g.phoneSetupFeedback(JSON.stringify(state),true,true,0).fitReady,true);
});

test('Native completion during a confirmation suppresses obsolete final-check coaching before saving',async()=>{
 const h=await setupHarness(),g=load('phoneSetupGuidance');await beginCalibration(h);await act(async()=>h.voices[0].done());
 const state={initialized:true,integrity:true,axisMotionRadians:[1,1,1],numericalCalibrationReady:false};
 await act(async()=>h.progress({phase:'alignment-cue',elapsedSeconds:10,setupTracking:JSON.stringify(state)}));await act(async()=>h.voices[1].done());
 await act(async()=>h.progress({phase:'alignment-move',elapsedSeconds:12,setupTracking:JSON.stringify(state)}));assert.equal(h.voices[2].text,g.setupMovementsComplete);
 await act(async()=>h.captures[0]({metadata:JSON.stringify({captureId:'calibration-123',status:'completed'}),error:null}));assert.equal(h.counts().save,0);
 await act(async()=>h.voices[2].done());assert.equal(h.counts().save,1);assert.match(h.voices[3].text,/Phone setup saved/);assert.equal(h.voices.some(v=>v.text===g.setupFitInstruction),false);
 await act(async()=>h.voices[3].done());await h.unmount();
});


test('Final check reports actual native frame-delay and changing-fit blockers instead of asking for larger motions',()=>{
 const g=load('phoneSetupGuidance'),state={initialized:true,integrity:true,axisMotionRadians:[1,1,1],numericalCalibrationReady:true};
 const check=reason=>g.phoneSetupFeedback(JSON.stringify(state),true,false,0,JSON.stringify({reason}));
 assert.equal(check('stale').hint,g.setupDelayedInstruction);assert.equal(check('slow-frames').hint,g.setupSlowFramesInstruction);assert.equal(check('fit-changing').hint,g.setupChangingInstruction);
 for(const reason of ['stale','slow-frames','fit-changing'])assert.equal(check(reason).fitReady,false);
});
