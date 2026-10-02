import type { ParticipantProfile, SessionRecord } from './store';

/** Recover explicit identities only. Never identify a person from age, sex or a label. */
export function recoverParticipantProfiles(profiles: ParticipantProfile[], sessions: SessionRecord[]): ParticipantProfile[] {
  const result = new Map(profiles.map(p => [p.id, p]));
  for (const s of [...sessions].sort((a,b)=>a.date.localeCompare(b.date))) {
    const id=s.participantId;
    if (typeof id!=='string'||!id.trim()||result.has(id)) continue;
    const snapshot=s.participantSnapshot?.id===id?s.participantSnapshot:undefined;
    const d=snapshot?.demographics??s.demographics;
    result.set(id,{
      id,label:snapshot?.label||s.participantLabel||id,
      favorite:false,archived:snapshot?.archived===true,createdAt:s.date,updatedAt:s.date,
      demographics:{
        ageYears:Number.isInteger(d?.ageYears)&&d!.ageYears!>=1&&d!.ageYears!<=120?d!.ageYears!:null,
        sex:d?.sex&&['female','male','intersex','prefer-not-to-say'].includes(d.sex)?d.sex:'prefer-not-to-say',
        heightCm:typeof d?.heightCm==='number'&&d.heightCm>=100&&d.heightCm<=230?d.heightCm:null,
      },
      clinical:{
        strokeType:snapshot?.clinical?.strokeType??'',lesionLocation:snapshot?.clinical?.lesionLocation??'',
        monthsSinceStroke:snapshot?.clinical?.monthsSinceStroke??null,premorbidGaitNotes:snapshot?.clinical?.premorbidGaitNotes??'',
        chronicityStatus:snapshot?.clinical?.chronicityStatus,affectedHemisphere:snapshot?.clinical?.affectedHemisphere,
        affectedBodySide:snapshot?.clinical?.affectedBodySide,historySource:snapshot?.clinical?.historySource,
        jointOrOrthopaedicNotes:snapshot?.clinical?.jointOrOrthopaedicNotes??'',
        assistiveDevice:snapshot?.clinical?.assistiveDevice??'other',
      },
    });
  }
  return [...result.values()];
}

/** Explicit retrospective assignment does not invent the person's historical measurements. */
export function assignRecordingParticipant(session:SessionRecord, profile:ParticipantProfile):SessionRecord {
  if(profile.archived)throw new Error('Choose an active participant.');
  if(session.participantId&&session.participantId!==profile.id)throw new Error('This recording already has a participant.');
  return {...session,participantId:profile.id,participantLabel:profile.label};
}
