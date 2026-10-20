const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
function load(name,mocks){const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(__dirname,'../src',name),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true}}).outputText,{module,exports:module.exports,require:id=>mocks[id],console,setTimeout,clearTimeout,AbortController,URL});return module.exports;}
function fixture(){
 const root='file:///app/camera-calibration/',files=new Map(),store={documentDirectory:'file:///app/',makeDirectoryAsync:async()=>{},writeAsStringAsync:async(p,v)=>files.set(p,v),readAsStringAsync:async p=>{if(!files.has(p))throw Error('missing');return files.get(p);},getInfoAsync:async p=>({exists:files.has(p),isDirectory:false,size:files.get(p)?.length??0}),deleteAsync:async p=>files.delete(p),moveAsync:async({from,to})=>{if(store.failMove)throw Error('disk error');files.set(to,files.get(from));files.delete(from);}};
 const camera=load('cameraCalibration.ts',{'react-native':{Platform:{OS:'web'}},'expo-file-system':store}),reference=load('referenceCalibration.ts',{'expo-file-system':store});
 const api=load('rapidCalibration.ts',{'expo-file-system':store,'./cameraCalibration':camera,'./referenceCalibration':reference,'./distanceValidation':{researchRequest:async()=>({status:'completed',result})}});
 const binding={installationId:'test',captureId:'calibration-123',cameraId:'1',width:640,height:480,imageAxes:'native-sensor-unrotated-unmirrored',sensorOrientationDegrees:270,stabilizationRequested:'off',capturePipeline:'native-camera-imu-v2',opticalSetup:'waist-bag-window'};
 const item=(key,value)=>[{key,value}],topic='/gaittrace/camera',imu='/gaittrace/imu';
 const geometry={EXTRI:{SO3_CmToBr:item(topic,{qx:0,qy:0,qz:0,qw:1}),POS_CmInBr:item(topic,{r0c0:0,r1c0:0,r2c0:0}),SO3_BiToBr:item(imu,{qx:0,qy:0,qz:0,qw:1}),POS_BiInBr:item(imu,{r0c0:0,r1c0:0,r2c0:0})},TEMPORAL:{TO_CmToBr:item(topic,0),TO_BiToBr:item(imu,0),RS_READOUT:item(topic,.03)}};
 const seed={schemaVersion:1,kind:'phone-learned-lens-seed-v1',method:'geocalib-eccv2024-seed',binding,lensReady:false,calibrationSeedReady:true,distanceReady:false,fullCalibrationReady:false,independentDistanceValidation:false,
  lens:{model:'opencv-pinhole-radtan5',cameraMatrix:[[500,0,320],[0,500,240],[0,0,1]],distortion:[.05,0,0,0,0]},learned:{sourceCommit:'97b8968e7798a66bf04fcf791fb535624241bda7',checkpointSha256:'13cc505928e3ff4eb26c00bff73861ab2b11b804a546323456cf5462e1f8f447',qualityAccepted:true,neuralWeightsUpdated:false,supportViews:5,queryViews:5,disjointViews:true,viewConsistencyFraction:.03,fullLensValidated:false,internalUncertaintyValidated:false}};
 const result={schemaVersion:1,kind:'phone-reference-camera-imu-calibration-v1',method:'ikalibr-tro-2025',status:'reference-solved-review-required',cameraImuCandidateReady:false,fullCalibrationReady:false,distanceReady:false,independentDistanceValidation:false,binding,lensProfile:seed,sourceSha256:'1'.repeat(64),reviewRequired:['physical-test'],upstreamParameters:{CalibParam:geometry},software:{image:'ulong2/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c',executableSha256:'2'.repeat(64)},enrollment:{method:api.RAPID_REVISION,experimental:true,neuralWeightsUpdated:false,shortScanGuaranteed:false,computerUsedOnce:true,ordinaryTestsRunOnPhone:true},trainingExample:{kind:'few-shot-camera-calibration-example-v1',sourceSha256:'1'.repeat(64),independentValidation:false,labelSource:'ikalibr-candidate-not-independent-truth'}};
 geometry.INTRI={Camera:item(topic,{ptr_wrapper:{data:{focal_length:[501,499],principal_point:[321,242],disto_param:[.05,.02,.01,.001,.002],img_width:640,img_height:480}}})};
 result.enrollment.refinedLensCandidate={...api.rapidRefinedLens(geometry),origin:'ikalibr-refined-candidate',independentLensValidation:false};
 return {api,camera,reference,result,binding,files,root,store};
}
test('Learned seed import preserves experimental status and rejects false evidence or mismatched optics',()=>{
 const f=fixture();assert.equal(f.api.validateRapidResult(f.result,f.binding).lensProfile.lensReady,false);
 for(const change of [r=>r.lensProfile.lensReady=true,r=>r.lensProfile.learned.viewConsistencyFraction=.09,r=>r.lensProfile.learned.checkpointSha256='0'.repeat(64),r=>r.binding.opticalSetup='clear-lens',r=>r.enrollment.neuralWeightsUpdated=true,r=>r.trainingExample.sourceSha256='0'.repeat(64),r=>r.upstreamParameters.CalibParam.TEMPORAL.RS_READOUT[0].value=.2]){const v=fixture();const binding=structuredClone(v.binding);change(v.result);assert.throws(()=>v.api.validateRapidResult(v.result,binding));}
});
test('Completed processing saves a review candidate; using it is explicit and failed replacement keeps earlier profiles',async()=>{
 const f=fixture(),computer={};f.files.set(f.root+'pending-rapid.json',JSON.stringify({id:'1'.repeat(24),binding:f.binding}));f.files.set(f.root+'reference.json','previous board reference');f.files.set(f.root+'lens.json','previous board lens');
 await f.api.pollRapid(computer,()=>false);assert.equal(f.files.has(f.root+'rapid-result.json'),true);assert.equal(f.files.has(f.root+'rapid-profile.json'),false);
 await f.api.activateRapid(f.result,f.binding);assert.equal(JSON.parse(f.files.get(f.root+'rapid-profile.json')).sourceSha256,f.result.sourceSha256);assert.equal(f.files.get(f.root+'reference.json'),'previous board reference');
 const before=f.files.get(f.root+'rapid-profile.json');f.store.failMove=true;await assert.rejects(f.api.activateRapid(f.result,f.binding),/disk error/);assert.equal(f.files.get(f.root+'rapid-profile.json'),before);
});
test('Actual profile selection links learned camera and full reference without granting distance readiness',async()=>{
 const f=fixture();f.files.set(f.root+'rapid-profile.json',JSON.stringify(f.result));f.files.set(f.root+'reference.json',JSON.stringify({...f.result,lensProfile:{binding:{...f.binding,captureId:'older'}}}));
 const lens=await f.camera.currentLensReport(f.binding);assert.equal(lens.kind,'phone-learned-lens-seed-v1');assert.equal((await f.reference.savedReference(lens)).sourceSha256,f.result.sourceSha256);assert.equal(await f.camera.currentLensReport({...f.binding,cameraId:'2'}),null);
});
test('Canceled result delivery cannot activate or overwrite a profile',async()=>{
 const f=fixture();f.files.set(f.root+'pending-rapid.json',JSON.stringify({id:'1'.repeat(24),binding:f.binding}));assert.equal(await f.api.pollRapid({},()=>true),null);assert.equal(f.files.has(f.root+'rapid-result.json'),false);assert.equal(f.files.has(f.root+'pending-rapid.json'),true);
});
test('Every new visible enrollment sentence and voice cue has Malay and Chinese translations',()=>{
 const messages=load('rapidMessages.ts',{}).rapidMessages,screen=fs.readFileSync(path.join(__dirname,'../src/screens/RapidCalibrationScreen.tsx'),'utf8');
 for(const key of ['Quick phone setup','Use experimental profile','Stillness captured. Now move the bagged phone in small loops. Tilt left, right, up and down. Keep furniture in view.','Capture checked. An experimental phone profile is ready.','Capture incomplete. Your previous profile is kept.']){assert.ok(messages[key]);assert.ok(messages[key].every(v=>v.length>0));}
 assert.ok(screen.includes('onDone:()=>{completed=true;}'));assert.ok(screen.includes('beginAlignmentMovement'));
});
test('App enrollment flow waits for full voice completion before motion, then transfers, reviews and explicitly selects the profile',async()=>{
 const React=require('react'),{act,create}=require('react-test-renderer'),node=name=>p=>React.createElement(name,p,p.children);let listener,resolveCapture,releaseVoice;const events=[];
 const bridge={addListener:(name,callback)=>{listener=callback;return{remove(){}};},stop:async()=>{},captureRapidCalibration:()=>new Promise(r=>resolveCapture=r),beginAlignmentMovement:async()=>events.push('motion-start'),phoneCalibrationInfo:async()=>JSON.stringify({})};
 const mocks={react:React,'react-native':{AppState:{addEventListener:()=>({remove(){}})},BackHandler:{addEventListener:()=>({remove(){}})},Image:'Image',Modal:'Modal',Pressable:'Pressable',View:'View'},'expo-camera':{useCameraPermissions:()=>[{granted:true}],CameraView:node('CameraView')},'expo-keep-awake':{useKeepAwake(){}},'expo-sharing':{},'../components/Screen':{Screen:p=>React.createElement('Screen',{},p.children,p.actions),Body:node('Body'),ui:{}},'../components/BigButton':node('Button'),'../i18n':{Text:node('Text'),t:s=>s},
  '../audio':{stopSpeaking(){},speakQueued:async(text,options)=>{events.push(text);if(text.startsWith('Stillness captured'))await new Promise(r=>releaseVoice=r);options.onDone();}},
  '../cameraCalibration':{calibrationBridge:()=>bridge,retainCalibrationCapture:async c=>c},'../referenceCalibration':{calibrationComputer:async()=>({}),createLensFeedback:()=>({send(){},close(){}})},
  '../rapidCalibration':{latestRapid:async()=>null,pendingRapid:async()=>null,savedRapidResult:async()=>null,rapidReady:async()=>{},submitRapid:async()=>events.push('upload'),pollRapid:async()=>({binding:{}}),activateRapid:async()=>events.push('selected')}};
 const Screen=load('screens/RapidCalibrationScreen.tsx',mocks).default;let tree;await act(async()=>tree=create(React.createElement(Screen,{navigation:{goBack(){}}})));
 const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);await act(async()=>button('Capture scene and sensors').props.onPress());
 assert.equal(typeof resolveCapture,'function');await act(async()=>listener({phase:'alignment-cue',imageUri:'file:///preview'}));assert.equal(events.includes('motion-start'),false);
 await act(async()=>releaseVoice());assert.equal(events.includes('motion-start'),true);
 await act(async()=>{resolveCapture({uri:'file:///capture.zip',metadata:JSON.stringify({status:'completed'}),error:null});});
 assert.ok(events.indexOf('upload')>events.indexOf('Capture finished. You can put the phone down while your computer checks it.'));assert.equal(events.includes('selected'),false);
 await act(async()=>button('Use experimental profile').props.onPress());assert.equal(events.includes('selected'),true);act(()=>tree.unmount());
});
