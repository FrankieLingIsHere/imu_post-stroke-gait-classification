import React, { useEffect, useState } from 'react';
import { TextInput, View } from 'react-native';
import { Text, t } from '../i18n';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Body, Card, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { getSession, getSessions, saveSession, saveParticipantDistanceCalibration, SessionRecord, AssessmentForm } from '../store';
import { recordingIssues } from '../recording';
import PatientSummary from '../components/PatientSummary';
import { colours } from '../theme';
import { researchFeatures } from '../researchFeatures';

const Field: React.ComponentType<any> = TextInput ?? View;
const inputStyle = { minHeight: 48, borderWidth: 1, borderColor: colours.border, borderRadius: 12, paddingHorizontal: 12, fontSize: 17, color: colours.textPrimary, backgroundColor: colours.surface };
const numberText = (value: number | null | undefined) => value == null ? '' : String(value);

export default function ResultScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Result'>) {
  const [session, setSession] = useState<SessionRecord>();
  const [previousRecording, setPreviousRecording] = useState<SessionRecord['recording'] | null>(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<AssessmentForm>({ completed: false, completionStatus: 'not-completed', timedZoneSeconds: null, distanceWalkedM: null, lapCount: null, restCount: 0, perceivedExertion: null, symptoms: '', clinicianNotes: '', observedGaitScore: null, observedGaitScale: '' });
  useEffect(() => { Promise.all([getSession(route.params.sessionId), getSessions()]).then(([current, sessions]) => {
    setSession(current);
    if (current?.assessment) {
      const saved = current.assessment;
      const partial = (current.assessmentSetup?.protocol === '2mwt' || current.assessmentSetup?.protocol === '6mwt') && saved.distanceWalkedM !== null && saved.lapCount !== null && current.assessmentSetup.courseLengthM
        ? saved.distanceWalkedM - saved.lapCount * current.assessmentSetup.courseLengthM : saved.distanceWalkedM;
      setForm({ ...saved, distanceWalkedM: partial });
    }
    else if (current?.assessmentSetup?.protocol === '10mwt') setForm(v => ({ ...v, distanceWalkedM: 10 }));
    const currentProtocol=current?.assessmentSetup?.protocol ?? 'research-walk';
    const currentAid=current?.participantSnapshot?.clinical.assistiveDevice;
    const previous = sessions.filter(s => s.id !== route.params.sessionId && !!current?.participantId && s.participantId === current.participantId && s.recording && !s.isPractice && s.duration === current.duration && (s.assessmentSetup?.protocol ?? 'research-walk') === currentProtocol && s.participantSnapshot?.clinical.assistiveDevice === currentAid).sort((a, b) => b.date.localeCompare(a.date))[0];
    setPreviousRecording(previous?.recording ?? null);
  }).catch(() => setError('Could not load details. Open My recordings to try again.')); }, [route.params.sessionId]);
  const r = session?.recording;
  const issues = r ? recordingIssues(r) : [];
  const protocol = session?.assessmentSetup?.protocol ?? 'research-walk';
  const phoneEstimate = r && session ? researchFeatures(r, session.demographics?.heightCm ?? null,session.participantSnapshot?.distanceCalibration).distanceEstimate : null;
  const setNumber = (key: 'timedZoneSeconds' | 'distanceWalkedM' | 'lapCount' | 'perceivedExertion' | 'observedGaitScore', raw: string) => {
    const value = raw.trim() === '' ? null : Number(raw);
    setForm(previous => ({ ...previous, [key]: value }));
  };
  async function saveAssessment() {
    if (!session) return;
    if (form.timedZoneSeconds !== null && (!Number.isFinite(form.timedZoneSeconds) || form.timedZoneSeconds <= 0)) { setError('Enter a valid stopwatch time greater than zero.'); return; }
    if (form.distanceWalkedM !== null && (!Number.isFinite(form.distanceWalkedM) || form.distanceWalkedM < 0)) { setError('Enter a valid measured distance.'); return; }
    if (form.lapCount !== null && (!Number.isInteger(form.lapCount) || form.lapCount < 0)) { setError('Lap count must be a whole number.'); return; }
    const setup = session.assessmentSetup;
    let measuredDistance = form.distanceWalkedM;
    if ((protocol === '2mwt' || protocol === '6mwt') && (measuredDistance !== null || form.lapCount !== null) && setup?.courseLengthM) measuredDistance = (measuredDistance ?? 0) + (form.lapCount ?? 0) * setup.courseLengthM;
    if (protocol === '10mwt' && measuredDistance === null) measuredDistance = setup?.timedDistanceM ?? 10;
    const speed = measuredDistance !== null && form.timedZoneSeconds !== null ? measuredDistance / form.timedZoneSeconds : null;
    const assessment = { ...form, distanceWalkedM: measuredDistance, completed: form.completionStatus !== 'not-completed', speedMps: speed, distanceSource: measuredDistance !== null ? 'measured-course' as const : 'unavailable' as const };
    let updated = { ...session, assessment };
    setSaving(true); setError('');
    try {
      const mayCalibrate=!!session.participantId&&!!session.participantSnapshot&&!!r&&['research-walk','2mwt','6mwt'].includes(protocol)&&typeof measuredDistance==='number'&&measuredDistance>0;
      if(mayCalibrate&&session.participantId&&session.participantSnapshot&&r){
        const reference=researchFeatures(r,session.demographics?.heightCm??null).gaitTiming.features.step_count?.value;
        const metersPerCandidateEvent=typeof reference==='number'&&reference>=8&&typeof measuredDistance==='number'?measuredDistance/reference:null;
        if(metersPerCandidateEvent!==null&&metersPerCandidateEvent>=0.08&&metersPerCandidateEvent<=1.2&&typeof measuredDistance==='number'&&typeof reference==='number'){
          const calibration={metersPerCandidateEvent,referenceDistanceM:measuredDistance,referenceEventCount:reference,updatedAt:new Date().toISOString()};
          const profile=await saveParticipantDistanceCalibration(session.participantId,calibration);
          if(profile)updated={...updated,participantSnapshot:profile};
        }
      }
      await saveSession(updated); setSession(updated);
      const partial = (protocol === '2mwt' || protocol === '6mwt') && measuredDistance !== null && form.lapCount !== null && setup?.courseLengthM ? measuredDistance - form.lapCount * setup.courseLengthM : measuredDistance;
      setForm({ ...assessment, distanceWalkedM: partial });
    }
    catch { setError('Could not save the assessment. Your recording remains on this phone; try saving again.'); }
    finally { setSaving(false); }
  }
  const showDistance = protocol !== 'tug';
  return <Screen eyebrow="STEP 4 · FINISHED" title="Your walk is saved" actions={<>
    <BigButton label="View summary & signals" onPress={() => navigation.navigate('Details', route.params)} />
    <BigButton label="Back to home" variant="outline" onPress={() => navigation.popToTop()} />
  </>}>
    {session?.protocolExecution&&<Card><Text style={ui.label}>Protocol capture timing</Text><Body>Capture includes time before Go. The app timer is not a worker-verified clinical outcome.</Body><Text style={ui.caption}>{t('Seconds from Go: {0}').replace('{0}',session.protocolExecution.elapsedFromGoSeconds?.toFixed(1)??t('Not provided'))}</Text><Text style={ui.caption}>{t('Capture ended: {0}').replace('{0}',t(session.protocolExecution.end))}</Text></Card>}
    {r?.platform === 'web' && <Body>Browser recording: export before refreshing or closing this tab. Sensor timing and rates may differ from Android.</Body>}
    {r ? <PatientSummary recording={r} previousRecording={previousRecording} /> : <Body>Loading recording details…</Body>}
    {phoneEstimate && <Card><Text style={ui.label}>Single-phone distance estimate · experimental</Text><Body>{phoneEstimate.distanceM !== null ? `${phoneEstimate.distanceM.toFixed(1)} m · ${phoneEstimate.speedMps?.toFixed(2) ?? '—'} m/s` : 'No estimate available from this recording.'}</Body>{session?.participantSnapshot?.distanceCalibration&&<Text style={ui.caption}>Using this participant’s reference walk: {session.participantSnapshot.distanceCalibration.referenceDistanceM.toFixed(1)} m across {session.participantSnapshot.distanceCalibration.referenceEventCount} candidate events.</Text>}<Text style={ui.caption}>{phoneEstimate.reason ?? 'Heuristic based on height and candidate step peaks. Not a measured distance or validated clinical speed; use a marked course and worker timing for rehabilitation outcomes.'}</Text></Card>}
    {r?.locationDistance && <Card><Text style={ui.label}>{t('Outdoor GPS distance cross-check')}</Text><Body>{r.locationDistance.distanceM === null ? t('No usable location fixes were received.') : `${r.locationDistance.distanceM.toFixed(1)} m`}{r.locationDistance.medianAccuracyM !== null ? ` · ${t('median reported accuracy')} ${r.locationDistance.medianAccuracyM.toFixed(1)} m` : ''}</Body><Text style={ui.caption}>{t(r.locationDistance.status === 'usable-cross-check' ? 'Location signal supports a rough outdoor cross-check only.' : 'Location signal quality was too weak for a useful distance cross-check.')}{' '}{t(r.locationDistance.note)}</Text></Card>}
    {session && <Card>
      <Text style={ui.label}>Assessment record · {protocol.toUpperCase()}</Text>
      <Body>Enter observed test results from the marked course and stopwatch. These fields are stored locally with this participant and are separate from the phone sensor estimates.</Body>
      {session.participantId&&['research-walk','2mwt','6mwt'].includes(protocol)&&<Text style={ui.caption}>A suitable measured walk can calibrate this participant’s future device-only distance estimate. Calibration uses the sensor’s candidate step events; it is still experimental and needs checking against measured routes.</Text>}
      <Text style={ui.caption}>Test status</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{([['completed','Completed'],['modified','Modified'],['not-completed','Not completed']] as const).map(([value,label])=><Text accessibilityRole="button" onPress={()=>setForm(v=>({...v,completionStatus:value}))} key={value} style={[ui.choice,form.completionStatus===value&&ui.selected]}>{label}</Text>)}</View>
      {protocol === 'tug' ? <Field accessibilityLabel={t('TUG total stopwatch seconds')} value={numberText(form.timedZoneSeconds)} onChangeText={(v:string)=>setNumber('timedZoneSeconds',v)} placeholder={t('Complete TUG time (seconds)')} keyboardType="decimal-pad" style={inputStyle}/> : <Field accessibilityLabel={t('Timed interval seconds')} value={numberText(form.timedZoneSeconds)} onChangeText={(v:string)=>setNumber('timedZoneSeconds',v)} placeholder={t(protocol==='10mwt'?'10 m timed-zone time (seconds)':'Observed timed interval (seconds)')} keyboardType="decimal-pad" style={inputStyle}/>}
      {showDistance && <Field accessibilityLabel={t('Measured distance metres')} value={numberText(form.distanceWalkedM)} onChangeText={(v:string)=>setNumber('distanceWalkedM',v)} placeholder={t(protocol==='10mwt'?'Timed zone distance defaults to 10 m':protocol==='2mwt'||protocol==='6mwt'?'Additional partial distance after full laps (m)':'Total measured distance (m)')} keyboardType="decimal-pad" style={inputStyle}/>}
      {(protocol==='2mwt'||protocol==='6mwt')&&<Field accessibilityLabel={t('Completed course laps')} value={numberText(form.lapCount)} onChangeText={(v:string)=>setNumber('lapCount',v)} placeholder={t('Full laps of {0} m loop').replace('{0}',String(session.assessmentSetup?.courseLengthM ?? '?'))} keyboardType="number-pad" style={inputStyle}/>}
      {(protocol==='2mwt'||protocol==='6mwt')&&<Field accessibilityLabel={t('Rest count')} value={String(form.restCount)} onChangeText={(v:string)=>setForm(p=>({...p,restCount:Math.max(0,Math.floor(Number(v)||0))}))} placeholder={t('Number of rests')} keyboardType="number-pad" style={inputStyle}/>}
      <Field accessibilityLabel={t('Perceived exertion score')} value={numberText(form.perceivedExertion)} onChangeText={(v:string)=>setNumber('perceivedExertion',v)} placeholder={t('Perceived exertion score (optional)')} keyboardType="decimal-pad" style={inputStyle}/>
      <Field accessibilityLabel={t('Observed gait scale')} value={form.observedGaitScale} onChangeText={(v:string)=>setForm(p=>({...p,observedGaitScale:v}))} placeholder={t('Observed gait scale/name (optional)')} style={inputStyle}/>
      <Field accessibilityLabel={t('Observed gait score')} value={numberText(form.observedGaitScore)} onChangeText={(v:string)=>setNumber('observedGaitScore',v)} placeholder={t('Observed gait score (optional)')} keyboardType="decimal-pad" style={inputStyle}/>
      <Field accessibilityLabel={t('Symptoms')} value={form.symptoms} onChangeText={(v:string)=>setForm(p=>({...p,symptoms:v}))} placeholder={t('Symptoms or reason for stopping (optional)')} multiline style={[inputStyle,{minHeight:72}]}/>
      <Field accessibilityLabel={t('Clinician notes')} value={form.clinicianNotes} onChangeText={(v:string)=>setForm(p=>({...p,clinicianNotes:v}))} placeholder={t('Worker observations and rehab notes')} multiline style={[inputStyle,{minHeight:88}]}/>
      {form.completed && <Body>Recorded outcome: {session.assessment?.distanceWalkedM !== null && session.assessment?.distanceWalkedM !== undefined ? `${session.assessment.distanceWalkedM} m` : ''}{form.timedZoneSeconds !== null ? ` in ${form.timedZoneSeconds} s` : ''}{session.assessment?.speedMps !== null && session.assessment?.speedMps !== undefined ? ` · ${session.assessment.speedMps.toFixed(2)} m/s (measured course)` : ''}</Body>}
      <BigButton label={saving?'Saving assessment…':'Save assessment to this phone'} loading={saving} onPress={()=>void saveAssessment()}/>
    </Card>}
    {issues.length > 0 && <Body muted>Saved with recording notes</Body>}
    {!!error && <Text style={ui.error}>{error}</Text>}
  </Screen>;
}
