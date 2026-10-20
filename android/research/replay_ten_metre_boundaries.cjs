// Replays an actual Java LiveDistanceGate snapshot through production TypeScript.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript'),assert=require('node:assert/strict');
function load(name){const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(__dirname,'../src',name+'.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,{module,exports:module.exports,require:id=>load(id.replace('./','')),console});return module.exports;}
const fixture=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const pending={sessionId:'boundary-replay',captureId:'gait-camera-boundary-replay',protocol:'10mwt',referenceSha256:'a'.repeat(64),binding:{}};
const q=fixture.boundaries;
const raw={manifest:{...pending,diagnostics:{walkStartedBootNs:q.startBootNs,walkEndedBootNs:q.finishBootNs,tenMetreBoundaries:q,endBoundarySource:'on-device-estimated-12m-crossing'}},reference:{kind:'phone-on-device-camera-imu-profile-v1',sourceSha256:pending.referenceSha256},states:fixture.states,processingLocation:'phone',processingRevision:'android-openvins-live-v1',captureEndSeconds:17.2};
const model=load('phoneDistanceModel'),result=model.phoneDistanceResult(raw,pending);
assert.equal(result.testOutcome.status,'experimental');
assert.equal(result.testOutcome.startOffsetSeconds,(q.timedStartBootNs-q.startBootNs)/1e9);
assert.equal(result.testOutcome.endOffsetSeconds,(q.timedEndBootNs-q.startBootNs)/1e9);
assert.equal(result.testOutcome.timedZoneSeconds,10);assert.equal(result.testOutcome.speedMps,1);
assert.equal(load('gaitDistanceModel').cameraDistanceOutcome({protocol:'10mwt',status:'complete',result}).meanSpeedMps,1);
for(const mutate of [b=>delete b.manifest.diagnostics.tenMetreBoundaries,b=>b.manifest.diagnostics.tenMetreBoundaries.timedStartBootNs+=1e8,b=>b.manifest.diagnostics.tenMetreBoundaries.axis=[0,1],b=>b.manifest.diagnostics.tenMetreBoundaries.usable=false,b=>b.states.splice(80,10)]){
 const bad=JSON.parse(JSON.stringify(raw));mutate(bad);assert.equal(model.phoneDistanceResult(bad,pending).testOutcome.status,'unavailable',String(mutate));
}
console.log(JSON.stringify({passed:true,productionJavaAndTypeScript:true,softwarePosesOnly:true,timedZoneSeconds:result.testOutcome.timedZoneSeconds,speedMps:result.testOutcome.speedMps,negativeControls:5},null,2));
