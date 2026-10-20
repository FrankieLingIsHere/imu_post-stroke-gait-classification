import {validGaitAssessment} from './gaitAssessment';
import {validCameraTrial} from './cameraTrial';
import {validGaitCameraDistance} from './gaitDistanceModel';
import type { SessionRecord } from './store';
import { SENSOR_NAMES, recordingIssues } from './recording';
import type { Recording, Sample, Streams, SensorName } from './recording';
import { validGoogleSummary } from './googleRecording';

/** Restrict local review to finite, bounded device exports produced by this app. */
export function parseReviewRecording(text:string):SessionRecord {
  const invalid=()=>new Error('Choose a valid Gait Steps device JSON export (up to 40 MB).');
  if(text.length>40*1024*1024)throw invalid();
  let payload:any;try {payload=JSON.parse(text);}catch{throw invalid();}
  const session=payload?.session,r=session?.recording;
  if(![2,3].includes(payload?.exportSchemaVersion)||payload.source!=='device'||!r||r.source!=='device'||r.schemaVersion!==2)throw invalid();
  if(typeof session.id!=='string'||session.id.length>160||!session.id||typeof session.date!=='string'||!Number.isFinite(Date.parse(session.date))||typeof session.isPractice!=='boolean'||!Number.isFinite(session.duration)||!Array.isArray(session.windows)||session.windows.length!==0)throw invalid();
  if(!Number.isFinite(r.elapsedSeconds)||r.elapsedSeconds<0||r.elapsedSeconds>600||!['completed','user-stopped','interrupted'].includes(r.stopReason)||!Array.isArray(r.guidanceEvents)||r.guidanceEvents.length>1000)throw invalid();
  for(const event of r.guidanceEvents)if(!event||typeof event.type!=='string'||!Number.isFinite(event.elapsedMs))throw invalid();
  for(const name of SENSOR_NAMES){
    const rows=r.streams?.[name];
    if(!Array.isArray(rows)||rows.length>100000||!Number.isFinite(r.requestedHz?.[name])||r.requestedHz[name]<=0)throw invalid();
    for(const sample of rows)if(!sample||![sample.x,sample.y,sample.z,sample.elapsedMs,sample.receivedAtUnixMs].every(Number.isFinite)||sample.elapsedMs<0||sample.elapsedMs>r.elapsedSeconds*1000+500||(sample.sensorTimestampSeconds!==null&&!Number.isFinite(sample.sensorTimestampSeconds)))throw invalid();
  }
  if(r.fitCheck && r.fitCheck.highPass10HzRmsG!==null&&!Number.isFinite(r.fitCheck.highPass10HzRmsG))throw invalid();
  if(r.googleRecording !== undefined && !validGoogleSummary(r.googleRecording))throw invalid();
  if(session.assessment?.gaitAssessment!==undefined&&!validGaitAssessment(session.assessment.gaitAssessment))throw invalid();
  if(session.cameraDistance!==undefined&&!validGaitCameraDistance(session.cameraDistance,session.id,session.assessmentSetup?.protocol??'research-walk'))throw invalid();
  if(session.cameraTrial!==undefined&&(!session.isPractice||!validCameraTrial(session.cameraTrial)||(session.cameraTrial.video.fileName!==null&&session.cameraTrial.video.fileName!==`camera-${session.id}.mp4`)))throw invalid();
  const trial=session.googleDistanceTrial;
  if(trial!==undefined&&(!trial||trial.version!=='google-distance-trial-v1'||![2,3,5,10].includes(trial.referenceDistanceM)||![undefined,'straight','5m-out-and-back'].includes(trial.routePattern)||(trial.referenceDistanceM===10&&trial.routePattern!=='5m-out-and-back')||(trial.referenceDistanceM!==10&&trial.routePattern==='5m-out-and-back')||![undefined,null,true,false].includes(trial.completedMarkedRoute)||![undefined,'quiet-stop','time-limit','user-stopped','interrupted'].includes(trial.end)||session.isPractice!==true))throw invalid();
  return session;
}

