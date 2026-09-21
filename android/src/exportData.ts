import type { SessionRecord } from './store';
import { SENSOR_NAMES, SENSOR_UNITS } from './recording';
import { describeMovement } from './movement';
import { researchFeatures } from './researchFeatures';
import { comparisonSignals } from './comparisonSignals';
import { alternatingTiming } from './alternatingTiming';
export function exportJSON(session: SessionRecord): string {
  return JSON.stringify({ exportSchemaVersion: 3, source: session.recording ? 'device' : 'legacy-simulation', note: 'Research capture, not diagnosis. Device streams are asynchronous and unresampled.', analysisOrigin: 'computed-from-saved-signals', alternatingTiming: session.recording ? alternatingTiming(session.recording) : null, comparisonSignals: session.recording ? comparisonSignals(session.recording) : null, movementSummary: session.recording ? describeMovement(session.recording) : null, researchFeatures: session.recording ? researchFeatures(session.recording) : null, session }, null, 2);
}
/** Separate tidy feature CSV; raw event CSV remains unchanged. JSON carries full provenance. */
export function exportFeatureCSV(session: SessionRecord): string {
  const rows: unknown[][] = [['session_id','source','feature_version','feature','value','unit','status','definition','reason','aggregation','placement_instruction','placement_verified','comparison_eligibility','capture_notes','estimator_version','platform','sensor_api','timestamp_basis']];
  if (session.recording) {
    const result = researchFeatures(session.recording);
    for (const [name, feature] of Object.entries(result.features)) {
      const timing = name in result.gaitTiming.features;
      rows.push([session.id,'device',result.version,name,feature.value,feature.unit,feature.status,feature.definition,feature.reason,timing?(session.recording.platform==='web'?'candidate-step-bouts-browser-sensor-time':'candidate-step-bouts-native-time'):result.aggregation,result.placementInstruction,false,result.comparisonEligibility,result.captureNotes.join(' | '),timing?result.gaitTiming.version:result.version,session.recording.platform,session.recording.acquisition?.api ?? 'expo-sensors',session.recording.timestampBasis]);
    }
  } else rows.push([session.id,'legacy-simulation','','','', '', 'unavailable','','Simulated recording; no device features.','','',false,'not-established','','','','','']);
  return rows.map(row => row.map(cell).join(',')).join('\r\n') + '\r\n';
}
function cell(value: unknown) { return '"' + String(value ?? '').replace(/"/g, '""') + '"'; }
/** Long format: one event per row, never invent a synchronized nine-axis sample. */
export function exportCSV(session: SessionRecord): string {
  const header = ['session_id', 'source', 'practice', 'started_at', 'planned_seconds', 'recorded_seconds', 'stop_reason', 'placement', 'coordinate_frame', 'sensor', 'units', 'requested_hz', 'elapsed_ms', 'received_at_unix_ms', 'sensor_timestamp_seconds', 'x', 'y', 'z', 'placement_review_required','platform','sensor_api','timestamp_basis'];
  const rows: unknown[][] = [header];
  const r = session.recording;
  if (r) for (const name of SENSOR_NAMES) for (const s of r.streams[name]) rows.push([
    session.id, 'device', session.isPractice, r.startedAt, session.duration, r.elapsedSeconds, r.stopReason,
    r.placement, r.coordinateFrame, name, SENSOR_UNITS[name], r.requestedHz[name],
    s.elapsedMs, s.receivedAtUnixMs, s.sensorTimestampSeconds, s.x, s.y, s.z, r.guidanceEvents.some(e => e.type === 'possible-placement-shift'),r.platform,r.acquisition?.api ?? 'expo-sensors',r.timestampBasis,
  ]);
  else for (const s of session.windows) rows.push([session.id, 'legacy-simulation', session.isPractice, session.date, session.duration, '', '', 'simulated', 'simulated', 'accelerometer', 'g', 100, s.timestamp - (session.windows[0]?.timestamp ?? 0), s.timestamp, '', s.x, s.y, s.z, 'unknown','','','']);
  return rows.map(row => row.map(cell).join(',')).join('\r\n') + '\r\n';
}
