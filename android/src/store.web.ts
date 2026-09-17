import type { SessionRecord } from './store';
import { locale } from './language';
import { parseReviewRecording } from './reviewRecording';

// Browser capture and review are memory-only. Export before closing or refreshing.
const sessions = new Map<string, SessionRecord>();
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
