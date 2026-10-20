const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const React = require('react');
const { create, act } = require('react-test-renderer');
function load(name, mocks = {}, globals = {}, cache = {}) {
  mocks={'../gaitDistance':{gaitDistanceBridge:()=>null,prepareGaitDistance:async()=>{},processGaitDistance:async()=>{}},...mocks};
  let file = path.resolve(__dirname, '../src', name);
  if (!fs.existsSync(file)) file += fs.existsSync(file + '.ts') ? '.ts' : '.tsx';
  if (cache[file]) return cache[file].exports;
  const module = { exports: {} }; cache[file] = module;
  const code = ts.transpileModule(fs.readFileSync(file,'utf8'), { compilerOptions: { esModuleInterop:true, target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React } }).outputText;
  vm.runInNewContext(code,{module,exports:module.exports,console,Date,Math,performance,setTimeout,clearTimeout,
    require:id => id in mocks ? mocks[id] : id.startsWith('.') ? load(path.resolve(path.dirname(file),id),mocks,globals,cache) : require(id), ...globals },{filename:file});
  return module.exports;
}
test('All three languages preserve dynamic times, sensor notes and captions', () => {
 const l=load('language');
 const input='10 sec quiet / possible rest · 2 sec combined movement · 0 sec possible handling · 3 sec uncertain';
 assert.equal(l.translate(input,'en'),input);
 assert.equal(l.translate(input,'zh'),'10秒安静／可能休息 · 2秒综合动作 · 0秒疑似手机操作 · 3秒不确定');
 assert.match(l.translate(input,'ms'),/10 saat/);
 assert.equal(l.translate('Showing 0–5.0 seconds after recording started','zh'),'显示记录开始后0–5.0秒');
 assert.equal(l.translate('magnetometer: sampling was slower than requested.','zh'),'磁力计：采样频率低于请求值。');
 assert.equal(l.translate('827 readings · 81.7 Hz observed · g','zh'),'827条读数 · 实测81.7 Hz · g');
 assert.equal(l.translate('Accelerometer · X / Y / Z','zh'),'加速度计 · X / Y / Z');
});
test('Translation catalog retains every placeholder and includes each active static speech cue', () => {
 const {messages}=load('translations');
 assert.ok(messages['For a standardized 6MWT, switch off both Voice Guidance and Direction Reminders during the walk. A worker should give only the standard timed messages.']);
 for(const [key,values] of Object.entries(messages)) for(const value of values) {
  assert.ok(value.trim(),key);assert.deepEqual((value.match(/\{\d+\}/g)||[]).sort(),(key.match(/\{\d+\}/g)||[]).sort(),key);
 }
 const file=fs.readFileSync(path.resolve(__dirname,'../src/screens/RecordScreen.tsx'),'utf8');
 for(const match of file.matchAll(/say\('([^']+)'\)/g)) assert.ok(messages[match[1]],match[1]);
});
test('All actual tutorial and worker-guide text has Malay and Chinese translations', () => {
 const {messages}=load('translations');const {protocolGuides}=load('protocolGuides');const {protocolTutorials}=load('protocolTutorials');
 for(const [protocol,guide] of Object.entries(protocolGuides)) {
  for(const text of [guide.title,guide.short,guide.body,guide.extra].filter(Boolean))assert.ok(messages[text],`${protocol}: ${text}`);
  assert.equal(protocolTutorials[protocol].length,3);
  for(const step of protocolTutorials[protocol])for(const text of [step.title,step.text]) {
   assert.ok(messages[text],text);for(const value of messages[text])assert.ok(value.trim(),text);
   assert.ok(step.text.split(/\s+/).length<=35,'Patient steps must remain brief');
  }
 }
});

test('Camera trial prompts and speech have complete Malay/Chinese catalog entries',()=>{
 const {messages}=load('translations'),c=load('cameraTrial');
 for(const cue of [c.cameraPlacementCue,c.cameraWalkCue,c.cameraFinishCue])assert.ok(messages[cue],cue);
 for(const file of ['screens/CameraIMUTrialScreen.tsx','components/CameraTrialReview.tsx']){
  const s=fs.readFileSync(path.resolve(__dirname,'../src',file),'utf8');
  for(const match of s.matchAll(/<Body>([^<{]+)<\/Body>|label="([^"{]+)"/g)){
   const text=match[1]??match[2];if(!messages[text])assert.equal(text,'Retry save',text);
  }
 }
 for(const [key,values] of Object.entries(load('cameraMessages').cameraMessages)){
  for(const value of values){assert.ok(value.trim());assert.ok(!/\?\?\?/.test(value),key);}
 }
});

test('Guided calibration waits for spoken instructions, selects real native views, and transfers alignment automatically',async()=>{
 const node=name=>props=>React.createElement(name,props,props.children);let progress,resolveLens,resolveAlignment,voice,begin=0,uploads=0;
 const voices=[];const computer={url:'http://192.168.1.2:8765',token:'x'};
 const bridge={addListener(_n,fn){progress=fn;return{remove(){}};},async phoneCalibrationInfo(){return '{}';},async digitalCalibrationBoard(){return 'file:///board.html';},captureGuidedLens(){return new Promise(r=>resolveLens=r);},captureAlignment(){return new Promise(r=>resolveAlignment=r);},async beginAlignmentMovement(){begin++;},async stop(){}};
 const native={View:node('View'),Image:node('Image'),Pressable:node('Pressable'),Modal:node('Modal'),AppState:{addEventListener(){return{remove(){}};}},BackHandler:{addEventListener(){return{remove(){}};}}};
 const mocks={'react-native':native,'expo-camera':{CameraView:node('Camera'),useCameraPermissions:()=>[{granted:true},async()=>({granted:true})]},'expo-keep-awake':{useKeepAwake(){}},'expo-sharing':{},'expo-file-system':{async readAsStringAsync(){return 'board';}},
  '../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../components/BigButton':{default:node('Button'),__esModule:true},'./CameraCalibrationScreen':{default:node('Legacy'),__esModule:true},'../i18n':{Text:node('Text'),t:s=>s},
  '../audio':{speakQueued(s,o){voices.push(s);return new Promise(r=>voice=()=>{o?.onDone?.();r();});},stopSpeaking(){}},
  '../cameraCalibration':{calibrationBridge:()=>bridge,async latestLensCapture(){return null;},async currentLensReport(){return null;},async savedReference(){return null;},async retainCalibrationCapture(r){return r;},async recoverLensReport(r){return r.report;}},
  '../referenceCalibration':{createLensFeedback(){return{send(){},close(){}};},async calibrationComputer(){return computer;},async pendingReference(){return null;},async savedReference(){return null;},async showComputerBoard(){},async submitAlignment(){uploads++;},async pollReference(){return {distanceReady:false};}}};
 const C=load('screens/PhoneCalibrationScreen',mocks).default;let tree;await act(async()=>{tree=create(React.createElement(C,{navigation:{goBack(){}}}));});
 const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);
 await act(async()=>{button('Calibrate camera lens').props.onPress();});assert.equal(resolveLens,undefined);
 await act(async()=>voice());assert.equal(typeof resolveLens,'function');
 assert.match(voices[0],/Watch the framing on your computer/);
 assert.ok(button('Share digital board')===undefined,'Actions are hidden during capture');
 act(()=>progress({phase:'lens',imageUri:'file:///view.jpg',lens:JSON.stringify({acceptedViews:12,hint:'Tilt the board view gently.'})}));
 assert.ok(tree.root.findAllByType('Text').some(n=>n.props.children==='Useful views kept: 12'));
 act(()=>progress({phase:'lens-fitting',imageUri:'file:///view.jpg',lens:JSON.stringify({acceptedViews:24,hint:'Checking lens parameters. You can hold the phone comfortably.'})}));
 assert.ok(tree.root.findAllByType('Body').some(n=>n.props.children==='Checking lens parameters. You can hold the phone comfortably.'));
 act(()=>progress({phase:'lens-saving',imageUri:'',lens:JSON.stringify({acceptedViews:48,coverageChecklist:{leftRightAngle:false,upDownAngle:false,horizontal:true,vertical:true}})}));
 assert.ok(tree.root.findAllByType('Body').some(n=>n.props.children==='Capture ended. Saving the calibration attempt.'));
 assert.ok(tree.root.findAllByType('Text').some(n=>n.props.children==='Useful views kept: 48'),'Final native count replaces throttled preview count');
 assert.ok(tree.root.findAllByType('Text').some(n=>n.props.children==='Side angles needed'));
 assert.ok(tree.root.findAllByType('Text').some(n=>n.props.children==='✓ Left/right positions captured'));
 await act(async()=>resolveLens({report:{lensReady:true},error:null}));assert.match(voices.at(-1),/Lens parameters saved/);
 await act(async()=>voice());assert.ok(button('Align camera and sensors'));
 await act(async()=>button('Align camera and sensors').props.onPress());assert.equal(resolveAlignment,undefined);
 await act(async()=>voice());assert.equal(typeof resolveAlignment,'function');
 await act(async()=>progress({phase:'alignment-cue',imageUri:''}));assert.equal(begin,0);
 await act(async()=>voice());assert.equal(begin,1);
 act(()=>progress({phase:'alignment-cue',imageUri:''}));assert.equal(begin,1,'Movement instruction must not repeat');
 await act(async()=>resolveAlignment({metadata:'{}',uri:'file:///alignment.zip'}));assert.equal(uploads,0);
 await act(async()=>voice());assert.equal(uploads,1);assert.match(voices.at(-1),/Reused for every participant on this phone/);
 await act(async()=>voice());assert.ok(button('Back to home'));assert.equal(button('Align camera and sensors'),undefined);
 assert.ok(button('Repeat calibration'));assert.doesNotMatch(tree.root.findAllByType('Body').map(n=>n.props.children).join(' '),/Sensor alignment is still needed/);act(()=>tree.unmount());
});

test('Saved or resumed reference exits setup; repeating alignment is explicit and reopening stays complete',async()=>{
 for(const resume of [false,true]){
  const node=name=>p=>React.createElement(name,p,p.children);let imported=!resume,captures=0,exits=0;
  const computer={url:'http://192.168.1.2:8765',token:'fixture'};
  const bridge={addListener(){return{remove(){}};},async phoneCalibrationInfo(){return '{}';},async captureAlignment(){captures++;},async beginAlignmentMovement(){},async stop(){}};
  const mocks={'react-native':{View:node('View'),Image:node('Image'),Pressable:node('Pressable'),Modal:node('Modal'),AppState:{addEventListener(){return{remove(){}};}},BackHandler:{addEventListener(){return{remove(){}};}}},'expo-camera':{CameraView:node('Camera'),useCameraPermissions:()=>[{granted:true},async()=>({granted:true})]},'expo-keep-awake':{useKeepAwake(){}},'expo-sharing':{},'expo-file-system':{},
   '../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../components/BigButton':{default:node('Button'),__esModule:true},'./CameraCalibrationScreen':{default:node('Legacy'),__esModule:true},'../i18n':{Text:node('Text'),t:s=>s},
   '../audio':{async speakQueued(_s,o){o?.onDone?.();},stopSpeaking(){}},
   '../cameraCalibration':{calibrationBridge:()=>bridge,async latestLensCapture(){return null;},async currentLensReport(){return {lensReady:true};}},
   '../referenceCalibration':{async calibrationComputer(){return computer;},async pendingReference(){return imported?null:{id:'retained'};},async savedReference(){return imported?{distanceReady:false}:null;},async pollReference(){imported=true;return {distanceReady:false};}}};
  const Component=load('screens/PhoneCalibrationScreen',mocks).default;let tree;
  const open=async()=>act(async()=>{tree=create(React.createElement(Component,{navigation:{goBack(){exits++;}}}));});
  const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);
  await open();
  if(resume)await act(async()=>button('Resume calibration processing').props.onPress());
  assert.equal(captures,0);assert.equal(button('Align camera and sensors'),undefined);
  assert.equal(button('Repeat camera and sensor alignment'),undefined);
  const bodyText=tree.root.findAllByType('Body').map(n=>n.props.children).join(' ');
  assert.doesNotMatch(bodyText,/Sensor alignment is still needed|Watch the framing/);
  assert.match(bodyText,/No repeat calibration is needed for a new participant/);
  assert.equal(tree.root.findAllByType('Button').filter(n=>n.props.label==='Back to home').length,1);
  act(()=>button('Repeat calibration').props.onPress());assert.ok(button('Repeat camera and sensor alignment'));
  assert.equal(captures,0,'Opening repeat options never starts another capture');
  act(()=>button('Back to home').props.onPress());assert.equal(exits,1);act(()=>tree.unmount());
  await open();assert.ok(button('Back to home'));assert.equal(button('Repeat camera and sensor alignment'),undefined);
  act(()=>tree.unmount());
 }
});

test('Every native lens hint has translated computer and optional tablet handling, including loss of board view',()=>{
 const guide=load('lensGuidance'),language=load('language'),source=fs.readFileSync(path.resolve(__dirname,'../modules/gait-camera-calibration/android/src/main/java/expo/modules/gaitcalibration/GuidedLensCalibration.java'),'utf8');
 const hints=[...source.matchAll(/(?:hint=|return )"([^"]+)"/g)].map(m=>m[1]);
 assert.ok(hints.length>=10);
 for(const text of [...hints.map(s=>guide.lensGuidance(s)),...hints.map(s=>guide.lensGuidance(s,'tablet')),guide.lensPreparation,guide.tabletLensPreparation]){
  assert.doesNotMatch(text,/whole board/);
  for(const l of ['ms','zh'])assert.notEqual(language.translate(text,l),text,text);
 }
 assert.match(guide.lensGuidance('Tilt the phone gently left and right.'),/aiming its camera back at the board/);
 assert.match(guide.lensGuidance('Tilt the phone gently left and right.','tablet'),/Turn the tablet/);
 assert.match(guide.lensGuidance('Keep the whole board in view.'),/back into view/);
 assert.equal(guide.lensGuidance('Lens parameters saved. Sensor alignment is still needed.'),'Lens parameters saved. Sensor alignment is still needed.');
});

