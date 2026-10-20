// Reuse a labelled emulator capture; never invent patient or clinical evidence.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const source=process.argv[2]||path.join(root,'android/dist/acceptance/native-recordings/2026-10-10T13-53-59-156Z-0c6e5593.json');
const s=JSON.parse(fs.readFileSync(source,'utf8').replace(/^\uFEFF/,''));
assert.equal(s.isPractice,true);assert.match(s.participantLabel||'',/^EMU-/);
assert.equal(s.assessmentSetup?.protocol,'10mwt');
s.id='EMU-partial-ten-result-review';delete s.assessment;
const output=path.join(root,'android/dist/emulator-lab/EMU-partial-ten.json');
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify({exportSchemaVersion:3,source:'device',session:s}));
console.log(output);
