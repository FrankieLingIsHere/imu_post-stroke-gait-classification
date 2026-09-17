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
 for(const [key,values] of Object.entries(messages)) for(const value of values) {
  assert.ok(value.trim(),key);assert.deepEqual((value.match(/\{\d+\}/g)||[]).sort(),(key.match(/\{\d+\}/g)||[]).sort(),key);
 }
 const file=fs.readFileSync(path.resolve(__dirname,'../src/screens/RecordScreen.tsx'),'utf8');
 for(const match of file.matchAll(/say\('([^']+)'\)/g)) assert.ok(messages[match[1]],match[1]);
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
function harness(screen, platform='android', browserResult=null) {
 let now=0,nextId=0,currentEngine,navigated=[],spoke=[],voiceOptions,appListener;
 const timers=new Map();let visibilityListener;
 const doc={visibilityState:'visible',addEventListener:(_,fn)=>visibilityListener=fn,removeEventListener:()=>visibilityListener=null};
 const globals={document:doc,AbortController,performance:{now:()=>now},setInterval:(fn,delay)=>{const id=++nextId;timers.set(id,{fn,delay,next:now+delay,repeat:true});return id},clearInterval:id=>timers.delete(id),setTimeout:(fn,delay)=>{const id=++nextId;timers.set(id,{fn,delay,next:now+delay});return id},clearTimeout:id=>timers.delete(id)};
 function advance(ms){act(()=>{const end=now+ms;while(now<end){now=Math.min(now+100,end);for(const [id,t] of [...timers]) if(t.next<=now){if(t.repeat)t.next+=t.delay;else timers.delete(id);t.fn();}}});}
 const steady={enough:true,steady:true,upright:true,context:'rest-or-quiet'};
 class Engine {
  constructor(){currentEngine=this;this.motionStatus={...steady};this.allReceiving=true;this.baselineReady=true;this.guidanceReady=true;this.begun=false;}
  connect(){} disconnect(){} restoreFitCheck(v){this.savedFitCheck=v} startFit(){this.fitStarted=true} finishFit(){this.savedFitCheck={status:'movement-then-settled',version:'guided-fit-v2'}} begin(){this.begun=true}
 }
 const native={Platform:{OS:platform},Text:'text',View:'view',Pressable:'pressable',Switch:'switch',StyleSheet:{create:x=>x},AppState:{currentState:'active',addEventListener:(_,fn)=>{appListener=fn;return {remove(){}}}},BackHandler:{addEventListener:()=>({remove(){}})}};
 const mocks={'react-native':native,'expo-keep-awake':{activateKeepAwakeAsync:async()=>{},deactivateKeepAwake:async()=>{}},'expo-haptics':{NotificationFeedbackType:{Error:'error',Warning:'warning',Success:'success'},notificationAsync:async()=>{}},
 '../components/Screen':{Screen:({children,actions,...p})=>React.createElement('screen',p,children,actions),Card:'card',Body:'body',ui:{row:{},fill:{},caption:{}}},'../components/BigButton':{default:'button',__esModule:true},
 '../i18n':{Text:'text',LanguagePicker:()=>null,t:x=>x,useLanguage:()=> 'en'},
 '../audio':{speak:async(text,opts)=>{spoke.push(text);voiceOptions=opts},stopSpeaking(){},ensureVoice:async()=>({identifier:'en',language:'en-MY'})},
 '../browserSensors':{checkBrowserSensors:async()=>browserResult},
 '../sensors':{SensorRecorder:Engine,checkSensors:async()=>{if(platform==='web'&&!browserResult?.ready)throw new Error('Browser must not check live sensors')}},'../store':{saveSession:async()=>{},generateSessionId:()=> 'test'},
 };
 const Component=load('screens/'+screen,mocks,globals).default;
 let renderer;act(()=>{renderer=create(React.createElement(Component,{navigation:{navigate:(...p)=>navigated.push(p),replace:(...p)=>navigated.push(p),goBack:()=>navigated.push(['back'])},route:{params:{duration:10,audioEnabled:true,isPractice:true,guidanceEnabled:true}}}))});
 const button=label=>renderer.root.findAllByType('button').find(n=>n.props.label===label);
 return {renderer,button,advance,get engine(){return currentEngine},get voiceOptions(){return voiceOptions},navigated,spoke,hide:()=>act(()=>{doc.visibilityState='hidden';visibilityListener?.()}),background:()=>act(()=>appListener('background')),close:()=>act(()=>renderer.unmount())};
}
test('Failed setup retries locally with eight seconds and does not navigate through setup or sound again', () => {
 const h=harness('RecordScreen');h.engine.allReceiving=false;h.advance(40500);
 assert.ok(h.button('Retry this check'));
 act(()=>h.button('Retry this check').props.onPress());
 assert.equal(h.renderer.root.findByType('screen').props.title,'Settle in. No rush.');
 assert.ok(h.spoke.some(s=>s.startsWith('You have 8 seconds')));
 assert.equal(h.navigated.length,0);h.advance(11500);assert.equal(h.engine.fitStarted,true);h.close();
});
test('Completed fit survives a later interruption, but retry cannot start until a new baseline passes', () => {
 const h=harness('RecordScreen');h.advance(24000);assert.equal(h.engine.fitStarted,true);
 h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);
 h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(3200);
 assert.equal(h.renderer.root.findByType('screen').props.title,'Ready to begin');h.background();
 act(()=>h.button('Retry this check').props.onPress());assert.ok(h.engine.savedFitCheck);
 h.engine.baselineReady=false;h.advance(12000);assert.equal(h.engine.begun,false);
 h.engine.baselineReady=true;h.advance(6500);assert.equal(h.engine.begun,true);assert.equal(h.engine.fitStarted,undefined);h.close();
});
test('Sound sample is optional on setup and can be skipped after two seconds without disabling guidance', async () => {
 const h=harness('PrepareScreen');
 const consent=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox');
 act(()=>consent.props.onPress());assert.equal(h.button('Start test').props.disabled,false);
 await act(async()=>h.button('Play voice sample').props.onPress());
 assert.equal(h.button('Start without sound test').props.disabled,true);
 h.advance(2000);assert.equal(h.button('Start without sound test').props.disabled,false);
 await act(async()=>h.button('Start without sound test').props.onPress());
 assert.equal(h.navigated[0][0],'Record');assert.equal(h.navigated[0][1].audioEnabled,true);h.close();
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
 assert.equal(h.button('Preview hands-free flow').props.disabled,false);
 assert.equal(h.renderer.root.findAllByType('pressable').filter(p=>p.props.accessibilityRole==='checkbox').length,0);
 await act(async()=>h.button('Preview hands-free flow').props.onPress());
 assert.deepEqual(h.navigated,[['Walkthrough']]);
 assert.equal(h.engine,undefined);
 h.close();
});