test('Guided calibration cancels before capture instead of starting after an interrupted instruction',async()=>{
 const node=name=>p=>React.createElement(name,p,p.children);let voice,captures=0,stops=0;
 const bridge={addListener(){return{remove(){}};},async phoneCalibrationInfo(){return '{}';},async captureGuidedLens(){captures++;},async stop(){stops++;}};
 const mocks={'react-native':{View:node('View'),Image:node('Image'),Pressable:node('Pressable'),Modal:node('Modal'),AppState:{addEventListener(){return{remove(){}};}},BackHandler:{addEventListener(){return{remove(){}};}}},'expo-camera':{CameraView:node('Camera'),useCameraPermissions:()=>[{granted:true},async()=>({granted:true})]},'expo-keep-awake':{useKeepAwake(){}},'expo-sharing':{},'expo-file-system':{},'../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../components/BigButton':{default:node('Button'),__esModule:true},'./CameraCalibrationScreen':{default:node('Legacy'),__esModule:true},'../i18n':{Text:node('Text'),t:s=>s},'../audio':{speakQueued(){return new Promise(r=>voice=r);},stopSpeaking(){}},'../cameraCalibration':{calibrationBridge:()=>bridge,async latestLensCapture(){return null;},async currentLensReport(){return null;}},'../referenceCalibration':{async calibrationComputer(){return null;},async pendingReference(){return null;},async savedReference(){return null;}}};
 const C=load('screens/PhoneCalibrationScreen',mocks).default;let tree;await act(async()=>{tree=create(React.createElement(C,{navigation:{goBack(){}}}));});
 const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);
 await act(async()=>button('Use a tablet instead').props.onPress());
 await act(async()=>button('Calibrate camera lens').props.onPress());act(()=>button('Cancel capture').props.onPress());await act(async()=>voice());
 assert.equal(captures,0);assert.equal(stops,1);assert.ok(button('Calibrate camera lens'));act(()=>tree.unmount());
});

test('Every guided calibration screen instruction and spoken cue has both patient translations',()=>{
 const {messages}=load('translations'),source=fs.readFileSync(path.resolve(__dirname,'../src/screens/PhoneCalibrationScreen.tsx'),'utf8');
 for(const match of source.matchAll(/<Body>([^<{]+)<\/Body>|label="([^"{]+)"|(?:sayComplete|speakQueued|setHint)\('([^']+)'\)/g)){
  const text=match[1]??match[2]??match[3];assert.ok(messages[text],text);
  for(const language of ['ms','zh'])assert.notEqual(load('language').translate(text,language),text,text);
 }
});

test('Specific native calibration failures and processing phases translate in both languages',()=>{
 const source=fs.readFileSync(path.resolve(__dirname,'../modules/gait-camera-calibration/android/src/main/java/expo/modules/gaitcalibration/GuidedLensCalibration.java'),'utf8');
 const method=source.slice(source.indexOf('public String failureMessage()'),source.indexOf('public JSONObject progress()'));
 const errors=[...method.matchAll(/return "([^"]+)"/g)].map(m=>m[1]);
 assert.equal(new Set(errors).size,6);
 for(const text of [...errors,'Checking lens parameters. You can hold the phone comfortably.','Capture ended. Saving the calibration attempt.']){
  for(const l of ['ms','zh'])assert.notEqual(load('language').translate(text,l),text,text);
 }
});

test('Kept-view counter and every calibration coverage state translate',()=>{
 for(const text of ['Useful views kept: 48','Better views replace older ones. Follow the remaining angle checks.',
 'Side angles captured','Side angles needed','High/low angles captured','High/low angles needed',
 'Left/right positions captured','Left/right positions needed','Top/bottom positions captured','Top/bottom positions needed']){
  for(const l of ['ms','zh'])assert.notEqual(load('language').translate(text,l),text,text);
 }
});

test('Researcher calibration UI follows native progress and keeps processing separate from readiness',async()=>{
 const node=name=>props=>React.createElement(name,props,props.children);
 let progress,resolveCapture;const speech=[],saved=[],shared=[];
 const bridge={addListener(_name,listener){progress=listener;return {remove(){}};},captureWithOptics(setup){assert.equal(setup,'waist-bag-window');return new Promise(r=>resolveCapture=r);},async stop(){}};
 const native={View:node('View'),Image:node('Image'),Pressable:node('Pressable'),AppState:{addEventListener(){return {remove(){}};}},BackHandler:{addEventListener(){return {remove(){}};}}};
 const Screen=props=>React.createElement('Screen',props,props.children,props.actions);
 const mocks={'react-native':native,'expo-camera':{useCameraPermissions:()=>[{granted:true},async()=>({granted:true})]},'expo-keep-awake':{useKeepAwake(){}},
  'expo-sharing':{async isAvailableAsync(){return true;},async shareAsync(uri){shared.push(uri);}},'expo-document-picker':{},'expo-file-system':{},
  '../components/Screen':{Screen,Body:node('Body'),ui:{}},'../components/BigButton':{default:node('Button'),__esModule:true},
  '../i18n':{Text:node('Text'),t:s=>s},'../audio':{async speakQueued(s,o){speech.push(s);o?.onDone?.();},stopSpeaking(){}},
  '../cameraCalibration':{calibrationBridge:()=>bridge,async latestCalibrationCapture(){return null;},async latestNoiseCapture(){return null;},async hasCalibrationGeometry(){return false;},async retainCalibrationCapture(v){saved.push(v);return v;},async retainCalibrationReport(){}}};
 const Component=load('screens/CameraCalibrationScreen',mocks).default;let tree;
 await act(async()=>{tree=create(React.createElement(Component,{navigation:{goBack(){}}}));});
 const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);
 act(()=>tree.root.findAllByType('Pressable').find(n=>n.props.accessibilityRole==='tab'&&n.props.children.props.children==='Camera board').props.onPress());
 await act(async()=>{void button('Capture calibration').props.onPress();});
 assert.ok(button('Cancel capture'));assert.equal(shared.length,0);
 await act(async()=>{progress({elapsedSeconds:1,frames:10,imageUri:'file://frame.jpg',phase:'still'});});
 await act(async()=>{progress({elapsedSeconds:6,frames:80,imageUri:'file://next.jpg',phase:'move'});});
 assert.deepEqual(speech.slice(0,2),['Hold the phone still, facing the board.','Slowly tilt and move the phone. Keep the board in view.']);
 await act(async()=>{resolveCapture({uri:'file://calibration.zip',metadata:'{}',error:null});});
 assert.equal(saved.length,1);assert.ok(button('Import processed calibration'));
 assert.ok(tree.root.findAllByType('Body').some(n=>n.props.children==='No distance calibration is active yet.'));
 await act(async()=>{await button('Export calibration capture').props.onPress();});assert.deepEqual(shared,['file://calibration.zip']);
 await act(async()=>tree.unmount());
});

test('Noise UI waits for completed guidance, uses native elapsed time and exports its separate ZIP',async()=>{
 const node=name=>props=>React.createElement(name,props,props.children);let progress,resolveVoice,resolveNoise,noiseCalls=0,permissions=0;const shared=[],retained=[];
 const bridge={addListener(_,f){progress=f;return {remove(){}};},captureNoise(){noiseCalls++;return new Promise(r=>resolveNoise=r);},async stop(){}};
 const mocks={'react-native':{View:node('View'),Image:node('Image'),Pressable:node('Pressable'),AppState:{addEventListener(){return {remove(){}};}},BackHandler:{addEventListener(){return {remove(){}};}}},
 'expo-camera':{useCameraPermissions:()=>[{granted:false},async()=>{permissions++;return {granted:true};}]},'expo-keep-awake':{useKeepAwake(){}},'expo-document-picker':{},'expo-file-system':{},
 'expo-sharing':{async isAvailableAsync(){return true;},async shareAsync(uri){shared.push(uri);}},
 '../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../components/BigButton':{default:node('Button'),__esModule:true},'../i18n':{Text:node('Text'),t:s=>s},
 '../audio':{speakQueued(s,o){return new Promise(r=>{resolveVoice=()=>{o?.onDone?.();r();};});},stopSpeaking(){}},
 '../cameraCalibration':{calibrationBridge:()=>bridge,async latestCalibrationCapture(){return null;},async latestNoiseCapture(){return null;},async retainNoiseCapture(v){retained.push(v);return v;},async hasCalibrationGeometry(){return false;}}};
 const C=load('screens/CameraCalibrationScreen',mocks).default;let tree;await act(async()=>{tree=create(React.createElement(C,{navigation:{goBack(){}}}));});
 const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);
 act(()=>tree.root.findAllByType('Pressable').find(n=>n.props.accessibilityRole==='tab'&&n.props.children.props.children==='Sensor noise').props.onPress());
 await act(async()=>{button('Measure sensor noise (5 min)').props.onPress();});assert.equal(noiseCalls,0);
 await act(async()=>resolveVoice());assert.equal(noiseCalls,1);assert.equal(permissions,0);
 act(()=>progress({elapsedSeconds:125,phase:'noise',imageUri:'',frames:0}));assert.ok(tree.root.findAllByType('Text').some(n=>Array.isArray(n.props.children)&&n.props.children[0]===175));
 await act(async()=>resolveNoise({uri:'file:///noise.zip',metadata:'{}',error:null}));assert.equal(retained.length,1);assert.equal(button('Measure sensor noise (5 min)'),undefined);
 await act(async()=>resolveVoice());assert.ok(button('Export sensor noise'));assert.equal(button('Import processed calibration'),undefined);
 await act(async()=>button('Export sensor noise').props.onPress());assert.deepEqual(shared,['file:///noise.zip']);act(()=>tree.unmount());
});

test('Native camera UI follows real controller stages and saves matching video/IMU metadata with injected hardware',async()=>{
 const React=require('react'),renderer=require('react-test-renderer');let now=0,tick,finishVideo;const spoken=[],sessions=[],files=new Map();
 const node=name=>props=>React.createElement(name,props,props.children);
 const native={View:node('View'),Text:node('Text'),TextInput:node('TextInput'),Pressable:node('Pressable'),Platform:{OS:'android'},AppState:{currentState:'active',addEventListener(){return {remove(){}};}},BackHandler:{addEventListener(){return {remove(){}};}}};
 const Camera=React.forwardRef((props,ref)=>{React.useImperativeHandle(ref,()=>({recordAsync:()=>new Promise(r=>finishVideo=r),stopRecording(){}}),[]);React.useEffect(()=>{props.onCameraReady();},[]);return React.createElement('Camera',props);});
 let engine;class Engine{
  constructor(){engine=this;this.allReceiving=true;this.baselineReady=true;this.motionStatus={enough:true,upright:true,steady:true,context:'rest-or-quiet'};this.pulses=0;}
  connect(){}begin(){this.recordingClock={monotonicMs:now,startedAt:'2026-10-06T00:00:00Z'};}disconnect(){}preserveSetupBaseline(){}candidateStepsAfter(){return this.pulses;}
  stop(reason){return {source:'device',schemaVersion:2,startedAt:'2026-10-06T00:00:00Z',elapsedSeconds:now/1000,stopReason:reason,requestedHz:{accelerometer:100,gyroscope:100,magnetometer:50},streams:{accelerometer:[{x:1,y:0,z:0,elapsedMs:0,sensorTimestampSeconds:0}],gyroscope:[],magnetometer:[]},guidanceEvents:[]};}
 }
 const storage={documentDirectory:'file://doc/',async getFreeDiskStorageAsync(){return 1024**3;},async makeDirectoryAsync(){},async getInfoAsync(p){return files.get(p)??{exists:false};},async moveAsync({to}){files.set(to,{exists:true,isDirectory:false,size:1024});}};
 const mocks={react:React,'react-native':native,'expo-camera':{CameraView:Camera,useCameraPermissions:()=>[{granted:true},async()=>({granted:true})]},'expo-keep-awake':{useKeepAwake(){}},'expo-file-system':storage,'expo-sharing':{},
 '../components/Screen':{Screen:props=>React.createElement('Screen',props,props.children,props.actions),Card:node('Card'),Body:node('Body'),ui:{row:{},choice:{},selected:{},label:{},caption:{},error:{}}},'../components/BigButton':node('Button'),'../components/CameraTrialReview':node('Review'),'../i18n':{Text:node('Text'),t:s=>s},'../sensors':{SensorRecorder:Engine,checkSensors:async()=>{}},'../audio':{speakQueued:(text,opts)=>{spoken.push({text,opts});return Promise.resolve();},stopSpeaking(){}},
 '../store':{generateSessionId:()=> 'paired-ui',saveSession:async s=>sessions.push(JSON.parse(JSON.stringify(s)))},'./store':{saveSession:async s=>sessions.push(JSON.parse(JSON.stringify(s)))},'./language':{translate:s=>s},'../theme':{colours:{border:'#ddd'}}};
 const Screen=load('screens/CameraIMUTrialScreen',mocks,{performance:{now:()=>now},setInterval:fn=>{tick=fn;return 1;},clearInterval(){}}).default;
 let tree;await renderer.act(async()=>{tree=renderer.create(React.createElement(Screen,{navigation:{goBack(){}}}));});
 const button=label=>tree.root.findAll(n=>n.type==='Button'&&n.props.label===label)[0];
 assert.equal(button('Start paired capture').props.disabled,false);
 await renderer.act(async()=>{button('Start paired capture').props.onPress();await new Promise(r=>setImmediate(r));});assert.equal(spoken.length,1);
 assert.ok(engine);assert.ok(spoken[0].text.split(/\s+/).length<=15);
 await renderer.act(async()=>{spoken[0].opts.onDone();});await renderer.act(async()=>{now=1000;tick();});await renderer.act(async()=>{now=6000;tick();});assert.equal(spoken.length,2);
 await renderer.act(async()=>{spoken[1].opts.onDone();});await renderer.act(async()=>{now=10000;tick();});assert.equal(sessions.length,0);
 engine.motionStatus={enough:true,upright:true,steady:false,context:'movement'};engine.pulses=1;
 await renderer.act(async()=>{tick();});engine.motionStatus={enough:true,upright:true,steady:true,context:'rest-or-quiet'};await renderer.act(async()=>{now=12000;tick();});await renderer.act(async()=>{now=16000;tick();});assert.equal(sessions[0].cameraTrial.video.status,'pending');assert.match(spoken.at(-1).text,/Finished/);const cueCount=spoken.length;
 await renderer.act(async()=>{finishVideo({uri:'file://cache/paired.mp4'});await new Promise(r=>setImmediate(r));});
 const s=sessions.at(-1);assert.equal(s.id,'paired-ui');assert.equal(s.cameraTrial.video.fileName,'camera-paired-ui.mp4');assert.equal(s.cameraTrial.end,'quiet-stop');assert.equal(s.cameraTrial.video.status,'saved');assert.equal(s.isPractice,true);
 assert.equal(s.cameraTrial.timing.vioReady,false);assert.equal(spoken.length,cueCount);await renderer.act(async()=>tree.unmount());
});
test('Speech uses translated text and matching installed voice; missing Malay voice errors explicitly', async () => {
 const l=load('language');l.setLanguage('zh');let spoken,failed;
 const speech={async isSpeakingAsync(){return false},async stop(){},async getAvailableVoicesAsync(){return [{language:'en-US',identifier:'en'},{language:'zh-CN',identifier:'zh'}]},speak(text,options){spoken={text,options}}};
 const audio=load('audio',{'expo-speech':speech,'./language':l},{console:{warn(){}}});
 await audio.speak('Begin walking at your comfortable pace.');
 assert.equal(spoken.text,'开始步行，请按舒适的节奏走。');assert.equal(spoken.options.voice,'zh');
 l.setLanguage('ms');spoken=null;
 await audio.speak('Begin walking at your comfortable pace.',{onError:e=>failed=e});
 assert.equal(spoken,null);assert.match(failed.message,/Voice unavailable/);
});
test('Cancelling while voice availability is loading prevents late speech', async () => {
 let resolveVoice,notifyVoice,spoken=false;
 const entered=new Promise(r=>notifyVoice=r);
 const speech={async isSpeakingAsync(){return false},async stop(){},getAvailableVoicesAsync(){notifyVoice();return new Promise(r=>resolveVoice=r)},speak(){spoken=true}};
 const audio=load('audio',{'expo-speech':speech});const task=audio.speak('Start');await entered;
 audio.stopSpeaking();resolveVoice([{language:'en-MY',identifier:'en'}]);await task;assert.equal(spoken,false);
});
test('Speech queue discards obsolete reminders without cutting the active instruction', async () => {
 const spoken=[]; let stops=0;
 const speech={async isSpeakingAsync(){return false},async stop(){stops++},async getAvailableVoicesAsync(){return [{language:'en-MY',identifier:'en'}]},speak(text,options){spoken.push({text,options})}};
 const audio=load('audio',{'expo-speech':speech});
 const flush=()=>new Promise(resolve=>setImmediate(resolve));
 const first=audio.speakQueued('Active instruction'); await flush();
 const obsolete=audio.speakQueued('Old fit reminder');
 audio.discardPendingSpeech();
 const next=audio.speakQueued('Fit complete'); await flush();
 assert.equal(spoken.length,1); assert.equal(stops,0);
 spoken[0].options.onDone(); await first; await obsolete; await flush();
 assert.deepEqual(spoken.map(s=>s.text),['Active instruction','Fit complete']);
 spoken[1].options.onDone(); await next;
});
test('Stopping queued speech clears its watchdog and cannot interrupt the retry',async()=>{
 const timers=new Map(),spoken=[];let sequence=0,stops=0,failed=0,completed=0;
 const speech={async isSpeakingAsync(){return false},async stop(){stops++},async getAvailableVoicesAsync(){return [{language:'en-MY',identifier:'en'}]},speak(text,options){spoken.push({text,options})}};
 const audio=load('audio',{'expo-speech':speech},{setTimeout:fn=>{const id=++sequence;timers.set(id,fn);return id;},clearTimeout:id=>timers.delete(id)});
 const flush=()=>new Promise(r=>setImmediate(r));
 const old=audio.speakQueued('Old instruction',{onError:()=>failed++,onDone:()=>completed++});await flush();assert.equal(timers.size,1);
 audio.stopSpeaking();await old;assert.equal(timers.size,0);assert.equal(completed,0);
 const next=audio.speakQueued('Retry instruction',{onError:()=>failed++,onDone:()=>completed++});await flush();assert.equal(timers.size,1);
 // A late callback from the platform for the cancelled utterance is obsolete.
 spoken[0].options.onDone();assert.equal(completed,0);assert.equal(stops,1);
 spoken[1].options.onDone();await next;assert.equal(completed,1);assert.equal(failed,0);assert.equal(timers.size,0);
});

