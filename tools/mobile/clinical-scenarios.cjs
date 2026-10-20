// Reproducible native IMU-flow checks. Distance tracking is tested separately.
const fs=require('node:fs'),path=require('node:path'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'android/dist/emulator-lab/clinical-scenarios');
fs.mkdirSync(out,{recursive:true});
const tap=label=>({action:'tap',label}),wait=seconds=>({action:'wait',seconds}),wave=seconds=>({action:'sensor-wave',seconds});
const protocols=process.argv.slice(2).length?process.argv.slice(2):['10mwt','tug','2mwt','6mwt'];
async function main(){
 const report={physicalPhoneUsed:false,simulatedSensors:true,distanceEnabled:false,audibleSpeechValidated:false,runs:[]};
 for(const p of protocols){
  if(!['10mwt','tug','2mwt','6mwt'].includes(p))throw Error('Unknown clinical protocol');
  const scenario=[tap('Start a walk'),{action:'tap-if-present',label:'Record motion only'},tap('Choose a saved person'),tap('EMU-SYNTHETIC-NOT-PATIENT'),tap('Language and audio settings'),{action:'set-switch',label:'Voice guidance',value:'false'},{action:'set-switch',label:'Practice walk',value:'true'},tap('Done'),tap('Continue'),{action:'tap-scroll',label:p.toUpperCase()},{action:'set-switch',label:'Phone distance',value:'false'},tap('Review stroke history'),
   {action:'tap-choice',group:'Affected brain hemisphere',label:'unknown'},{action:'tap-choice',group:'Affected body side',label:'unknown'},{action:'scroll'},
   {action:'tap-choice',group:'Time since stroke',label:'unknown'},tap('Patient or caregiver'),tap('Done')];
  if(p==='2mwt'||p==='6mwt')scenario.push({action:'scroll'},{action:'type',label:'Measured course length in metres',value:'3'},{action:'dismiss-keyboard'});
  scenario.push(tap('Continue'),tap('I can walk without hands-on help, using my usual cane or quad stick if needed. The path is clear and I agree to save movement data.'),tap('Start test'),wait(20),wave(5),wait(12),wave(6));
  if(p==='2mwt'||p==='6mwt'){
   // Real Android wall-clock durations, including stationary rests. No clock shortcut.
   let seconds=p==='2mwt'?120:360;while(seconds>0){const chunk=Math.min(seconds,55);scenario.push(wait(chunk),{action:'source'});seconds-=chunk;}
  }else scenario.push(wait(25)); // Eight-second quiet warning + ten-second resume grace, with sensor-window margin.
  scenario.push({action:'assert',label:'Recording saved'},tap('Back to home'));
  const file=path.join(out,p+'.json');fs.writeFileSync(file,JSON.stringify(scenario,null,2));
  const began=new Date().toISOString();console.log('Starting actual Android '+p+' recording flow.');
  const code=await new Promise((resolve,reject)=>{const log=fs.createWriteStream(path.join(out,p+'.log'));const child=spawn(process.execPath,[path.join(__dirname,'interact.cjs'),'--scenario',file],{cwd:root});child.stdout.on('data',b=>{log.write(b);process.stdout.write(b);});child.stderr.on('data',b=>log.write(b));child.on('error',reject);child.on('close',c=>{log.end();resolve(c);});});
  let saved;
  if(code===0){
   const adb=path.join(root,'android/dist/native-distance-tools/android-sdk/platform-tools/adb.exe');
   const device=(...a)=>execFileSync(adb,['-s','emulator-5560',...a],{encoding:'utf8',maxBuffer:64*1024*1024,timeout:30000});
   const name=device('shell','ls','-t','/data/data/com.gaitsteps.app/files/recordings').trim().split(/\r?\n/)[0];
   if(!/^[a-zA-Z0-9_-]+\.json$/.test(name))throw Error('Unexpected virtual recording filename');
   const raw=device('shell','cat','/data/data/com.gaitsteps.app/files/recordings/'+name),s=JSON.parse(raw);
   fs.writeFileSync(path.join(out,p+'-recording.json'),raw);
   saved={id:s.id,protocol:s.assessmentSetup?.protocol,isPractice:s.isPractice,participant:s.participantLabel,execution:s.protocolExecution,stopReason:s.recording?.stopReason,assessmentCompleted:s.assessment?.completed,streamCounts:Object.fromEntries(Object.entries(s.recording?.streams??{}).map(([k,v])=>[k,v.length]))};
  }
  const expected=p==='2mwt'||p==='6mwt'?'duration':'auto-stop-estimate';
  const passed=code===0&&saved?.protocol===p&&saved.isPractice===true&&saved.stopReason==='completed'&&saved.execution?.end===expected&&saved.assessmentCompleted===false&&Object.values(saved.streamCounts).every(n=>n>0);
  report.runs.push({protocol:p,startedAt:began,completedAt:new Date().toISOString(),exitCode:code,scenario:file,saved,passed});fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
  if(!passed)throw Error(p+' interaction or saved-record contract failed; retained log and screen identify the actual reply.');
 }
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
