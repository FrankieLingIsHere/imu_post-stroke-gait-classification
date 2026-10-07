const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const React = require('react');
const { create, act } = require('react-test-renderer');
function load(name, mocks = {}, globals = {}, cache = {}) {
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
  '../cameraCalibration':{calibrationBridge:()=>bridge,async currentLensReport(){return null;},async savedReference(){return null;},async retainCalibrationCapture(r){return r;},async recoverLensReport(r){return r.report;}},
  '../referenceCalibration':{createLensFeedback(){return{send(){},close(){}};},async calibrationComputer(){return computer;},async pendingReference(){return null;},async savedReference(){return null;},async showComputerBoard(){},async submitAlignment(){uploads++;},async pollReference(){return {distanceReady:false};}}};
 const C=load('screens/PhoneCalibrationScreen',mocks).default;let tree;await act(async()=>{tree=create(React.createElement(C,{navigation:{goBack(){}}}));});
 const button=label=>tree.root.findAllByType('Button').find(n=>n.props.label===label);
 await act(async()=>{button('Calibrate camera lens').props.onPress();});assert.equal(resolveLens,undefined);
 await act(async()=>voice());assert.equal(typeof resolveLens,'function');
 assert.match(voices[0],/Watch the framing on your computer/);
 assert.ok(button('Share digital board')===undefined,'Actions are hidden during capture');
 act(()=>progress({phase:'lens',imageUri:'file:///view.jpg',lens:JSON.stringify({acceptedViews:12,hint:'Tilt the board view gently.'})}));
 assert.ok(tree.root.findAllByType('Text').some(n=>n.props.children==='Clear views saved: 12'));
 await act(async()=>resolveLens({report:{lensReady:true},error:null}));assert.match(voices.at(-1),/Lens parameters saved/);
 await act(async()=>voice());assert.ok(button('Align camera and sensors'));
 await act(async()=>button('Align camera and sensors').props.onPress());assert.equal(resolveAlignment,undefined);
 await act(async()=>voice());assert.equal(typeof resolveAlignment,'function');
 await act(async()=>progress({phase:'alignment-cue',imageUri:''}));assert.equal(begin,0);
 await act(async()=>voice());assert.equal(begin,1);
 act(()=>progress({phase:'alignment-cue',imageUri:''}));assert.equal(begin,1,'Movement instruction must not repeat');
 await act(async()=>resolveAlignment({metadata:'{}',uri:'file:///alignment.zip'}));assert.equal(uploads,0);
 await act(async()=>voice());assert.equal(uploads,1);assert.match(voices.at(-1),/Research review is still needed/);
 await act(async()=>voice());assert.ok(button('Align camera and sensors'));act(()=>tree.unmount());
});

test('Every native lens hint has translated computer and optional tablet handling, including loss of board view',()=>{
 const guide=load('lensGuidance'),language=load('language'),source=fs.readFileSync(path.resolve(__dirname,'../modules/gait-camera-calibration/android/src/main/java/expo/modules/gaitcalibration/GuidedLensCalibration.java'),'utf8');
 const hints=[...source.matchAll(/(?:hint=|return )"([^"]+)"/g)].map(m=>m[1]);
 assert.ok(hints.length>=10);
 for(const text of [...hints.map(s=>guide.lensGuidance(s)),...hints.map(s=>guide.lensGuidance(s,'tablet')),guide.lensPreparation,guide.tabletLensPreparation]){
  assert.doesNotMatch(text,/whole board/);
  for(const l of ['ms','zh'])assert.notEqual(language.translate(text,l),text,text);
 }
 assert.match(guide.lensGuidance('Tilt the phone gently left and right.'),/Turn the phone/);
 assert.match(guide.lensGuidance('Tilt the phone gently left and right.','tablet'),/Turn the tablet/);
 assert.match(guide.lensGuidance('Keep the whole board in view.'),/back into view/);
 assert.equal(guide.lensGuidance('Lens parameters saved. Sensor alignment is still needed.'),'Lens parameters saved. Sensor alignment is still needed.');
});

