import { Recording, SENSOR_NAMES, SENSOR_UNITS, recordingIssues, streamStats } from './recording';
import { describeMovement } from './movement';
import { estimateGaitTiming } from './gaitTiming';

/** Export-only signal descriptors. No reference comparison, classification or score. */
export function researchFeatures(r: Recording) {
  const features: Record<string, { value: number | null; unit: string; status: string; definition: string; reason: string | null }> = {};
  for (const sensor of SENSOR_NAMES) {
    const rows = r.streams[sensor];
    const valid = rows.length >= 2 && rows.every(s => [s.x,s.y,s.z].every(Number.isFinite));
    const mean = valid ? rows.reduce((a, s) => a + Math.hypot(s.x,s.y,s.z), 0) / rows.length : 0;
    const values = {
      magnitude_mean: [mean, 'Sample-weighted mean of sqrt(x²+y²+z²).'],
      magnitude_sd: [valid ? Math.sqrt(rows.reduce((a,s) => a + (Math.hypot(s.x,s.y,s.z)-mean)**2,0)/(rows.length-1)) : 0, 'Sample SD of vector magnitude, denominator n−1.'],
      vector_rms: [valid ? Math.sqrt(rows.reduce((a,s) => a+s.x*s.x+s.y*s.y+s.z*s.z,0)/rows.length) : 0, 'sqrt(mean(x²+y²+z²)); not gravity-removed or demeaned.'],
    } as const;
    for (const [name, [value, definition]] of Object.entries(values)) features[`${sensor}_${name}`] = {
      value: valid && Number.isFinite(value) ? value : null, unit: SENSOR_UNITS[sensor],
      status: valid && Number.isFinite(value) ? 'descriptive-only' : 'unavailable', definition,
      reason: valid && Number.isFinite(value) ? null : 'Fewer than two finite samples, or nonfinite calculation.',
    };
  }
  for (const [name, unit] of Object.entries({ step_count:'steps', cadence:'steps/min', walking_speed:'m/s', stride_time_cv:'fraction', stride_time_asymmetry:'fraction', walking_duration:'s' })) {
    features[name] = { value:null, unit, status:'unavailable', definition:'Not estimated by this feature pipeline.', reason:'No validated compatible walking/event estimator or distance protocol implemented.' };
  }
  const gaitTiming = estimateGaitTiming(r);
  Object.assign(features, gaitTiming.features);
  return {
    gaitTiming,
    version:'phone-research-features-v2', origin:'computed-from-saved-signals',
    aggregation:'single-session-all-saved-samples', scope:'Includes pauses, turns and possible handling. Signal descriptors have no sample exclusions, filtering, resampling, gravity removal or calibration correction. Experimental timing uses its separately documented processing and exclusions.',
    placementInstruction:r.placement, anatomicalPlacementVerified:false,
    coordinateFrame:r.coordinateFrame, elapsedSeconds:r.elapsedSeconds,
    comparisonEligibility:'not-established', clinicalValidation:false,
    captureNotes:recordingIssues(r),
    streamCoverage:Object.fromEntries(SENSOR_NAMES.map(n => [n,streamStats(r.streams[n],r.elapsedSeconds)])),
    motionContext:describeMovement(r), features,
  };
}