test('Browser capture starts only after all-sensor check and separate user consent; preview stays available',async()=>{
 const sensors=Object.fromEntries(['accelerometer','gyroscope','magnetometer'].map(n=>[n,{status:'ready',count:150,hz:50}]));
 const h=harness('PrepareScreen','web',{ready:true,sensors});
 await act(async()=>h.button('Check this phone’s sensors').props.onPress());
 assert.equal(h.button('Start test').props.disabled,true);
 assert.ok(h.button('Preview hands-free flow'));
 const consent=h.renderer.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox');
 act(()=>consent.props.onPress());assert.equal(h.button('Start test').props.disabled,false);
 await act(async()=>h.button('Start test').props.onPress());
 assert.equal(h.navigated[0][0],'Record');h.close();
});
test('Failed browser capability check cannot unlock recording',async()=>{
 const sensors=Object.fromEntries(['accelerometer','gyroscope','magnetometer'].map(n=>[n,{status:n==='magnetometer'?'unavailable':'ready',count:0,hz:0}]));
 const h=harness('PrepareScreen','web',{ready:false,sensors});
 await act(async()=>h.button('Check this phone’s sensors').props.onPress());
 assert.equal(h.button('Start test'),undefined);assert.ok(h.button('Preview hands-free flow'));h.close();
});

test('Browser sensor loss or hidden tab interrupts and saves an active walk',async()=>{
 for(const cause of ['hidden','lost']){
  const h=harness('RecordScreen','web');
  h.advance(23500);h.engine.motionStatus={enough:true,steady:false,upright:true,context:'movement'};h.advance(1500);
  h.engine.motionStatus={enough:true,steady:true,upright:true,context:'rest-or-quiet'};h.advance(9500);assert.equal(h.engine.begun,true);
  let reason;
  h.engine.stop=r=>{reason=r;return {stopReason:r,startedAt:'2026-09-17T00:00:00Z',elapsedSeconds:1,streams:{accelerometer:[],gyroscope:[],magnetometer:[]},guidanceEvents:[]}};
  await act(async()=>{if(cause==='hidden')h.hide();else{h.engine.allReceiving=false;h.advance(100)}});
  assert.equal(reason,'interrupted');assert.equal(h.navigated.at(-1)[0],'Result');h.close();
 }
});