test('Android cold speech engine waits for voices before speaking and still requires actual completion',async()=>{
 const delays=[],spoken=[];let reads=0,completed=0;
 const speech={async isSpeakingAsync(){return false},async stop(){},async getAvailableVoicesAsync(){return ++reads<3?[]:[{language:'en-MY',identifier:'en'}]},speak(text,options){spoken.push({text,options})}};
 const audio=load('audio',{'expo-speech':speech},{setTimeout:(fn,ms)=>{if(ms===250)delays.push(fn);return 1;},clearTimeout(){}});
 const flush=()=>new Promise(r=>setImmediate(r));
 const cue=audio.speakQueued('Hold still',{onDone:()=>completed++});await flush();assert.equal(spoken.length,0);
 delays.shift()();await flush();assert.equal(spoken.length,0);
 delays.shift()();await flush();assert.equal(reads,3);assert.equal(spoken.length,1);assert.equal(completed,0);
 spoken[0].options.onDone();await cue;assert.equal(completed,1);
});

test('Cancelling during speech-engine binding prevents the obsolete cue from playing when voices appear',async()=>{
 const delays=[];let ready=false,spoken=0,completed=0;
 const speech={async isSpeakingAsync(){return false},async stop(){},async getAvailableVoicesAsync(){return ready?[{language:'en-MY',identifier:'en'}]:[]},speak(){spoken++}};
 const audio=load('audio',{'expo-speech':speech},{setTimeout:(fn,ms)=>{if(ms===250)delays.push(fn);return 1;},clearTimeout(){}});
 const flush=()=>new Promise(r=>setImmediate(r));
 const cue=audio.speakQueued('Obsolete cue',{onDone:()=>completed++});await flush();audio.stopSpeaking();await cue;
 ready=true;delays.shift()();await flush();assert.equal(spoken,0);assert.equal(completed,0);
});

test('Voice readiness is bounded and a loaded engine without the selected language fails without a fixed delay',async()=>{
 let reads=0,waits=0;
 const audio=load('audio',{'expo-speech':{getAvailableVoicesAsync:async()=>{reads++;return [];}}},{setTimeout:fn=>{waits++;fn();return 1;}});
 await assert.rejects(audio.ensureVoice(),/Voice unavailable/);assert.equal(reads,33);assert.equal(waits,32);
 const other=load('audio',{'expo-speech':{getAvailableVoicesAsync:async()=>[{language:'fr-FR',identifier:'fr'}]}},{setTimeout:()=>{throw Error('Unexpected delay');}});
 await assert.rejects(other.ensureVoice(),/Voice unavailable/);
});
test('Fresh candidate pulses reject stationary noise, rotation and pre-stage motion', () => {
 const {candidateStepsSince,FitCheck}=load('placement');
 const samples=fn=>Array.from({length:201},(_,i)=>({elapsedMs:i*20,sensorTimestampSeconds:i*.02,...fn(i*.02)}));
 assert.equal(candidateStepsSince(samples(t=>({x:1+.005*Math.sin(t*30),y:0,z:0})),0),0);
 assert.equal(candidateStepsSince(samples(t=>({x:Math.cos(t),y:Math.sin(t),z:0})),0),0);
 const walking=samples(t=>({x:1+.1*Math.sin(t*4*Math.PI),y:0,z:0}));
 assert.ok(candidateStepsSince(walking,0)>=3);
 assert.equal(candidateStepsSince(walking,4100),0);
 const fit=new FitCheck();
 for(let now=0;now<10000;now+=100) assert.equal(fit.update(now,true,{enough:true,upright:true,steady:true,context:'movement'}),'waiting');
});
function harness(screen, platform='android', browserResult=null,params={},overrides={}) {
 let now=0,nextId=0,currentEngine,navigated=[],spoke=[],voiceOptions,appListener;
 const timers=new Map();let visibilityListener,focusListener;
 const doc={visibilityState:'visible',addEventListener:(_,fn)=>visibilityListener=fn,removeEventListener:()=>visibilityListener=null};
 const globals={document:doc,AbortController,performance:{now:()=>now},setInterval:(fn,delay)=>{const id=++nextId;timers.set(id,{fn,delay,next:now+delay,repeat:true});return id},clearInterval:id=>timers.delete(id),setTimeout:(fn,delay)=>{const id=++nextId;timers.set(id,{fn,delay,next:now+delay});return id},clearTimeout:id=>timers.delete(id)};
 function advance(ms){act(()=>{const end=now+ms;while(now<end){now=Math.min(now+100,end);for(const [id,t] of [...timers]) if(t.next<=now){if(t.repeat)t.next+=t.delay;else timers.delete(id);t.fn();}}});}
 const steady={enough:true,steady:true,upright:true,context:'rest-or-quiet'};
 class Engine {
  constructor(options){this.options=options;currentEngine=this;this.motionStatus={...steady};this.allReceiving=true;this.baselineReady=true;this.guidanceReady=true;this.begun=false;}
  connect(){} disconnect(){} preserveSetupBaseline(){this.baselinePreserved=true} restoreFitCheck(v){this.savedFitCheck=v} startFit(){this.fitStarted=true} candidateStepsAfter(){return this.motionStatus.context==='movement'?1:0} finishFit(){this.savedFitCheck={status:'movement-then-settled',version:'guided-fit-v2'}} begin(){this.begun=true}
 }
 const native={Platform:{OS:platform},Text:'text',TextInput:'input',Modal:({visible,children})=>visible?React.createElement('modal',null,children):null,View:'view',ScrollView:'scrollview',Pressable:'pressable',Switch:'switch',StyleSheet:{create:x=>x},AppState:{currentState:'active',addEventListener:(_,fn)=>{appListener=fn;return {remove(){}}}},BackHandler:{addEventListener:()=>({remove(){}})}};
 const savedProfiles=new Map();let saveFails=false;
 const mocks={'react-native':native,'expo-location':{Accuracy:{High:4},requestForegroundPermissionsAsync:async()=>({status:'granted'}),getProviderStatusAsync:async()=>({locationServicesEnabled:true}),watchPositionAsync:async()=>({remove(){}})},'expo-keep-awake':{activateKeepAwakeAsync:async()=>{},deactivateKeepAwake:async()=>{}},'expo-haptics':{NotificationFeedbackType:{Error:'error',Warning:'warning',Success:'success'},notificationAsync:async()=>{}},
 '../components/Screen':{Screen:({children,actions,navigation,...p})=>React.createElement('screen',p,navigation,children,actions),Card:'card',Body:'body',ui:{row:{},fill:{},caption:{}}},'../components/BigButton':{default:'button',__esModule:true},
 '../components/ClinicalCapture':{default:p=>React.createElement('clinical',p),__esModule:true},
 '../components/ProtocolTutorial':{default:()=>null,__esModule:true},
 '../i18n':{Text:'text',LanguagePicker:()=>null,t:x=>x,useLanguage:()=> 'en'},
 '../audio':{speak:async(text,opts)=>{spoke.push(text);voiceOptions=opts},speakQueued:(text,opts)=>{spoke.push(text);voiceOptions=opts;return {finally(fn){fn();return Promise.resolve();}}},discardPendingSpeech(){},stopSpeaking(){},ensureVoice:async()=>({identifier:'en',language:'en-MY'})},
 '../onDeviceSetup':{phoneDistanceProfile:async()=>({testOnly:true})},
 '../browserSensors':{checkBrowserSensors:async()=>browserResult},
 '../sensors':{SensorRecorder:Engine,checkSensors:async()=>{if(platform==='web'&&!browserResult?.ready)throw new Error('Browser must not check live sensors')}},'../store':{getParticipants:async()=>[...savedProfiles.values()],saveParticipant:async p=>{if(saveFails)throw new Error('Storage unavailable');savedProfiles.set(p.id,JSON.parse(JSON.stringify(p)));},saveSession:async()=>{},generateSessionId:()=> 'test'},
 };
 if(overrides.__actualClinical)mocks['../components/ClinicalCapture']={__esModule:true,default:load('components/ClinicalCapture',{
  'react-native':native,'./Screen':mocks['../components/Screen'],'./BigButton':mocks['../components/BigButton'],'../i18n':mocks['../i18n']
 },globals).default};
 const Component=load('screens/'+screen,{...mocks,...overrides},globals).default;
 let renderer;act(()=>{renderer=create(React.createElement(Component,{navigation:{addListener:(_event,fn)=>{focusListener=fn;return()=>{focusListener=null;};},navigate:(...p)=>navigated.push(p),replace:(...p)=>navigated.push(p),goBack:()=>navigated.push(['back'])},route:{params:{duration:10,audioEnabled:true,isPractice:true,guidanceEnabled:true,...params}}}))});
 const button=label=>renderer.root.findAllByType('button').find(n=>n.props.label===label);
 async function finishSetup(){await act(async()=>{});act(()=>{renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.onChangeText('67');});act(()=>renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio').props.onPress());act(()=>button('Continue').props.onPress());const research=renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio'&&n.findAllByType('text').some(t=>t.props.children==='Research walk'));if(research)act(()=>research.props.onPress());act(()=>button('Continue').props.onPress());}
 return {renderer,button,advance,finishSetup,savedProfiles,focus:()=>act(async()=>focusListener?.()),failSave:()=>{saveFails=true},get engine(){return currentEngine},get voiceOptions(){return voiceOptions},navigated,spoke,hide:()=>act(()=>{doc.visibilityState='hidden';visibilityListener?.()}),background:()=>act(()=>appListener('background')),close:()=>act(()=>renderer.unmount())};
}
test('Setup waits for the participant instead of expiring automatically', () => {
 const h=harness('RecordScreen');h.engine.allReceiving=false;h.advance(40500);
 assert.equal(h.button('Retry this check'),undefined);
 assert.equal(h.renderer.root.findByType('screen').props.title,'Checking the phone');
 assert.equal(h.navigated.length,0);h.close();
});
test('Stationary fit cannot advance and generic movement without a fresh pulse cannot start recording', () => {
 const h=harness('RecordScreen'); h.advance(24000);
 h.engine.motionStatus={enough:true,steady:true,upright:true,context:'movement'};h.advance(10000);
 assert.equal(h.renderer.root.findByType('screen').props.title,'Short movement check');
 assert.equal(h.engine.begun,false);
 h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);
 h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(13000);
 assert.equal(h.engine.begun,false);
 h.engine.candidateStepsAfter=()=>0;
 h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1000);
 assert.equal(h.engine.begun,false);
 h.engine.candidateStepsAfter=()=>1;h.advance(100);
 assert.equal(h.engine.begun,true);h.close();
});
test('Completed fit survives a later interruption, but retry cannot start until a new baseline passes', () => {
 const h=harness('RecordScreen');h.advance(24000);assert.equal(h.engine.fitStarted,true);
 h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);
 h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(3200);
 assert.equal(h.renderer.root.findByType('screen').props.title,'Ready to begin');h.background();
 act(()=>h.button('Retry this check').props.onPress());assert.ok(h.engine.savedFitCheck);
 h.engine.baselineReady=false;h.advance(12000);assert.equal(h.engine.begun,false);
 h.engine.baselineReady=true;h.advance(13000);assert.equal(h.engine.begun,false);h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1000);assert.equal(h.engine.begun,true);assert.equal(h.spoke.includes('Recording started. Walk at your comfortable pace.'),false);assert.equal(h.engine.fitStarted,undefined);h.close();
});
test('Sound sample is optional on setup and can be skipped after two seconds without disabling guidance', async () => {
 const h=harness('PrepareScreen');await h.finishSetup();
 const consent=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox'&&String(n.props.accessibilityLabel).startsWith('I can walk without hands-on help'));
 act(()=>consent.props.onPress());assert.equal(h.button('Start test').props.disabled,false);
 await act(async()=>h.button('Play voice sample').props.onPress());
 assert.equal(h.button('Start without sound test').props.disabled,true);
 h.advance(2000);assert.equal(h.button('Start without sound test').props.disabled,false);
 await act(async()=>h.button('Start without sound test').props.onPress());
 assert.equal(h.navigated[0][0],'Record');assert.equal(h.navigated[0][1].audioEnabled,true);h.close();
});