/** Rebuild a reviewable recording from the app's long-format raw CSV export. */
function* csvReview(text: string): Generator<void,SessionRecord> {
  const invalid = () => new Error('Choose a raw GaitTrace recording CSV export.');
  if (text.length > 128 * 1024 * 1024) throw invalid();
  // Parse one row at a time: six-minute exports repeat wide metadata columns.
  // Retaining every parsed cell can exhaust a phone's JS heap.
  function* lines(){let start=0;while(start<text.length){const end=text.indexOf('\n',start);const line=text.slice(start,end<0?text.length:end).replace(/\r$/,'');start=end<0?text.length:end+1;if(line.trim())yield line;}}
  const input=lines();const headerLine=input.next();if(headerLine.done)throw invalid();
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
  const header = parseLine(headerLine.value);
  // The first raw CSV format ended at placement_review_required. Newer exports
  // append platform, API and timestamp provenance; those columns are optional.
  const required = ['session_id','source','practice','started_at','planned_seconds','recorded_seconds','stop_reason','placement','coordinate_frame','sensor','units','requested_hz','elapsed_ms','received_at_unix_ms','sensor_timestamp_seconds','x','y','z'];
  if (!required.every(k => header.includes(k))) throw invalid();
  const columns=new Map(header.map((name,index)=>[name,index]));
  const at = (name: string) => columns.get(name)??-1;
  const firstLine=input.next();if(firstLine.done)throw invalid();
  const first=parseLine(firstLine.value),id=first[at('session_id')];if(!id||first.length<header.length)throw invalid();
  const firstBySensor:Partial<Record<SensorName,string[]>>={},mismatched=new Set<string>();
  const constantKeys=['participant_id','experiment_kind','trial_reference_distance_m','trial_route_completed','trial_end','trial_route_pattern','protocol_flow_version','protocol_go_offset_ms','protocol_elapsed_seconds','protocol_end','protocol_go_source'];
  function* rows(){yield first;for(const line of input)yield parseLine(line);}
  const streams: Streams = { accelerometer: [], gyroscope: [], magnetometer: [] };
  let rowCount=0;
  for (const row of rows()) {
    if(++rowCount%500===0)yield;
    if(row.length<header.length||row[at('source')]!=='device'||row[at('session_id')]!==id)throw invalid();
    for(const key of constantKeys)if(row[at(key)]!==first[at(key)])mismatched.add(key);
    const name = row[at('sensor')] as SensorName;
    if (!SENSOR_NAMES.includes(name)) throw invalid();
    firstBySensor[name]??=row;
    const number = (key: string) => Number(row[at(key)]);
    const sample: Sample = { x: number('x'), y: number('y'), z: number('z'), elapsedMs: number('elapsed_ms'), receivedAtUnixMs: number('received_at_unix_ms'), sensorTimestampSeconds: row[at('sensor_timestamp_seconds')] ? number('sensor_timestamp_seconds') : null };
    if (!Object.values(sample).every(v => v === null || Number.isFinite(v))) throw invalid();
    streams[name].push(sample);
    if(streams[name].length>100000)throw invalid();
  }
  const stop = first[at('stop_reason')] as Recording['stopReason'];
  if (!['completed','user-stopped','interrupted'].includes(stop)) throw invalid();
  const recording: Recording = {
    schemaVersion: 2, source: 'device', startedAt: first[at('started_at')], elapsedSeconds: numberFrom(first, at('recorded_seconds')),
    requestedHz: { accelerometer: numberFrom(firstBySensor.accelerometer ?? first, at('requested_hz')), gyroscope: numberFrom(firstBySensor.gyroscope ?? first, at('requested_hz')), magnetometer: numberFrom(firstBySensor.magnetometer ?? first, at('requested_hz')) },
    units: { accelerometer: 'g', gyroscope: 'rad/s', magnetometer: 'uT' }, platform: first[at('platform')] || 'unknown', osVersion: 'imported-csv', placement: first[at('placement')] === 'lower-back-upright-screen-out' ? 'lower-back-upright-screen-out' : 'lower-back-landscape-screen-out', coordinateFrame: 'device', accelerationIncludesGravity: true,
    magnetometerCalibration: 'OS-calibrated; app accuracy unverified', timestampBasis: first[at('timestamp_basis')]?.includes('browser') ? 'elapsedMs: monotonic JS receipt; receivedAtUnixMs: wall clock; sensorTimestampSeconds: browser Sensor.timestamp / 1000' : 'elapsedMs: monotonic JS receipt; receivedAtUnixMs: wall clock; sensorTimestampSeconds: native event', stopReason: stop, guidanceEnabled: false, voiceEnabled: false, guidanceEvents: [], streams,
  };
  if(!Number.isFinite(Date.parse(recording.startedAt))||recording.elapsedSeconds<0||recording.elapsedSeconds>600||SENSOR_NAMES.some(name=>recording.requestedHz[name]<=0||streams[name].some(s=>s.elapsedMs<0||s.elapsedMs>recording.elapsedSeconds*1000+500)))throw invalid();
  const ageIndex = header.indexOf('age_years');
  const sexIndex = header.indexOf('sex');
  const ageValue = ageIndex >= 0 && first[ageIndex] !== '' ? Number(first[ageIndex]) : null;
  const sexValue = sexIndex >= 0 && ['female','male','intersex','prefer-not-to-say'].includes(first[sexIndex]) ? first[sexIndex] as 'female'|'male'|'intersex'|'prefer-not-to-say' : 'prefer-not-to-say';
  const ageYears = ageValue !== null && Number.isInteger(ageValue) && ageValue >= 1 && ageValue <= 120 ? ageValue : null;
  const session: SessionRecord = { id, date: recording.startedAt, duration: numberFrom(first, at('planned_seconds')), isPractice: first[at('practice')] === 'true', demographics: { ageYears, sex: sexValue }, quality: recordingIssues(recording).length?'repeat':'good', windowCount: 0, windows: [], recording };
  const identity=first[at('participant_id')];
  if(identity){session.participantId=identity;session.participantLabel=first[at('participant_label')]||identity;}
  const protocol=first[at('assessment_protocol')];
  if(protocol&&['research-walk','10mwt','tug','2mwt','6mwt'].includes(protocol)){
    session.assessmentSetup={protocol:protocol as NonNullable<SessionRecord['assessmentSetup']>['protocol'],courseLengthM:null,timedDistanceM:null,speedCondition:'comfortable',turnDirection:'self-selected'};
    if(first[at('protocol_flow_version')]==='protocol-flow-v1'){
      const offset=first[at('protocol_go_offset_ms')],elapsed=first[at('protocol_elapsed_seconds')],end=first[at('protocol_end')],source=first[at('protocol_go_source')];
      if(!['duration','worker-ended','auto-stop-estimate','distance-ended','interrupted','capture-limit'].includes(end)||!['speech-start-callback','worker-tap','automatic-silent-cue'].includes(source)||constantKeys.filter(k=>k.startsWith('protocol_')).some(k=>mismatched.has(k)))throw invalid();
      for(const value of [offset,elapsed])if(value&&(!Number.isFinite(Number(value))||Number(value)<0))throw invalid();
      session.protocolExecution={version:'protocol-flow-v1',protocol:session.assessmentSetup.protocol,goOffsetMs:offset?Number(offset):null,elapsedFromGoSeconds:elapsed?Number(elapsed):null,goSource:source as NonNullable<SessionRecord['protocolExecution']>['goSource'],end:end as NonNullable<SessionRecord['protocolExecution']>['end'],clinicalOutcomeVerified:false};
    }
  }
  const height=first[at('height_cm')];
  if(height&&Number.isFinite(Number(height))&&Number(height)>=100&&Number(height)<=230)session.demographics!.heightCm=Number(height);
  if(first[at('experiment_kind')]==='google-distance-trial-v1'){
    const reference=Number(first[at('trial_reference_distance_m')]);
    const completed=first[at('trial_route_completed')],end=first[at('trial_end')];
    const patternIndex=at('trial_route_pattern');
    const pattern=patternIndex>=0?first[patternIndex]:'';
    if(!session.isPractice||![2,3,5,10].includes(reference)||!['','straight','5m-out-and-back'].includes(pattern)||(reference===10&&pattern!=='5m-out-and-back')||(reference!==10&&pattern==='5m-out-and-back')||!['','true','false'].includes(completed)||!['','quiet-stop','time-limit','user-stopped','interrupted'].includes(end))throw invalid();
    for(const key of ['experiment_kind','trial_reference_distance_m','trial_route_completed','trial_end',...(patternIndex>=0?['trial_route_pattern']:[])])if(mismatched.has(key))throw invalid();
    session.googleDistanceTrial={version:'google-distance-trial-v1',referenceDistanceM:reference as 2|3|5|10,routePattern:pattern?pattern as NonNullable<SessionRecord['googleDistanceTrial']>['routePattern']:undefined,completedMarkedRoute:completed===''?null:completed==='true',end:end?end as NonNullable<SessionRecord['googleDistanceTrial']>['end']:undefined};
  }
  if(mismatched.has('participant_id'))throw invalid();
  return session;
}
function numberFrom(row: string[], index: number) { const value = Number(row[index]); if (!Number.isFinite(value)) throw new Error('Invalid CSV number.'); return value; }

/** Share validation between synchronous consumers and cooperative native imports. */
export function parseReviewRecordingCsv(text:string):SessionRecord {
 const parser=csvReview(text);let step=parser.next();while(!step.done)step=parser.next();return step.value;
}
export async function parseReviewRecordingCsvAsync(text:string,signal?:AbortSignal):Promise<SessionRecord> {
 const parser=csvReview(text);
 try{for(;;){if(signal?.aborted)throw new Error('Import cancelled.');const step=parser.next();if(step.done)return step.value;await new Promise(resolve=>setTimeout(resolve,0));}}
 finally{parser.return(undefined as never);}
}
