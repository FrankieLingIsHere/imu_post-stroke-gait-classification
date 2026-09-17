/** Pure data contracts and diagnostics. No clinical or model-admission claims. */
export const SENSOR_NAMES = ['accelerometer', 'gyroscope', 'magnetometer'] as const;
export type SensorName = typeof SENSOR_NAMES[number];
export const SENSOR_UNITS: Record<SensorName, string> = { accelerometer: 'g', gyroscope: 'rad/s', magnetometer: 'uT' };
export const REQUESTED_HZ: Record<SensorName, number> = { accelerometer: 100, gyroscope: 100, magnetometer: 50 };
export interface Sample {
  x: number; y: number; z: number;
  elapsedMs: number; receivedAtUnixMs: number;
  /** Unmodified Expo native event time in seconds; not Unix time. Null if not supplied. */
  sensorTimestampSeconds: number | null;
}
export type Streams = Record<SensorName, Sample[]>;
export interface Recording {
  schemaVersion: 2; source: 'device'; startedAt: string; elapsedSeconds: number;
  requestedHz: Record<SensorName, number>; units: Record<SensorName, string>;
  platform: string; osVersion: string;
  placement: 'lower-back-upright-screen-out'; coordinateFrame: 'device';
  accelerationIncludesGravity: true;
  magnetometerCalibration: 'OS-calibrated; app accuracy unverified';
  timestampBasis: 'elapsedMs: monotonic JS receipt; receivedAtUnixMs: wall clock; sensorTimestampSeconds: native event';
  stopReason: 'completed' | 'user-stopped' | 'interrupted';
  guidanceEnabled: boolean; voiceEnabled: boolean;
  guidanceEvents: { elapsedMs: number; type: 'possible-turn' | 'strong-motion' | 'possible-handling' | 'possible-placement-shift'; angleDegrees?: number }[];
  motionRulesVersion?: 'motion-context-v2';
  setupCheck?: { version: 'steady-upright-v1' | 'guided-fit-v2'; anatomicalPlacementVerified: false; steadySeconds: number; retries?: number; language?: 'en' | 'ms' | 'zh' };
  fitCheck?: { version: 'guided-fit-v2'; status: 'movement-then-settled'; proximity: 'unavailable'; tightnessVerified: false; stepsCounted: false; highPass10HzRmsG: number | null; streams: Streams };
  baseline?: {
    version: 'stationary-reference-v1'; requestedSeconds: 3;
    startedAt: string; streams: Streams;
    mean: Record<SensorName, { x: number; y: number; z: number }>;
    rawWalkingValuesCorrected: false;
  };
  streams: Streams;
}
export function emptyStreams(): Streams { return { accelerometer: [], gyroscope: [], magnetometer: [] }; }
export function validAxes(s: { x: number; y: number; z: number }): boolean { return [s.x, s.y, s.z].every(Number.isFinite); }
export function streamStats(samples: Sample[], elapsedSeconds: number) {
  if (!samples.length) return { count: 0, hz: 0, spanSeconds: 0, maxGapMs: elapsedSeconds * 1000, timing: 'receipt' };
  const native = samples.every((s, i) => s.sensorTimestampSeconds !== null && (i === 0 || s.sensorTimestampSeconds! > samples[i - 1].sensorTimestampSeconds!));
  const times = samples.map(s => native ? s.sensorTimestampSeconds! * 1000 : s.elapsedMs);
  const span = (times[times.length - 1] - times[0]) / 1000;
  let gap = Math.max(samples[0].elapsedMs, elapsedSeconds * 1000 - samples[samples.length - 1].elapsedMs, 0);
  for (let i = 1; i < times.length; i++) gap = Math.max(gap, times[i] - times[i - 1]);
  return { count: samples.length, hz: span > 0 ? (samples.length - 1) / span : 0, spanSeconds: Math.max(0, span), maxGapMs: gap, timing: native ? 'native' : 'receipt' };
}
export function recordingIssues(r: Recording): string[] {
  const issues: string[] = [];
  if (r.guidanceEvents.some(e => e.type === 'possible-placement-shift')) issues.push('Sustained phone-angle change: placement or posture needs review.');
  if (r.stopReason !== 'completed') issues.push('Recording ended early.');
  for (const name of SENSOR_NAMES) {
    const stat = streamStats(r.streams[name], r.elapsedSeconds);
    if (!stat.count) issues.push(`No ${name} readings received.`);
    else {
      if (stat.maxGapMs > 250) issues.push(`${name}: a data gap exceeded 0.25 seconds.`);
      if (stat.hz < r.requestedHz[name] * 0.8) issues.push(`${name}: sampling was slower than requested.`);
      if (stat.timing !== 'native') issues.push(`${name}: native timing unavailable or non-monotonic.`);
    }
  }
  return issues;
}
/** Relative phone yaw only, with stationary calibration, upright gating and sparse cues. */
export class DirectionTracker {
  private calibration: { y: number; t: number }[] = [];
  private bias: number | null = null;
  private last: number | null = null;
  private angle = 0;
  private overSince: number | null = null;
  private lastCue = -Infinity;
  private upright = false;
  calibrate(y: number, t: number, upright: boolean) {
    if (!upright) { this.calibration = []; return; }
    this.calibration.push({ y, t });
    this.calibration = this.calibration.filter(s => t - s.t <= 2500);
  }
  begin() {
    const a = this.calibration;
    if (a.length < 30 || a[a.length - 1].t - a[0].t < 1800) return;
    const mean = a.reduce((v, s) => v + s.y, 0) / a.length;
    const sd = Math.sqrt(a.reduce((v, s) => v + (s.y - mean) ** 2, 0) / a.length);
    if (sd < 0.035 && Math.abs(mean) < 0.08) this.bias = mean;
  }
  update(y: number, t: number, upright: boolean): number | null {
    this.upright = upright;
    if (this.bias === null) return null;
    const dt = this.last === null ? 0 : (t - this.last) / 1000;
    this.last = t;
    if (!upright || dt > 0.25 || dt < 0) { this.bias = null; return null; }
    this.angle += (y - this.bias) * dt * 180 / Math.PI;
    if (Math.abs(this.angle) > 25) {
      if (this.overSince === null) this.overSince = t;
      if (t - this.overSince >= 2000 && t - this.lastCue >= 12000) { this.lastCue = t; return this.angle; }
    } else this.overSince = null;
    return null;
  }
  get ready() { return this.bias !== null && this.upright; }
}
