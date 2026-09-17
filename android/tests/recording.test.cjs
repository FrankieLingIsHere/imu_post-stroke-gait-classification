// Deterministic contract tests. Hardware events are injected; these are not device trials.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function load(name, mocks = {}, globals = {}, cache = {}) {
  const filename = path.resolve(__dirname, '../src', name + '.ts');
  if (cache[filename]) return cache[filename].exports;
  const module = { exports: {} }; cache[filename] = module;
  const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: { esModuleInterop: true, target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS } }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, console, Date, Math, performance,
    require: id => id in mocks ? mocks[id] : id.startsWith('.') ? load(path.relative(path.resolve(__dirname, '../src'), path.resolve(path.dirname(filename), id)), mocks, globals, cache) : require(id), ...globals }, { filename });
  return module.exports;
}
const pure = load('recording');
const exporting = load('exportData');
const sample = (t, x = 1, y = 2, z = 3) => ({ x, y, z, elapsedMs: t, receivedAtUnixMs: 1700000000000 + t, sensorTimestampSeconds: 123 + t / 1000 });
function rig() {
  let now = 0;
  const sensors = Object.fromEntries(['Accelerometer', 'Gyroscope', 'Magnetometer'].map(n => [n, {
    callback: null, available: true, permission: true,
    async isAvailableAsync() { return this.available; },
    async requestPermissionsAsync() { return { granted: this.permission }; },
    setUpdateInterval(ms) { this.interval = ms; },
    addListener(callback) { this.callback = callback; return { remove: () => { this.callback = null; } }; }
  }]));
  const api = load('sensors', { 'expo-sensors': sensors, 'react-native': { Platform: { OS: 'android', Version: 35 } } }, { performance: { now: () => now } });
  return { sensors, api, setTime(t) { now = t; }, emit(name, t, value) { now = t; sensors[name].callback?.(value); } };
}
function recordFixture() {
  return { schemaVersion: 2, source: 'device', startedAt: '2026-09-12T00:00:00Z', elapsedSeconds: 1, requestedHz: pure.REQUESTED_HZ, units: pure.SENSOR_UNITS, stopReason: 'completed', placement: 'lower-back-upright-screen-out', coordinateFrame: 'device', streams: {
    accelerometer: Array.from({ length: 100 }, (_, i) => sample(i * 10)),
    gyroscope: Array.from({ length: 100 }, (_, i) => sample(i * 10)),
    magnetometer: Array.from({ length: 50 }, (_, i) => sample(i * 20)),
  }, guidanceEvents: [] };
}
test('All three sensors must be available and permitted', async () => {
  const r = rig(); await r.api.checkSensors();
  r.sensors.Magnetometer.available = false;
  await assert.rejects(r.api.checkSensors(), /magnetometer/);
  r.sensors.Magnetometer.available = true; r.sensors.Gyroscope.permission = false;
  await assert.rejects(r.api.checkSensors(), /motion access/);
});
test('Nine axes, independent rates, unmodified native timestamp and partial tails survive capture', () => {
  const r = rig(); const recorder = new r.api.SensorRecorder({ guidanceEnabled: false, voiceEnabled: true }, () => {});
  recorder.connect(); assert.equal(r.sensors.Accelerometer.interval, 10); assert.equal(r.sensors.Magnetometer.interval, 20);
  recorder.begin();
  r.emit('Accelerometer', 10, { x: 0.123456789, y: -2, z: 3, timestamp: 999.1 });
  r.emit('Gyroscope', 12, { x: 4, y: 5, z: 6, timestamp: 999.2 });
  r.emit('Magnetometer', 14, { x: 7, y: 8, z: 9, timestamp: 999.3 });
  r.emit('Accelerometer', 20, { x: 10, y: 11, z: 12, timestamp: 999.4 });
  const result = recorder.stop('user-stopped');
  assert.equal(result.streams.accelerometer.length, 2); assert.equal(result.streams.gyroscope.length, 1);
  assert.equal(result.streams.accelerometer[0].x, 0.123456789);
  assert.equal(result.streams.gyroscope[0].z, 6); assert.equal(result.streams.magnetometer[0].y, 8);
  assert.equal(result.streams.accelerometer[0].sensorTimestampSeconds, 999.1);
  assert.equal(result.streams.accelerometer[0].elapsedMs, 10);
  assert.equal(result.stopReason, 'user-stopped');
  assert.equal(recorder.stop('completed'), result);
  for (const sensor of Object.values(r.sensors)) assert.equal(sensor.callback, null);
});
test('Setup readings are excluded; non-finite events cannot poison JSON', () => {
  const r = rig(); const recorder = new r.api.SensorRecorder({ guidanceEnabled: false, voiceEnabled: false }, () => {});
  recorder.connect(); r.emit('Accelerometer', 10, { x: 1, y: 2, z: 3 }); recorder.begin();
  r.emit('Accelerometer', 20, { x: NaN, y: 2, z: 3 });
  const result = recorder.stop('interrupted');
  assert.equal(result.streams.accelerometer.length, 0);
  assert.ok(pure.recordingIssues(result).some(s => s.includes('No accelerometer')));
});
test('No missing sensor timestamps are invented', () => {
  const r = rig(); const recorder = new r.api.SensorRecorder({ guidanceEnabled: false, voiceEnabled: false }, () => {});
  recorder.connect(); recorder.begin(); r.emit('Magnetometer', 10, { x: 1, y: 2, z: 3 });
  assert.equal(recorder.stop('completed').streams.magnetometer[0].sensorTimestampSeconds, null);
});
test('Native event times measure rate despite batched callback arrival', () => {
  const samples = Array.from({ length: 100 }, (_, i) => ({ ...sample(i * 10), elapsedMs: 500 }));
  const stat = pure.streamStats(samples, 1);
  assert.ok(Math.abs(stat.hz - 100) < 1e-6); assert.equal(stat.timing, 'native');
});
test('Missing streams, slow rates, gaps and early stops become capture notes', () => {
  const r = recordFixture(); assert.equal(pure.recordingIssues(r).length, 0);
  r.streams.magnetometer = []; r.stopReason = 'interrupted';
  r.streams.gyroscope = [sample(0), sample(900)];
  const issues = pure.recordingIssues(r).join(' ');
  assert.match(issues, /No magnetometer/); assert.match(issues, /ended early/); assert.match(issues, /gap exceeded/); assert.match(issues, /slower/);
});
test('Constant acceleration is not classified as poor walking', () => {
  assert.equal(pure.recordingIssues(recordFixture()).length, 0);
});
test('Uncalibrated or moving phones do not trigger direction reminders', () => {
  const tracker = new pure.DirectionTracker();
  for (let t = 0; t < 3000; t += 10) tracker.calibrate(0.5, t, true);
  tracker.begin();
  for (let t = 3000; t < 10000; t += 10) assert.equal(tracker.update(1, t, true), null);
});
test('A sustained relative turn produces sparse reminders; tilt disables estimation', () => {
  const tracker = new pure.DirectionTracker();
  for (let t = 0; t <= 2500; t += 10) tracker.calibrate(0.01, t, true);
  tracker.begin(); const cues = [];
  for (let t = 2510; t < 20000; t += 10) {
    const angle = tracker.update(0.3, t, true); if (angle !== null) cues.push(t);
  }
  assert.ok(cues.length >= 1); for (let i = 1; i < cues.length; i++) assert.ok(cues[i] - cues[i - 1] >= 12000);
  tracker.update(0.3, 20010, false);
  assert.equal(tracker.ready, false); assert.equal(tracker.update(1, 20020, true), null);
});
test('CSV preserves all asynchronous events and explicit units without aligned rows', () => {
  const r = recordFixture(); const session = { id: 'test', date: r.startedAt, duration: 10, isPractice: false, windows: [], recording: r };
  const csv = exporting.exportCSV(session);
  assert.equal(csv.trim().split('\r\n').length, 251);
  for (const unit of ['g', 'rad/s', 'uT']) assert.ok(csv.includes('"' + unit + '"'));
  assert.equal(JSON.parse(exporting.exportJSON(session)).session.recording.streams.magnetometer.length, 50);
});
test('Legacy exports always identify simulated data and do not invent extra sensors', () => {
  const session = { id: 'old', date: '2026-09-01', duration: 10, isPractice: false, windows: [{ x: 1, y: 2, z: 3, timestamp: 100 }] };
  assert.equal(JSON.parse(exporting.exportJSON(session)).source, 'legacy-simulation');
  assert.match(exporting.exportCSV(session), /legacy-simulation/);
  assert.doesNotMatch(exporting.exportCSV(session), /"gyroscope"/);
});
test('Raw recording files round trip; retry after index failure is idempotent', async () => {
  const values = new Map(), files = new Map(); let fail = true;
  const storage = { async getItem(k) { return values.get(k) ?? null; }, async setItem(k, v) { if (fail) throw Error('quota'); values.set(k, v); } };
  const disk = { documentDirectory: '/documents/', async makeDirectoryAsync() {}, async writeAsStringAsync(k, v) { files.set(k, v); }, async readAsStringAsync(k) { if (!files.has(k)) throw Error('missing'); return files.get(k); } };
  const store = load('store', { '@react-native-async-storage/async-storage': storage, 'expo-file-system': disk });
  const session = { id: 'test', date: '2026-09-12', duration: 10, isPractice: false, quality: 'good', windows: [], windowCount: 0, recording: recordFixture() };
  await assert.rejects(store.saveSession(session), /quota/); fail = false;
  await store.saveSession(session); await store.saveSession(session);
  assert.equal((await store.getSessions()).length, 1);
  assert.equal((await store.getSession('test')).recording.streams.accelerometer.length, 100);
  values.set('gaitsteps:sessions', JSON.stringify([{ id: 'old', date: '2026-09-01', windows: [] }]));
  assert.equal((await store.getSessions()).length, 2);
  values.set('gaitsteps:index:v2', '{corrupt');
  await assert.rejects(store.getSessions());
});



