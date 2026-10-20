const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),ts=require('typescript'),path=require('node:path');
function load(name,mocks){const module={exports:{}};let file=path.join(__dirname,'../src/'+name+'.ts');if(!fs.existsSync(file))file+='x';vm.runInNewContext(ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true}}).outputText,{module,exports:module.exports,require:id=>mocks[id]});return module.exports;}
function fixture(){
 const root='file:///app/files/',cache='file:///app/cache/',files=new Map(),deleted=[];
 const prefix=p=>p.endsWith('/')?p:p+'/';
 const storage={documentDirectory:root,cacheDirectory:cache,getInfoAsync:async p=>files.has(p)?{exists:true,isDirectory:false,size:files.get(p).length}:[...files.keys()].some(k=>k.startsWith(prefix(p)))?{exists:true,isDirectory:true}:{exists:false},
  readDirectoryAsync:async p=>[...new Set([...files.keys()].filter(k=>k.startsWith(prefix(p))).map(k=>k.slice(prefix(p).length).split('/')[0]))],
  deleteAsync:async p=>{if(p===storage.fail)throw Error('Disk error');deleted.push(p);for(const k of [...files.keys()])if(k===p||k.startsWith(prefix(p)))files.delete(k);},
  readAsStringAsync:async p=>files.get(p),writeAsStringAsync:async(p,v)=>files.set(p,v)};
 return {root,cache,files,deleted,storage,api:load('recordingStorage',{'expo-file-system':storage})};
}
test('Selected deletion removes JSON, video and bundled exports; preserves other walks, profiles and calibration',async()=>{
 const f=fixture();for(const name of ['recordings/a.json','recordings/b.json','camera-trials/camera-a.mp4','camera-trials/camera-b.mp4','camera-calibration/reference.json'])f.files.set(f.root+name,'raw');f.files.set(f.cache+'gait-exports/gait-recordings-all.csv','both a and b');f.files.set(f.cache+'unrelated/icon.png','icon');
 await f.api.removeRecordingFiles(['a']);assert.equal(f.files.has(f.root+'recordings/a.json'),false);assert.equal(f.files.has(f.root+'camera-trials/camera-a.mp4'),false);assert.equal(f.files.has(f.cache+'gait-exports/gait-recordings-all.csv'),false);
 for(const p of ['recordings/b.json','camera-trials/camera-b.mp4','camera-calibration/reference.json'])assert.equal(f.files.has(f.root+p),true);
 assert.equal(f.files.has(f.cache+'unrelated/icon.png'),true);
 await assert.rejects(f.api.removeRecordingFiles(['../../outside']),/identifier/);
});
test('All cleanup includes unindexed raw folders, ZIP duplicates and caches; keeps only reusable calibration',async()=>{
 const f=fixture();for(const name of ['recordings/orphan.json','camera-trials/camera-orphan.mp4','camera-distance-trials/distance-trial-1.zip','camera-distance-trials/distance-trial-1/frames/1.jpg','camera-distance-trials/pending-validation.json','camera-imu-noise/noise.zip','camera-calibration/calibration-1.zip','camera-calibration/calibration-1/frames/1.jpg','camera-calibration/latest-lens.json','camera-calibration/pending-reference.json','camera-calibration/lens.json','camera-calibration/reference.json','camera-calibration/rapid-profile.json','camera-calibration/computer.json','camera-calibration/geometry.json','camera-calibration/noise.json','other/keep.txt'])f.files.set(f.root+name,'data');for(const name of ['gait-exports/one.csv','Camera/partial.mp4','update-bundle.js'])f.files.set(f.cache+name,'cache');
 assert.ok(await f.api.recordingStorageBytes()>0);await f.api.removeAllRecordingFiles();await f.api.removeResearchCaptures();assert.equal(await f.api.recordingStorageBytes(),0);
 assert.deepEqual([...f.files.keys()].sort(),['camera-calibration/lens.json','camera-calibration/reference.json','camera-calibration/rapid-profile.json','camera-calibration/computer.json','camera-calibration/geometry.json','camera-calibration/noise.json','other/keep.txt'].map(n=>f.root+n).concat(f.cache+'update-bundle.js').sort());
});
test('File deletion failure is surfaced, never reported as successful or silently backed up',async()=>{
 const f=fixture();f.files.set(f.root+'recordings/a.json','raw');f.storage.fail=f.root+'recordings/a.json';await assert.rejects(f.api.removeRecordingFiles(['a']),/Disk error/);assert.equal(f.files.get(f.root+'recordings/a.json'),'raw');assert.equal(f.deleted.length,0);
});

