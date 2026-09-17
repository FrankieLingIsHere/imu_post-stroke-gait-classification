import type { SessionRecord } from './store';
import { SENSOR_NAMES } from './recording';

/** Restrict local review to finite, bounded device exports produced by this app. */
export function parseReviewRecording(text:string):SessionRecord {
  const invalid=()=>new Error('Choose a valid Gait Steps device JSON export (up to 20 MB).');
  if(text.length>20*1024*1024)throw invalid();
  let payload:any;try {payload=JSON.parse(text);}catch{throw invalid();}
  const session=payload?.session,r=session?.recording;
  if(![2,3].includes(payload?.exportSchemaVersion)||payload.source!=='device'||!r||r.source!=='device'||r.schemaVersion!==2)throw invalid();
  if(typeof session.id!=='string'||session.id.length>160||!session.id||typeof session.date!=='string'||!Number.isFinite(Date.parse(session.date))||typeof session.isPractice!=='boolean'||!Number.isFinite(session.duration)||!Array.isArray(session.windows)||session.windows.length!==0)throw invalid();
  if(!Number.isFinite(r.elapsedSeconds)||r.elapsedSeconds<0||r.elapsedSeconds>120||!['completed','user-stopped','interrupted'].includes(r.stopReason)||!Array.isArray(r.guidanceEvents)||r.guidanceEvents.length>1000)throw invalid();
  for(const event of r.guidanceEvents)if(!event||typeof event.type!=='string'||!Number.isFinite(event.elapsedMs))throw invalid();
  for(const name of SENSOR_NAMES){
    const rows=r.streams?.[name];
    if(!Array.isArray(rows)||rows.length>100000||!Number.isFinite(r.requestedHz?.[name])||r.requestedHz[name]<=0)throw invalid();
    for(const sample of rows)if(!sample||![sample.x,sample.y,sample.z,sample.elapsedMs,sample.receivedAtUnixMs].every(Number.isFinite)||sample.elapsedMs<0||sample.elapsedMs>r.elapsedSeconds*1000+500||(sample.sensorTimestampSeconds!==null&&!Number.isFinite(sample.sensorTimestampSeconds)))throw invalid();
  }
  if(r.fitCheck && r.fitCheck.highPass10HzRmsG!==null&&!Number.isFinite(r.fitCheck.highPass10HzRmsG))throw invalid();
  return session;
}
