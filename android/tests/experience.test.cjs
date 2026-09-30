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
function harness(screen, platform='android', browserResult=null) {
 let now=0,nextId=0,currentEngine,navigated=[],spoke=[],voiceOptions,appListener;
 const timers=new Map();let visibilityListener;
 const doc={visibilityState:'visible',addEventListener:(_,fn)=>visibilityListener=fn,removeEventListener:()=>visibilityListener=null};
 const globals={document:doc,AbortController,performance:{now:()=>now},setInterval:(fn,delay)=>{const id=++nextId;timers.set(id,{fn,delay,next:now+delay,repeat:true});return id},clearInterval:id=>timers.delete(id),setTimeout:(fn,delay)=>{const id=++nextId;timers.set(id,{fn,delay,next:now+delay});return id},clearTimeout:id=>timers.delete(id)};
 function advance(ms){act(()=>{const end=now+ms;while(now<end){now=Math.min(now+100,end);for(const [id,t] of [...timers]) if(t.next<=now){if(t.repeat)t.next+=t.delay;else timers.delete(id);t.fn();}}});}
 const steady={enough:true,steady:true,upright:true,context:'rest-or-quiet'};
 class Engine {
  constructor(){currentEngine=this;this.motionStatus={...steady};this.allReceiving=true;this.baselineReady=true;this.guidanceReady=true;this.begun=false;}
  connect(){} disconnect(){} restoreFitCheck(v){this.savedFitCheck=v} startFit(){this.fitStarted=true} candidateStepsAfter(){return this.motionStatus.context==='movement'?1:0} finishFit(){this.savedFitCheck={status:'movement-then-settled',version:'guided-fit-v2'}} begin(){this.begun=true}
 }
 const native={Platform:{OS:platform},Text:'text',TextInput:'input',Modal:({visible,children})=>visible?React.createElement('modal',null,children):null,View:'view',ScrollView:'scrollview',Pressable:'pressable',Switch:'switch',StyleSheet:{create:x=>x},AppState:{currentState:'active',addEventListener:(_,fn)=>{appListener=fn;return {remove(){}}}},BackHandler:{addEventListener:()=>({remove(){}})}};
 const savedProfiles=new Map();let saveFails=false;
 const mocks={'react-native':native,'expo-location':{Accuracy:{High:4},requestForegroundPermissionsAsync:async()=>({status:'granted'}),getProviderStatusAsync:async()=>({locationServicesEnabled:true}),watchPositionAsync:async()=>({remove(){}})},'expo-keep-awake':{activateKeepAwakeAsync:async()=>{},deactivateKeepAwake:async()=>{}},'expo-haptics':{NotificationFeedbackType:{Error:'error',Warning:'warning',Success:'success'},notificationAsync:async()=>{}},
 '../components/Screen':{Screen:({children,actions,...p})=>React.createElement('screen',p,children,actions),Card:'card',Body:'body',ui:{row:{},fill:{},caption:{}}},'../components/BigButton':{default:'button',__esModule:true},
 '../components/ProtocolTutorial':{default:()=>null,__esModule:true},
 '../i18n':{Text:'text',LanguagePicker:()=>null,t:x=>x,useLanguage:()=> 'en'},
 '../audio':{speak:async(text,opts)=>{spoke.push(text);voiceOptions=opts},speakQueued:(text,opts)=>{spoke.push(text);voiceOptions=opts;return {finally(fn){fn();return Promise.resolve();}}},discardPendingSpeech(){},stopSpeaking(){},ensureVoice:async()=>({identifier:'en',language:'en-MY'})},
 '../browserSensors':{checkBrowserSensors:async()=>browserResult},
 '../sensors':{SensorRecorder:Engine,checkSensors:async()=>{if(platform==='web'&&!browserResult?.ready)throw new Error('Browser must not check live sensors')}},'../store':{getParticipants:async()=>[...savedProfiles.values()],saveParticipant:async p=>{if(saveFails)throw new Error('Storage unavailable');savedProfiles.set(p.id,JSON.parse(JSON.stringify(p)));},saveSession:async()=>{},generateSessionId:()=> 'test'},
 };
 const Component=load('screens/'+screen,mocks,globals).default;
 let renderer;act(()=>{renderer=create(React.createElement(Component,{navigation:{navigate:(...p)=>navigated.push(p),replace:(...p)=>navigated.push(p),goBack:()=>navigated.push(['back'])},route:{params:{duration:10,audioEnabled:true,isPractice:true,guidanceEnabled:true}}}))});
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
 assert.deepEqual(h.navigated,[['Walkthrough']]);
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
 act(()=>h.button('More options').props.onPress());
 assert.equal(h.renderer.root.findAllByType('modal').length,1);
 const voice=h.renderer.root.findByProps({accessibilityLabel:'Voice guidance'});
 act(()=>voice.props.onValueChange(false));
 act(()=>h.button('More participant details').props.onPress());
 act(()=>h.renderer.root.findByProps({accessibilityLabel:'Height in centimetres'}).props.onChangeText('168'));
 act(()=>h.button('Done').props.onPress());
 assert.equal(h.renderer.root.findAllByType('modal').length,0);
 assert.equal(h.renderer.root.findAllByProps({accessibilityLabel:'Height in centimetres'}).length,0);
 act(()=>h.button('More options').props.onPress());
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Voice guidance'}).props.value,false);
 act(()=>h.button('More participant details').props.onPress());
 assert.equal(h.renderer.root.findByProps({accessibilityLabel:'Height in centimetres'}).props.value,'168');
 act(()=>h.button('Done').props.onPress());
 h.close();
});

test('Test selection closes its menu and preserves the chosen protocol on return',async()=>{
 const h=harness('PrepareScreen');await h.finishSetup();
 act(()=>h.button('Previous').props.onPress());
 act(()=>h.button('Research walk').props.onPress());
 const choice=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='radio'&&n.findAllByType('text').some(t=>t.props.children==='6MWT'));
 act(()=>choice.props.onPress());
 assert.equal(h.renderer.root.findAllByType('modal').length,0);
 assert.ok(h.button('6MWT'));
 assert.ok(h.renderer.root.findByProps({accessibilityLabel:'Measured course length in metres'}));
 h.close();
});