test('Setup validates identity and saves one participant with the recording, even on retry', async () => {
 const h=harness('PrepareScreen');await act(async()=>{});
 act(()=>h.button('Continue').props.onPress());
 assert.equal(h.renderer.root.findByType('screen').props.title,'Who is walking?');assert.equal(h.savedProfiles.size,0);
 await h.finishSetup();assert.equal(h.savedProfiles.size,0);
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());
 const first=h.navigated[0][1];assert.equal(h.savedProfiles.size,1);assert.equal(first.demographics.ageYears,67);assert.equal(first.participantSnapshot.id,first.participantId);
 await act(async()=>h.button('Start test').props.onPress());assert.equal(h.savedProfiles.size,1);assert.equal(h.navigated[1][1].participantId,first.participantId);h.close();
});
test('A participant write failure blocks recording and reports a translated error',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();h.failSave();
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());assert.equal(h.navigated.length,0);assert.equal(h.savedProfiles.size,0);
 assert.equal(h.renderer.root.findByProps({accessibilityRole:'alert'}).children.join(''),'Could not save participant. Try again.');h.close();
});
test('Android permission activity pause cannot silently cancel Start test',async()=>{
 let permissionReturned;
 const h=harness('PrepareScreen','android',null,{}, {'../sensors':{checkSensors:()=>new Promise(resolve=>permissionReturned=resolve)}});
 await h.finishSetup();
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='checkbox').props.onPress());
 let start;await act(async()=>{start=h.button('Start test').props.onPress();});
 h.background();
 await act(async()=>{permissionReturned();await start;});
 assert.equal(h.navigated.length,1);assert.equal(h.navigated[0][0],'Record');h.close();
});
test('Changing person after a saved test creates a new identity rather than rewriting the first person',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());const first=h.navigated[0][1];
 act(()=>h.button('Previous').props.onPress());act(()=>h.button('Previous').props.onPress());
 act(()=>h.button('Edit participant details').props.onPress());
 act(()=>h.button('Walking aid and health details').props.onPress());
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Study ID or participant label'}).props.onChangeText('STUDY-002'));act(()=>h.button('Done').props.onPress());
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.value,'');
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.onChangeText('70'));
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='radio').props.onPress());
 act(()=>h.button('Continue').props.onPress());act(()=>h.button('Continue').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());const second=h.navigated[1][1];
 assert.notEqual(first.participantId,second.participantId);assert.equal(h.savedProfiles.size,2);
 assert.match(h.savedProfiles.get(first.participantId).label,/^GT-/);assert.equal(first.participantSnapshot.demographics.ageYears,67);h.close();
});
test('Participant resolution never merges by demographics and preserves existing clinical fields',()=>{
 const {resolveTestParticipant:resolve}=load('testParticipant');
 const input={newId:'new',label:'P01',ageYears:67,sex:'female',heightCm:null,assistiveDevice:'none'};
 for(const change of [{ageYears:null},{ageYears:NaN},{ageYears:12.5},{sex:null},{label:''}])assert.throws(()=>resolve([],{...input,...change}));
 const existing=resolve([],input);existing.favorite=true;existing.clinical.lesionLocation='recorded site';existing.demographics.weightKg=70;
 assert.throws(()=>resolve([existing],{...input,newId:'other',label:' p01 '}),/already exists/);
 const different=resolve([existing],{...input,newId:'other',label:'P02'});assert.equal(different.id,'other');
 const updated=resolve([existing],{...input,id:'new',ageYears:68});assert.equal(updated.clinical.lesionLocation,'recorded site');assert.equal(updated.demographics.weightKg,70);assert.equal(updated.favorite,true);assert.equal(existing.demographics.ageYears,67);
 assert.throws(()=>resolve([{...existing,archived:true}],{...input,id:'new'}),/unavailable/);
});

test('Clinical intake requires explicit history and never invents chronicity for an older profile',()=>{
 const {resolveTestParticipant:resolve}=load('testParticipant');
 const {clinicalIntakeIssue}=load('clinicalIntake');
 const input={newId:'p1',label:'P01',ageYears:67,sex:'female',heightCm:null,assistiveDevice:'none'};
 const old=resolve([],input);
 assert.match(clinicalIntakeIssue(old.clinical),/Complete the stroke history/);
 const unknown=resolve([old],{...input,id:'p1',affectedHemisphere:'unknown',affectedBodySide:'unknown',chronicityStatus:'unknown',historySource:'patient-or-caregiver-report'});
 assert.equal(clinicalIntakeIssue(unknown.clinical),null);
 assert.equal(unknown.clinical.monthsSinceStroke,null);
 const invalid=resolve([unknown],{...input,id:'p1',chronicityStatus:'known',monthsSinceStroke:null});
 assert.match(clinicalIntakeIssue(invalid.clinical),/whole months/);
 const known=resolve([invalid],{...input,id:'p1',chronicityStatus:'known',monthsSinceStroke:18});
 assert.equal(clinicalIntakeIssue(known.clinical),null);
 assert.equal(known.clinical.monthsSinceStroke,18);
});

test('New clinical intake and outcome prompts are translated in both additional languages',()=>{
 const {translate}=load('language');
 for(const prompt of ['Affected brain hemisphere','Affected body side','Time since stroke','Whole months since stroke','History source','Complete the stroke history before a clinical test. Unknown is an available answer.','Enter measured distance or completed laps before marking this test complete.']){
  assert.notEqual(translate(prompt,'ms'),prompt);
  assert.notEqual(translate(prompt,'zh'),prompt);
 }
});
test('Tutorial renders every diagram and stops speech when moving between steps or notes',async()=>{
 let spoken=[],stops=0,closed=0;
 const Component=load('components/ProtocolTutorial',{
  'react-native':{Modal:'modal',View:'view',useWindowDimensions:()=>({height:568,width:320,fontScale:1.5})},
  'react-native-safe-area-context':{SafeAreaView:'safe'},
  'react-native-svg':{__esModule:true,default:'svg',Path:'path',Rect:'rect',Circle:'circle',Line:'line',Text:'svgtext'},
  '../i18n':{Text:'text',t:x=>x,useLanguage:()=> 'en'},
  '../audio':{speak:async text=>spoken.push(text),stopSpeaking:()=>stops++},
  './Screen':{Screen:({children,actions,navigation,...p})=>React.createElement('screen',p,navigation,children,actions),Body:'body',ui:{row:{},fill:{}}},
  './BigButton':{__esModule:true,default:'button'},
 }).default;
 for(const protocol of ['research-walk','10mwt','2mwt','6mwt','tug']){
  let renderer;act(()=>{renderer=create(React.createElement(Component,{protocol,onClose:()=>closed++}))});
  const button=name=>renderer.root.findAllByType('button').find(n=>n.props.label===name);
  for(let step=0;step<3;step++){
   assert.equal(renderer.root.findAllByType('svg').length,1);
   await act(async()=>button('Read aloud').props.onPress());const before=stops;
   if(step===0){act(()=>button('Worker protocol notes').props.onPress());assert.ok(stops>before);act(()=>button('Back to tutorial').props.onPress());}
   act(()=>button(step===2?'Done':'Next step').props.onPress());
  }
  act(()=>renderer.unmount());
 }
 assert.equal(closed,5);assert.equal(spoken.length,15);
});
test('Language selection updates rendered text, persists, and wins over a delayed saved preference', async () => {
 const l=load('language');let resolveRead;const writes=[];
 const i18n=load('i18n',{'react-native':{Text:'text',View:'view',Pressable:'pressable'},'./language':l,'@react-native-async-storage/async-storage':{getItem:()=>new Promise(r=>resolveRead=r),setItem:async(k,v)=>writes.push([k,v])}});
 let renderer;act(()=>{renderer=create(React.createElement(React.Fragment,null,React.createElement(i18n.LanguagePicker),React.createElement(i18n.Text,null,10,' sec')))});
 const restoring=i18n.restoreLanguage();
 act(()=>renderer.root.findAllByType('pressable')[2].props.onPress());
 assert.equal(l.getLanguage(),'zh');assert.deepEqual(writes[0],['gait-language-v1','zh']);
 await act(async()=>{resolveRead('ms');await restoring});
 assert.equal(l.getLanguage(),'zh');assert.equal(renderer.root.findAllByType('text').at(-1).children.join(''),'10秒');
 act(()=>renderer.unmount());
});


test('Patient interpretation prioritises placement, missing coverage and possible handling over rhythm', () => {
 const {patientSummary}=load('patientSummary');
 const s={usableSeconds:10,quietSeconds:0,movementSeconds:10,possibleHandlingSeconds:0,segments:[],trend:'more',repeatingMotion:true};
 assert.match(patientSummary(s,true)[0].title,/position/);
 assert.match(patientSummary({...s,segments:[{context:'missing-data'}]},false)[0].title,/Not enough/);
 assert.equal(patientSummary({...s,possibleHandlingSeconds:1},false).length,1);
 assert.match(patientSummary({...s,usableSeconds:5},false)[0].title,/Not enough/);
});
test('Patient interpretation preserves rest and uncertainty without inferring fatigue, speed or unequal steps', () => {
 const {patientSummary,patientMessages}=load('patientSummary');
 const s={usableSeconds:10,quietSeconds:3,movementSeconds:7,possibleHandlingSeconds:0,segments:[],trend:'less',repeatingMotion:null};
 const paused=patientSummary(s,false);
 assert.match(paused[0].text,/Rest is welcome/);
 assert.match(paused[1].text,/do not judge/);
 assert.match(paused[2].text,/does not tell us whether you slowed down or became tired/);
 const active=patientSummary({...s,quietSeconds:0,repeatingMotion:true},false);
 assert.match(active[1].text,/does not show whether your left and right steps were equal/);
 const unclear=patientSummary({...s,quietSeconds:0,repeatingMotion:false,movementSeconds:0},false);
 assert.match(unclear[2].text,/not enough/);
 for(const state of [s,{...s,quietSeconds:0,repeatingMotion:true},{...s,movementSeconds:0},{...s,trend:'more'},{...s,trend:'similar'},{...s,trend:'unavailable'},{...s,usableSeconds:0},{...s,possibleHandlingSeconds:1}]) for(const shift of [true,false]) for(const item of patientSummary(state,shift)) {
  assert.ok(patientMessages[item.title]); assert.ok(patientMessages[item.text]);
 }
});


test('Browser frame remains phone-sized on laptops and fills narrow mobile screens',()=>{
 let size={width:1440,height:1000};
 const Frame=load('components/PhoneFrame',{'react-native':{Platform:{OS:'web'},View:'view',useWindowDimensions:()=>size},'../i18n':{Text:'text'}}).default;
 let renderer;act(()=>{renderer=create(React.createElement(Frame,null,React.createElement('content')))});
 assert.equal(renderer.root.findAllByType('view')[1].props.style.width,430);
 assert.equal(renderer.root.findAllByType('view')[1].props.style.height,900);
 act(()=>{size={width:390,height:700};renderer.update(React.createElement(Frame,null,React.createElement('content')))});
 assert.equal(renderer.root.findAllByType('view')[1].props.style.width,'100%');
 assert.equal(renderer.root.findAllByType('view')[1].props.style.borderWidth,0);
 act(()=>renderer.unmount());
});


test('Browser setup opens explanation without sensor checks, consent or creating a recording',async()=>{
 const h=harness('PrepareScreen','web');
 assert.notEqual(h.button('Preview hands-free flow').props.disabled,true);
 assert.equal(h.renderer.root.findAllByType('pressable').filter(p=>p.props.accessibilityRole==='checkbox').length,0);
 await act(async()=>h.button('Preview hands-free flow').props.onPress());
 assert.deepEqual(JSON.parse(JSON.stringify(h.navigated)),[['Walkthrough',{protocol:'research-walk'}]]);
 assert.equal(h.engine,undefined);
 h.close();
});


test('Browser capture starts only after all-sensor check and separate user consent; preview stays available',async()=>{
 const sensors=Object.fromEntries(['accelerometer','gyroscope','magnetometer'].map(n=>[n,{status:'ready',count:150,hz:50}]));
 const h=harness('PrepareScreen','web',{ready:true,sensors});await h.finishSetup();
 await act(async()=>h.button('Check this phone’s sensors').props.onPress());
 assert.equal(h.button('Start test'),undefined);
 await act(async()=>h.button('Agree and check sensors').props.onPress());
 assert.equal(h.button('Start test').props.disabled,true);
 assert.ok(h.button('Preview hands-free flow'));
 const consent=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox');
 act(()=>consent.props.onPress());assert.equal(h.button('Start test').props.disabled,false);
 await act(async()=>h.button('Start test').props.onPress());
 assert.equal(h.navigated[0][0],'Record');h.close();
});
test('Failed browser capability check cannot unlock recording',async()=>{
 const sensors=Object.fromEntries(['accelerometer','gyroscope','magnetometer'].map(n=>[n,{status:n==='magnetometer'?'unavailable':'ready',count:0,hz:0}]));
 const h=harness('PrepareScreen','web',{ready:false,sensors});await h.finishSetup();
 await act(async()=>h.button('Check this phone’s sensors').props.onPress());
 await act(async()=>h.button('Agree and check sensors').props.onPress());
 assert.equal(h.button('Start test'),undefined);assert.ok(h.button('Preview hands-free flow'));h.close();
});

test('Browser sensor loss or hidden tab interrupts and saves an active walk',async()=>{
 for(const cause of ['hidden','lost']){
  const h=harness('RecordScreen','web');
  h.advance(23500);h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);
  h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(18500);assert.equal(h.engine.begun,false);h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1000);assert.equal(h.engine.begun,true);
  let reason;
  h.engine.stop=r=>{reason=r;return {stopReason:r,startedAt:'2026-09-17T00:00:00Z',elapsedSeconds:1,streams:{accelerometer:[],gyroscope:[],magnetometer:[]},guidanceEvents:[]}};
  await act(async()=>{if(cause==='hidden')h.hide();else{h.engine.allReceiving=false;h.advance(100)}});
    await act(async()=>{h.advance(2000);await Promise.resolve();});assert.equal(reason,'interrupted');assert.equal(h.navigated.at(-1)[0],'Result');h.close();
 }
});


