import type { Recording } from './recording';
import { estimateGaitTiming } from './gaitTiming';

export type DistanceEstimate = {
  distanceM: number | null;
  speedMps: number | null;
  status: 'measured-protocol' | 'experimental-step-model' | 'unavailable';
  method: string;
  reason: string | null;
};

export interface DistanceCalibration { metersPerCandidateEvent: number; referenceDistanceM: number; referenceEventCount: number; updatedAt: string; }

/** Exact speed when a worker supplies a measured course distance and timed interval. */
export function measuredProtocolSpeed(distanceM: number, seconds: number): DistanceEstimate {
  if (!Number.isFinite(distanceM) || distanceM <= 0 || !Number.isFinite(seconds) || seconds <= 0) return {
    distanceM: null, speedMps: null, status: 'unavailable', method: 'measured-course', reason: 'Positive measured distance and timed seconds are required.'
  };
  return { distanceM, speedMps: distanceM / seconds, status: 'measured-protocol', method: 'worker-measured-course-distance-divided-by-timed-interval', reason: null };
}

/**
 * Single-phone fallback: approximate step length from height and candidate peaks.
 * This is deliberately labelled experimental; it is not a validated stroke measure.
 */
export function estimateFromHeight(r: Recording, heightCm: number | null): DistanceEstimate {
  if (!Number.isFinite(heightCm) || heightCm === null || heightCm < 100 || heightCm > 230) return {
    distanceM: null, speedMps: null, status: 'unavailable', method: 'height-calibrated-step-model', reason: 'A valid participant height is required for the experimental step-length estimate.'
  };
  const stepLengthM = 0.413 * heightCm / 100;
  return estimateFromCandidateLength(r, stepLengthM,'candidate-peaks-times-0.413-height-step-length-heuristic');
}

/** Participant-specific scale learned from a worker-measured reference walk. */
export function estimateFromCalibration(r: Recording, calibration: DistanceCalibration): DistanceEstimate {
  const length = calibration?.metersPerCandidateEvent;
  if (!Number.isFinite(length) || length <= 0 || length > 2) return { distanceM:null, speedMps:null, status:'unavailable', method:'participant-calibrated-candidate-events', reason:'The stored calibration is invalid.' };
  return estimateFromCandidateLength(r, length, 'participant-calibrated-candidate-events');
}

function estimateFromCandidateLength(r: Recording, metersPerEvent: number, method = 'candidate-peaks-times-0.413-height-step-length-heuristic'): DistanceEstimate {
  const timing=estimateGaitTiming(r), count=timing.features.step_count?.value, boutSeconds=timing.features.candidate_bout_duration?.value;
  if (count === null || count === undefined || boutSeconds === null || boutSeconds === undefined || count < 4 || boutSeconds <= 0) return { distanceM:null, speedMps:null, status:'unavailable', method, reason:'No accepted candidate step bout supports an estimate.' };
  const activeSeconds=boutSeconds+(timing.features.step_time_mean?.value??0)*timing.bouts.length;
  const distanceM=count*metersPerEvent;
  return { distanceM, speedMps:activeSeconds>0?distanceM/activeSeconds:null, status:'experimental-step-model', method, reason:'Sensor-derived estimate; candidate events may miss or double-count steps, and stride length varies with speed, fatigue, aid and asymmetry. Validate against measured distance before research use.' };
}
