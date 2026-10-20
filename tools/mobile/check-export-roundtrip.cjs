// Replay exports from the disposable emulator using actual pure app modules.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{createRequire}=require('node:module');
const root=path.resolve(__dirname,'../..'),app=path.join(root,'android'),requireApp=createRequire(path.join(app,'package.json')),ts=requireApp('typescript');
const cache={};function load(name){let file=path.resolve(app,'src',name);if(!file.endsWith('.ts'))file+='.ts';if(cache[file])return cache[file].exports;const module={exports:{}};cache[file]=module;
 vm.runInNewContext(ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{esModuleInterop:true,target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText,{module,exports:module.exports,console,Date,Math,performance,require:id=>id==='./releaseInfo'?{releaseInfo:()=>({appVersion:'emulator-test',buildNumber:'28',embedded:true})}:id.startsWith('.')?load(path.resolve(path.dirname(file),id)):requireApp(id)},{filename:file});return module.exports;}
const folder=path.join(app,'dist/acceptance/native-recordings'),output=path.join(app,'dist/acceptance/export-roundtrip');fs.mkdirSync(output,{recursive:true});
const records=fs.readdirSync(folder).filter(n=>n.endsWith('.json')&&n!=='verification-summary.json').map(n=>JSON.parse(fs.readFileSync(path.join(folder,n),'utf8')));
const six=records.find(s=>s.assessmentSetup?.protocol==='6mwt');assert.ok(six,'Run and retain the native 6MWT first.');
const exporter=load('exportData'),parser=load('reviewRecording'),checks=[];
for(const format of ['json','csv']){
 const text=format==='json'?exporter.exportJSON(six):exporter.exportCSV(six);fs.writeFileSync(path.join(output,'six-minute.'+format),text);
 const parsed=format==='json'?parser.parseReviewRecording(text):parser.parseReviewRecordingCsv(text);
 for(const name of ['accelerometer','gyroscope','magnetometer'])assert.equal(parsed.recording.streams[name].length,six.recording.streams[name].length);
 assert.equal(parsed.participantId,six.participantId);assert.equal(parsed.protocolExecution.end,'duration');assert.equal(parsed.isPractice,true);
 checks.push({format,bytes:Buffer.byteLength(text),passed:true,rawSampleCountsPreserved:true});
 const fresh={...six,id:'EMU-six-'+format+'-import'};
 fs.writeFileSync(path.join(output,'native-import.'+format),format==='json'?exporter.exportJSON(fresh):exporter.exportCSV(fresh));
}
fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({physicalPhoneUsed:false,recordingId:six.id,checks},null,2));console.log(JSON.stringify(checks));