test('Setup menus preserve settings and optional participant details without expanding the main page',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 assert.equal(h.renderer.root.findAllByType('switch').length,0);
 act(()=>h.button('Language and audio settings').props.onPress());
 assert.equal(h.renderer.root.findAllByType('modal').length,1);
 const voice=h.renderer.root.findByProps({accessibilityLabel:'Voice guidance'});
 act(()=>voice.props.onValueChange(false));
 act(()=>h.button('Done').props.onPress());
 act(()=>h.button('Previous').props.onPress());act(()=>h.button('Previous').props.onPress());
 act(()=>h.button('Walking aid and health details').props.onPress());
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Height in centimetres'}).props.onChangeText('168'));
 act(()=>h.button('Done').props.onPress());
 assert.equal(h.renderer.root.findAllByType('modal').length,0);
 assert.equal(h.renderer.root.findAllByProps({accessibilityLabel:'Height in centimetres'}).length,0);
 act(()=>h.button('Language and audio settings').props.onPress());
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Voice guidance'}).props.value,false);
 act(()=>h.button('Done').props.onPress());act(()=>h.button('Walking aid and health details').props.onPress());
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Height in centimetres'}).props.value,'168');
 act(()=>h.button('Done').props.onPress());
 h.close();
});

test('New collection sessions require an explicit test choice and retain it on return',async()=>{
 const h=harness('PrepareScreen');await act(async()=>{});
 act(()=>{h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.onChangeText('65');});
 act(()=>h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio').props.onPress());
 act(()=>h.button('Continue').props.onPress());assert.equal(h.button('Continue').props.disabled,true);
 assert.equal(h.button('Change test: Research walk'),undefined);
 act(()=>h.button('Continue').props.onPress());assert.ok(h.renderer.root.findAllByType('text').some(n=>n.props.children==='Choose a test to continue.'));assert.equal(h.button('Start test'),undefined);
 const choice=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityLabel==='TUG');assert.ok(choice);act(()=>choice.props.onPress());
 assert.equal(h.button('Continue').props.disabled,false);assert.ok(h.button('Change test: TUG'));
 act(()=>h.button('Previous').props.onPress());act(()=>h.button('Continue').props.onPress());assert.ok(h.button('Change test: TUG'));h.close();
});

test('Test selection closes its menu and preserves the chosen protocol on return',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 act(()=>h.button('Previous').props.onPress());
 act(()=>h.button('Change test: Research walk').props.onPress());
 const choice=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio'&&n.findAllByType('text').some(t=>(Array.isArray(t.props.children)?t.props.children.includes('6MWT'):t.props.children==='6MWT')));
 act(()=>choice.props.onPress());
 assert.equal(h.renderer.root.findAllByType('modal').length,0);
 assert.ok(h.button('Change test: 6MWT'));
 assert.ok(h.renderer.root.findByProps({accessibilityLabel:'Measured course length in metres'}));
 h.close();
});

test('Clinical test setup requires explicit history and saves it with the selected participant',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 act(()=>h.button('Previous').props.onPress());
 act(()=>h.button('Change test: Research walk').props.onPress());
 const radioWith=text=>h.renderer.root.findAllByType('pressable').filter(n=>n.props.accessibilityRole==='radio'&&n.findAllByType('text').some(t=>Array.isArray(t.props.children)?t.props.children.includes(text):t.props.children===text));
 act(()=>radioWith('10MWT')[0].props.onPress());
 act(()=>h.button('Continue').props.onPress());
 assert.equal(h.renderer.root.findByType('screen').props.title,'Choose your test');
 assert.match(JSON.stringify(h.renderer.toJSON()),/Complete the stroke history/);
 act(()=>h.button('Review stroke history').props.onPress());
 act(()=>radioWith('left')[0].props.onPress());
 act(()=>radioWith('right')[1].props.onPress());
 act(()=>radioWith('known')[0].props.onPress());
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Whole months since stroke'}).props.onChangeText('18'));
 act(()=>radioWith('Patient or caregiver')[0].props.onPress());
 act(()=>h.button('Done').props.onPress());
 act(()=>h.button('Continue').props.onPress());
 assert.equal(h.renderer.root.findByType('screen').props.title,'Sound and readiness');
 const checks=h.renderer.root.findAllByType('pressable').filter(n=>n.props.accessibilityRole==='checkbox');
 act(()=>checks[0].props.onPress());
 await act(async()=>h.button('Start test').props.onPress());
 const saved=h.navigated.at(-1)[1];
 assert.equal(saved.assessmentSetup.protocolVariant,'10mwt-12m-central10m-v1');
 assert.equal(saved.participantSnapshot.clinical.affectedHemisphere,'left');
 assert.equal(saved.participantSnapshot.clinical.affectedBodySide,'right');
 assert.equal(saved.participantSnapshot.clinical.monthsSinceStroke,18);
 h.close();
});

test('Result worker save persists modified 10MWT without inventing distance or speed',async()=>{
 const saved=[];let beforeRemove;let failSave=false;const dispatched=[];
 let session={id:'partial-ten',date:'2026-10-11',windows:[],isPractice:false,assessmentSetup:{protocol:'10mwt',timedDistanceM:10,courseLengthM:12},protocolExecution:{end:'auto-stop-estimate',elapsedFromGoSeconds:20}};
 const Screen=load('screens/ResultScreen',{
  'react-native':{View:'view',Pressable:'pressable',TextInput:'input'},
  '@react-navigation/native':{useFocusEffect:cb=>React.useEffect(cb,[cb])},
  '../components/Screen':{Screen:({children,actions,navigation,...p})=>React.createElement('screen',p,navigation,children,actions),Card:({children})=>React.createElement('card',null,children),Body:({children})=>React.createElement('text',null,children),ui:{}},
  '../components/BigButton':{__esModule:true,default:p=>React.createElement('button',p)},
  '../components/PatientSummary':{__esModule:true,default:()=>null},
  '../components/CameraTrialReview':{__esModule:true,default:()=>null},
  '../components/GaitDistanceReview':{__esModule:true,default:()=>null},
  '../export':{shareRecording:async()=>{}},
  '../i18n':{Text:({children,...p})=>React.createElement('text',p,children),t:x=>x},
  '../store':{getSession:async()=>session,getSessions:async()=>[session],saveSession:async s=>{if(failSave)throw new Error("disk full");saved.push(s);session=s;},saveParticipantDistanceCalibration:async()=>null},
 }).default;
 let renderer;await act(async()=>{renderer=create(React.createElement(Screen,{route:{params:{sessionId:session.id,openAssessment:true}},navigation:{navigate(){},popToTop(){},addListener:(name,cb)=>{beforeRemove=cb;return ()=>{};},dispatch:a=>dispatched.push(a)}}));});
 const text=JSON.stringify(renderer.toJSON());assert.match(text,/Recording saved/);assert.match(text,/Test finish needs checking/);
 act(()=>renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityLabel==='Modified').props.onPress());
 act(()=>renderer.root.findAllByType('input').find(n=>n.props.accessibilityLabel==='Timed interval seconds').props.onChangeText('12'));
 await act(async()=>renderer.root.findAllByType('button').find(n=>n.props.label==='Save worker draft').props.onPress());
 assert.equal(saved.length,1);assert.equal(saved[0].assessment,undefined);assert.equal(saved[0].workerOutcomeDraft.form.timedZoneSeconds,12);
 assert.match(JSON.stringify(renderer.toJSON()),/Worker draft saved/);
 act(()=>renderer.unmount());
 await act(async()=>{renderer=create(React.createElement(Screen,{route:{params:{sessionId:session.id,openAssessment:true}},navigation:{navigate(){},popToTop(){},addListener:(name,cb)=>{beforeRemove=cb;return ()=>{};},dispatch:a=>dispatched.push(a)}}));});
 assert.equal(renderer.root.findAllByType('input').find(n=>n.props.accessibilityLabel==='Timed interval seconds').props.value,'12');
 // Numeric edits must dirty a saved draft; Back waits for persistence before dispatch.
 act(()=>renderer.root.findAllByType('input').find(n=>n.props.accessibilityLabel==='Timed interval seconds').props.onChangeText('13'));
 let prevented=false;failSave=true;
 await act(async()=>{beforeRemove({preventDefault(){prevented=true;},data:{action:{type:'GO_BACK'}}});});
 assert.equal(prevented,true);assert.equal(dispatched.length,0);assert.match(JSON.stringify(renderer.toJSON()),/Could not save worker draft/);
 failSave=false;await act(async()=>{beforeRemove({preventDefault(){prevented=true;},data:{action:{type:'GO_BACK'}}});});
 assert.equal(prevented,true);assert.equal(dispatched.length,1);assert.equal(session.workerOutcomeDraft.form.timedZoneSeconds,13);
 act(()=>renderer.root.findAllByType('input').find(n=>n.props.accessibilityLabel==='Timed interval seconds').props.onChangeText('12'));
 await act(async()=>renderer.root.findAllByType('button').find(n=>n.props.label==='Save assessment to this phone').props.onPress());
 assert.equal(saved.length,3);assert.equal(session.workerOutcomeDraft,undefined);assert.doesNotMatch(JSON.stringify(renderer.toJSON()),/Worker draft saved/);
 assert.equal(saved[2].assessment.completionStatus,'modified');assert.equal(session.assessment.completed,false);assert.equal(session.assessment.distanceWalkedM,null);assert.equal(session.assessment.speedMps,null);assert.equal(session.assessment.timedZoneSeconds,12);
 act(()=>renderer.unmount());
});

