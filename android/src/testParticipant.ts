import type { ParticipantProfile, ParticipantSex, AssistiveDevice, ClinicalSide } from './store';

export interface TestParticipantInput {
  id?: string; newId: string; label: string; ageYears: number | null;
  sex: ParticipantSex | null; heightCm: number | null; assistiveDevice: AssistiveDevice;
  affectedHemisphere?: ClinicalSide; affectedBodySide?: ClinicalSide;
  chronicityStatus?: 'known' | 'unknown'; monthsSinceStroke?: number | null;
  historySource?: 'patient-or-caregiver-report' | 'clinician-record';
}
export const participantKey = (label: string) => label.trim().normalize('NFKC').toLocaleLowerCase();

/** A study label identifies a person. Demographic similarity never does. */
export function resolveTestParticipant(profiles: ParticipantProfile[], input: TestParticipantInput, now = new Date().toISOString()): ParticipantProfile {
  if (!input.label.trim()) throw new Error('Enter a study ID or participant label.');
  if (input.ageYears === null || !Number.isInteger(input.ageYears) || input.ageYears < 1 || input.ageYears > 120) throw new Error('Enter an age from 1 to 120.');
  if (!input.sex || !['female','male','prefer-not-to-say'].includes(input.sex)) throw new Error('Choose a sex option, or choose Prefer not to say.');
  const matches = profiles.filter(p => participantKey(p.label) === participantKey(input.label));
  if (matches.length > 1 || (matches.length && matches[0].id !== input.id && matches[0].id !== input.newId)) throw new Error('This label already exists. Select that saved participant or use a different ID.');
  const existing = input.id ? profiles.find(p => p.id === input.id) : profiles.find(p => p.id === input.newId);
  if (input.id && (!existing || existing.archived)) throw new Error('This participant is unavailable. Choose another participant.');
  if (input.heightCm !== null && (!Number.isFinite(input.heightCm) || input.heightCm < 100 || input.heightCm > 230)) throw new Error('Enter height from 100 to 230 cm.');
  return {
    ...existing, id: existing?.id ?? input.newId, label: input.label.trim(),
    favorite: existing?.favorite ?? false, archived: false, createdAt: existing?.createdAt ?? now, updatedAt: now,
    demographics: { ...existing?.demographics, ageYears: input.ageYears, sex: input.sex, heightCm: input.heightCm },
    clinical: { strokeType:'', lesionLocation:'', monthsSinceStroke:null, premorbidGaitNotes:'', jointOrOrthopaedicNotes:'', ...existing?.clinical, assistiveDevice:input.assistiveDevice,
      ...(input.affectedHemisphere ? { affectedHemisphere: input.affectedHemisphere } : {}),
      ...(input.affectedBodySide ? { affectedBodySide: input.affectedBodySide } : {}),
      ...(input.chronicityStatus ? { chronicityStatus: input.chronicityStatus, monthsSinceStroke: input.chronicityStatus === 'known' ? input.monthsSinceStroke ?? null : null } : {}),
      ...(input.historySource ? { historySource: input.historySource } : {}),
    },
  };
}
