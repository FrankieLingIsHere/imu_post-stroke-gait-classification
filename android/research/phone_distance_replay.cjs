// Offline verification of the actual app's phone-result rule. No training/phone-speed claim.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ts=require('../node_modules/typescript');
function load(name){const module={exports:{}};vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(__dirname,'../src',name+'.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,{module,exports:module.exports,require:id=>load(id.replace('./',''))});return module.exports;}
const [input,states,out]=process.argv.slice(2);if(!out)throw Error('Usage: node phone_distance_replay.cjs ADAPTER_JSON STATES_CSV RESULT_JSON');
const raw=JSON.parse(fs.readFileSync(input,'utf8')),lines=fs.readFileSync(states,'utf8').trim().split(/\r?\n/);
if(states.endsWith('.ndjson'))raw.states=lines.filter(s=>s.startsWith('{')).map(s=>JSON.parse(s).state);
else {const keys=lines.shift().split(',');raw.states=lines.map(line=>Object.fromEntries(line.split(',').map((v,i)=>[keys[i],Number(v)])));}
raw.processingLocation='phone';raw.processingSeconds=null;
const m=raw.manifest,pending={sessionId:m.sessionId,captureId:m.captureId,protocol:m.protocol,referenceSha256:raw.reference.sourceSha256,binding:Object.fromEntries(load('gaitDistanceModel').distanceBindingKeys.map(k=>[k,m[k]]))};
const result=load('phoneDistanceModel').phoneDistanceResult(raw,pending);load('gaitDistanceModel').validateGaitDistanceResult(result,pending);
fs.writeFileSync(out,JSON.stringify({historicalArtifactReplay:raw.softwareControl!==true,softwareControl:raw.softwareControl===true,actualAndroidExecution:false,result},null,2));
console.log(JSON.stringify({status:result.reason,distanceM:result.completeRouteEstimateMetres,actualAndroidExecution:false}));
