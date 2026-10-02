import type { SessionRecord } from './store';
import { SENSOR_NAMES, SENSOR_UNITS } from './recording';
import { describeMovement } from './movement';
import { researchFeatures } from './researchFeatures';
import { protocolPhoneEstimate } from './distanceEstimation';
import { comparisonSignals } from './comparisonSignals';
import { alternatingTiming } from './alternatingTiming';
const GOOGLE_COLUMNS = ['google_distance_m','google_steps','google_mean_speed_mps','google_record_status','google_distance_coverage_fraction','google_window_start_unix_ms','google_window_end_unix_ms','google_poll_count','google_boundary_records_excluded','google_cleanup_status','google_provider_version','experiment_kind','trial_reference_distance_m','trial_route_completed','trial_end','trial_route_pattern'];
function googleCells(session: SessionRecord): unknown[] {
  const g = session.recording?.googleRecording;
  return [g?.distanceM??'',g?.steps??'',g?.meanSpeedMps??'',g?.status??'not-recorded',g?.distanceCoverageFraction??'',g?.startUnixMs??'',g?.endUnixMs??'',g?.polls.length??'',g?.boundaryRecordsExcluded??'',g?.subscriptionCleanup??'',g?.version??'',session.googleDistanceTrial?.version??'',session.googleDistanceTrial?.referenceDistanceM??'',session.googleDistanceTrial?.completedMarkedRoute??'',session.googleDistanceTrial?.end??'',session.googleDistanceTrial?.routePattern??''];
}
export function exportJSON(session: SessionRecord): string {
  const features=session.recording?researchFeatures(session.recording,session.demographics?.heightCm??null,session.participantSnapshot?.distanceCalibration):null;
  return JSON.stringify({ exportSchemaVersion: 3, source: session.recording ? 'device' : 'legacy-simulation', note: 'Research capture, not diagnosis. Device streams are asynchronous and unresampled.', analysisOrigin: 'computed-from-saved-signals', alternatingTiming: session.recording ? alternatingTiming(session.recording) : null, comparisonSignals: session.recording ? comparisonSignals(session.recording) : null, movementSummary: session.recording ? describeMovement(session.recording) : null, researchFeatures:features, protocolPhoneEstimate:features?protocolPhoneEstimate(features.distanceEstimate,session.assessmentSetup?.protocol??'research-walk',session.protocolExecution?.elapsedFromGoSeconds):null, session }, null, 2);
}
/** Separate tidy feature CSV; raw event CSV remains unchanged. JSON carries full provenance. */
export function exportFeatureCSV(session: SessionRecord): string {
  const rows: unknown[][] = [['session_id','source','feature_version','feature','value','unit','status','definition','reason','aggregation','placement_instruction','placement_verified','comparison_eligibility','capture_notes','estimator_version','platform','sensor_api','timestamp_basis','app_version','build_number','runtime_version','update_id','channel','embedded','participant_id','participant_label','age_years','sex','height_cm','weight_kg','stroke_type','lesion_location','months_since_stroke','assistive_device','protocol','completion_status','measured_distance_m','timed_interval_s','measured_speed_mps','distance_source','lap_count','rest_count','perceived_exertion','observed_gait_scale','observed_gait_score','phone_estimated_distance_m','phone_estimated_speed_mps','phone_distance_status','phone_distance_method','gps_distance_m','gps_median_accuracy_m','gps_accepted_fixes','gps_status','gps_raw_coordinates_saved','affected_hemisphere','affected_body_side','chronicity_status','history_source',...GOOGLE_COLUMNS]];
  if (session.recording) {
    const result = researchFeatures(session.recording, session.demographics?.heightCm ?? null, session.participantSnapshot?.distanceCalibration);
    const phoneOutcome=protocolPhoneEstimate(result.distanceEstimate,session.assessmentSetup?.protocol??'research-walk',session.protocolExecution?.elapsedFromGoSeconds);
    for (const [name, feature] of Object.entries(result.features)) {
      const timing = name in result.gaitTiming.features;
      const release = session.recording.appRelease;
      const assessment=session.assessment;
      const profile=session.participantSnapshot;
      const gps=session.recording.locationDistance;
      rows.push([session.id,'device',result.version,name,feature.value,feature.unit,feature.status,feature.definition,feature.reason,timing?(session.recording.platform==='web'?'candidate-step-bouts-browser-sensor-time':'candidate-step-bouts-native-time'):result.aggregation,result.placementInstruction,false,result.comparisonEligibility,result.captureNotes.join(' | '),timing?result.gaitTiming.version:result.version,session.recording.platform,session.recording.acquisition?.api ?? 'expo-sensors',session.recording.timestampBasis,release?.appVersion ?? '',release?.buildNumber ?? '',release?.runtimeVersion ?? '',release?.updateId ?? '',release?.channel ?? '',release?.embedded ?? '',session.participantId ?? '',session.participantLabel ?? '',session.demographics?.ageYears ?? '',session.demographics?.sex ?? '',session.demographics?.heightCm ?? '',profile?.demographics.weightKg ?? '',profile?.clinical.strokeType ?? '',profile?.clinical.lesionLocation ?? '',profile?.clinical.monthsSinceStroke ?? '',profile?.clinical.assistiveDevice ?? '',session.assessmentSetup?.protocol ?? '',assessment?.completionStatus ?? '',assessment?.distanceSource==='measured-course'?(assessment.distanceWalkedM ?? ''):'',assessment?.timedZoneSeconds ?? '',assessment?.speedMps ?? '',assessment?.distanceSource ?? 'unavailable',assessment?.lapCount ?? '',assessment?.restCount ?? '',assessment?.perceivedExertion ?? '',assessment?.observedGaitScale ?? '',assessment?.observedGaitScore ?? '',phoneOutcome.distanceM ?? '',phoneOutcome.meanSpeedMps ?? '',phoneOutcome.status,phoneOutcome.method,gps?.distanceM ?? '',gps?.medianAccuracyM ?? '',gps?.acceptedFixes ?? '',gps?.status ?? 'not-recorded',gps?.rawCoordinatesSaved ?? '',profile?.clinical.affectedHemisphere ?? '',profile?.clinical.affectedBodySide ?? '',profile?.clinical.chronicityStatus ?? '',profile?.clinical.historySource ?? '',...googleCells(session)]);
    }
  } else rows.push([session.id,'legacy-simulation','','','', '', 'unavailable','','Simulated recording; no device features.','','',false,'not-established','','','','','','','','','','',session.assessmentSetup?.protocol ?? '',session.assessment?.completionStatus ?? '',session.assessment?.distanceWalkedM ?? '',session.assessment?.timedZoneSeconds ?? '',session.assessment?.speedMps ?? '',session.assessment?.distanceSource ?? 'unavailable',session.assessment?.lapCount ?? '',session.assessment?.restCount ?? '',session.assessment?.perceivedExertion ?? '',session.assessment?.observedGaitScale ?? '',session.assessment?.observedGaitScore ?? '']);
  return rows.map(row => row.map(cell).join(',')).join('\r\n') + '\r\n';
}
function cell(value: unknown) { return '"' + String(value ?? '').replace(/"/g, '""') + '"'; }
/** Long format: one event per row, never invent a synchronized nine-axis sample. */
export function exportCSV(session: SessionRecord): string {
  return csvForSessions([session]);
}
export function exportCSVBundle(sessions: SessionRecord[]): string {
  return csvForSessions(sessions);
}
function csvForSessions(sessions: SessionRecord[]): string {
  const header = ['session_id', 'source', 'practice', 'age_years', 'sex', 'started_at', 'planned_seconds', 'recorded_seconds', 'stop_reason', 'placement', 'coordinate_frame', 'sensor', 'units', 'requested_hz', 'elapsed_ms', 'received_at_unix_ms', 'sensor_timestamp_seconds', 'x', 'y', 'z', 'placement_review_required','platform','sensor_api','timestamp_basis','app_version','build_number','runtime_version','update_id','channel','embedded','gps_distance_m','gps_median_accuracy_m','gps_accepted_fixes','gps_status','gps_raw_coordinates_saved','participant_id','participant_label','height_cm','assessment_protocol','protocol_flow_version','protocol_go_offset_ms','protocol_go_source','protocol_elapsed_seconds','protocol_end',...GOOGLE_COLUMNS];
  const rows: unknown[][] = [header];
  for (const session of sessions) appendCsvRows(rows, session);
  return rows.map(row => row.map(cell).join(',')).join('\r\n') + '\r\n';
}
function appendCsvRows(rows: unknown[][], session: SessionRecord) {
  const r = session.recording;
  if (r) for (const name of SENSOR_NAMES) for (const s of r.streams[name]) rows.push([
    session.id, 'device', session.isPractice, session.demographics?.ageYears ?? '', session.demographics?.sex ?? 'prefer-not-to-say', r.startedAt, session.duration, r.elapsedSeconds, r.stopReason,
    r.placement, r.coordinateFrame, name, SENSOR_UNITS[name], r.requestedHz[name],
    s.elapsedMs, s.receivedAtUnixMs, s.sensorTimestampSeconds, s.x, s.y, s.z, r.guidanceEvents.some(e => e.type === 'possible-placement-shift'),r.platform,r.acquisition?.api ?? 'expo-sensors',r.timestampBasis,r.appRelease?.appVersion ?? '',r.appRelease?.buildNumber ?? '',r.appRelease?.runtimeVersion ?? '',r.appRelease?.updateId ?? '',r.appRelease?.channel ?? '',r.appRelease?.embedded ?? '',r.locationDistance?.distanceM ?? '',r.locationDistance?.medianAccuracyM ?? '',r.locationDistance?.acceptedFixes ?? '',r.locationDistance?.status ?? 'not-recorded',r.locationDistance?.rawCoordinatesSaved ?? '',session.participantId??'',session.participantLabel??'',session.demographics?.heightCm??'',session.assessmentSetup?.protocol??'',session.protocolExecution?.version??'',session.protocolExecution?.goOffsetMs??'',session.protocolExecution?.goSource??'',session.protocolExecution?.elapsedFromGoSeconds??'',session.protocolExecution?.end??'',...googleCells(session),
  ]);
  else for (const s of session.windows) rows.push([session.id, 'legacy-simulation', session.isPractice, '', '', session.date, session.duration, '', '', 'simulated', 'simulated', 'accelerometer', 'g', 100, s.timestamp - (session.windows[0]?.timestamp ?? 0), s.timestamp, '', s.x, s.y, s.z, 'unknown','','','','','','','','','','','','','','',session.participantId??'',session.participantLabel??'',session.demographics?.heightCm??'','','','','','','']);
}
