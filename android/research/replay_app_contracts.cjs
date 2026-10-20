/** Execute actual TypeScript contracts on local retained replays. No React or sensor substitute. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
function load(name,cache={}){
 const file=path.resolve(__dirname,'../src',name.endsWith('.ts')?name:name+'.ts');
 if(cache[file])return cache[file].exports;const module={exports:{}};cache[file]=module;
 vm.runInNewContext(ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText,{module,exports:module.exports,require:id=>id.startsWith('.')?load(path.resolve(path.dirname(file),id),cache):require(id)});
 return module.exports;
}
function evaluate(raw){
 const p=raw.reference,pending={sessionId:raw.manifest.sessionId,captureId:raw.manifest.captureId,protocol:raw.manifest.protocol,referenceSha256:p.sourceSha256,binding:p.binding};
 load('onDeviceProfile').validateOnDeviceProfile(p,p.binding);
 const result=load('phoneDistanceModel').phoneDistanceResult(raw,pending);
 load('gaitDistanceModel').validateGaitDistanceResult(result,pending);
 return result;
}
module.exports={load,evaluate};
