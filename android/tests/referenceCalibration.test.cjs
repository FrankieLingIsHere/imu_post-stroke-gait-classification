const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),ts=require('typescript');
function load(storage={},fetch=async()=>({ok:true,json:async()=>({})})){
 const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.resolve(__dirname,'../src/referenceCalibration.ts'),'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText,
 {module,exports:module.exports,require:()=>storage,URL,fetch,AbortController,setTimeout,clearTimeout});return module.exports;
}
const computer={kind:'gaittrace-local-calibration-pair-v1',url:'http://192.168.1.42:8765',token:'a'.repeat(64)};
test('Local calibration pairing accepts private IPv4 only and rejects malformed/scoring endpoints',()=>{
 const a=load();assert.equal(a.validateCalibrationComputer(computer),computer);
 for(const url of ['https://example.com:8765','http://8.8.8.8:8765','http://192.168.1.999:8765','http://192.168.1.1:80','http://127.0.0.1:8765','http://192.168.1.1:8765/path'])assert.throws(()=>a.validateCalibrationComputer({...computer,url}));
 assert.throws(()=>a.validateCalibrationComputer({...computer,token:'x'.repeat(64)}));
});
test('QR pairing verifies actual processor identity before saving the connection',async()=>{
 const saved=[];const storage={documentDirectory:'file:///doc/',async makeDirectoryAsync(){},async writeAsStringAsync(p,v){saved.push({p,v});}};
 const a=load(storage,async(_url,options)=>{assert.equal(options.headers.Authorization,'Bearer '+computer.token);return {ok:true,json:async()=>({kind:'gaittrace-local-calibration-service-v1',method:'ikalibr-tro-2025',distanceReady:false})};});
 await a.connectCalibrationComputer(JSON.stringify(computer));assert.equal(saved.length,1);
 await assert.rejects(load(storage,async()=>({ok:true,json:async()=>({method:'fake'})})).connectCalibrationComputer(JSON.stringify(computer)));assert.equal(saved.length,1);
});
test('Reference output never grants metric readiness or accepts another device',()=>{
 const a=load(),binding={installationId:'one',captureId:'calibration-1',cameraId:'1',width:640,height:480,imageAxes:'native-sensor-unrotated-unmirrored',sensorOrientationDegrees:270,stabilizationRequested:'off',capturePipeline:'native-camera-imu-v2',opticalSetup:'waist-bag-window'};
 const r={schemaVersion:1,kind:'phone-reference-camera-imu-calibration-v1',method:'ikalibr-tro-2025',status:'reference-solved-review-required',cameraImuCandidateReady:false,fullCalibrationReady:false,distanceReady:false,independentDistanceValidation:false,binding,upstreamParameters:{CalibParam:{}},reviewRequired:['physical-bounds'],sourceSha256:'a'.repeat(64),software:{image:'ulong2/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c',executableSha256:'b'.repeat(64)}};
 assert.equal(a.validateReferenceCalibration(r,binding).distanceReady,false);
 assert.throws(()=>a.validateReferenceCalibration({...r,distanceReady:true},binding));assert.throws(()=>a.validateReferenceCalibration(r,{...binding,installationId:'other'}));
 assert.throws(()=>a.validateReferenceCalibration({...r,upstreamParameters:null},binding));
});
test('Optional computer feedback coalesces pending updates and stops cleanly without blocking the lens capture',async()=>{
 const calls=[];let release;
 const a=load({},async(url,options)=>{calls.push({url,options});return new Promise(r=>release=r);});
 const display=a.createLensFeedback(computer);
 display.send({acceptedViews:1,hint:'Move the tablet.',status:'checking'});
 display.send({acceptedViews:2,hint:'Pause.',status:'checking'});
 display.send({acceptedViews:3,hint:'Turn.',status:'checking'});
 assert.equal(calls.length,1,'One request in flight');
 assert.equal(calls[0].url,computer.url+'/api/lens-progress');
 assert.equal(calls[0].options.headers.Authorization,'Bearer '+computer.token);
 assert.deepEqual(JSON.parse(calls[0].options.body),{acceptedViews:1,hint:'Move the tablet.',status:'checking'});
 display.close();assert.equal(calls[0].options.signal.aborted,true);
 release({ok:true});await new Promise(r=>setImmediate(r));
 display.send({acceptedViews:4,hint:'Late.',status:'checking'});assert.equal(calls.length,1,'No late or queued sends after closing');
 const failed=load({},async()=>{throw Error('Wi-Fi unavailable');}).createLensFeedback(computer);
 assert.doesNotThrow(()=>failed.send({acceptedViews:0,hint:'Continue on phone.',status:'checking'}));
 await new Promise(r=>setImmediate(r));failed.close();
});
test('Computer framing sends only the latest local JPEG through bounded optional transport',async()=>{
 const calls=[];const storage={EncodingType:{Base64:'base64'},async readAsStringAsync(uri,options){assert.equal(uri,'file:///native-frame.jpg');assert.equal(options.encoding,'base64');return 'real-frame-base64';}};
 const a=load(storage,async(url,options)=>{calls.push(JSON.parse(options.body));return {ok:true};});
 const display=a.createLensFeedback(computer);
 display.send({acceptedViews:2,hint:'Pause.',status:'checking'},'file:///native-frame.jpg');
 await new Promise(r=>setImmediate(r));assert.equal(calls[0].jpeg,'real-frame-base64');display.close();
 let readDone;const slow=load({EncodingType:{Base64:'base64'},readAsStringAsync(){return new Promise(r=>readDone=r);}},async()=>{throw Error('A cancelled frame must not be uploaded');}).createLensFeedback(computer);
 slow.send({acceptedViews:3,hint:'Pause.',status:'checking'},'file:///native-frame.jpg');slow.close();readDone('late-frame');await new Promise(r=>setImmediate(r));
});