test('Cancelling guidance prevents pending speech from starting later', async () => {
  let resolveSpeaking, spoken = [];
  const speech = { async getAvailableVoicesAsync() { return [{identifier:'test-en',language:'en-MY'}]; }, isSpeakingAsync: () => new Promise(resolve => { resolveSpeaking = resolve; }), async stop() {}, speak(text) { spoken.push(text); } };
  const audio = load('audio', { 'expo-speech': speech });
  const pending = audio.speak('Begin walking'); audio.stopSpeaking(); resolveSpeaking(false); await pending;
  assert.equal(spoken.length, 0);
});
test('Replacing speech waits for the previous utterance to stop', async () => {
  const order = [];
  const speech = { async getAvailableVoicesAsync() { return [{identifier:'test-en',language:'en-MY'}]; }, async isSpeakingAsync() { return true; }, async stop() { await Promise.resolve(); order.push('stopped'); }, speak(text) { order.push(text); } };
  await load('audio', { 'expo-speech': speech }).speak('Finish');
  assert.deepEqual(order, ['stopped', 'Finish']);
});
test('A failed voice test is reported to its screen, not silently accepted', async () => {
  let failed = false;
  const speech = { async getAvailableVoicesAsync() { return [{identifier:'test-en',language:'en-MY'}]; }, async isSpeakingAsync() { throw new Error('No speech engine'); } };
  const audio = load('audio', { 'expo-speech': speech }, { console: { warn() {} } });
  await audio.speak('Sound check', { onError() { failed = true; } });
  assert.equal(failed, true);
});

