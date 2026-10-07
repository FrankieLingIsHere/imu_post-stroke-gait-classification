const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),ts=require('typescript');
function api(storage={}){const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(require('node:path').join(__dirname,'../src/cameraCalibration.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,{module,exports:module.exports,require:id=>id==='react-native'?{Platform:{OS:'web'}}:storage});return module.exports;}
function fixture(){const binding={installationId:'one-phone',captureId:'calibration-123',cameraId:'1',width:640,height:480,imageAxes:'native-sensor-unrotated-unmirrored',sensorOrientationDegrees:270,stabilizationRequested:'off'};
 return {capture:{metadata:JSON.stringify({...binding,status:'completed'})},report:{schemaVersion:1,kind:'phone-camera-imu-calibration-v1',status:'geometry-candidate',distanceReady:false,independentDistanceValidation:false,errors:[],binding,cameraImuRotationTiming:{passed:true},translationAcceleration:{passed:true},lens:{cameraMatrix:[[400,0,320],[0,400,240],[0,0,1]],heldOutP90Pixels:.3}}};}
test('Processed calibration is phone-specific, never distance validation',()=>{const {report,capture}=fixture();const a=api();assert.equal(a.validateCalibrationReport(report,capture).distanceReady,false);assert.equal(a.calibrationBridge(),null);});
test('Different phone, camera, resolution or incomplete capture cannot reuse calibration',()=>{for(const key of ['installationId','cameraId','width','imageAxes','captureId']){const {report,capture}=fixture();report.binding[key]='different';assert.throws(()=>api().validateCalibrationReport(report,capture),/another phone/);}const {report,capture}=fixture();capture.metadata=JSON.stringify({...report.binding,status:'user-stopped'});assert.throws(()=>api().validateCalibrationReport(report,capture));});
test('Rejected processing, invalid intrinsics and claimed distance readiness stay rejected',()=>{for(const mutate of [r=>r.status='rejected',r=>r.distanceReady=true,r=>r.independentDistanceValidation=true,r=>r.cameraImuRotationTiming.passed=false,r=>r.lens.cameraMatrix[0][0]=-1,r=>r.lens.heldOutP90Pixels=3]){const {report,capture}=fixture();mutate(report);assert.throws(()=>api().validateCalibrationReport(report,capture));}});
test('New acquisition profile cannot lose or change its optical window binding',()=>{
 const {report,capture}=fixture();const meta={...JSON.parse(capture.metadata),capturePipeline:'native-camera-imu-v2',opticalSetup:'waist-bag-window'};capture.metadata=JSON.stringify(meta);
 assert.throws(()=>api().validateCalibrationReport(report,capture));Object.assign(report.binding,{capturePipeline:meta.capturePipeline,opticalSetup:meta.opticalSetup});assert.equal(api().validateCalibrationReport(report,capture),report);
 report.binding.opticalSetup='clear-lens';assert.throws(()=>api().validateCalibrationReport(report,capture));
});
test('Noise capture is stored separately without overwriting the board or self-copying',async()=>{
 const f=storageFixture(),uri=f.storage.documentDirectory+'camera-imu-noise/imu-noise-123.zip';f.set(uri,'noise ZIP');f.set(f.directory+'latest.json','board index');
 const record=await api(f.storage).retainNoiseCapture({uri:uri.replace('file:///','file:/'),metadata:JSON.stringify({kind:'phone-imu-noise-capture-v1',captureId:'imu-noise-123',distanceReady:false}),error:null});
 assert.equal(record.uri,uri);assert.equal(f.copies.length,0);assert.equal(f.get(f.directory+'latest.json'),'board index');
 await assert.rejects(api(f.storage).retainNoiseCapture({uri,metadata:JSON.stringify({kind:'phone-imu-noise-capture-v1',captureId:'../other',distanceReady:false})}),/Invalid/);
});
function storageFixture(){
 const directory='file:///data/user/0/com.gaitsteps.app/files/camera-calibration/';
 const normalize=uri=>decodeURIComponent(uri.replace(/^file:\/+/, '/'));const files=new Map(),copies=[];
 const storage={documentDirectory:'file:///data/user/0/com.gaitsteps.app/files/',async makeDirectoryAsync(){},
  async getInfoAsync(uri){if(uri===directory)return {exists:true,isDirectory:true,size:0};const v=files.get(normalize(uri));return v===undefined?{exists:false}:{exists:true,isDirectory:false,size:v.length};},
  async readAsStringAsync(uri){const v=files.get(normalize(uri));if(v===undefined)throw Error('Missing file');return v;},
  async writeAsStringAsync(uri,value){files.set(normalize(uri),value);},
  async copyAsync({from,to}){if(normalize(from)===normalize(to))throw Error('Source and destination are the same');copies.push({from,to});files.set(normalize(to),files.get(normalize(from)));},
  async readDirectoryAsync(){return [...files.keys()].filter(p=>p.startsWith(normalize(directory))).map(p=>p.slice(normalize(directory).length)).filter(p=>!p.includes('/'));}};
 return {directory,files,copies,storage,set:(uri,value)=>files.set(normalize(uri),value),get:uri=>files.get(normalize(uri))};
}
test('Native ZIP already in document storage is indexed without copying onto itself',async()=>{
 const f=storageFixture(),id='calibration-1791295928044',uri=f.directory+id+'.zip';f.set(uri,'actual native ZIP bytes');
 const record=await api(f.storage).retainCalibrationCapture({uri:uri.replace('file:///','file:/'),metadata:JSON.stringify({captureId:id}),error:null});
 assert.equal(record.uri,uri);assert.equal(f.copies.length,0);assert.equal(JSON.parse(f.get(f.directory+'latest.json')).uri,uri);
});
test('Separate cache ZIP is copied, and missing/empty ZIPs cannot be marked saved',async()=>{
 const f=storageFixture();f.set('file:///cache/capture.zip','bytes');
 await api(f.storage).retainCalibrationCapture({uri:'file:///cache/capture.zip',metadata:JSON.stringify({captureId:'calibration-123'}),error:null});assert.equal(f.copies.length,1);
 for(const uri of ['file:///cache/missing.zip','file:///cache/empty.zip']){f.set('file:///cache/empty.zip','');await assert.rejects(api(f.storage).retainCalibrationCapture({uri,metadata:JSON.stringify({captureId:'calibration-124'}),error:null}),/missing or empty/);}
});
test('Capture lost by the build-8 self-copy failure is recovered from native manifest and ZIP',async()=>{
 const f=storageFixture();for(const id of ['calibration-100','calibration-1791295928044']){f.set(f.directory+id+'.zip','native zip');f.set(f.directory+id+'/manifest.json',JSON.stringify({schemaVersion:1,captureId:id,status:'completed',error:null}));}
 const result=await api(f.storage).latestCalibrationCapture();assert.equal(JSON.parse(result.metadata).captureId,'calibration-1791295928044');assert.equal(f.copies.length,0);assert.ok(f.get(f.directory+'latest.json'));
});
test('Recovery skips empty ZIP or missing manifest and never invents a complete capture',async()=>{
 const f=storageFixture();f.set(f.directory+'latest.json','invalid JSON');f.set(f.directory+'calibration-300.zip','');f.set(f.directory+'calibration-200.zip','zip without manifest');
 f.set(f.directory+'calibration-100.zip','partial ZIP');f.set(f.directory+'calibration-100/manifest.json',JSON.stringify({schemaVersion:1,captureId:'calibration-100',status:'interrupted',error:'Camera disconnected'}));
 const result=await api(f.storage).latestCalibrationCapture();assert.equal(JSON.parse(result.metadata).status,'interrupted');assert.equal(result.error,'Camera disconnected');
});

function lensFixture(){
 const binding={installationId:'one-phone',captureId:'calibration-321',cameraId:'1',width:640,height:480,imageAxes:'native-sensor-unrotated-unmirrored',sensorOrientationDegrees:270,stabilizationRequested:'off',focusRequestedDioptres:0,capturePipeline:'native-camera-imu-v2',opticalSetup:'waist-bag-window'};
 const report={schemaVersion:1,kind:'phone-camera-lens-calibration-v1',method:'opencv-zhang-2000',status:'lens-candidate',lensReady:true,fullCalibrationReady:false,distanceReady:false,independentDistanceValidation:false,errors:[],acceptedViews:24,binding,
  lens:{model:'opencv-pinhole-radtan5',cameraMatrix:[[500,0,320],[0,500,240],[0,0,1]],distortion:[0,0,0,0,0],heldOutP90Pixels:.2,focalSubsetDriftFraction:.001,principalSubsetDriftFraction:.001}};
 return {binding,report,capture:{uri:'file:///cache/lens.zip',metadata:JSON.stringify({...binding,status:'completed',captureMode:'guided-lens-zhang',lensCalibration:report,error:null}),error:null}};
}
test('Published lens profile never grants distance and cannot cross phone/optics bindings',()=>{
 const a=api(),{binding,report}=lensFixture();assert.equal(a.validateLensReport(report,binding).distanceReady,false);
 for(const key of ['installationId','cameraId','width','focusRequestedDioptres','capturePipeline','opticalSetup'])assert.throws(()=>a.validateLensReport(report,{...binding,[key]:'other'}));
 for(const mutate of [r=>r.method='custom-fit',r=>r.fullCalibrationReady=true,r=>r.lensReady=false,r=>r.acceptedViews=undefined,r=>r.lens.heldOutP90Pixels=3,r=>r.lens.distortion[0]=NaN,r=>r.lens.focalSubsetDriftFraction=.2]){
  const f=lensFixture();mutate(f.report);assert.throws(()=>a.validateLensReport(f.report,f.binding));
 }
});
test('Automatic lens result recovery rejects interrupted captures and preserves the legacy capture index',async()=>{
 const f=storageFixture(),a=api(f.storage),v=lensFixture();f.set(v.capture.uri,'actual lens ZIP');f.set(f.directory+'latest.json','old geometry index');
 const stored=await a.retainCalibrationCapture(v.capture);assert.equal(f.get(f.directory+'latest.json'),'old geometry index');assert.ok(f.get(f.directory+'latest-lens.json'));
 assert.equal((await a.recoverLensReport(stored)).kind,'phone-camera-lens-calibration-v1');
 const partial={...v.capture,metadata:JSON.stringify({...JSON.parse(v.capture.metadata),status:'user-stopped'})};assert.equal(await a.recoverLensReport(partial),null);
 f.set(f.directory+'lens.json',JSON.stringify(v.report));assert.equal((await a.currentLensReport(v.binding)).lensReady,true);
 assert.equal(await a.currentLensReport({...v.binding,opticalSetup:'clear-lens'}),null);
});
