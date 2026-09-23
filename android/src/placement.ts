import type { Sample } from './recording';
import type { MotionWindow } from './movement';

/** Provisional magnitude pulses, not verified foot contacts. Never reuse pre-stage samples. */
export function candidateStepsSince(samples: Sample[], since: number): number {
  const fresh = samples.filter(s => s.elapsedMs >= since);
  let count = 0, lastPeak = -Infinity, valley = 1, peak = 1, rising = false;
  for (let i = 0; i < fresh.length; i++) {
    const s = fresh[i], value = Math.hypot(s.x, s.y, s.z);
    if (!Number.isFinite(value) || (i && (s.elapsedMs <= fresh[i - 1].elapsedMs || s.elapsedMs - fresh[i - 1].elapsedMs > 100))) {
      count = 0; rising = false; valley = peak = value; continue;
    }
    if (i === 0) { valley = peak = value; continue; }
    if (!rising) {
      valley = Math.min(valley, value);
      if (value - valley >= 0.06) { rising = true; peak = value; }
    } else {
      peak = Math.max(peak, value);
      if (peak - value >= 0.04) {
        if (s.elapsedMs - lastPeak >= 300) { count++; lastPeak = s.elapsedMs; }
        rising = false; valley = value;
      }
    }
  }
  return count;
}

/** Engineering descriptors only. No anatomical placement or strap-tightness verdict. */
export function highFrequencyRms(samples: Sample[]): number | null {
  if (samples.length < 50) return null;
  let energy = 0, time = 0;
  const out = { x: 0, y: 0, z: 0 };
  const rc = 1 / (2 * Math.PI * 10);
  for (let i = 1; i < samples.length; i++) {
    const a = samples[i - 1], b = samples[i];
    if (a.sensorTimestampSeconds === null || b.sensorTimestampSeconds === null) return null;
    const dt = b.sensorTimestampSeconds - a.sensorTimestampSeconds;
    // Require actual native timing and >=40 Hz throughout; never fabricate filter input.
    if (dt <= 0 || dt > 0.025) return null;
    for (const axis of ['x', 'y', 'z'] as const) out[axis] = rc / (rc + dt) * (out[axis] + b[axis] - a[axis]);
    if (i > 20) { energy += (out.x ** 2 + out.y ** 2 + out.z ** 2) * dt; time += dt; }
  }
  return time >= 0.5 ? Math.sqrt(energy / time) : null;
}
export class FitCheck {
  private movementSince: number | null = null;
  private movementSeen = false;
  private settledSince: number | null = null;
  private handlingSince: number | null = null;
  update(now: number, fresh: boolean, motion: MotionWindow): 'waiting' | 'review' | 'settled' {
    if (!fresh || !motion.enough) {
      this.movementSince = this.settledSince = this.handlingSince = null;
      this.movementSeen = false;
      return 'waiting';
    }
    if (motion.context === 'possible-handling') {
      this.handlingSince ??= now;
      if (now - this.handlingSince >= 1500) return 'review';
    } else this.handlingSince = null;
    if (motion.context === 'movement' && !motion.steady) {
      this.movementSince ??= now;
      if (now - this.movementSince >= 1000) this.movementSeen = true;
    } else this.movementSince = null;
    if (this.movementSeen && motion.steady && motion.upright) this.settledSince ??= now;
    else this.settledSince = null;
    return this.settledSince !== null && now - this.settledSince >= 3000 ? 'settled' : 'waiting';
  }
}
export class ShiftMonitor {
  private since: number | null = null;
  private flagged = false;
  constructor(private reference: { x: number; y: number; z: number }) {}
  update(now: number, samples: Sample[]): number | null {
    if (samples.length < 10 || samples[samples.length - 1].elapsedMs - samples[0].elapsedMs < 1500 ||
      samples.some((s, i) => i > 0 && (s.elapsedMs <= samples[i - 1].elapsedMs || s.elapsedMs - samples[i - 1].elapsedMs > 250))) { this.since = null; return null; }
    const mean = { x: 0, y: 0, z: 0 };
    for (const s of samples) for (const axis of ['x', 'y', 'z'] as const) mean[axis] += s[axis] / samples.length;
    const g = Math.hypot(mean.x, mean.y, mean.z), ref = Math.hypot(this.reference.x, this.reference.y, this.reference.z);
    if (g < 0.8 || g > 1.2 || ref < 0.8 || ref > 1.2) { this.since = null; return null; }
    const angle = Math.acos(Math.max(-1, Math.min(1, (mean.x * this.reference.x + mean.y * this.reference.y + mean.z * this.reference.z) / (g * ref)))) * 180 / Math.PI;
    if (angle <= 15) this.since = null;
    else this.since ??= now;
    if (!this.flagged && this.since !== null && now - this.since >= 2000) { this.flagged = true; return angle; }
    return null;
  }
}