test('Guided calibration cancels before capture instead of starting after an interrupted instruction',async()=>{
 const node=name=>p=>React.createElement(name,p,p.children);let voice,captures=0,stops=0;
 const bridge={addListener(){return{remove(){}};},async phoneCalibrationInfo(){return '{}';},async captureGuidedLens(){captures++;},async stop(){stops++;}};
 const mocks={'react-native':{View:node('View'),Image:node('Image'),Pressable:node('Pressable'),Modal:node('Modal'),AppState:{addEventListener(){return{remove(){}};}},BackHandler:{addEventListener(){return{remove(){}};}}},'expo-camera':{CameraView:node('Camera'),useCameraPermissions:()=>[{granted:true},async()=>({granted:true})]},'expo-keep-awake':{useKeepAwake(){}},'expo-sharing':{},'expo-file-system':{},'../components/Screen':{Screen:p=>React.createElement('Screen',p,p.children,p.actions),Body:node('Body'),ui:{}},'../components/BigButton':{default:node('Button'),__esModule:true},'./CameraCalibrationScreen':{default:node('Legacy'),__esModule:true},'../i18n':{Text:node('Text'),t:s=>s},'../audio':{speakQueued(){return new Promise(r=>voice=r);},stopSpeaking(){}},'../cameraCalibration':{calibrationBridge:()=>bridge,async currentLensReport(){return null;}},'../referenceCalibration':{async calibrationComputer(){return null;},async pendingReference(){return null;},async savedReference(){return null;}}};
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
function harness(screen, platform='android', browserResult=null,params={}) {
 let now=0,nextId=0,currentEngine,navigated=[],spoke=[],voiceOptions,appListener;
 const timers=new Map();let visibilityListener;
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
 '../components/Screen':{Screen:({children,actions,...p})=>React.createElement('screen',p,children,actions),Card:'card',Body:'body',ui:{row:{},fill:{},caption:{}}},'../components/BigButton':{default:'button',__esModule:true},
 '../components/ClinicalCapture':{default:p=>React.createElement('clinical',p),__esModule:true},
 '../components/ProtocolTutorial':{default:()=>null,__esModule:true},
 '../i18n':{Text:'text',LanguagePicker:()=>null,t:x=>x,useLanguage:()=> 'en'},
 '../audio':{speak:async(text,opts)=>{spoke.push(text);voiceOptions=opts},speakQueued:(text,opts)=>{spoke.push(text);voiceOptions=opts;return {finally(fn){fn();return Promise.resolve();}}},discardPendingSpeech(){},stopSpeaking(){},ensureVoice:async()=>({identifier:'en',language:'en-MY'})},
 '../browserSensors':{checkBrowserSensors:async()=>browserResult},
 '../sensors':{SensorRecorder:Engine,checkSensors:async()=>{if(platform==='web'&&!browserResult?.ready)throw new Error('Browser must not check live sensors')}},'../store':{getParticipants:async()=>[...savedProfiles.values()],saveParticipant:async p=>{if(saveFails)throw new Error('Storage unavailable');savedProfiles.set(p.id,JSON.parse(JSON.stringify(p)));},saveSession:async()=>{},generateSessionId:()=> 'test'},
 };
 const Component=load('screens/'+screen,mocks,globals).default;
 let renderer;act(()=>{renderer=create(React.createElement(Component,{navigation:{navigate:(...p)=>navigated.push(p),replace:(...p)=>navigated.push(p),goBack:()=>navigated.push(['back'])},route:{params:{duration:10,audioEnabled:true,isPractice:true,guidanceEnabled:true,...params}}}))});
 const button=label=>renderer.root.findAllByType('button').find(n=>n.props.label===label);
 async function finishSetup(){await act(async()=>{});act(()=>{renderer.root.findByProps({accessibilityLabel:'Study ID or participant label'}).props.onChangeText('STUDY-001');renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.onChangeText('67');});act(()=>renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio').props.onPress());act(()=>button('Continue').props.onPress());act(()=>button('Continue').props.onPress());}
 return {renderer,button,advance,finishSetup,savedProfiles,failSave:()=>{saveFails=true},get engine(){return currentEngine},get voiceOptions(){return voiceOptions},navigated,spoke,hide:()=>act(()=>{doc.visibilityState='hidden';visibilityListener?.()}),background:()=>act(()=>appListener('background')),close:()=>act(()=>renderer.unmount())};
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
test('Changing person after a saved test creates a new identity rather than rewriting the first person',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='checkbox').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());const first=h.navigated[0][1];
 act(()=>h.button('Previous').props.onPress());act(()=>h.button('Previous').props.onPress());
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Study ID or participant label'}).props.onChangeText('STUDY-002'));
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.value,'');
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.onChangeText('70'));
 act(()=>h.renderer.root.findAllByType('pressable').find(p=>p.props.accessibilityRole==='radio').props.onPress());
 act(()=>h.button('Continue').props.onPress());act(()=>h.button('Continue').props.onPress());
 await act(async()=>h.button('Start test').props.onPress());const second=h.navigated[1][1];
 assert.notEqual(first.participantId,second.participantId);assert.equal(h.savedProfiles.size,2);
 assert.equal(h.savedProfiles.get(first.participantId).label,'STUDY-001');assert.equal(first.participantSnapshot.demographics.ageYears,67);h.close();
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
  './Screen':{Screen:({children,actions,...p})=>React.createElement('screen',p,children,actions),Body:'body',ui:{row:{},fill:{}}},
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
 act(()=>h.button('Set height and walking aid').props.onPress());
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Height in centimetres'}).props.onChangeText('168'));
 act(()=>h.button('Done').props.onPress());
 assert.equal(h.renderer.root.findAllByType('modal').length,0);
 assert.equal(h.renderer.root.findAllByProps({accessibilityLabel:'Height in centimetres'}).length,0);
 act(()=>h.button('Language and audio settings').props.onPress());
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Voice guidance'}).props.value,false);
 act(()=>h.button('Done').props.onPress());act(()=>h.button('Set height and walking aid').props.onPress());
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Height in centimetres'}).props.value,'168');
 act(()=>h.button('Done').props.onPress());
 h.close();
});