test('Dashboard includes unassigned, archived and practice recordings while separating measured trends',async()=>{
 const profiles=[{id:'p1',label:'Archived person',archived:true,favorite:false,demographics:{ageYears:65},clinical:{assistiveDevice:'none'}}];
 const rows=[{id:'unknown',date:'2026-10-01',windows:[],hasDeviceRecording:true},{id:'practice',participantId:'p1',date:'2026-09-30',windows:[],isPractice:true,hasDeviceRecording:true},{id:'old-index',participantId:'p1',date:'2026-09-29',windows:[]}];
 const opened=[],reads=[];
 const Screen=load('screens/DashboardScreen',{
   'react-native':{View:'view',Pressable:'pressable'},
   '@react-navigation/native':{useFocusEffect:cb=>React.useEffect(cb,[cb])},
   '../components/Screen':{Screen:({children,actions})=>React.createElement('screen',null,children,actions),Card:({children})=>React.createElement('card',null,children),Body:({children})=>React.createElement('text',null,children),ui:{}},
   '../components/BigButton':{__esModule:true,default:p=>React.createElement('button',p)},
   '../i18n':{Text:({children,...p})=>React.createElement('text',p,children),t:x=>x},
   '../store':{getParticipants:async()=>profiles,getSessions:async()=>rows,getSession:async id=>{reads.push(id);return {recording:{source:'device'}}},formatSessionDate:x=>x},
   'react-native-svg':{__esModule:true,default:'svg',Circle:'circle',Polyline:'polyline'},
 }).default;
 let renderer;await act(async()=>{renderer=create(React.createElement(Screen,{navigation:{navigate:(...a)=>opened.push(a),popToTop(){}}}));});
 assert.deepEqual(reads,['old-index']);
 assert.match(JSON.stringify(renderer.toJSON()),/2026-10-01/);
 act(()=>renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio').props.onPress());
 const text=JSON.stringify(renderer.toJSON());
 assert.match(text,/2026-09-30/);assert.match(text,/2026-09-29/);assert.match(text,/Practice/);assert.doesNotMatch(text,/Legacy simulation/);
 assert.equal(renderer.root.findAllByType('svg').length,0);
 act(()=>renderer.unmount());
});


// Complete software handoffs: actual RecordScreen + ClinicalCapture + local store.
// Hardware/clocks/filesystem are substituted and the saved fixtures are practice-only.
for(const [protocol,duration,tracked=false] of [['research-walk',10],['research-walk',20],['research-walk',30],['10mwt',180],['10mwt',180,true],['tug',180],['2mwt',120],['6mwt',360]]) {
 test(`Acceptance: ${protocol}/${duration}${tracked?' tracked':''} setup → capture → persisted result`,async()=>{
  const controls=[],files=new Map(),preferences=new Map();let beganAt=0,now=0,stopCalls=0,camera;
  const fixtureId=`EMU-${protocol}-${duration}${tracked?'-tracked':''}`;
  class Capture{
   constructor(id,p){camera=this;this.attachment={sessionId:id,protocol:p,status:'capturing'};this.progress={usable:true,complete:false};}
   get live(){return {initialized:true,integrity:true,positionStdMetres:.05,receivedAt:Date.now(),walkProgress:this.progress};}
   async ready(){}begin(){}finish(){}finished(){return new Promise(()=>{});}async attach(){}async cancel(){}
  }
  const storage={documentDirectory:'file:///sandbox/',makeDirectoryAsync:async()=>{},writeAsStringAsync:async(p,s)=>files.set(p,s),readAsStringAsync:async p=>files.get(p),getInfoAsync:async p=>({exists:files.has(p)}),deleteAsync:async p=>files.delete(p)};
  const store=load('store',{'expo-file-system':storage,'@react-native-async-storage/async-storage':{getItem:async k=>preferences.get(k)??null,setItem:async(k,v)=>preferences.set(k,v),removeItem:async k=>preferences.delete(k)}});
  const profile={id:'EMU-PRACTICE',label:'EMU-SYNTHETIC-NOT-PATIENT',favorite:false,archived:false,createdAt:new Date().toISOString(),updatedAt:new Date().toISOString(),demographics:{ageYears:67,sex:'female'},clinical:{strokeType:'unknown',lesionLocation:'unknown',monthsSinceStroke:null,chronicityStatus:'unknown',affectedHemisphere:'unknown',affectedBodySide:'unknown',historySource:'patient-or-caregiver-report',premorbidGaitNotes:'',jointOrOrthopaedicNotes:'',assistiveDevice:'none'}};
  await store.saveParticipant(profile);
  const h=harness('RecordScreen','android',null,{duration,audioEnabled:false,isPractice:true,useCameraDistance:tracked,participantId:profile.id,participantLabel:profile.label,participantSnapshot:profile,demographics:profile.demographics,assessmentSetup:{protocol,courseLengthM:protocol==='10mwt'?12:3,timedDistanceM:protocol==='10mwt'?10:null}},
   {__actualClinical:true,'../gaitDistance':{GaitDistanceCapture:Capture,prepareGaitDistance:async()=>({})},'../store':{...store,generateSessionId:()=>fixtureId},'../recording':{recordingIssues:()=>[]}});
  h.engine.begin=()=>{h.engine.begun=true;beganAt=now;};
  h.engine.stop=reason=>{stopCalls++;return {schemaVersion:2,source:'device',platform:'sandbox-synthetic',guidanceEvents:[],startedAt:new Date().toISOString(),elapsedSeconds:(now-beganAt)/1000,stopReason:reason,streams:{accelerometer:[],gyroscope:[],magnetometer:[]},requestedHz:{accelerometer:50,gyroscope:50,magnetometer:50},units:{accelerometer:'g',gyroscope:'rad/s',magnetometer:'uT'}};};
  const advance=async(ms,note)=>{now+=ms;controls.push({action:'advance simulated clock',ms,note});h.advance(ms);await act(async()=>{});};
  const move=()=>{controls.push({action:'substitute motion window',context:'movement',note:'not physical gait'});h.engine.motionStatus={enough:true,placementReady:true,upright:false,steady:false,context:'movement'};};
  const settle=()=>{controls.push({action:'substitute motion window',context:'rest-or-quiet',note:'stable personal lean accepted'});h.engine.motionStatus={enough:true,placementReady:true,upright:false,steady:true,context:'rest-or-quiet'};};
  await act(async()=>{});settle();await advance(7000,'quiet personal baseline');
  assert.equal(h.engine.begun,false);move();await advance(1800,'fit movement');settle();await advance(4500,'fit settled');
  if(protocol==='research-walk'){
   await advance(9500,'start countdown');assert.equal(h.engine.begun,false,'stillness must not start research timer');
   move();await advance(500,'fresh candidate pulse');assert.equal(h.engine.begun,true);
   await advance(2000,'walking');settle();await advance(2000,'rest is retained');move();await advance((duration-4)*1000,'remaining recording duration');
  }else{
   if(tracked)await advance(5500,'wait for camera-ready handoff and renewed quiet gate');
   await advance(100,'mount actual clinical component');await advance(100,'start quiet auto-arm window');await advance(3200,'quiet auto-arm and silent Go');assert.equal(h.engine.begun,true);
   move();await advance(3000,'qualifying movement');
   if(tracked){
    camera.progress={usable:true,complete:false,courseProgressM:1};controls.push({action:'controlled distance boundary',metres:1});await advance(100,'central zone entered');
    settle();await advance(10000,'rest must not finish tracked 10MWT');assert.equal(stopCalls,0);
    camera.progress={usable:true,complete:false,courseProgressM:11};controls.push({action:'controlled distance boundary',metres:11});await advance(100,'central zone exited, deceleration still required');assert.equal(stopCalls,0);
    camera.progress={usable:true,complete:true,courseProgressM:12};controls.push({action:'controlled distance boundary',metres:12});await advance(100,'full 1+10+1 course complete');
   }else if(protocol==='2mwt'||protocol==='6mwt'){settle();await advance(10000,'rest must not end endurance capture');assert.equal(stopCalls,0);move();await advance((duration-13)*1000,'full protocol clock, no shortened duration');}
   else{settle();await advance(8100,'sustained stillness: finish warning');await advance(10200,'resume grace after warning: provisional endpoint');}
  }
  await advance(2500,'finish cue and persistence');
  assert.equal(stopCalls,1);assert.equal(h.navigated.at(-1)[0],'Result');
  const saved=await store.getSession(fixtureId);
  assert.ok(saved.recording);assert.equal(saved.isPractice,true);assert.equal(saved.participantId,profile.id);assert.equal(saved.assessment.completed,false);
  assert.equal((await store.getSessions()).length,1);assert.equal((await store.getParticipants()).length,1);
  if(protocol!=='research-walk'){assert.equal(saved.protocolExecution.protocol,protocol);assert.equal(saved.protocolExecution.clinicalOutcomeVerified,false);assert.equal(saved.protocolExecution.end,tracked?'distance-ended':protocol==='2mwt'||protocol==='6mwt'?'duration':'auto-stop-estimate');}
  const output=path.resolve(__dirname,'../dist/acceptance');fs.mkdirSync(output,{recursive:true});
  fs.writeFileSync(path.join(output,`${protocol}-${duration}${tracked?'-tracked':''}.json`),JSON.stringify({passed:true,physicalPhoneUsed:false,simulatedHardware:true,distanceAccuracyValidated:false,qualityValidated:false,controls,resultRoute:h.navigated.at(-1),saved},null,2));h.close();
 });
}

function clinicalHarness(protocol,audioEnabled=true,distance,holdReady=false,failRest=false){
 let now=0,tick,resolveIntro,resolveReady,rejectReady,alive=true,begun=0,goOptions,context='rest-or-quiet';
 const spoken=[],finished=[];
 const Component=load('components/ClinicalCapture',{
  'react-native':{View:'view'},
  './Screen':{Screen:({children,actions,navigation,...p})=>React.createElement('screen',p,navigation,children,actions),Body:'body',ui:{}},
  './BigButton':{__esModule:true,default:'button'},
  '../i18n':{Text:'text',t:x=>x},
 },{performance:{now:()=>now},setInterval:fn=>{tick=fn;return 1},clearInterval:()=>{tick=null}}).default;
 const say=(text,options)=>{
  spoken.push(text);
  if(failRest&&text.startsWith('If you are resting'))return Promise.reject(Error('Voice failed'));
  if(spoken.length===1)return new Promise(resolve=>{resolveIntro=resolve});
  if(text==='Ready. Stay still. I will say Go shortly.'&&holdReady)return new Promise((resolve,reject)=>{resolveReady=resolve;rejectReady=reject;});
  goOptions=options;return Promise.resolve();
 };
 let renderer;
 act(()=>{renderer=create(React.createElement(Component,{protocol,audioEnabled,say,distance,receiving:()=>alive,motion:()=>({enough:true,steady:context==='rest-or-quiet',context}),onBegin:()=>begun++,onFinish:e=>finished.push(e),onCancel(){}}));});
 const button=label=>renderer.root.findAllByType('button').find(n=>n.props.label===label);
 return {renderer,button,spoken,finished,get begun(){return begun},get goOptions(){return goOptions},
 ready:async()=>{await act(async()=>resolveIntro())},
 flush:async()=>{await act(async()=>Promise.resolve())},completeReady:async()=>{await act(async()=>resolveReady())},failReady:async()=>{await act(async()=>rejectReady(Error('Speech failed')))},
 advance:ms=>act(()=>{now+=ms;tick?.()}),loseSensors:()=>{alive=false},
 move:()=>{context='movement'},settle:()=>{context='rest-or-quiet'},
 close:()=>act(()=>renderer.unmount())};
}
test('Clinical start arms automatically after stillness and clocks from audible Go',async()=>{
 const h=clinicalHarness('2mwt');
 assert.equal(h.begun,0);
 await h.ready();h.advance(0);h.advance(3000);
 assert.equal(h.begun,0);await h.flush();assert.equal(h.begun,1);h.advance(700);
 assert.match(JSON.stringify(h.renderer.toJSON()),/I will say Go shortly/);
 act(()=>h.goOptions.onStart());
 h.advance(119900);assert.equal(h.finished.length,0);
 h.advance(100);assert.equal(h.finished.length,1);
 assert.equal(h.finished[0].elapsedFromGoSeconds,120);
 assert.equal(h.finished[0].goOffsetMs,700);assert.equal(h.finished[0].end,'duration');
 assert.deepEqual(h.spoken.slice(1),['Ready. Stay still. I will say Go shortly.','Go.']);h.close();
});
test('Six-minute protocol continues through stationary time and ends automatically',async()=>{
 const h=clinicalHarness('6mwt',false);await h.ready();
 h.advance(0);h.advance(3000);
 h.advance(359900);assert.equal(h.finished.length,0);
 h.advance(100);assert.equal(h.finished[0].elapsedFromGoSeconds,360);
 assert.equal(h.finished[0].goSource,'automatic-silent-cue');assert.equal(h.spoken.length,1);h.close();
});

test('Tracked 10MWT keeps rests, finishes only at the live 12 m boundary and interrupts lost tracking',async()=>{
 let current={initialized:true,integrity:true,positionStdMetres:.02,walkProgress:{usable:true,zone:'approach',complete:false}};
 const h=clinicalHarness('10mwt',false,()=>({...current,receivedAt:Date.now()}));await h.ready();h.advance(0);h.advance(3000);
 h.move();h.advance(4000);h.settle();h.advance(20000);assert.equal(h.finished.length,0);
 current.walkProgress={usable:true,zone:'finish',complete:false};h.advance(100);assert.equal(h.finished.length,0);
 current.walkProgress={usable:true,zone:'complete',complete:true};h.advance(100);assert.equal(h.finished[0].end,'distance-ended');assert.equal(h.finished[0].clinicalOutcomeVerified,false);h.close();
 const loss=clinicalHarness('10mwt',false,()=>({...current,integrity:false,receivedAt:Date.now()}));await loss.ready();loss.advance(0);loss.advance(3000);loss.advance(100);assert.equal(loss.finished[0].end,'interrupted');loss.close();
 const stale=clinicalHarness('10mwt',false,()=>({...current,receivedAt:Date.now()-2000}));await stale.ready();stale.advance(0);stale.advance(3000);stale.advance(100);assert.equal(stale.finished[0].end,'interrupted');stale.close();
});
test('TUG and 10MWT allow a resume grace before provisional saving; capture limit is not completion',async()=>{
 for(const protocol of ['tug','10mwt']){
  const h=clinicalHarness(protocol,false);await h.ready();
  h.advance(0);h.advance(3000);h.move();h.advance(100);h.advance(4000);h.settle();h.advance(100);h.advance(8000);assert.equal(h.finished.length,0);h.advance(10000);
  assert.equal(h.finished[0].end,'auto-stop-estimate');assert.equal(h.finished[0].clinicalOutcomeVerified,false);h.close();
  const capped=clinicalHarness(protocol,false);await capped.ready();
  capped.advance(0);capped.advance(3000);
  capped.advance(180000);assert.equal(capped.finished[0].end,'capture-limit');capped.close();
 }
});

test('Rest warning completes before the grace clock and renewed movement cancels its finish',async()=>{
 const h=clinicalHarness('tug',true);await h.ready();h.advance(0);h.advance(3000);await h.flush();
 act(()=>h.goOptions.onStart());h.move();h.advance(100);h.advance(2500);h.settle();h.advance(100);h.advance(8000);
 assert.equal(h.finished.length,0);assert.ok(h.spoken.some(s=>s.startsWith('If you are resting')));
 h.advance(20000);assert.equal(h.finished.length,0); // Promise completion has not been delivered yet.
 h.move();h.advance(100);await h.flush();h.advance(12000);assert.equal(h.finished.length,0);
 h.settle();h.advance(100);h.advance(8000);await h.flush();h.advance(9900);assert.equal(h.finished.length,0);
 h.advance(100);assert.equal(h.finished[0].end,'auto-stop-estimate');h.close();
});

test('Returning participant confirms the aid without repeating demographic intake',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());const first=h.navigated[0][1];
 act(()=>h.button('Previous').props.onPress());act(()=>h.button('Previous').props.onPress());
 assert.equal(h.renderer.root.findAllByProps({accessibilityLabel:'Age in years'}).length,0);
 act(()=>h.button('Quad cane').props.onPress());act(()=>h.button('Continue').props.onPress());act(()=>h.button('Continue').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());const second=h.navigated[1][1];
 assert.equal(second.participantId,first.participantId);assert.equal(second.demographics.ageYears,67);
 assert.equal(second.participantSnapshot.clinical.assistiveDevice,'quad-cane');assert.equal(h.savedProfiles.size,1);h.close();
});

test('A failed rest warning cannot silently save a completed test',async()=>{
 const h=clinicalHarness('10mwt',true,undefined,false,true);await h.ready();h.advance(0);h.advance(3000);await h.flush();
 act(()=>h.goOptions.onStart());h.move();h.advance(100);h.advance(2500);h.settle();h.advance(100);h.advance(8000);await h.flush();
 h.advance(30000);assert.equal(h.finished.length,0);assert.match(JSON.stringify(h.renderer.toJSON()),/finish warning could not be played/);
 h.advance(180000);assert.equal(h.finished[0].end,'capture-limit');h.close();
});

test('Signal overview tap maps the actual chart width to a bounded recording time',()=>{
 const Chart=load('components/SignalChart',{'react-native':{View:'view',Pressable:'pressable'},'react-native-svg':{__esModule:true,default:'svg',Polyline:'polyline',Line:'line'},'../i18n':{Text:'text',t:s=>s,useLanguage:()=>{}},'./Screen':{ui:{}}}).default;
 const selected=[];let renderer;act(()=>{renderer=create(React.createElement(Chart,{samples:[{elapsedMs:0,x:0,y:1,z:2},{elapsedMs:359900,x:1,y:2,z:3}],start:0,end:360,units:'g',onSelectTime:s=>selected.push(s)}));});
 const plot=renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityLabel==='Inspect a moment in the recording');
 act(()=>plot.props.onLayout({nativeEvent:{layout:{width:640}}}));
 act(()=>plot.props.onPress({nativeEvent:{locationX:320}}));assert.equal(selected[0],180);
 act(()=>plot.props.onPress({nativeEvent:{locationX:700}}));assert.equal(selected[1],360);
 assert.equal(renderer.root.findAllByType('polyline').length,3);act(()=>renderer.unmount());
});
test('Missing Go callbacks and lost sensors interrupt clinical capture instead of inventing time',async()=>{
 const h=clinicalHarness('tug');await h.ready();
 h.advance(0);h.advance(3000);await h.flush();
 h.advance(10000);assert.equal(h.finished[0].goOffsetMs,null);assert.equal(h.finished[0].elapsedFromGoSeconds,null);
 assert.equal(h.finished[0].end,'interrupted');h.close();
 const loss=clinicalHarness('2mwt',false);await loss.ready();
 loss.advance(0);loss.advance(3000);
 loss.loseSensors();loss.advance(100);assert.equal(loss.finished[0].end,'interrupted');loss.close();
});

test('Every clinical test waits for the full ready warning before capture and audible Go',async()=>{
 const checks=[];
 for(const protocol of ['10mwt','tug','2mwt','6mwt']){
   const h=clinicalHarness(protocol,true,undefined,true);await h.ready();h.advance(0);h.advance(3000);
   h.advance(7000);assert.equal(h.begun,0);assert.equal(h.finished.length,0);assert.ok(!h.spoken.includes('Go.'));
   await h.completeReady();assert.equal(h.begun,1);assert.equal(h.spoken.at(-1),'Go.');
   h.advance(800);assert.equal(h.finished.length,0);act(()=>h.goOptions.onStart());
   h.advance(100);assert.equal(h.finished.length,0);
   checks.push({protocol,passed:true,spoken:h.spoken,controls:[{atMs:0,action:'Finish test-specific introduction; remain still'},{atMs:3000,action:'Three seconds quiet starts ready warning; capture has not begun'},{atMs:10000,action:'Finish delayed ready warning; capture begins and Go is requested'},{atMs:10800,action:'Deliver speech onStart for Go; clinical timer starts here'},{atMs:10900,action:'Verify no premature finish'}]});h.close();
 }
 const out=path.resolve(__dirname,'../dist/acceptance/elder-audio-flow.json');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify({simulatedSpeechCallbacks:true,audibleSpeechValidated:false,olderAdultUsabilityStudy:false,checks},null,2));
});

