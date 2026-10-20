const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript'),React=require('react'),{act,create}=require('react-test-renderer');
function load(name,mocks){const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(__dirname,'../src',name),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true}}).outputText,{module,exports:module.exports,require:id=>mocks[id],console});return module.exports;}
const node=name=>p=>React.createElement(name,p,p.children);
function mocks(platform='android'){
 return {react:React,'react-native':{View:'View',Image:'Image',Modal:p=>p.visible?React.createElement('Modal',p,p.children):null,Pressable:'Pressable',StyleSheet:{create:s=>s},Platform:{OS:platform},AppState:{addEventListener:()=>({remove(){}})},BackHandler:{addEventListener:()=>({remove(){}})}},
 '../components/Screen':{Screen:p=>React.createElement('Screen',{},p.children,p.actions),Body:node('Body'),Card:node('Card'),ui:{}},'../components/BigButton':node('Button'),
 '../i18n':{Text:node('Text'),LanguagePicker:node('LanguagePicker'),t:s=>s},'../theme':{colours:{}},'../flowLab':{flowLabEnabled:false},
 '../components/ReviewImport':node('ReviewImport'),'../components/PwaInstall':node('PwaInstall'),'../components/ReleaseInfo':node('ReleaseInfo'),
 'expo-camera':{useCameraPermissions:()=>[{granted:true},async()=>({granted:true})],CameraView:node('CameraView')},'expo-keep-awake':{useKeepAwake(){}},'expo-file-system':{},'expo-sharing':{},'expo-document-picker':{},
 '../audio':{speakQueued:async()=>{},stopSpeaking(){}},'../noiseValidation':{},
 '../cameraCalibration':{calibrationBridge:()=>({addListener:()=>({remove(){}}),phoneCalibrationInfo:async()=>JSON.stringify({cameraId:'1'})}),latestLensCapture:async()=>null,currentLensReport:async()=>({}),latestCalibrationCapture:async()=>null,latestNoiseCapture:async()=>null},
 '../referenceCalibration':{calibrationComputer:async()=>null,pendingReference:async()=>null,savedReference:async()=>({})},'../lensGuidance':{roundLabels:{}}};
}
test('Installed Android checklist traverses expanded Home and the actual calibration screen into the default noise tab',async()=>{
 const m=mocks(),routes=[],navigation={navigate:r=>routes.push(r),goBack(){}},Home=load('screens/HomeScreen.tsx',m).default;let home,phone;
 await act(async()=>{home=create(React.createElement(Home,{navigation}));});
 const buttons=tree=>tree.root.findAllByType('Button'),button=(tree,label)=>buttons(tree).find(n=>n.props.label===label);
 assert.equal(button(home,'Phone calibration'),undefined,'Research controls start collapsed');
 assert.ok(button(home,'Start a walk'));assert.ok(button(home,'My recordings'));assert.ok(button(home,'Participants and profiles'));
 assert.equal(button(home,'Progress dashboard'),undefined);assert.equal(button(home,'How to use the app'),undefined);
 act(()=>button(home,'Tools and help').props.onPress());
 assert.ok(button(home,'Progress dashboard'));assert.ok(button(home,'How to use the app'));
 assert.ok(button(home,'Set up this phone'));assert.equal(button(home,'Phone calibration'),undefined);assert.equal(button(home,'Distance validation'),undefined);assert.equal(home.root.findAllByType('ReleaseInfo').length,1);
 act(()=>button(home,'Set up this phone').props.onPress());assert.deepEqual(routes,['PhoneSetup']);routes.length=0;
 act(()=>button(home,'Tools and help').props.onPress());
 act(()=>button(home,'Advanced research tools (computer required)').props.onPress());assert.ok(button(home,'Phone calibration'));assert.ok(button(home,'Distance validation'));
 act(()=>button(home,'Distance validation').props.onPress());act(()=>button(home,'Tools and help').props.onPress());act(()=>button(home,'Phone calibration').props.onPress());assert.deepEqual(routes,['CameraDistanceTrial','CameraCalibration']);
 m['./CameraCalibrationScreen']=load('screens/CameraCalibrationScreen.tsx',m);
 const Phone=load('screens/PhoneCalibrationScreen.tsx',m).default;
 await act(async()=>{phone=create(React.createElement(Phone,{navigation}));});
 const link=phone.root.findAllByType('Pressable').find(n=>n.props.accessibilityRole==='button'&&n.findAllByType('Text').some(t=>t.props.children==='Research capture tools'));assert.ok(link);
 await act(async()=>link.props.onPress());
 assert.ok(button(phone,'Measure sensor noise (5 min)'));assert.equal(button(phone,'Capture calibration'),undefined);
 const tab=phone.root.findAllByType('Pressable').find(n=>n.props.accessibilityRole==='tab'&&n.findAllByType('Text').some(t=>t.props.children==='Sensor noise'));assert.equal(tab.props.accessibilityState.selected,true);
 act(()=>phone.unmount());act(()=>home.unmount());
});
test('Browser preview deliberately has no Android-only research navigation',async()=>{
 const m=mocks('web'),Home=load('screens/HomeScreen.tsx',m).default;let tree;await act(async()=>tree=create(React.createElement(Home,{navigation:{navigate(){}}})));
 act(()=>tree.root.findAllByType('Button').find(n=>n.props.label==='Tools and help').props.onPress());
 assert.equal(tree.root.findAllByType('Button').some(n=>['Phone calibration','Distance validation'].includes(n.props.label)),false);act(()=>tree.unmount());
});
