import type { SessionRecord } from './store';
import { SENSOR_NAMES } from './recording';
import type { Recording, Sample, Streams, SensorName } from './recording';

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

/** Rebuild a reviewable recording from the app's long-format raw CSV export. */
export function parseReviewRecordingCsv(text: string): SessionRecord {
  const invalid = () => new Error('Choose a raw GaitTrace recording CSV export.');
  if (text.length > 40 * 1024 * 1024) throw invalid();
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) throw invalid();
  const parseLine = (line: string) => {
    const out: string[] = []; let value = ''; let quoted = false;
    for (let i = 0; i < line.length; i++) { const ch = line[i];
      if (ch === '"' && quoted && line[i + 1] === '"') { value += '"'; i++; }
      else if (ch === '"') quoted = !quoted;
      else if (ch === ',' && !quoted) { out.push(value); value = ''; }
      else value += ch;
    }
    out.push(value); return out;
  };
  const header = parseLine(lines[0]);
  // The first raw CSV format ended at placement_review_required. Newer exports
  // append platform, API and timestamp provenance; those columns are optional.
  const required = ['session_id','source','practice','started_at','planned_seconds','recorded_seconds','stop_reason','placement','coordinate_frame','sensor','units','requested_hz','elapsed_ms','received_at_unix_ms','sensor_timestamp_seconds','x','y','z'];
  if (!required.every(k => header.includes(k))) throw invalid();
  const at = (name: string) => header.indexOf(name);
  const rows = lines.slice(1).map(parseLine).filter(row => row.length >= header.length);
  if (!rows.length || rows.some(row => row[at('source')] !== 'device')) throw invalid();
  const first = rows[0]; const id = first[at('session_id')];
  if (!id || rows.some(row => row[at('session_id')] !== id)) throw invalid();
  const streams: Streams = { accelerometer: [], gyroscope: [], magnetometer: [] };
  for (const row of rows) {
    const name = row[at('sensor')] as SensorName;
    if (!SENSOR_NAMES.includes(name)) throw invalid();
    const number = (key: string) => Number(row[at(key)]);
    const sample: Sample = { x: number('x'), y: number('y'), z: number('z'), elapsedMs: number('elapsed_ms'), receivedAtUnixMs: number('received_at_unix_ms'), sensorTimestampSeconds: row[at('sensor_timestamp_seconds')] ? number('sensor_timestamp_seconds') : null };
    if (!Object.values(sample).every(v => v === null || Number.isFinite(v))) throw invalid();
    streams[name].push(sample);
  }
  const stop = first[at('stop_reason')] as Recording['stopReason'];
  if (!['completed','user-stopped','interrupted'].includes(stop)) throw invalid();
  const recording: Recording = {
    schemaVersion: 2, source: 'device', startedAt: first[at('started_at')], elapsedSeconds: numberFrom(first, at('recorded_seconds')),
    requestedHz: { accelerometer: numberFrom(rows.find(r => r[at('sensor')] === 'accelerometer') ?? first, at('requested_hz')), gyroscope: numberFrom(rows.find(r => r[at('sensor')] === 'gyroscope') ?? first, at('requested_hz')), magnetometer: numberFrom(rows.find(r => r[at('sensor')] === 'magnetometer') ?? first, at('requested_hz')) },
    units: { accelerometer: 'g', gyroscope: 'rad/s', magnetometer: 'uT' }, platform: first[at('platform')] || 'unknown', osVersion: 'imported-csv', placement: first[at('placement')] === 'lower-back-upright-screen-out' ? 'lower-back-upright-screen-out' : 'lower-back-landscape-screen-out', coordinateFrame: 'device', accelerationIncludesGravity: true,
    magnetometerCalibration: 'OS-calibrated; app accuracy unverified', timestampBasis: first[at('timestamp_basis')]?.includes('browser') ? 'elapsedMs: monotonic JS receipt; receivedAtUnixMs: wall clock; sensorTimestampSeconds: browser Sensor.timestamp / 1000' : 'elapsedMs: monotonic JS receipt; receivedAtUnixMs: wall clock; sensorTimestampSeconds: native event', stopReason: stop, guidanceEnabled: false, voiceEnabled: false, guidanceEvents: [], streams,
  };
  const ageIndex = header.indexOf('age_years');
  const sexIndex = header.indexOf('sex');
  const ageValue = ageIndex >= 0 && first[ageIndex] !== '' ? Number(first[ageIndex]) : null;
  const sexValue = sexIndex >= 0 && ['female','male','intersex','prefer-not-to-say'].includes(first[sexIndex]) ? first[sexIndex] as 'female'|'male'|'intersex'|'prefer-not-to-say' : 'prefer-not-to-say';
  const ageYears = ageValue !== null && Number.isInteger(ageValue) && ageValue >= 1 && ageValue <= 120 ? ageValue : null;
  const session: SessionRecord = { id, date: recording.startedAt, duration: numberFrom(first, at('planned_seconds')), isPractice: first[at('practice')] === 'true', demographics: { ageYears, sex: sexValue }, quality: 'good', windowCount: 0, windows: [], recording };
  return session;
}
function numberFrom(row: string[], index: number) { const value = Number(row[index]); if (!Number.isFinite(value)) throw new Error('Invalid CSV number.'); return value; }