test('Readiness requires repeated finite events from every sensor and expires when stale', () => {
  const r = rig(); const recorder = new r.api.SensorRecorder({ guidanceEnabled: false, voiceEnabled: false }, () => {});
  recorder.connect(); assert.equal(recorder.allReceiving, false);
  for (const name of ['Accelerometer', 'Gyroscope', 'Magnetometer']) {
    r.emit(name, 10, { x: 1, y: 2, z: 3 });
    r.emit(name, 20, { x: 1, y: 2, z: 3 });
  }
  assert.equal(recorder.allReceiving, false);
  for (const name of ['Accelerometer', 'Gyroscope', 'Magnetometer']) r.emit(name, 30, { x: 1, y: 2, z: 3 });
  assert.equal(recorder.allReceiving, true);
  r.setTime(531); assert.equal(recorder.allReceiving, false);
  for (const name of ['Accelerometer', 'Gyroscope', 'Magnetometer']) r.emit(name, 540, { x: NaN, y: 2, z: 3 });
  assert.equal(recorder.allReceiving, false);
  recorder.disconnect();
});

const movement = load('movement');
test('A real continuous three-second settling gate resets on movement or stale streams', () => {
  const gate = new movement.SettlingGate();
  const good = { enough: true, upright: true, steady: true };
  assert.equal(gate.update(0, true, good), false);
  assert.equal(gate.update(1000, true, good), false);
  assert.equal(gate.update(2999, true, good), false);
  assert.equal(gate.update(3000, true, good), true);
  assert.equal(gate.update(3100, false, good), false);
  assert.equal(gate.update(3200, true, good), false);
  assert.equal(gate.update(6200, true, { ...good, steady: false }), false);
  assert.equal(gate.update(6300, true, { ...good, upright: false }), false);
});
test('Phone checks distinguish steady upright, sideways and strong-motion signals', () => {
  const gyro = Array.from({length: 100}, (_,i) => sample(i*10,0,0,0));
  const upright = Array.from({length: 100}, (_,i) => sample(i*10,0,1,0));
  assert.equal(movement.motionWindow(upright, gyro).steady, true);
  assert.equal(movement.motionWindow(upright, gyro).upright, true);
  const side = upright.map(s => ({...s, x:1, y:0}));
  assert.equal(movement.motionWindow(side, gyro).upright, false);
  const shaken = upright.map((s,i) => ({...s, x: i % 2 ? 1 : -1}));
  assert.equal(movement.motionWindow(shaken, gyro).strong, true);
  assert.equal(movement.motionWindow(shaken, gyro).steady, false);
});
test('Strong motion needs persistence and has a twelve-second cue cooldown', () => {
  const tracker = new movement.StrongMotionTracker();
  assert.equal(tracker.update(0,true),false);
  assert.equal(tracker.update(1000,true),false);
  assert.equal(tracker.update(1500,true),true);
  assert.equal(tracker.update(2000,true),false);
  assert.equal(tracker.update(13000,true),false);
  assert.equal(tracker.update(13500,true),true);
  assert.equal(tracker.update(14000,false),false);
});
test('A measured baseline is stored separately without subtracting it from walking values', () => {
  const r = rig(); const recorder = new r.api.SensorRecorder({ guidanceEnabled: true, voiceEnabled: true }, () => {});
  recorder.connect();
  for(let t=0;t<=4000;t+=10) {
    r.emit('Accelerometer',t,{x:0,y:1,z:0,timestamp:100+t/1000});
    r.emit('Gyroscope',t,{x:0.01,y:0.02,z:0.03,timestamp:100+t/1000});
    r.emit('Magnetometer',t,{x:20,y:30,z:40,timestamp:100+t/1000});
  }
  recorder.begin();
  r.emit('Accelerometer',4010,{x:0,y:1.2,z:0,timestamp:104.01});
  const result=recorder.stop('completed');
  assert.ok(result.baseline.streams.accelerometer.length>=299);
  assert.ok(Math.abs(result.baseline.mean.gyroscope.y-0.02)<1e-10);
  assert.equal(result.streams.accelerometer.length,1);
  assert.equal(result.streams.accelerometer[0].y,1.2);
  assert.equal(result.baseline.rawWalkingValuesCorrected,false);
});
test('Injected shaking triggers an actual recorder cue and preserves every raw sample', () => {
  const r=rig(); let warnings=0;
  const recorder=new r.api.SensorRecorder({guidanceEnabled:false,voiceEnabled:true},()=>{},()=>warnings++);
  recorder.connect(); recorder.begin();
  for(let t=0;t<4000;t+=10) {
    r.emit('Gyroscope',t,{x:0,y:0,z:0,timestamp:100+t/1000});
    r.emit('Accelerometer',t,{x:t%20 ? 1 : -1,y:1,z:0,timestamp:100+t/1000});
    r.emit('Magnetometer',t,{x:20,y:30,z:40,timestamp:100+t/1000});
  }
  const result=recorder.stop('completed');
  assert.equal(warnings,1);
  assert.equal(result.guidanceEvents.filter(e=>e.type==='possible-handling').length,1);
  assert.equal(result.streams.accelerometer.length,400);
});
function longFixture(fn) {
  const r=recordFixture(); r.elapsedSeconds=10;
  r.streams.accelerometer=Array.from({length:1000},(_,i)=>sample(i*10,0,fn(i/100),0));
  r.streams.gyroscope=Array.from({length:1000},(_,i)=>sample(i*10,0,0,0));
  return r;
}
test('Stationary summary does not invent rhythm, steps or a clinical gait score', () => {
  const result=movement.describeMovement(longFixture(()=>1));
  assert.equal(result.quietSeconds,10); assert.equal(result.repeatingMotion,false);
  assert.equal(result.gaitAssessmentScore,null); assert.equal(result.trend,'unavailable');
});
test('Repeating phone motion is described as rhythm without claiming gait', () => {
  const result=movement.describeMovement(longFixture(t=>1+0.1*Math.sin(2*Math.PI*2*t)));
  assert.equal(result.repeatingMotion,true); assert.equal(result.gaitAssessmentScore,null);
  assert.match(result.limitations,/Shaking can mimic rhythm/);
});
test('Summary distinguishes stronger late motion and withholds rhythm across gaps', () => {
  const r=longFixture(t=>1+(t<5?0.05:0.2)*Math.sin(2*Math.PI*2*t));
  assert.equal(movement.describeMovement(r).trend,'more');
  r.streams.accelerometer=r.streams.accelerometer.filter(s=>s.elapsedMs<4000 || s.elapsedMs>6000);
  assert.equal(movement.describeMovement(r).repeatingMotion,null);
});

