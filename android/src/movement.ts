import type { Sample, Recording } from './recording';
export interface MotionWindow {
  enough: boolean; upright: boolean; steady: boolean; strong: boolean;
  accelerationRmsG: number; rotationRms: number;
  context: 'rest-or-quiet' | 'movement' | 'possible-handling' | 'uncertain' | 'missing-data';
  accelerationChangeRms: number;
}
export function motionWindow(accel: Sample[], gyro: Sample[], landscape = false): MotionWindow {
  const span = (a: Sample[]) => a.length > 1 ? a[a.length - 1].elapsedMs - a[0].elapsedMs : 0;
  const continuous = (a: Sample[]) => a.every((s, i) => i === 0 || (s.elapsedMs > a[i - 1].elapsedMs && s.elapsedMs - a[i - 1].elapsedMs <= 250));
  const enough = accel.length >= 10 && gyro.length >= 10 && span(accel) >= 700 && span(gyro) >= 700 && continuous(accel) && continuous(gyro);
  const mean = { x: 0, y: 0, z: 0 };
  for (const s of accel) for (const a of ['x', 'y', 'z'] as const) mean[a] += s[a] / accel.length;
  const g = Math.hypot(mean.x, mean.y, mean.z);
  const accelerationRmsG = Math.sqrt(accel.reduce((v, s) => v + (s.x - mean.x) ** 2 + (s.y - mean.y) ** 2 + (s.z - mean.z) ** 2, 0) / Math.max(accel.length, 1));
  const rotationRms = Math.sqrt(gyro.reduce((v, s) => v + s.x ** 2 + s.y ** 2 + s.z ** 2, 0) / Math.max(gyro.length, 1));
  // Time-weighted change rate avoids equating a large, smooth movement with shaking.
  let changeEnergy = 0, changeTime = 0;
  for (let i = 1; i < accel.length; i++) {
    const nativeNow = accel[i].sensorTimestampSeconds, nativeBefore = accel[i - 1].sensorTimestampSeconds;
    const dt = nativeNow !== null && nativeBefore !== null && nativeNow > nativeBefore ? nativeNow - nativeBefore : (accel[i].elapsedMs - accel[i - 1].elapsedMs) / 1000;
    if (dt <= 0 || dt > 0.25) continue;
    changeEnergy += ((accel[i].x - accel[i - 1].x) ** 2 + (accel[i].y - accel[i - 1].y) ** 2 + (accel[i].z - accel[i - 1].z) ** 2) / dt;
    changeTime += dt;
  }
  const accelerationChangeRms = Math.sqrt(changeEnergy / Math.max(changeTime, 0.001));
  const strong = enough && (accelerationRmsG > 0.45 || rotationRms > 2.5);
  const quiet = accelerationRmsG < 0.025 && rotationRms < 0.08;
  // Provisional broad phone-motion bounds, NOT a validated patient gait range.
  // Translation cannot be established from these signals. Uncertainty is retained.
  const possibleHandling = strong && (rotationRms > 2.5 || accelerationChangeRms > 15 || rotationRms < 0.02);
  const pairedMovement = accelerationRmsG >= 0.025 && accelerationRmsG <= 0.8 && rotationRms >= 0.02 && rotationRms <= 2.5;
  const context: MotionWindow['context'] = !enough ? 'missing-data' : quiet ? 'rest-or-quiet' : possibleHandling ? 'possible-handling' : pairedMovement ? 'movement' : 'uncertain';
  const magnitudes = accel.map(s => Math.hypot(s.x, s.y, s.z));
  const magnitudeMean = magnitudes.reduce((sum, v) => sum + v, 0) / Math.max(1, magnitudes.length);
  const magnitudeSd = Math.sqrt(magnitudes.reduce((sum, v) => sum + (v - magnitudeMean) ** 2, 0) / Math.max(1, magnitudes.length));
  // Legacy summaries retain portrait semantics. New belt setup accepts either landscape end up.
  const upright = g > 0.8 && g < 1.2 && (landscape ? Math.abs(mean.x) : mean.y) / g >= Math.cos(20 * Math.PI / 180);
  return { enough, upright, steady: enough && magnitudeSd < 0.05 && accelerationRmsG < 0.06 && rotationRms < 0.15,
    strong, accelerationRmsG, rotationRms, accelerationChangeRms, context };
}
/** Conditions must hold continuously; this gate does not identify anatomical placement. */
export class SettlingGate {
  private since: number | null = null;
  update(now: number, streamsReady: boolean, motion: MotionWindow) {
    const suitable = streamsReady && motion.enough && motion.upright && motion.steady;
    if (!suitable) this.since = null;
    else if (this.since === null) this.since = now;
    return this.since !== null && now - this.since >= 3000;
  }
}
export class StrongMotionTracker {
  private since: number | null = null;
  private lastCue = -Infinity;
  update(t: number, strong: boolean) {
    if (!strong) { this.since = null; return false; }
    if (this.since === null) this.since = t;
    if (t - this.since < 1500 || t - this.lastCue < 12000) return false;
    this.lastCue = t; return true;
  }
}
export interface MovementSummary {
  version: 'movement-description-v2';
  usableSeconds: number; quietSeconds: number; strongMotionSeconds: number;
  movementSeconds: number; possibleHandlingSeconds: number; uncertainSeconds: number;
  segments: { startSeconds: number; endSeconds: number; context: MotionWindow['context'] }[];
  trend: 'more' | 'less' | 'similar' | 'unavailable';
  repeatingMotion: boolean | null;
  gaitAssessmentScore: null;
  limitations: string;
}
export function describeMovement(r: Recording): MovementSummary {
  const blocks: { time: number; motion: MotionWindow }[] = [];
  const acc = r.streams.accelerometer, gyro = r.streams.gyroscope;
  for (let t = 0; t + 1 <= r.elapsedSeconds + 0.01; t++) {
    const a = acc.filter(s => s.elapsedMs >= t * 1000 && s.elapsedMs < (t + 1) * 1000);
    const g = gyro.filter(s => s.elapsedMs >= t * 1000 && s.elapsedMs < (t + 1) * 1000);
    const m = motionWindow(a, g);
    if (m.enough) blocks.push({ time: t, motion: m });
  }
  let trend: MovementSummary['trend'] = 'unavailable';
  const active = blocks.filter(b => b.motion.context !== 'rest-or-quiet' && b.motion.context !== 'possible-handling');
  if (active.length >= 6 && blocks.length >= Math.floor(r.elapsedSeconds) * 0.8) {
    const midpoint = r.elapsedSeconds / 2;
    const first = active.filter(b => b.time < midpoint), last = active.filter(b => b.time >= midpoint);
    const average = (b: typeof blocks) => b.reduce((sum, x) => sum + x.motion.accelerationRmsG, 0) / Math.max(1, b.length);
    const early = average(first), late = average(last);
    if (first.length >= 2 && last.length >= 2) trend = early < 0.025 && late < 0.025 ? 'similar' : late > early * 1.25 ? 'more' : late < early * 0.8 ? 'less' : 'similar';
  }
  // Only describe periodicity for sufficient, closely spaced samples. It is NOT cadence or verified gait.
  let repeatingMotion: boolean | null = null;
  if (acc.length >= 100 && r.elapsedSeconds >= 6) {
    const start = acc[0].elapsedMs, end = acc[acc.length - 1].elapsedMs;
    let gap = 0; for (let i = 1; i < acc.length; i++) gap = Math.max(gap, acc[i].elapsedMs - acc[i - 1].elapsedMs);
    if (gap <= 100 && end - start >= r.elapsedSeconds * 800) {
      const values: number[] = []; let j = 0;
      for (let t = start; t <= end; t += 40) {
        while (j + 1 < acc.length && acc[j + 1].elapsedMs < t) j++;
        const a = acc[j], b = acc[Math.min(j + 1, acc.length - 1)];
        const w = b.elapsedMs > a.elapsedMs ? (t - a.elapsedMs) / (b.elapsedMs - a.elapsedMs) : 0;
        values.push(Math.hypot(a.x + w * (b.x - a.x), a.y + w * (b.y - a.y), a.z + w * (b.z - a.z)));
      }
      const mean = values.reduce((s, x) => s + x, 0) / values.length;
      const centered = values.map(x => x - mean);
      const variance = centered.reduce((s, x) => s + x * x, 0) / centered.length;
      repeatingMotion = false;
      if (variance > 0.0004) for (let lag = 9; lag <= 50; lag++) {
        let cross = 0, a2 = 0, b2 = 0;
        for (let i = lag; i < centered.length; i++) { cross += centered[i] * centered[i - lag]; a2 += centered[i] ** 2; b2 += centered[i - lag] ** 2; }
        if (cross / Math.sqrt(a2 * b2 || 1) > 0.6) { repeatingMotion = true; break; }
      }
    }
  }
  const quietSeconds = blocks.filter(b => b.motion.context === 'rest-or-quiet').length;
  const possibleHandlingSeconds = blocks.filter(b => b.motion.context === 'possible-handling').length;
  // Do not interpret pauses as a loss of gait rhythm, or handling as walking rhythm.
  if ((quietSeconds > 0 && quietSeconds < blocks.length) || possibleHandlingSeconds > 0) repeatingMotion = null;
  if (r.guidanceEvents.some(e => e.type === 'possible-placement-shift')) { trend = 'unavailable'; repeatingMotion = null; }
  const segments: MovementSummary['segments'] = [];
  for (let t = 0; t < Math.floor(r.elapsedSeconds); t++) {
    const context = blocks.find(b => b.time === t)?.motion.context ?? 'missing-data';
    const last = segments[segments.length - 1];
    if (last && last.context === context) last.endSeconds = t + 1;
    else segments.push({ startSeconds: t, endSeconds: t + 1, context });
  }
  return { version: 'movement-description-v2', usableSeconds: blocks.length,
    quietSeconds, possibleHandlingSeconds,
    movementSeconds: blocks.filter(b => b.motion.context === 'movement').length,
    uncertainSeconds: blocks.filter(b => b.motion.context === 'uncertain').length,
    segments,
    strongMotionSeconds: blocks.filter(b => b.motion.strong).length, trend, repeatingMotion, gaitAssessmentScore: null,
    limitations: 'Describes phone motion only. Shaking can mimic rhythm. Placement and walking are not verified. No diagnosis, normal/abnormal category, recovery judgement or G.A.I.T. score.' };
}
