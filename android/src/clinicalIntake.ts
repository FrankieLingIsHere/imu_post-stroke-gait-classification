import type { ParticipantProfile } from './store';

/** Explicit unknown is allowed; missing fields on older profiles need review. */
export function clinicalIntakeIssue(clinical: ParticipantProfile['clinical']): string | null {
  if (!['left','right','bilateral','unknown'].includes(clinical.affectedHemisphere ?? '') ||
      !['left','right','bilateral','unknown'].includes(clinical.affectedBodySide ?? '') ||
      !['known','unknown'].includes(clinical.chronicityStatus ?? '') ||
      !['patient-or-caregiver-report','clinician-record'].includes(clinical.historySource ?? ''))
    return 'Complete the stroke history before a clinical test. Unknown is an available answer.';
  if (clinical.chronicityStatus === 'known' &&
    (clinical.monthsSinceStroke === null || !Number.isInteger(clinical.monthsSinceStroke) || clinical.monthsSinceStroke < 0 || clinical.monthsSinceStroke > 1200))
    return 'Enter whole months since stroke from 0 to 1200, or select Unknown.';
  return null;
}