test('Large smooth paired movement is not automatically called phone handling', () => {
  const acc=Array.from({length:100},(_,i)=>sample(i*10,0,1+0.7*Math.sin(2*Math.PI*i/100),0));
  const gyro=Array.from({length:100},(_,i)=>sample(i*10,0,0.2*Math.sin(2*Math.PI*i/100),0));
  const result=movement.motionWindow(acc,gyro);
  assert.equal(result.strong,true);
  assert.equal(result.context,'movement');
});
test('Acceleration-only strong shaking and excessive rotation remain uncertain handling flags', () => {
  const acc=Array.from({length:100},(_,i)=>sample(i*10,0,1+0.7*Math.sin(2*Math.PI*i/100),0));
  const stillGyro=Array.from({length:100},(_,i)=>sample(i*10,0,0,0));
  assert.equal(movement.motionWindow(acc,stillGyro).context,'possible-handling');
  const stillAcc=Array.from({length:100},(_,i)=>sample(i*10,0,1,0));
  const spin=Array.from({length:100},(_,i)=>sample(i*10,0,3,0));
  assert.equal(movement.motionWindow(stillAcc,spin).context,'possible-handling');
});
test('Quiet rest and sparse data are different; neither requires a handling cue', () => {
  const a=Array.from({length:100},(_,i)=>sample(i*10,0,1,0));
  const g=Array.from({length:100},(_,i)=>sample(i*10,0,0,0));
  assert.equal(movement.motionWindow(a,g).context,'rest-or-quiet');
  assert.equal(movement.motionWindow(a,[]).context,'missing-data');
});
test('Walk-rest-walk keeps all data and does not treat the rest as deterioration', () => {
  const r=longFixture(t=>t>=3 && t<6 ? 1 : 1+0.1*Math.sin(2*Math.PI*2*t));
  r.streams.gyroscope=Array.from({length:1000},(_,i)=>sample(i*10,0,i>=300&&i<600?0:0.1*Math.sin(2*Math.PI*2*i/100),0));
  const result=movement.describeMovement(r);
  assert.equal(result.quietSeconds,3);
  assert.equal(result.movementSeconds,7);
  assert.equal(result.trend,'similar');
  assert.equal(result.repeatingMotion,null);
  assert.ok(result.segments.some(s=>s.context==='rest-or-quiet' && s.startSeconds===3 && s.endSeconds===6));
  assert.equal(r.streams.accelerometer.length,1000);
});
test('Rest for the remainder of a recording is accepted without a false downward trend', () => {
  const r=longFixture(t=>t<5 ? 1+0.1*Math.sin(2*Math.PI*2*t) : 1);
  const summary=movement.describeMovement(r);
  assert.equal(summary.quietSeconds,5);
  assert.equal(summary.trend,'unavailable');
  assert.equal(pure.recordingIssues({...r,streams:{...r.streams,magnetometer:Array.from({length:500},(_,i)=>sample(i*20))}}).length,0);
});
test('A live walk-rest-walk sequence produces no rest or handling warning', () => {
  const r=rig(); let handling=0, direction=0;
  const recorder=new r.api.SensorRecorder({guidanceEnabled:true,voiceEnabled:true},()=>direction++,()=>handling++);
  recorder.connect(); recorder.begin();
  for(let t=0;t<10000;t+=10) {
    const rest=t>=3000 && t<6000;
    r.emit('Gyroscope',t,{x:0,y:rest?0:0.1*Math.sin(2*Math.PI*2*t/1000),z:0,timestamp:100+t/1000});
    r.emit('Accelerometer',t,{x:0,y:rest?1:1+0.1*Math.sin(2*Math.PI*2*t/1000),z:0,timestamp:100+t/1000});
    r.emit('Magnetometer',t,{x:20,y:30,z:40,timestamp:100+t/1000});
  }
  const result=recorder.stop('completed');
  assert.equal(handling,0); assert.equal(direction,0);
  assert.equal(result.streams.accelerometer.length,1000);
  assert.equal(result.stopReason,'completed');
});

