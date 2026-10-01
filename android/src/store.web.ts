import { recoverParticipantProfiles, assignRecordingParticipant } from './participantLinks';
import type { SessionRecord, ParticipantProfile } from './store';
import type { DistanceCalibration } from './distanceEstimation';
import { locale } from './language';
import { parseReviewRecording } from './reviewRecording';

// Browser capture and review are memory-only. Export before closing or refreshing.
const sessions = new Map<string, SessionRecord>();
const participants = new Map<string, ParticipantProfile>();
export async function getParticipants() {
  const recovered=recoverParticipantProfiles([...participants.values()],[...sessions.values()]);
  for(const p of recovered)participants.set(p.id,p);
  return recovered;
}
export async function saveParticipant(profile: ParticipantProfile) { participants.set(profile.id, JSON.parse(JSON.stringify(profile))); }
export async function toggleParticipantFavorite(id: string) { const p=participants.get(id);if(p)await saveParticipant({...p,favorite:!p.favorite,updatedAt:new Date().toISOString()}); }
export async function archiveParticipant(id: string) { const p=participants.get(id);if(p)await saveParticipant({...p,archived:true,updatedAt:new Date().toISOString()}); }
export async function saveParticipantDistanceCalibration(id:string, distanceCalibration:DistanceCalibration) { const p=participants.get(id);if(!p)return undefined;const updated={...p,distanceCalibration,updatedAt:new Date().toISOString()};await saveParticipant(updated);return updated; }
export function importReviewRecording(text: string) {
  const session = parseReviewRecording(text); sessions.set(session.id, session); return session.id;
}
export async function getSessions() { return [...sessions.values()].sort((a,b)=>b.date.localeCompare(a.date)); }
export async function getSession(id:string) { return sessions.get(id); }
export async function saveSession(session:SessionRecord) {
  if(session.recording?.platform !== 'web' || session.recording.acquisition?.api !== 'generic-sensor-api-v1') throw new Error('Only browser sensor recordings can be saved here.');
  sessions.set(session.id, session);
}
export function generateSessionId() { return new Date().toISOString().replace(/[:.]/g,'-')+'-'+Math.random().toString(16).slice(2,10); }
export function formatSessionDate(date:string) { return new Date(date).toLocaleString(locale(),{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}); }
export function formatDuration(seconds:number) { return seconds+' seconds'; }

export async function linkSessionParticipant(sessionId:string,participantId:string):Promise<SessionRecord> {
  const session=sessions.get(sessionId),profile=(await getParticipants()).find(p=>p.id===participantId);
  if(!session||!profile)throw new Error('Recording or participant not found.');
  const linked=assignRecordingParticipant(session,profile);
  sessions.set(sessionId,linked);
  return linked;
}