test('Test selection closes its menu and preserves the chosen protocol on return',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 act(()=>h.button('Previous').props.onPress());
 act(()=>h.button('Change test: Research walk').props.onPress());
 const choice=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio'&&n.findAllByType('text').some(t=>Array.isArray(t.props.children)&&t.props.children.includes('6MWT')));
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


function clinicalHarness(protocol,audioEnabled=true){
 let now=0,tick,resolveIntro,alive=true,begun=0,goOptions,context='rest-or-quiet';
 const spoken=[],finished=[];
 const Component=load('components/ClinicalCapture',{
  'react-native':{View:'view'},
  './Screen':{Screen:({children,actions,...p})=>React.createElement('screen',p,children,actions),Body:'body',ui:{}},
  './BigButton':{__esModule:true,default:'button'},
  '../i18n':{Text:'text',t:x=>x},
 },{performance:{now:()=>now},setInterval:fn=>{tick=fn;return 1},clearInterval:()=>{tick=null}}).default;
 const say=(text,options)=>{
  spoken.push(text);
  if(spoken.length===1)return new Promise(resolve=>{resolveIntro=resolve});
  goOptions=options;return Promise.resolve();
 };
 let renderer;
 act(()=>{renderer=create(React.createElement(Component,{protocol,audioEnabled,say,receiving:()=>alive,motion:()=>({enough:true,steady:context==='rest-or-quiet',context}),onBegin:()=>begun++,onFinish:e=>finished.push(e),onCancel(){}}));});
 const button=label=>renderer.root.findAllByType('button').find(n=>n.props.label===label);
 return {renderer,button,spoken,finished,get begun(){return begun},get goOptions(){return goOptions},
 ready:async()=>{await act(async()=>resolveIntro())},
 advance:ms=>act(()=>{now+=ms;tick?.()}),loseSensors:()=>{alive=false},
 move:()=>{context='movement'},settle:()=>{context='rest-or-quiet'},
 close:()=>act(()=>renderer.unmount())};
}
test('Clinical start arms automatically after stillness and clocks from audible Go',async()=>{
 const h=clinicalHarness('2mwt');
 assert.equal(h.begun,0);
 await h.ready();h.advance(0);h.advance(3000);
 assert.equal(h.begun,1);h.advance(700);
 assert.match(JSON.stringify(h.renderer.toJSON()),/Wait for Go/);
 act(()=>h.goOptions.onStart());
 h.advance(119900);assert.equal(h.finished.length,0);
 h.advance(100);assert.equal(h.finished.length,1);
 assert.equal(h.finished[0].elapsedFromGoSeconds,120);
 assert.equal(h.finished[0].goOffsetMs,700);assert.equal(h.finished[0].end,'duration');
 assert.deepEqual(h.spoken.slice(1),['Go.']);h.close();
});
test('Six-minute protocol continues through stationary time and ends automatically',async()=>{
 const h=clinicalHarness('6mwt',false);await h.ready();
 h.advance(0);h.advance(3000);
 h.advance(359900);assert.equal(h.finished.length,0);
 h.advance(100);assert.equal(h.finished[0].elapsedFromGoSeconds,360);
 assert.equal(h.finished[0].goSource,'automatic-silent-cue');assert.equal(h.spoken.length,1);h.close();
});
test('TUG and 10MWT auto-save after sustained movement and stop; the capture limit is not completion',async()=>{
 for(const protocol of ['tug','10mwt']){
  const h=clinicalHarness(protocol,false);await h.ready();
  h.advance(0);h.advance(3000);h.move();h.advance(100);h.advance(4000);h.settle();h.advance(100);h.advance(8000);
  assert.equal(h.finished[0].end,'auto-stop-estimate');assert.equal(h.finished[0].clinicalOutcomeVerified,false);h.close();
  const capped=clinicalHarness(protocol,false);await capped.ready();
  capped.advance(0);capped.advance(3000);
  capped.advance(180000);assert.equal(capped.finished[0].end,'capture-limit');capped.close();
 }
});
test('Missing Go callbacks and lost sensors interrupt clinical capture instead of inventing time',async()=>{
 const h=clinicalHarness('tug');await h.ready();
 h.advance(0);h.advance(3000);
 h.advance(10000);assert.equal(h.finished[0].goOffsetMs,null);assert.equal(h.finished[0].elapsedFromGoSeconds,null);
 assert.equal(h.finished[0].end,'interrupted');h.close();
 const loss=clinicalHarness('2mwt',false);await loss.ready();
 loss.advance(0);loss.advance(3000);
 loss.loseSensors();loss.advance(100);assert.equal(loss.finished[0].end,'interrupted');loss.close();
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
 act(()=>{h.renderer.root.findByProps({accessibilityLabel:'Study ID or participant label'}).props.onChangeText('TRIAL-001');h.renderer.root.findByProps({accessibilityLabel:'Age in years'}).props.onChangeText('67');});
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
 act(()=>h.button('Review stroke history').props.onPress());
 for(const [label,value] of [['Stroke type (optional)','ischemic'],['Lesion location (optional)','subcortical'],['Pre-existing gait pattern/asymmetry','prior limp'],['Joint conditions or orthopaedic history','knee surgery']])act(()=>h.renderer.root.findByProps({accessibilityLabel:label}).props.onChangeText(value));
 act(()=>h.button('Done').props.onPress());act(()=>h.button('Set height and walking aid').props.onPress());
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
