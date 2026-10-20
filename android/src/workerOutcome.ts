import type { AssessmentForm, SessionRecord } from './store';

/** Worker observations remain separate from sensor estimates and test-end detection. */
export function workerOutcome(session: SessionRecord, form: AssessmentForm, inputHasPartialLaps = false) {
  const protocol = session.assessmentSetup?.protocol ?? 'research-walk';
  const completed = form.completionStatus === 'completed';
  const expected = protocol === '2mwt' ? 120 : protocol === '6mwt' ? 360 : null;
  let distance = form.distanceWalkedM;
  let time = form.timedZoneSeconds;
  if (protocol === '10mwt') distance = completed ? session.assessmentSetup?.timedDistanceM ?? null : null;
  if (protocol === 'tug') distance = null;
  if (inputHasPartialLaps && expected && session.assessmentSetup?.courseLengthM && (distance !== null || form.lapCount !== null)) {
    distance = (distance ?? 0) + (form.lapCount ?? 0) * session.assessmentSetup.courseLengthM;
  }
  if (completed && expected && time === null) time = expected;
  const capture = session.protocolExecution?.elapsedFromGoSeconds;
  const intervalMatches = expected === null || (time !== null && Math.abs(time - expected) <= 1 && (capture == null || capture >= expected - 1));
  const speed = completed && intervalMatches && distance !== null && distance > 0 && time !== null && time > 0 ? distance / time : null;
  return { ...form, completed, timedZoneSeconds: time, distanceWalkedM: distance, speedMps: speed,
    distanceSource: distance !== null ? 'measured-course' as const : 'unavailable' as const };
}

export function workerOutcomeError(session: SessionRecord, form: AssessmentForm): string | null {
  if (form.timedZoneSeconds !== null && (!Number.isFinite(form.timedZoneSeconds) || form.timedZoneSeconds <= 0)) return 'Enter a valid stopwatch time greater than zero.';
  if (form.distanceWalkedM !== null && (!Number.isFinite(form.distanceWalkedM) || form.distanceWalkedM < 0)) return 'Enter a valid measured distance.';
  if (form.lapCount !== null && (!Number.isInteger(form.lapCount) || form.lapCount < 0)) return 'Lap count must be a whole number.';
  if (form.completionStatus !== 'completed') return null;
  const protocol = session.assessmentSetup?.protocol;
  if ((protocol === '10mwt' || protocol === 'tug') && form.timedZoneSeconds === null) return 'Enter the worker stopwatch time before marking this test complete.';
  if (protocol === '2mwt' || protocol === '6mwt') {
    if (form.distanceWalkedM === null && form.lapCount === null) return 'Enter measured distance or completed laps before marking this test complete.';
    const expected = protocol === '2mwt' ? 120 : 360;
    const capture = session.protocolExecution?.elapsedFromGoSeconds;
    // One second is timer-resolution tolerance, not a clinical accuracy claim.
    if ((form.timedZoneSeconds !== null && Math.abs(form.timedZoneSeconds - expected) > 1) || (capture != null && capture < expected - 1)) return 'The full test interval was not recorded. Choose Modified or Not completed.';
  }
  return null;
}