test('Movement during the ready warning rechecks stillness; cancellation and voice errors cannot launch a test',async()=>{
 const h=clinicalHarness('tug',true,undefined,true);await h.ready();h.advance(0);h.advance(3000);h.move();await h.completeReady();
 assert.equal(h.begun,0);assert.ok(!h.spoken.includes('Go.'));h.settle();h.advance(0);h.advance(3000);await h.completeReady();assert.equal(h.begun,1);h.close();
 const cancelled=clinicalHarness('2mwt',true,undefined,true);await cancelled.ready();cancelled.advance(0);cancelled.advance(3000);cancelled.close();await cancelled.completeReady();assert.equal(cancelled.begun,0);
 const failed=clinicalHarness('6mwt',true,undefined,true);await failed.ready();failed.advance(0);failed.advance(3000);await failed.failReady();assert.equal(failed.begun,0);assert.ok(!failed.spoken.includes('Go.'));failed.close();
});

test('Patient clinical cues are brief, fully translated and never instruct walking during the ready warning',async()=>{
 const {protocolFlows,clinicalReady}=load('protocolFlow'),{messages}=load('translations'),language=load('language');
 for(const protocol of ['10mwt','tug','2mwt','6mwt']){
   const f=protocolFlows[protocol];assert.ok(f.intro.split(/\s+/).length<=40);assert.match(f.intro,/When I say Go/);assert.ok(f.finish.split(/\s+/).length<=12);
   for(const key of [f.intro,f.active,f.finish,clinicalReady])for(const lang of ['ms','zh']){assert.ok(messages[key],key);assert.notEqual(language.translate(key,lang),key);}
   const h=clinicalHarness(protocol,true,undefined,true);await h.ready();h.advance(0);h.advance(3000);
   const bodies=h.renderer.root.findAllByType('body').map(n=>n.props.children);
   assert.ok(bodies.includes(clinicalReady));assert.ok(!bodies.includes(f.active));h.close();
 }
 for(const key of ['Getting the phone ready…','Stand comfortably and let the phone settle.','Keep still for a moment.','Phone check. Stand comfortably and keep still. You can use your usual walking aid.','Reading file: {0}%','Checking and saving the recording…','Stay still. No buttons are needed.'])assert.ok(messages[key],key);
});
test('Every clinical protocol branches after fit checks and disables generic direction guidance',()=>{
 for(const protocol of ['10mwt','tug','2mwt','6mwt']){
  const h=harness('RecordScreen','android',null,{assessmentSetup:{protocol}});
  h.advance(24000);
  h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);
  h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(4000);
  const child=h.renderer.root.findByType('clinical');
  assert.equal(child.props.protocol,protocol);assert.equal(h.engine.baselinePreserved,true);assert.equal(h.engine.options.guidanceEnabled,false);
  assert.equal(h.engine.begun,false);
  act(()=>child.props.onBegin());assert.equal(h.engine.begun,true);
  assert.ok(!h.spoke.includes('Begin walking now. The recording starts when you take your first step.'));
  h.close();
 }
});
test('Main camera capture follows each clinical Go/end and never injects the separate practice trial',async()=>{
 for(const protocol of ['10mwt','tug','2mwt','6mwt']){
  const calls=[],saved=[];let camera,resolveFinished;
  class Capture{
   constructor(id,p){camera=this;this.attachment={sessionId:id,protocol:p,status:'capturing'};calls.push('camera-start');}
   async ready(){calls.push('camera-ready');}begin(){calls.push('camera-begin');}finish(reason){calls.push('camera-end:'+reason);}
   finished(){return new Promise(r=>resolveFinished=r);}async attach(){calls.push('attach');}async cancel(){calls.push('cancel');}
  }
  const speech={speak:async()=>{},speakQueued:async text=>calls.push(text),discardPendingSpeech(){},stopSpeaking(){}};
  const h=harness('RecordScreen','android',null,{audioEnabled:false,useCameraDistance:true,assessmentSetup:{protocol}},{'../gaitDistance':{GaitDistanceCapture:Capture,prepareGaitDistance:async()=>({})},'../audio':speech,'../recording':{recordingIssues:()=>[]},'../store':{generateSessionId:()=> 'test',saveSession:async s=>saved.push(s)}});
  await act(async()=>{});assert.deepEqual(calls,[]);h.advance(24000);await act(async()=>{});assert.deepEqual(calls,[]);h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);await act(async()=>{});assert.deepEqual(calls,[]);h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(4000);await act(async()=>{});h.advance(5100);await act(async()=>{});
  const child=h.renderer.root.findByType('clinical');assert.deepEqual(calls,['camera-start','camera-ready']);act(()=>child.props.onBegin());assert.equal(calls.includes('camera-begin'),false);act(()=>child.props.onGo(12));assert.equal(calls.at(-1),'camera-begin');
  h.engine.stop=reason=>({startedAt:'2026-10-09T00:00:00Z',elapsedSeconds:120,stopReason:reason});
  act(()=>child.props.onFinish({version:'protocol-flow-v1',protocol,goOffsetMs:12,elapsedFromGoSeconds:120,goSource:'automatic-silent-cue',end:'duration',clinicalOutcomeVerified:false}));
  assert.equal(calls.at(-1),'camera-end:completed');await act(async()=>{});h.advance(2000);await act(async()=>{});
  assert.equal(saved.length,1);assert.equal(saved[0].cameraDistance.sessionId,saved[0].id);assert.equal(saved[0].assessment.completed,false);assert.ok(calls.includes('attach'));h.close();resolveFinished?.();await act(async()=>{});
 }
});

test('Camera startup occurs after pouch-fit movement and Go waits for native readiness and completed speech',async()=>{
 let nativeReady,voiceDone;const calls=[];
 class Capture{
  constructor(){calls.push('camera-start');}ready(){return new Promise(resolve=>nativeReady=resolve);}async cancel(){}
 }
 const cue='Movement check complete. Stay still while camera tracking starts.';
 const speech={speak:async()=>{},speakQueued:async text=>{if(text===cue)await new Promise(resolve=>voiceDone=resolve);},discardPendingSpeech(){},stopSpeaking(){}};
 const h=harness('RecordScreen','android',null,{audioEnabled:true,useCameraDistance:true,assessmentSetup:{protocol:'2mwt'}},{'../gaitDistance':{GaitDistanceCapture:Capture,prepareGaitDistance:async()=>({})},'../audio':speech});
 await act(async()=>{});h.advance(24000);await act(async()=>{});assert.deepEqual(calls,[]);
 h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);await act(async()=>{});assert.deepEqual(calls,[]);
 h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(4000);await act(async()=>{});assert.deepEqual(calls,['camera-start']);
 h.advance(5100);await act(async()=>{});assert.equal(h.renderer.root.findAllByType('clinical').length,0);
 await act(async()=>nativeReady());h.advance(100);assert.equal(h.renderer.root.findAllByType('clinical').length,0);
 await act(async()=>voiceDone());h.advance(100);assert.equal(h.renderer.root.findAllByType('clinical').length,1);h.close();
 const {messages}=load('translations');for(const key of [cue,'Stand still while camera tracking starts.','Camera tracking could not start. No test started. Rest, then check the phone when safe.'])assert.ok(messages[key],key);
});
test('Shared preview and protocol guidance strings are translated into Malay and Chinese',()=>{
 const {messages}=load('translations'),{protocolFlows,assistedNotice,clinicalGo,clinicalInterrupted,clinicalLimit}=load('protocolFlow');
 for(const flow of Object.values(protocolFlows))for(const key of [flow.intro,flow.active,flow.finish])assert.ok(messages[key],key);
 for(const key of [assistedNotice,clinicalGo,clinicalInterrupted,clinicalLimit])assert.ok(messages[key],key);
});

test('New translations contain real Chinese text and no encoding replacement runs',()=>{
 for(const name of ['protocolMessages','experienceMessages']){
  const catalog=load(name)[name];
  for(const [key,values] of Object.entries(catalog)){
   assert.doesNotMatch(key,/\?{2,}/,key);
   for(const value of values)assert.doesNotMatch(value,/\?{2,}/,key);
   assert.match(values[1],/[\u3400-\u9fff]/,key);
  }
 }
});


test('Short Google trial requires a measured route and stays separate from clinical test choices',()=>{
 const h=harness('GoogleDistanceTrialScreen');
 assert.equal(h.button('Set up this short trial').props.disabled,true);
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'I measured this route and the path is clear.'}).props.onPress());
 act(()=>h.button('Set up this short trial').props.onPress());
 const [name,p]=h.navigated[0];assert.equal(name,'Prepare');assert.equal(p.googleDistanceTrial.referenceDistanceM,3);assert.equal(p.assessmentSetup.protocol,'research-walk');assert.equal(p.isPractice,true);assert.equal(p.useGoogleDistance,true);assert.equal(p.useGpsDistance,false);
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Route length: 2 m'}).props.onPress());
 assert.equal(h.button('Set up this short trial').props.disabled,true);h.close();
});

test('Separate Google experiment offers a labelled 5 m out-and-back route without entering 10MWT',()=>{
 const h=harness('GoogleDistanceTrialScreen');
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'10 m total · 5 m out and back'}).props.onPress());
 assert.equal(h.button('Set up this short trial').props.disabled,true);
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'I measured this route and the path is clear.'}).props.onPress());
 act(()=>h.button('Set up this short trial').props.onPress());
 const [name,p]=h.navigated[0];
 assert.equal(name,'Prepare');assert.equal(p.duration,90);
 assert.equal(p.googleDistanceTrial.referenceDistanceM,10);
 assert.equal(p.googleDistanceTrial.routePattern,'5m-out-and-back');
 assert.equal(p.assessmentSetup.protocol,'research-walk');
 assert.equal(p.assessmentSetup.courseLengthM,5);
 assert.equal(p.isPractice,true);h.close();
});

test('Short-trial stop gate needs an armed walk followed by continuous stillness',()=>{
 const {GoogleTrialStopGate}=load('googleDistanceTrial');const g=new GoogleTrialStopGate();
 assert.equal(g.update(10000,true,true,true),null);g.begin(10000);
 assert.equal(g.update(11000,true,true,true),null);
 assert.equal(g.update(14900,true,true,true),null);
 assert.equal(g.update(15000,true,true,false),null);
 assert.equal(g.update(16000,true,true,true),null);
 assert.equal(g.update(19000,true,false,true),null);
 assert.equal(g.update(20000,true,true,true),null);
 assert.equal(g.update(24000,true,true,true),'quiet-stop');
 const cap=new GoogleTrialStopGate();cap.begin(0);assert.equal(cap.update(60000,true,true,false),'time-limit');
 const lost=new GoogleTrialStopGate();lost.begin(0);assert.equal(lost.update(100,true,true,false),null);assert.equal(lost.update(200,false,true,true),'interrupted');
});

test('Out-and-back Google trial tolerates a brief turn pause but ends after 8 seconds at the return mark',()=>{
 const {GoogleTrialStopGate}=load('googleDistanceTrial');const gate=new GoogleTrialStopGate(8,90);
 gate.begin(0);
 assert.equal(gate.update(10000,true,true,true),null);
 assert.equal(gate.update(16000,true,true,true),null);
 assert.equal(gate.update(17000,true,true,false),null);
 assert.equal(gate.update(30000,true,true,true),null);
 assert.equal(gate.update(38000,true,true,true),'quiet-stop');
 const limit=new GoogleTrialStopGate(8,90);limit.begin(0);
 assert.equal(limit.update(89000,true,true,false),null);
 assert.equal(limit.update(90000,true,true,false),'time-limit');
});

test('Short-trial recording waits for a step then ends hands-free after quiet, rather than waiting 60 seconds',()=>{
 const h=harness('RecordScreen','android',null,{duration:60,googleDistanceTrial:{version:'google-distance-trial-v1',referenceDistanceM:3},assessmentSetup:{protocol:'research-walk'}});
 h.engine.stop=r=>({stopReason:r,startedAt:'2026-10-02T00:00:00Z',elapsedSeconds:6,streams:{accelerometer:[],gyroscope:[],magnetometer:[]},guidanceEvents:[]});
 h.advance(24000);h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);
 h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(13000);
 assert.equal(h.engine.begun,false);
 h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(200);
 assert.equal(h.engine.begun,true);h.advance(2000);
 h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(4100);
 assert.equal(h.renderer.root.findByType('screen').props.title,'Take a comfortable rest');
 assert.ok(h.spoke.includes(load('googleDistanceTrial').googleTrialFinish));h.close();
});


test('Trial preparation skips clinical test selection and hides unrelated defaults and GPS',async()=>{
 const h=harness('PrepareScreen','android',null,{duration:60,useGoogleDistance:true,googleDistanceTrial:{version:'google-distance-trial-v1',referenceDistanceM:3},assessmentSetup:{protocol:'research-walk',courseLengthM:3}});
 await act(async()=>{});
 act(()=>{h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.onChangeText('67');});
 act(()=>h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio').props.onPress());act(()=>h.button('Continue').props.onPress());
 assert.equal(h.renderer.root.findByType('screen').props.title,'Sound and readiness');
 act(()=>h.button('Language and audio settings').props.onPress());
 assert.equal(h.button('Use default settings'),undefined);
 assert.equal(h.renderer.root.findAllByProps({accessibilityLabel:'Optional outdoor GPS distance cross-check'}).length,0);
 const google=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityLabel?.startsWith('Google distance test'));
 assert.equal(google.props.disabled,true);assert.equal(google.props.accessibilityState.checked,true);h.close();
});