const placement = load('placement');
test('Fit check requires movement then continuous settling; rest alone never verifies fit', () => {
  const fit = new placement.FitCheck();
  const quiet = { enough: true, upright: true, steady: true, context: 'rest-or-quiet' };
  for (let t = 0; t <= 5000; t += 100) assert.equal(fit.update(t, true, quiet), 'waiting');
  for (let t = 5100; t <= 6600; t += 100) fit.update(t, true, { ...quiet, steady: false, context: 'movement' });
  assert.equal(fit.update(6700, true, quiet), 'waiting');
  assert.equal(fit.update(9600, true, quiet), 'waiting');
  assert.equal(fit.update(9700, true, quiet), 'settled');
});
test('Fit check resets on missing data and flags sustained possible handling without a tightness claim', () => {
  const fit = new placement.FitCheck();
  const motion = { enough: true, upright: true, steady: false, context: 'movement' };
  fit.update(0, true, motion); fit.update(1100, true, motion);
  fit.update(1200, false, motion);
  const quiet = { ...motion, steady: true, context: 'rest-or-quiet' };
  fit.update(1300, true, quiet);
  assert.equal(fit.update(5000, true, quiet), 'waiting');
  assert.equal(fit.update(5100, true, { ...motion, context: 'possible-handling' }), 'waiting');
  assert.equal(fit.update(6600, true, { ...motion, context: 'possible-handling' }), 'review');
});
test('10 Hz high-pass descriptor separates test frequencies and rejects missing or slow native timing', () => {
  const sine = hz => Array.from({length: 300}, (_, i) => sample(i * 10, Math.sin(2 * Math.PI * hz * i / 100), 1, 0));
  assert.ok(placement.highFrequencyRms(sine(20)) > placement.highFrequencyRms(sine(2)) * 3);
  assert.equal(placement.highFrequencyRms(sine(2).map(s => ({ ...s, sensorTimestampSeconds: null }))), null);
  assert.equal(placement.highFrequencyRms(sine(2).map((s, i) => ({ ...s, sensorTimestampSeconds: i * 0.05 }))), null);
});
test('Placement shift needs sustained change, ignores yaw about gravity, and emits once', () => {
  const monitor = new placement.ShiftMonitor({ x: 0, y: 1, z: 0 });
  const window = (t, deg) => Array.from({length: 200}, (_, i) => sample(t - 1990 + i * 10, Math.sin(deg * Math.PI / 180), Math.cos(deg * Math.PI / 180), 0));
  assert.equal(monitor.update(2000, window(2000, 0)), null);
  assert.equal(monitor.update(3000, window(3000, 20)), null);
  assert.equal(monitor.update(4000, window(4000, 0)), null);
  assert.equal(monitor.update(5000, window(5000, 20)), null);
  assert.equal(monitor.update(6900, window(6900, 20)), null);
  assert.ok(monitor.update(7000, window(7000, 20)) > 15);
  assert.equal(monitor.update(10000, window(10000, 20)), null);
});
test('Fit raw streams remain separate and sustained placement shifts reach recording review notes', () => {
  const h = rig(); const recorder = new h.api.SensorRecorder({ guidanceEnabled: false, voiceEnabled: false }, () => {});
  recorder.connect(); recorder.startFit();
  for (let t = 0; t < 4000; t += 10) for (const name of ['Accelerometer', 'Gyroscope', 'Magnetometer']) h.emit(name, t, { x: 0, y: name === 'Accelerometer' ? 1 : 0, z: 0, timestamp: t / 1000 });
  recorder.finishFit(); h.setTime(4000); recorder.begin();
  for (let t = 4000; t < 10000; t += 10) for (const name of ['Accelerometer', 'Gyroscope', 'Magnetometer']) h.emit(name, t, { x: name === 'Accelerometer' ? 0.5 : 0, y: name === 'Accelerometer' ? Math.sqrt(0.75) : 0, z: 0, timestamp: t / 1000 });
  const r = recorder.stop('completed');
  assert.equal(r.fitCheck.streams.accelerometer.length, 400);
  assert.equal(r.streams.accelerometer.length, 600);
  assert.equal(r.fitCheck.tightnessVerified, false);
  assert.equal(r.guidanceEvents.filter(e => e.type === 'possible-placement-shift').length, 1);
  assert.ok(pure.recordingIssues(r).some(s => s.includes('placement or posture')));
  assert.equal(load('movement').describeMovement(r).trend, 'unavailable');
  assert.equal(load('movement').describeMovement(r).repeatingMotion, null);
  const csv = exporting.exportCSV({ id: 'shifted', recording: r, duration: 6, windows: [] });
  assert.match(csv, /placement_review_required/);
  assert.match(csv.split('\r\n')[1], /"true","android","expo-sensors"/);
});


