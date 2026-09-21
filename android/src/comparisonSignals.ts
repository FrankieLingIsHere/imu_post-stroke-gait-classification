import { Recording, SENSOR_NAMES, streamStats } from './recording';

/** Derived rotation-invariant projections, never a replacement for raw acquisition. */
export function comparisonSignals(r: Recording) {
  const reference = r.baseline?.mean.accelerometer;
  const norm = reference ? Math.hypot(reference.x, reference.y, reference.z) : 0;
  const valid = !!reference && norm >= 0.8 && norm <= 1.2 &&
    !r.guidanceEvents.some(e => e.type === 'possible-placement-shift');
  return {
    version: 'baseline-projections-v1',
    status: valid ? 'experimental' : 'unavailable',
    reference: 'stationary baseline gravity direction; fixed throughout recording',
    rawModified: false, resampled: false, anatomicalAxesVerified: false,
    limitation: 'Horizontal magnitude has no forward/lateral direction or side. Static baseline cannot track posture changes. No equivalence to a 100 Hz dataset is established.',
    sampling: Object.fromEntries(SENSOR_NAMES.map(name => [name, streamStats(r.streams[name], r.elapsedSeconds)])),
    streams: valid ? Object.fromEntries(SENSOR_NAMES.map(name => [name, r.streams[name].map(s => {
      const vertical = (s.x * reference!.x + s.y * reference!.y + s.z * reference!.z) / norm;
      return { elapsedMs: s.elapsedMs, sensorTimestampSeconds: s.sensorTimestampSeconds,
        vertical, horizontalMagnitude: Math.sqrt(Math.max(0, s.x*s.x+s.y*s.y+s.z*s.z-vertical*vertical)) };
    })])) : null,
    units: r.units, accelerationIncludesGravity: true,
  };
}
