const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
function load(name){const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(__dirname,'../src',name+'.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,{module,exports:module.exports,require:id=>load(id.replace('./','')),console});return module.exports;}
const model=load('phoneDistanceModel');
function states(){return Array.from({length:347},(_,i)=>{const t=i/20;return {imu_time_s:t,initialized:1,px:Math.max(0,Math.min(12.3,t-1)),py:0,pz:0,vx:t>=1&&t<13.3?1:0,vy:0,vz:0,ba_norm:.01,bg_norm:.001,tic_norm:.04,g_norm:9.80665,rotation_change_deg:0,reboot:0};});}
test('Phone rule admits a continuous route and rejects resets, late initialization, jumps and ending drift',()=>{
 const s=states(),r=model.assessPhoneStates(s,1,13.3,17.3,'straight');assert.equal(r.fullRouteCovered,true);assert.ok(Math.abs(r.completeRouteEstimateMetres-12.3)<1e-8);
 const late=s.map(r=>({...r,initialized:r.imu_time_s<2?0:1}));assert.equal(model.assessPhoneStates(late,1,13.3,17.3,'straight').reason,'partial-route');
 for(const mutate of [a=>a[50].reboot=1,a=>a[50].px+=1,a=>a[50].px=NaN,a=>a[50].imu_time_s=null,a=>a[a.length-1].initialized=0]){const rows=states();mutate(rows);assert.equal(model.assessPhoneStates(rows,1,13.3,17.3,'straight').reason,'tracking-integrity-failed');}
 const drift=s.map(r=>({...r,px:r.px+Math.max(0,r.imu_time_s-13.3)*.1}));assert.equal(model.assessPhoneStates(drift,1,13.3,17.3,'straight').reason,'standing-drift');
});
test('Phone 10MWT uses 1 + 10 + 1 metres and refuses a timed zone for an incomplete 12 m course',()=>{
 const pending={sessionId:'sample',captureId:'gait-camera-sample',protocol:'10mwt',referenceSha256:'a'.repeat(64),binding:{}};
 const raw={manifest:{sessionId:'sample',captureId:'gait-camera-sample',protocol:'10mwt',diagnostics:{walkStartedBootNs:1e9,walkEndedBootNs:13.3e9,endBoundarySource:'main-protocol-native-command'}},reference:{sourceSha256:pending.referenceSha256},states:states(),processingLocation:'phone',processingRevision:'android-vins-fixed-rows-quiet-v1',captureEndSeconds:17.3,sourceSha256:'b'.repeat(64)};
 const result=model.phoneDistanceResult(raw,pending);assert.equal(result.method,'vins-mono-on-device-v1');assert.equal(result.testOutcome.timedZoneSeconds,10);assert.equal(result.testOutcome.speedMps,1);assert.equal(result.testOutcome.startOffsetSeconds,1);assert.equal(result.testOutcome.endOffsetSeconds,11);assert.equal(result.referenceDistanceMetres,null);assert.equal(result.clinicalOutcomeVerified,false);
 raw.states=raw.states.map(r=>({...r,px:r.px*.8}));assert.equal(model.phoneDistanceResult(raw,pending).testOutcome.status,'unavailable');
 assert.throws(()=>model.phoneDistanceResult({...raw,processingLocation:'computer'},pending));
});
test('Live 10MWT retains native crossings and withholds missing or inconsistent boundary evidence',()=>{
 const pending={sessionId:'sample',captureId:'gait-camera-sample',protocol:'10mwt',referenceSha256:'a'.repeat(64),binding:{}};
 const q={version:'ten-metre-boundaries-v1',usable:true,startBootNs:1e9,timedStartBootNs:2e9,timedEndBootNs:12e9,finishBootNs:13e9,origin:[0,0],axis:[1,0]};
 const raw={manifest:{sessionId:'sample',captureId:'gait-camera-sample',protocol:'10mwt',diagnostics:{walkStartedBootNs:1e9,walkEndedBootNs:13e9,tenMetreBoundaries:q}},reference:{kind:'phone-on-device-camera-imu-profile-v1',sourceSha256:pending.referenceSha256},states:states().map(r=>({...r,px:Math.min(12,r.px),py:r.px<1?0:Math.min(.15,(r.px-1)*.02)})),processingLocation:'phone',processingRevision:'android-openvins-live-v1',captureEndSeconds:17.3};
 const result=model.phoneDistanceResult(raw,pending);assert.equal(result.testOutcome.speedMps,1);assert.equal(result.testOutcome.timedZoneSeconds,10);
 for(const mutate of [b=>delete b.manifest.diagnostics.tenMetreBoundaries,b=>b.manifest.diagnostics.tenMetreBoundaries.timedStartBootNs+=1e8,b=>b.manifest.diagnostics.tenMetreBoundaries.axis=[0,1],b=>b.manifest.diagnostics.tenMetreBoundaries.usable=false,b=>b.states.splice(80,10)]){
  const bad=JSON.parse(JSON.stringify(raw));mutate(bad);assert.equal(model.phoneDistanceResult(bad,pending).testOutcome.status,'unavailable');
 }
});