test('Research exports carry reproducible signal features and explicitly unavailable gait measures', () => {
 const session={id:'features',recording:recordFixture(),windows:[]};
 const parsed=JSON.parse(exporting.exportJSON(session));
 assert.equal(parsed.exportSchemaVersion,3);
 const f=parsed.researchFeatures;
 assert.equal(f.version,'phone-research-features-v2');
 assert.ok(Math.abs(f.features.accelerometer_magnitude_mean.value-Math.sqrt(14))<1e-12);
 assert.ok(Math.abs(f.features.accelerometer_vector_rms.value-Math.sqrt(14))<1e-12);
 assert.ok(f.features.accelerometer_magnitude_sd.value<1e-12);
 assert.equal(f.features.cadence.value,null);
 assert.equal(f.features.walking_speed.status,'unavailable');
 assert.equal(f.comparisonEligibility,'not-established');
 assert.equal(f.anatomicalPlacementVerified,false);
 assert.deepEqual(parsed.session.recording.streams,JSON.parse(JSON.stringify(session.recording.streams)));
 const csv=exporting.exportFeatureCSV(session);
 assert.equal(csv.trim().split('\r\n').length,20);
 assert.match(csv, /"cadence","","steps\/min","unavailable"/);
 assert.doesNotMatch(csv, /z_score|normality_score|stroke_probability/);
});
test('Missing sensor features and legacy simulation never become zero measurements', () => {
 const r=recordFixture();r.streams.gyroscope=[];
 const f=JSON.parse(exporting.exportJSON({id:'missing',recording:r,windows:[]})).researchFeatures;
 assert.equal(f.features.gyroscope_vector_rms.value,null);
 assert.equal(f.features.gyroscope_vector_rms.status,'unavailable');
 assert.ok(f.captureNotes.includes('No gyroscope readings received.'));
 assert.equal(JSON.parse(exporting.exportJSON({id:'old',windows:[]})).researchFeatures,null);
 assert.match(exporting.exportFeatureCSV({id:'old',windows:[]}),/legacy-simulation/);
});


