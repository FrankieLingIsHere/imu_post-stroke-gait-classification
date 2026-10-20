const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
const React=require('react'),{create,act}=require('react-test-renderer');
function load(name,mocks,cache={}){
 let file=path.resolve(__dirname,'../src',name);if(!fs.existsSync(file))file+=fs.existsSync(file+'.ts')?'.ts':'.tsx';
 if(cache[file])return cache[file].exports;const module={exports:{}};cache[file]=module;
 vm.runInNewContext(ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{esModuleInterop:true,module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React}}).outputText,
 {module,exports:module.exports,console,require:id=>id in mocks?mocks[id]:id.startsWith('.')?load(path.resolve(path.dirname(file),id),mocks,cache):require(id)});return module.exports;
}
test('Recording list keeps bulk controls out of its footer while preserving selection and export',async()=>{
 const records=Array.from({length:5},(_,i)=>({id:'fixture-'+i,date:'2026-10-11T08:00:00Z',duration:10,participantId:'demo',participantLabel:'Not patient data'}));let exported;
 const mocks={'react-native':{Platform:{OS:'android'},View:'view',Pressable:'pressable',Modal:({visible,children})=>visible?React.createElement('modal',null,children):null,useWindowDimensions:()=>({height:640,fontScale:1.5}),Alert:{alert(){}}},
 '@react-navigation/native':{useFocusEffect:fn=>React.useEffect(fn,[fn])},'../i18n':{Text:'text',t:s=>s,useLanguage:()=> 'en'},
 '../components/Screen':{Screen:({children,actions,...p})=>React.createElement('screen',p,React.createElement('content',null,children),React.createElement('footer',null,actions)),Card:'card',Body:'body',ui:{row:{},label:{},fill:{},caption:{},choice:{}}},'../components/BigButton':{default:'button',__esModule:true},
 '../store':{getSessions:async()=>records,getSession:async id=>records.find(r=>r.id===id),formatSessionDate:()=> '11 October',deleteSessions:async()=>{}},
 '../gaitAssessment':{orderGaitReviews:r=>r,gaitReviewStatus:()=>({required:true,complete:false,status:'pending'})},'../export':{shareRecordingsCSV:async r=>exported=r}};
 let tree;await act(async()=>tree=create(React.createElement(load('screens/HistoryScreen',mocks).default,{navigation:{navigate(){},popToTop(){}}})));
 const button=label=>tree.root.findAllByType('button').find(n=>n.props.label===label);
 assert.equal(tree.root.findByType('footer').findAllByType('button').length,1);
 assert.equal(tree.root.findByType('footer').findByType('button').props.label,'Export or delete');
 assert.equal(button('Export selected CSV'),undefined);assert.equal(tree.root.findAllByType('card').length,2);
 const circle=tree.root.findAllByType('pressable').find(n=>n.props.accessibilityRole==='checkbox');
 await act(async()=>circle.props.onPress({stopPropagation(){}}));
 await act(async()=>button('Export or delete').props.onPress());
 assert.equal(button('Export selected CSV').props.disabled,false);
 await act(async()=>{button('Export selected CSV').props.onPress();});
 assert.deepEqual(Array.from(exported,r=>r.id),['fixture-0']);
 await act(async()=>button('Done').props.onPress());assert.equal(button('Export selected CSV'),undefined);
 await act(async()=>button('Next').props.onPress());assert.equal(tree.root.findAllByType('card').length,2);
 await act(async()=>tree.unmount());
});

test('New recording-management labels are localized in Malay and Chinese',()=>{
 const {translate}=load('language',{});
 for(const label of ['Recordings','Manage recordings','Export or delete','{0} assessments to complete','Page {0} of {1}'])
  for(const language of ['ms','zh']){const value=translate(label,language);assert.notEqual(value,label);assert.ok(value.trim());assert.doesNotMatch(value,/\?{2,}/);}
});