test('Test-created profiles retain full clinical context without changing earlier snapshots',()=>{
 const {resolveTestParticipant:resolve}=load('testParticipant');
 const input={newId:'p1',label:'P01',ageYears:67,sex:'female',heightCm:160,weightKg:61,assistiveDevice:'quad-cane',strokeType:' ischemic ',lesionLocation:' subcortical ',premorbidGaitNotes:' prior limp ',jointOrOrthopaedicNotes:' knee surgery '};
 const first=resolve([],input);
 assert.equal(first.demographics.weightKg,61);assert.equal(first.clinical.strokeType,'ischemic');assert.equal(first.clinical.lesionLocation,'subcortical');assert.equal(first.clinical.premorbidGaitNotes,'prior limp');assert.equal(first.clinical.jointOrOrthopaedicNotes,'knee surgery');
 const updated=resolve([first],{...input,id:'p1',strokeType:'hemorrhagic',weightKg:62});
 assert.equal(first.clinical.strokeType,'ischemic');assert.equal(first.demographics.weightKg,61);assert.equal(updated.clinical.strokeType,'hemorrhagic');
 for(const weightKg of [NaN,19,301])assert.throws(()=>resolve([],{...input,weightKg}),/weight/);
 assert.equal(resolve([first],{newId:'p1',id:'p1',label:'P01',ageYears:67,sex:'female',heightCm:160,assistiveDevice:'none'}).clinical.premorbidGaitNotes,'prior limp');
});

test('Profile completion prompts are translated and clinical guides link the supplied database',()=>{
 const {messages}=load('translations'),{protocolGuides}=load('protocolGuides');
 for(const key of ['Clinical history is required for clinical tests. For research participants, record what is known.','Open clinical protocol source','Could not open the protocol source.','Stroke type (optional)','Lesion location (optional)','Weight kg','Pre-existing gait pattern/asymmetry','Joint conditions or orthopaedic history'])assert.ok(messages[key],key);
 for(const protocol of ['10mwt','tug','2mwt','6mwt'])assert.match(protocolGuides[protocol].sourceUrl,/^https:\/\/www\.sralab\.org\/rehabilitation-measures\//);
 assert.equal(protocolGuides['research-walk'].sourceUrl,undefined);
});


test('Setup clinical and physical details reach the saved profile and recording snapshot',async()=>{
 const h=harness('PrepareScreen');await act(async()=>{});
 act(()=>h.button('Walking aid and health details').props.onPress());act(()=>h.button('Review stroke history').props.onPress());
 for(const [label,value] of [['Stroke type (optional)','ischemic'],['Lesion location (optional)','subcortical'],['Pre-existing gait pattern/asymmetry','prior limp'],['Joint conditions or orthopaedic history','knee surgery']])act(()=>h.renderer.root.findByProps({accessibilityLabel:label}).props.onChangeText(value));
 act(()=>h.button('Done').props.onPress());act(()=>h.button('Walking aid and health details').props.onPress());
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Weight kg'}).props.onChangeText('61'));
 act(()=>h.button('Done').props.onPress());await h.finishSetup();
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());
 const profile=h.navigated[0][1].participantSnapshot;
 assert.equal(profile.demographics.weightKg,61);assert.equal(profile.clinical.strokeType,'ischemic');assert.equal(profile.clinical.lesionLocation,'subcortical');assert.equal(profile.clinical.premorbidGaitNotes,'prior limp');assert.equal(profile.clinical.jointOrOrthopaedicNotes,'knee surgery');
 assert.equal(h.savedProfiles.get(profile.id).clinical.premorbidGaitNotes,'prior limp');h.close();
});


test('Observer G.A.I.T. has 31 source-bounded items and no total for missing observations',()=>{
 const {gaitRubric,GAIT_FORM_VERSION}=load('gaitRubric');const {newGaitAssessment,gaitAssessmentSummary,validGaitAssessment}=load('gaitAssessment');
 assert.equal(gaitRubric.length,31);assert.equal(gaitRubric.reduce((n,i)=>n+i.max,0),62);
 const g=newGaitAssessment();assert.equal(g.version,GAIT_FORM_VERSION);assert.equal(gaitAssessmentSummary(g).total,null);
 for(const i of gaitRubric)g.ratings[i.id]={optionId:i.options.find(o=>o.score===i.max).id,notes:'',qualifiers:load('gaitAssessment').gaitQualifiers(i.id).filter(v=>!['left','extension'].includes(v))};
 assert.equal(gaitAssessmentSummary(g).total,null);g.assessor='RATER';g.limb='left';g.observationSource='video';
 assert.equal(gaitAssessmentSummary(g).total,62);assert.equal(validGaitAssessment(g),true);
 g.ratings['11'].optionId=null;assert.equal(gaitAssessmentSummary(g).rated,30);assert.equal(gaitAssessmentSummary(g).total,null);
 g.ratings['11'].optionId='31-0';assert.equal(validGaitAssessment(g),false);
});
test('Observer G.A.I.T. retains equal-score branch choices and multilingual interface coverage',()=>{
 const {gaitRubric}=load('gaitRubric'),{gaitMessages}=load('gaitMessages');
 const knee=gaitRubric.find(i=>i.id===13);assert.equal(new Set(knee.options.map(o=>o.branch)).size,4);assert.equal(knee.options.length,16);
 for(const i of gaitRubric){assert.ok(gaitMessages[`G.A.I.T. item ${i.id}`]);assert.equal(new Set(i.options.map(o=>o.id)).size,i.options.length);}
 for(const [key,values] of Object.entries(gaitMessages)){assert.match(values[1],/[\u3400-\u9fff]/,key);for(const v of values)assert.doesNotMatch(v,/\?{2,}/);}
 const {messages}=load('translations');for(const [k,v] of Object.entries(messages)){assert.doesNotMatch(k,/\?{3,}/);for(const s of v)assert.doesNotMatch(s,/\?{3,}/,k);}
});


test('Sensor-free lab is disabled in release and native contexts, and never contains measured streams',()=>{
 const env={env:{EXPO_PUBLIC_FLOW_LAB:'1'}};
 assert.equal(load('flowLab',{}, {__DEV__:false,document:{},process:env}).flowLabEnabled,false);
 assert.equal(load('flowLab',{}, {__DEV__:true,process:env}).flowLabEnabled,false);
 const lab=load('flowLab',{}, {__DEV__:true,document:{},process:env});assert.equal(lab.flowLabEnabled,true);
 const f=lab.flowLabFixtures();assert.equal(f.session.recording,undefined);assert.equal(f.session.isPractice,true);assert.equal(f.session.windows.length,0);
});


test('Calibration round voice completes each instruction before announcing the latest round',async()=>{
 const g=load('lensGuidance');const spoken=[];let done;const guide=g.createLensVoiceGuide(text=>{spoken.push(text);return new Promise(r=>done=r);},error=>{throw error;});
 const flush=()=>new Promise(r=>setImmediate(r));
 guide.update('side-angles',g.lensRoundCue('side-angles','computer'),'computer');
 guide.update('high-low-angles',g.lensRoundCue('high-low-angles','computer'),'computer');
 assert.equal(spoken.length,1,'No interruption while side-angle instruction plays');
 done();await flush();assert.equal(spoken[1],'Side angles complete.');
 done();await flush();assert.match(spoken[2],/above the board centre and aim down/);
 guide.update('horizontal','Move the phone a little sideways, watching the computer framing.','computer');
 guide.update('vertical','Move the phone a little up and down, watching the computer framing.','computer');
 done();await flush();assert.equal(spoken[3],'High and low angles complete.');
 done();await flush();assert.match(spoken[4],/up and down/,'Only latest needed instruction plays');
 guide.stop();done();await guide.completion;
 assert.equal(spoken.length,5);
 for(const text of [...Object.values(g.roundLabels),...spoken])for(const lang of ['ms','zh'])assert.notEqual(load('language').translate(text,lang),text,text);
});

test('Distance practice, no-walk, route choices and noise-processing feedback translate in every patient language',()=>{
 for(const text of ['Capture saved.','Route shape','Straight route','Route with turns','Wait for the practice cue.','Practice, return to the start, then stand still.','Take a few comfortable practice steps, turn and return to your start mark. Then stand still. This is practice, not the measured walk.','Practice complete. The measured walk starts after this instruction. Walk to your finish mark, then stand still. Begin walking now.','No walking was detected. The trial is saved.','Your computer is checking sensor noise.','Check saved sensor noise','Short-term sensor noise checked. Distance accuracy still needs a walking trial.','Sensor noise needs review. Keep the saved capture.'])
  for(const lang of ['ms','zh'])assert.notEqual(load('language').translate(text,lang),text,text);
});
test('Personal stance accepts stable lean, preserves raw tilt, and still rejects motion and data gaps',()=>{
 const {motionWindow,SettlingGate}=load('movement'),{ShiftMonitor}=load('placement');
 const samples=(angle,shake=false)=>Array.from({length:251},(_,i)=>{const a=angle*Math.PI/180;return {x:Math.cos(a)+(shake?.2*Math.sin(i):0),y:Math.sin(a),z:0,elapsedMs:i*20,sensorTimestampSeconds:i*.02,receivedAtUnixMs:i*20};});
 const gyro=Array.from({length:251},(_,i)=>({x:0,y:0,z:0,elapsedMs:i*20,sensorTimestampSeconds:i*.02,receivedAtUnixMs:i*20}));
 for(const angle of [-55,-35,0,35,55]){
  const a=samples(angle),m=motionWindow(a,gyro,true);assert.equal(m.placementReady,true);assert.equal(m.steady,true);
  const gate=new SettlingGate(5000);assert.equal(gate.update(0,true,m),false);assert.equal(gate.update(5000,true,m),true);
  const shift=new ShiftMonitor(a[0]);assert.equal(shift.update(0,a),null);assert.equal(shift.update(5000,a),null);
  const changed=samples(angle+25);assert.equal(shift.update(6000,changed),null);assert.ok(shift.update(8500,changed)>15);
 }
 const bad=motionWindow(samples(35,true),gyro,true),gate=new SettlingGate(5000);assert.equal(gate.update(0,true,bad),false);assert.equal(gate.update(10000,true,bad),false);
 const gap=samples(35).filter((_,i)=>i<50||i>100);assert.equal(motionWindow(gap,gyro,true).enough,false);
});
test('Recorder saves a quiet tilted baseline and exports its reference without rewriting sensor axes',()=>{
 let now=0;const sensor={};const {SensorRecorder}=load('sensors',{'expo-sensors':{Accelerometer:sensor,Gyroscope:sensor,Magnetometer:sensor},'react-native':{Platform:{OS:'android',Version:11}},'./releaseInfo':{releaseInfo:()=>({})}},{performance:{now:()=>now}});
 const r=new SensorRecorder({guidanceEnabled:false,voiceEnabled:false},()=>{},()=>{}),a=35*Math.PI/180;
 for(let i=0;i<=275;i++){now=i*20;for(const [n,v] of [['accelerometer',[Math.cos(a),Math.sin(a),0]],['gyroscope',[0,0,0]],['magnetometer',[30,0,0]]])r.receive(n,{x:v[0],y:v[1],z:v[2],timestamp:now/1000});}
 assert.equal(r.baselineReady,true);r.preserveSetupBaseline();r.begin();now+=20;r.receive('accelerometer',{x:Math.cos(a),y:Math.sin(a),z:0,timestamp:now/1000});const recording=r.stop('completed');
 assert.ok(Math.abs(recording.baseline.postureReference.phoneTiltFromLandscapeDegrees-35)<1e-8);assert.equal(recording.baseline.rawWalkingValuesCorrected,false);assert.equal(recording.baseline.postureReference.anatomicalPostureVerified,false);assert.equal(recording.streams.accelerometer[0].x,Math.cos(a));
 const e=load('exportData'),session={id:'posture-test',date:new Date().toISOString(),duration:10,isPractice:false,windows:[],recording};const exported=JSON.parse(e.exportJSON(session));assert.equal(exported.session.recording.baseline.postureReference.version,'personal-gravity-reference-v1');assert.match(e.exportCSV(session),/phone_tilt_from_landscape_deg/);
});


test('A new phone must finish setup before profile entry; returning from setup preserves the flow',async()=>{
 let profile=null;
 const h=harness('PrepareScreen','android',null,{}, {'../onDeviceSetup':{phoneDistanceProfile:async()=>profile}});
 await act(async()=>{});
 assert.equal(h.renderer.root.findByType('screen').props.title,'Before your first walk');
 assert.equal(h.renderer.root.findAllByType('input').length,0);assert.equal(h.button('Start test'),undefined);
 act(()=>h.button('Set up this phone').props.onPress());assert.equal(h.navigated[0][0],'PhoneSetup');assert.equal(h.savedProfiles.size,0);
 profile={testOnly:true};await h.focus();
 assert.equal(h.renderer.root.findByType('screen').props.title,'Who is walking?');
 assert.equal(h.renderer.root.findAllByProps({accessibilityLabel:'Study ID or participant label'}).length,0);
 await h.finishSetup();act(()=>h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());
 const saved=h.navigated.find(n=>n[0]==='Record')[1];assert.match(saved.participantLabel,/^GT-[A-Z0-9]+/);
 assert.equal(h.savedProfiles.get(saved.participantId).label,saved.participantLabel);assert.equal(saved.demographics.ageYears,67);h.close();
});

test('Missing phone setup never erases entered demographics when discovered again at test start',async()=>{
 let profile={testOnly:true};
 const h=harness('PrepareScreen','android',null,{}, {'../onDeviceSetup':{phoneDistanceProfile:async()=>profile},'../gaitDistance':{prepareGaitDistance:async()=>{throw new Error('Phone setup changed or has not completed. Set up this phone again.');}}});
 await h.finishSetup();act(()=>h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());assert.equal(h.renderer.root.findByType('screen').props.title,'Before your first walk');assert.equal(h.savedProfiles.size,0);
 await h.focus();act(()=>h.button('Previous').props.onPress());act(()=>h.button('Previous').props.onPress());assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.value,'67');h.close();
});

test('Automatic participant labels are stable, avoid existing labels and do not encode demographics',()=>{
 const {automaticStudyLabel:label}=load('testParticipant');const id='participant-123456789-abcdef12';
 const first=label([],id);assert.equal(first,label([],id));assert.match(first,/^GT-[A-Z0-9]+$/);
 assert.notEqual(label([{id:'another',label:first}],id),first);
 assert.notEqual(label([],id),label([],id+'X'));
});


test('Explicit motion-only choice preserves real collection without claiming camera distance or requiring calibration',async()=>{
 let cameraChecks=0;
 const h=harness('PrepareScreen','android',null,{}, {'../onDeviceSetup':{phoneDistanceProfile:async()=>null},'../gaitDistance':{prepareGaitDistance:async()=>{cameraChecks++;throw Error('Must not request camera calibration');}}});await act(async()=>{});
 assert.ok(h.button('Set up this phone'));act(()=>h.button('Record motion only').props.onPress());await h.finishSetup();
 act(()=>h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox').props.onPress());await act(async()=>h.button('Start test').props.onPress());
 assert.equal(cameraChecks,0);assert.equal(h.navigated[0][0],'Record');assert.equal(h.navigated[0][1].useCameraDistance,false);assert.match(h.navigated[0][1].participantLabel,/^GT-/);h.close();
});