const timingApi=load('gaitTiming');
function timingFixture({hz=2, rate=100, seconds=12, rest=false, handling=false, batched=false}={}) {
 const r=recordFixture();r.elapsedSeconds=seconds;
 const rows=Array.from({length:Math.floor(seconds*rate)+1},(_,i)=>{
  const t=i/rate, paused=rest && t>=4 && t<7;
  return {...sample(t*1000,0,paused?1:1+.15*Math.sin(2*Math.PI*hz*t),0),elapsedMs:batched?Math.ceil(t)*1000:t*1000};
 });
 r.streams.accelerometer=rows;
 r.streams.gyroscope=rows.map(s=>({...s,x:handling?3:.06,y:0,z:0}));
 return r;
}
test('Experimental native-timed step peaks reproduce supported synthetic intervals across rates',()=>{
 for(const hz of [1,1.5,2,2.5]) for(const rate of [50,81.7,100]) {
  const out=timingApi.estimateGaitTiming(timingFixture({hz,rate}));
  assert.equal(out.status,'experimental-estimate',`hz=${hz}, rate=${rate}`);
  assert.ok(Math.abs(out.features.cadence.value-60*hz)<2);
  assert.ok(Math.abs(out.features.step_time_mean.value-1/hz)<.02);
  assert.equal(out.features.step_count.value,out.bouts.reduce((n,b)=>n+b.eventTimesSeconds.length,0));
  assert.equal(out.clinicalValidation,false);
 }
});
test('Timing ignores batched JS arrival intervals when native timestamps are intact',()=>{
 const a=timingApi.estimateGaitTiming(timingFixture());
 const b=timingApi.estimateGaitTiming(timingFixture({batched:true}));
 assert.deepEqual(a.bouts,b.bouts);
});
test('Pause periods split timing bouts instead of inflating step time',()=>{
 const out=timingApi.estimateGaitTiming(timingFixture({rest:true}));
 assert.equal(out.bouts.length,2);
 assert.ok(out.bouts.flatMap(b=>b.intervalsSeconds).every(x=>x<.6));
 assert.ok(out.features.candidate_bout_duration.value<9);
 assert.ok(Math.abs(out.features.cadence.value-120)<2);
});
test('Stillness, strong handling, placement shift and invalid native clocks withhold timing',()=>{
 for(const mode of ['still','handling','shift','clock','nonfinite']) {
  const r=timingFixture({handling:mode==='handling'});
  if(mode==='still')r.streams.accelerometer.forEach(s=>s.y=1);
  if(mode==='shift')r.guidanceEvents.push({type:'possible-placement-shift',elapsedMs:5000});
  if(mode==='clock')r.streams.accelerometer[3].sensorTimestampSeconds=null;
  if(mode==='nonfinite')r.streams.accelerometer[3].y=NaN;
  const out=timingApi.estimateGaitTiming(r);
  assert.equal(out.features.cadence.value,null,mode);
  assert.equal(out.features.step_count.value,null,mode);
 }
});
test('A native gap is never bridged into a step interval',()=>{
 const r=timingFixture();r.streams.accelerometer=r.streams.accelerometer.filter(s=>s.elapsedMs<4000||s.elapsedMs>=7000);
 const out=timingApi.estimateGaitTiming(r);
 assert.ok(out.bouts.length>=2);
 assert.ok(out.excluded.some(e=>e.reason.includes('gap')));
 assert.ok(out.bouts.flatMap(b=>b.intervalsSeconds).every(x=>x<.6));
});
test('Feature exports retain experimental event provenance and never invent stride side or speed',()=>{
 const out=JSON.parse(exporting.exportJSON({id:'timing',recording:timingFixture(),windows:[]}));
 assert.equal(out.researchFeatures.features.cadence.status,'experimental-estimate');
 assert.ok(out.researchFeatures.gaitTiming.bouts[0].eventTimesSeconds.length>0);
 for(const key of ['stride_time_cv','stride_time_asymmetry','walking_speed','walking_duration'])assert.equal(out.researchFeatures.features[key].value,null);
 assert.equal(out.researchFeatures.comparisonEligibility,'not-established');
});


