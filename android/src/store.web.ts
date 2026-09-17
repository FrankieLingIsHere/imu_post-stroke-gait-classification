import type { SessionRecord } from './store';
import { locale } from './language';
import { parseReviewRecording } from './reviewRecording';

// Browser review is memory-only. No patient files are bundled, uploaded or persisted.
const sessions = new Map<string, SessionRecord>();
export function importReviewRecording(text: string) {
  const session = parseReviewRecording(text); sessions.set(session.id, session); return session.id;
}
export async function getSessions() { return [...sessions.values()].sort((a,b)=>b.date.localeCompare(a.date)); }
export async function getSession(id:string) { return sessions.get(id); }
export async function saveSession(_session:SessionRecord) { throw new Error('Browser review does not record sensors.'); }
export function generateSessionId() { return String(Date.now()); }
export function formatSessionDate(date:string) { return new Date(date).toLocaleString(locale(),{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}); }
export function formatDuration(seconds:number) { return seconds+' seconds'; }
