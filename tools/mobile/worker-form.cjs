// Native 31-item navigation/persistence fixture. Ratings are test inputs, not clinical observations.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'android/dist/emulator-lab/worker-form');
fs.mkdirSync(out,{recursive:true});
const controls=[{action:'tap',label:'Summary'},{action:'scroll'},{action:'tap',label:'Open G.A.I.T. worker assessment'},{action:'type',label:'Assessor ID or initials',value:'EMU-RATER-NOT-CLINICAL'},{action:'dismiss-keyboard'},{action:'tap',label:'left'},{action:'scroll'},{action:'tap',label:'Video observation'},{action:'tap',label:'Begin items'}];
for(let i=1;i<=31;i++)controls.push({action:'tap-first-radio'},{action:'tap',label:i===31?'Review assessment':'Next item'});
controls.push({action:'assert',label:'Items rated: 31 of 31'},{action:'assert',label:'G.A.I.T. total: 0 / 62'},{action:'assert-in-bounds',label:'Finish assessment'},{action:'tap',label:'Finish assessment'},{action:'assert',label:'Recording details'},{action:'tap',label:'Review G.A.I.T. worker assessment'},{action:'assert',label:'Items rated: 31 of 31'},{action:'source'});
const file=path.join(out,'controls.json');fs.writeFileSync(file,JSON.stringify(controls,null,2));
if(process.argv.includes('--generate-only'))console.log(file);
else{const run=spawnSync(process.execPath,[path.join(__dirname,'interact.cjs'),'--scenario',file],{cwd:root,stdio:'inherit'});process.exitCode=run.status??1;}