test('Browser review accepts bounded device exports without altering sensor samples',()=>{
 const session={id:'review',date:'2026-09-17T00:00:00Z',isPractice:true,duration:10,windows:[],recording:{...recordFixture(),source:'device'}};
 const parsed=load('reviewRecording').parseReviewRecording(exporting.exportJSON(session));
 assert.deepEqual(JSON.parse(JSON.stringify(parsed)),JSON.parse(JSON.stringify(session)));
});
test('Browser review rejects simulation, missing streams, invalid numeric samples and unbounded duration',()=>{
 const api=load('reviewRecording');
 const make=()=>({exportSchemaVersion:3,source:'device',session:{id:'review',date:'2026-09-17T00:00:00Z',isPractice:true,duration:10,windows:[],recording:{...recordFixture(),source:'device'}}});
 for(const mutate of [p=>p.source='legacy-simulation',p=>delete p.session.recording.streams.gyroscope,p=>p.session.recording.streams.accelerometer[0].x='bad',p=>p.session.recording.elapsedSeconds=100000,p=>p.session.windows=[null]]) {
  const input=make();mutate(input);assert.throws(()=>api.parseReviewRecording(JSON.stringify(input)),/valid Gait Steps/);
 }
 assert.throws(()=>api.parseReviewRecording('not JSON'));
});
test('Browser imported recordings are review-only and cannot start native persistence',async()=>{
 const store=load('store.web');
 const session={id:'review',date:'2026-09-17T00:00:00Z',isPractice:true,duration:10,windows:[],recording:{...recordFixture(),source:'device'}};
 assert.equal((await store.getSessions()).length,0);
 assert.equal(store.importReviewRecording(exporting.exportJSON(session)),'review');
 assert.equal((await store.getSessions()).length,1);
 assert.equal((await store.getSession('review')).id,'review');
 await assert.rejects(store.saveSession(session),/Only browser sensor recordings/);
});
