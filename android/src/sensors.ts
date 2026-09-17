import { Accelerometer, Gyroscope, Magnetometer } from 'expo-sensors';
import { Platform } from 'react-native';
import { DirectionTracker, emptyStreams, REQUESTED_HZ, SENSOR_NAMES, SENSOR_UNITS, validAxes } from './recording';
import type { Recording, Sample, SensorName } from './recording';
import { motionWindow, StrongMotionTracker } from './movement';
import { highFrequencyRms, ShiftMonitor } from './placement';
const hardware = { accelerometer: Accelerometer, gyroscope: Gyroscope, magnetometer: Magnetometer };
export async function checkSensors(): Promise<void> {
  if (Platform.OS === 'web') throw new Error('Open the Android app to record all three motion sensors. Browser preview cannot collect this recording.');
  for (const name of SENSOR_NAMES) {
    const permission = await hardware[name].requestPermissionsAsync();
    if (!permission.granted) throw new Error(`Allow motion access in phone settings to use the ${name}.`);
    if (!await hardware[name].isAvailableAsync()) throw new Error(`This phone has no available ${name}. All three sensors are required for this study recording.`);
  }
}
export class SensorRecorder {
  private subscriptions: { remove(): void }[] = [];
  private streams = emptyStreams();
  private direction = new DirectionTracker();
  private startTime: number | null = null;
  private startedAt = '';
  private gravity = { x: 0, y: 0, z: 0 };
  private accelAt = -Infinity;
  private received: Partial<Record<SensorName, { count: number; last: number }>> = {};
  private events: Recording['guidanceEvents'] = [];
  private lastGyroAt = -Infinity;
  private stopped: Recording | null = null;
  private recent = emptyStreams();
  private strongMotion = new StrongMotionTracker();
  private lastMotionCheck = -Infinity;
  private baseline: Recording['baseline'];
  private fitStarted: number | null = null;
  private fitStreams = emptyStreams();
  private fitCheck: Recording['fitCheck'];
  get savedFitCheck() { return this.fitCheck; }
  restoreFitCheck(value: Recording['fitCheck']) { this.fitCheck = value; }
  private shift: ShiftMonitor | null = null;
  startFit() { this.fitStarted = performance.now(); this.fitStreams = emptyStreams(); }
  finishFit() {
    this.fitCheck = { version: 'guided-fit-v2', status: 'movement-then-settled', proximity: 'unavailable', tightnessVerified: false, stepsCounted: false, highPass10HzRmsG: highFrequencyRms(this.fitStreams.accelerometer), streams: this.fitStreams };
    this.fitStarted = null;
  }
  constructor(private options: { guidanceEnabled: boolean; voiceEnabled: boolean }, private cue: (angle: number) => void, private motionCue: () => void = () => {}) {}
  connect() {
    try {
      for (const name of SENSOR_NAMES) {
        hardware[name].setUpdateInterval(1000 / REQUESTED_HZ[name]);
        this.subscriptions.push(hardware[name].addListener(m => this.receive(name, m)));
      }
    } catch (e) { this.disconnect(); throw e; }
  }
  private receive(name: SensorName, m: { x: number; y: number; z: number; timestamp?: number }) {
    if (!validAxes(m)) return;
    const now = performance.now();
    const recentSample: Sample = { x: m.x, y: m.y, z: m.z, elapsedMs: now, receivedAtUnixMs: Date.now(), sensorTimestampSeconds: Number.isFinite(m.timestamp) ? m.timestamp! : null };
    this.recent[name].push(recentSample);
    if (this.fitStarted !== null) this.fitStreams[name].push({ ...recentSample, elapsedMs: now - this.fitStarted });
    this.recent[name] = this.recent[name].filter(s => now - s.elapsedMs <= 4000);
    this.received[name] = { count: (this.received[name]?.count ?? 0) + 1, last: now };
    if (name === 'accelerometer') {
      this.accelAt = now;
      for (const a of ['x', 'y', 'z'] as const) this.gravity[a] = this.gravity[a] * 0.92 + m[a] * 0.08;
    }
    const g = Math.hypot(this.gravity.x, this.gravity.y, this.gravity.z);
    const upright = now - this.accelAt < 250 && g > 0.85 && g < 1.15 && this.gravity.y / g > 0.9;
    if (this.startTime === null) {
      if (name === 'gyroscope') this.direction.calibrate(m.y, now, upright && Math.hypot(m.x, m.y, m.z) < 0.15);
      return;
    }
    const sample: Sample = { x: m.x, y: m.y, z: m.z, elapsedMs: now - this.startTime, receivedAtUnixMs: Date.now(), sensorTimestampSeconds: Number.isFinite(m.timestamp) ? m.timestamp! : null };
    this.streams[name].push(sample);
    if (name === 'accelerometer' && now - this.lastMotionCheck >= 100) {
      this.lastMotionCheck = now;
      const shiftAngle = this.shift?.update(now, this.recent.accelerometer.filter(s => now - s.elapsedMs <= 2000));
      if (shiftAngle != null) this.events.push({ elapsedMs: sample.elapsedMs, type: 'possible-placement-shift', angleDegrees: shiftAngle });
      if (this.strongMotion.update(now, this.motionStatus.context === 'possible-handling')) {
        this.events.push({ elapsedMs: sample.elapsedMs, type: 'possible-handling' });
        this.motionCue();
      }
    }
    if (name === 'gyroscope') {
      this.lastGyroAt = now;
      const angle = this.direction.update(m.y, now, upright);
      if (this.options.guidanceEnabled && angle !== null && this.motionStatus.context === 'movement') {
        this.events.push({ elapsedMs: sample.elapsedMs, type: 'possible-turn', angleDegrees: angle });
        this.cue(angle);
      }
    }
  }
  get readiness(): Record<SensorName, boolean> {
    const now = performance.now();
    return Object.fromEntries(SENSOR_NAMES.map(n => {
      const stream = this.received[n];
      return [n, !!stream && stream.count >= 3 && now - stream.last <= 500];
    })) as Record<SensorName, boolean>;
  }
  get allReceiving() { return SENSOR_NAMES.every(n => this.readiness[n]); }
  get guidanceReady() { return this.direction.ready && performance.now() - this.lastGyroAt < 250; }
  get motionStatus() {
    const now = performance.now();
    return motionWindow(this.recent.accelerometer.filter(s => now - s.elapsedMs <= 1000), this.recent.gyroscope.filter(s => now - s.elapsedMs <= 1000));
  }
  get baselineReady() {
    const now = performance.now();
    return SENSOR_NAMES.every(n => {
      const samples = this.recent[n].filter(s => now - s.elapsedMs <= 3000);
      return samples.length >= 3 && samples[samples.length - 1].elapsedMs - samples[0].elapsedMs >= 2500;
    });
  }
  begin() {
    const now = performance.now();
    const baselineStreams = emptyStreams();
    const mean = {} as NonNullable<Recording['baseline']>['mean'];
    for (const name of SENSOR_NAMES) {
      baselineStreams[name] = this.recent[name].filter(s => now - s.elapsedMs <= 3000).map(s => ({ ...s, elapsedMs: s.elapsedMs - (now - 3000) }));
      const samples = baselineStreams[name];
      mean[name] = { x: 0, y: 0, z: 0 };
      for (const sample of samples) for (const axis of ['x', 'y', 'z'] as const) mean[name][axis] += sample[axis] / samples.length;
    }
    // Baselines are optional for older/programmatic recordings; never invent absent samples.
    if (SENSOR_NAMES.every(n => baselineStreams[n].length >= 3 && baselineStreams[n][baselineStreams[n].length - 1].elapsedMs - baselineStreams[n][0].elapsedMs >= 2500)) {
      this.baseline = { version: 'stationary-reference-v1', requestedSeconds: 3, startedAt: new Date(Date.now() - 3000).toISOString(), streams: baselineStreams, mean, rawWalkingValuesCorrected: false };
    }
    this.shift = this.baseline ? new ShiftMonitor(this.baseline.mean.accelerometer) : null;
    this.streams = emptyStreams(); this.direction.begin(); this.startTime = now; this.startedAt = new Date().toISOString();
  }
  stop(reason: Recording['stopReason']): Recording {
    if (this.stopped) return this.stopped;
    this.disconnect();
    this.stopped = {
      schemaVersion: 2, source: 'device', startedAt: this.startedAt, elapsedSeconds: this.startTime === null ? 0 : (performance.now() - this.startTime) / 1000,
      requestedHz: REQUESTED_HZ, units: SENSOR_UNITS, platform: Platform.OS, osVersion: String(Platform.Version),
      placement: 'lower-back-upright-screen-out', coordinateFrame: 'device', accelerationIncludesGravity: true,
      magnetometerCalibration: 'OS-calibrated; app accuracy unverified',
      timestampBasis: 'elapsedMs: monotonic JS receipt; receivedAtUnixMs: wall clock; sensorTimestampSeconds: native event',
      stopReason: reason, ...this.options, guidanceEvents: this.events, streams: this.streams,
      baseline: this.baseline, fitCheck: this.fitCheck,
      motionRulesVersion: 'motion-context-v2',
    };
    return this.stopped;
  }
  disconnect() { this.subscriptions.forEach(s => s.remove()); this.subscriptions = []; }
}