test('Cleanup retains the on-phone profile and excludes it from disposable capture size',async()=>{
 const f=fixture();f.files.set(f.root+'camera-calibration/on-device-profile.json','reusable-profile');f.files.set(f.root+'camera-calibration/calibration-123.zip','raw');
 await f.api.removeResearchCaptures();assert.equal(f.files.get(f.root+'camera-calibration/on-device-profile.json'),'reusable-profile');assert.equal(await f.api.recordingStorageBytes(),0);
});
test('Deleting a recording removes its main camera ZIP and unpacked frames while preserving other participants',async()=>{
 const f=fixture();for(const id of ['a','b'])for(const file of ['gait-camera-'+id+'.zip','gait-camera-'+id+'/frames/0.jpg'])f.files.set(f.root+'gait-camera-captures/'+file,'data');
 await f.api.removeRecordingFiles(['a']);assert.equal([...f.files.keys()].filter(k=>k.includes('gait-camera-a')).length,0);assert.equal([...f.files.keys()].filter(k=>k.includes('gait-camera-b')).length,2);
 await f.api.removeAllRecordingFiles();assert.equal([...f.files.keys()].filter(k=>k.includes('gait-camera-')).length,0);
});
test('Session deletion removes both modern and legacy storage, preserving unrelated sessions and participant metadata',async()=>{
 const f=fixture(),data=new Map([['gaitsteps:index:v2',JSON.stringify([{id:'a',date:'2026-10-08'},{id:'b',date:'2026-10-08'}])],['gaitsteps:sessions',JSON.stringify([{id:'a',date:'2026-10-08'},{id:'c',date:'2026-10-08'}])],['gaitsteps:participants:v1','[]']]);
 const store=load('store',{'./recordingStorage':f.api,'./language':{},'./participantLinks':{recoverParticipantProfiles:p=>p},'./reviewRecording':{},'@react-native-async-storage/async-storage':{getItem:async k=>data.get(k)??null,setItem:async(k,v)=>data.set(k,v),removeItem:async k=>data.delete(k)},'expo-file-system':f.storage});
 f.files.set(f.root+'recordings/a.json','raw');await store.deleteSessions(['a']);assert.deepEqual(JSON.parse(data.get('gaitsteps:index:v2')).map(s=>s.id),['b']);assert.deepEqual(JSON.parse(data.get('gaitsteps:sessions')).map(s=>s.id),['c']);assert.equal(data.get('gaitsteps:participants:v1'),'[]');
 await store.clearRecordedData();assert.equal(data.has('gaitsteps:index:v2'),false);assert.equal(data.has('gaitsteps:sessions'),false);assert.equal(data.has('gaitsteps:participants:v1'),true);
});
test('Storage screen requires deliberate destructive confirmation, then refreshes emptied storage',async()=>{
 const React=require('react'),renderer=require('react-test-renderer');let dialog,calls=0;
 const mock={'react':React,'react-native':{Platform:{OS:'android'},Alert:{alert:(...args)=>dialog=args}},'@react-navigation/native':{useFocusEffect:cb=>React.useEffect(cb,[cb])},
  '../components/Screen':{Screen:p=>React.createElement('Screen',{},p.children,p.actions),Body:p=>React.createElement('Body',{},p.children),ui:{}},'../components/BigButton':p=>React.createElement('Button',p),'../i18n':{useLanguage(){},t:s=>s,Text:p=>React.createElement('Text',{},p.children)},
  '../store':{getSessions:async()=>[{id:'a'},{id:'b'}],clearRecordedData:async()=>{calls++;}},'../recordingStorage':{recordingStorageBytes:async()=>calls?0:2048}};
 const Screen=load('screens/StorageScreen',mock).default;let tree;await renderer.act(async()=>{tree=renderer.create(React.createElement(Screen,{navigation:{popToTop(){}}}));await new Promise(r=>setImmediate(r));});
 renderer.act(()=>tree.root.findAllByType('Button').find(b=>b.props.label==='Delete all recorded data').props.onPress());assert.equal(calls,0);assert.equal(dialog[2][0].style,'cancel');assert.equal(dialog[2][1].style,'destructive');
 await renderer.act(async()=>{dialog[2][1].onPress();await new Promise(r=>setImmediate(r));});assert.equal(calls,1);assert.ok(tree.root.findAllByType('Body').some(b=>b.props.children==='Recorded data deleted. No app backup was kept.'));renderer.act(()=>tree.unmount());
});
