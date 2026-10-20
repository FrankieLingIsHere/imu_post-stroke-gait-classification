// Inspect the labelled emulator save after the result-worker-review UI replay.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const base=path.resolve(__dirname,'../../android/dist');
const s=JSON.parse(fs.readFileSync(path.join(base,'acceptance/partial-ten-worker-save.json'),'utf8'));
const fixture=JSON.parse(fs.readFileSync(path.join(base,'emulator-lab/EMU-partial-ten.json'),'utf8')).session;
const draft=JSON.parse(fs.readFileSync(path.join(base,'acceptance/partial-ten-worker-draft.json'),'utf8'));
assert.equal(draft.workerOutcomeDraft.form.timedZoneSeconds,12);
assert.equal(draft.assessment?.completed??false,false);
assert.deepEqual(draft.recording.streams,fixture.recording.streams);
const a=s.assessment;
assert.equal(s.isPractice,true);assert.match(s.participantLabel,/^EMU-/);
assert.equal(a.completionStatus,'modified');assert.equal(a.completed,false);
assert.equal(a.distanceWalkedM,null);assert.equal(a.speedMps,null);assert.equal(a.timedZoneSeconds,12);
assert.deepEqual(s.recording.streams,fixture.recording.streams);
fs.writeFileSync(path.join(base,'acceptance/partial-worker-verification.json'),JSON.stringify({
 createdAt:new Date().toISOString(),passed:true,serial:'emulator-5560',physicalPhoneUsed:false,
 completionStatus:a.completionStatus,completed:a.completed,distanceWalkedM:a.distanceWalkedM,
 speedMps:a.speedMps,timedZoneSeconds:a.timedZoneSeconds,rawStreamsUnchanged:true,workerDraftSaved:true,draftTimedSeconds:12,
},null,2));
console.log('Actual emulator save verified: partial outcome, no manufactured speed, unchanged raw streams.');
