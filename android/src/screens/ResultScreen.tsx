import { workerOutcome, workerOutcomeError } from '../workerOutcome';
import React, { useEffect, useMemo, useState, useRef } from 'react';
import { TextInput, View, Pressable } from 'react-native';
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
import { protocolPhoneEstimate } from '../distanceEstimation';
import { validGaitAssessment, gaitReviewStatus } from '../gaitAssessment';
import {useFocusEffect} from '@react-navigation/native';
import { shareRecording } from '../export';
import CameraTrialReview from '../components/CameraTrialReview';
import GaitDistanceReview from '../components/GaitDistanceReview';

const Field: React.ComponentType<any> = TextInput ?? View;
const inputStyle = { minHeight: 48, borderWidth: 1, borderColor: colours.inputBorder, borderRadius: 12, paddingHorizontal: 12, fontSize: 17, color: colours.textPrimary, backgroundColor: colours.surface };
const numberText = (value: number | null | undefined) => value == null ? '' : String(value);

export default function ResultScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Result'>) {
  const [session, setSession] = useState<SessionRecord>();
  const [previousRecording, setPreviousRecording] = useState<SessionRecord['recording'] | null>(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const leaving=useRef(false);
  const [observationsOpen,setObservationsOpen]=useState(false);
  const [draftSaved,setDraftSaved]=useState(false);
  const [showReference,setShowReference]=useState(route.params.openAssessment ?? false);
  async function confirmTrial(completedMarkedRoute:boolean){
    if(!session?.googleDistanceTrial||saving)return;
    setSaving(true);setError('');
    try{const updated={...session,googleDistanceTrial:{...session.googleDistanceTrial,completedMarkedRoute}};await saveSession(updated);setSession(updated);}
    catch{setError('Could not save the assessment. Your recording remains on this phone; try saving again.');}
    finally{setSaving(false);}
  }
  async function exportTrial(){
    if(!session||saving)return;setSaving(true);setError('');
    try{await shareRecording(session,'json');}
    catch{setError('Could not export this trial. Try again.');}
    finally{setSaving(false);}
  }
  const [form, setForm] = useState<AssessmentForm>({ completed: false, completionStatus: 'not-completed', timedZoneSeconds: null, distanceWalkedM: null, lapCount: null, restCount: 0, perceivedExertion: null, symptoms: '', clinicianNotes: '', observedGaitScore: null, observedGaitScale: '' });
  useFocusEffect(React.useCallback(() => { let active=true; Promise.all([getSession(route.params.sessionId), getSessions()]).then(([current, sessions]) => {
    if(!active)return;
    setSession(current);
    leaving.current=false;
    if(current?.workerOutcomeDraft){setForm({...current.workerOutcomeDraft.form,gaitAssessment:current.assessment?.gaitAssessment});setDraftSaved(true);}
    else if (current?.assessment) {
      const saved = current.assessment;
      const partial = (current.assessmentSetup?.protocol === '2mwt' || current.assessmentSetup?.protocol === '6mwt') && saved.distanceWalkedM !== null && saved.lapCount !== null && current.assessmentSetup.courseLengthM
        ? saved.distanceWalkedM - saved.lapCount * current.assessmentSetup.courseLengthM : saved.distanceWalkedM;
      setForm({ ...saved, distanceWalkedM: partial });setDraftSaved(true);
    } else {setForm({completed:false,completionStatus:'not-completed',timedZoneSeconds:null,distanceWalkedM:null,lapCount:null,restCount:0,perceivedExertion:null,symptoms:'',clinicianNotes:'',observedGaitScore:null,observedGaitScale:''});setDraftSaved(false);}

    const currentProtocol=current?.assessmentSetup?.protocol ?? 'research-walk';
    const currentAid=current?.participantSnapshot?.clinical.assistiveDevice;
    const previous = sessions.filter(s => s.id !== route.params.sessionId && !!current?.participantId && s.participantId === current.participantId && s.recording && !s.isPractice && s.duration === current.duration && (s.assessmentSetup?.protocol ?? 'research-walk') === currentProtocol && s.participantSnapshot?.clinical.assistiveDevice === currentAid).sort((a, b) => b.date.localeCompare(a.date))[0];
    setPreviousRecording(previous?.recording ?? null);
  }).catch(() => {if(active)setError('Could not load details. Open My recordings to try again.');});return()=>{active=false;}; }, [route.params.sessionId]));
  const r = session?.recording;
  const issues = r ? recordingIssues(r) : [];
  const protocol = session?.assessmentSetup?.protocol ?? 'research-walk';
  const phoneEstimate = useMemo(() => r && session ? researchFeatures(r, session.demographics?.heightCm ?? null,session.participantSnapshot?.distanceCalibration).distanceEstimate : null, [r, session?.demographics?.heightCm, session?.participantSnapshot?.distanceCalibration]);
  const phoneOutcome=phoneEstimate?protocolPhoneEstimate(phoneEstimate,protocol,session?.protocolExecution?.elapsedFromGoSeconds):null;
  const setNumber = (key: 'timedZoneSeconds' | 'distanceWalkedM' | 'lapCount' | 'perceivedExertion' | 'observedGaitScore', raw: string) => {
    const value = raw.trim() === '' ? null : Number(raw);
    editForm(previous => ({ ...previous, [key]: value }));
  };
  const editForm:typeof setForm=update=>{setDraftSaved(false);setForm(update);};
  async function saveDraft():Promise<boolean> {
    if(!session||saving)return false;
    if([form.timedZoneSeconds,form.distanceWalkedM,form.lapCount,form.restCount,form.perceivedExertion,form.observedGaitScore].some(v=>v!==null&&!Number.isFinite(v))){setError('Correct invalid numbers before saving the draft.');return false;}
    setSaving(true);setError('');
    try {
      const latest=await getSession(session.id);if(!latest)throw new Error('This recording could not be found.');
      const {gaitAssessment,...draft}=form;
      const updated={...latest,workerOutcomeDraft:{updatedAt:new Date().toISOString(),form:draft}};
      await saveSession(updated);setSession(updated);setDraftSaved(true);return true;
    } catch {setError('Could not save worker draft. Stay here and try again.');return false;}
    finally {setSaving(false);}
  }
  useEffect(()=>navigation.addListener?.('beforeRemove',event=>{
    if(!showReference||!session||draftSaved||leaving.current)return;
    event.preventDefault();if(saving)return;
    void saveDraft().then(saved=>{if(saved){leaving.current=true;navigation.dispatch(event.data.action);}});
  }),[navigation,showReference,session,form,draftSaved,saving]);
  async function saveAssessment() {
    if (!session) return;
    if(form.gaitAssessment&&!validGaitAssessment(form.gaitAssessment)){setError('Invalid G.A.I.T. item ratings. Review the form before saving.');return;}
    const outcomeError = workerOutcomeError(session, form);
    if (outcomeError) { setError(outcomeError); return; }
    const setup = session.assessmentSetup;
    setSaving(true); setError('');
    try {
    const latest=await getSession(session.id);if(!latest){setError('This recording could not be found.');return;}
    const assessment = workerOutcome(latest, {...form,gaitAssessment:latest.assessment?.gaitAssessment??form.gaitAssessment}, true);
    const measuredDistance = assessment.distanceWalkedM;
    let updated:SessionRecord = { ...latest, assessment, workerOutcomeDraft:undefined };
      const mayCalibrate=assessment.completed&&assessment.speedMps!==null&&!!session.participantId&&!!session.participantSnapshot&&!!r&&['research-walk','2mwt','6mwt'].includes(protocol)&&typeof measuredDistance==='number'&&measuredDistance>0;
      if(mayCalibrate&&session.participantId&&session.participantSnapshot&&r){
        const reference=researchFeatures(r,session.demographics?.heightCm??null).gaitTiming.features.step_count?.value;
        const metersPerCandidateEvent=typeof reference==='number'&&reference>=8&&typeof measuredDistance==='number'?measuredDistance/reference:null;
        if(metersPerCandidateEvent!==null&&metersPerCandidateEvent>=0.08&&metersPerCandidateEvent<=1.2&&typeof measuredDistance==='number'&&typeof reference==='number'){
          const calibration={metersPerCandidateEvent,referenceDistanceM:measuredDistance,referenceEventCount:reference,updatedAt:new Date().toISOString()};
          const profile=await saveParticipantDistanceCalibration(session.participantId,calibration);
          if(profile)updated={...updated,participantSnapshot:profile};
        }
      }
      await saveSession(updated); setSession(updated); setDraftSaved(true);
      const partial = (protocol === '2mwt' || protocol === '6mwt') && measuredDistance !== null && form.lapCount !== null && setup?.courseLengthM ? measuredDistance - form.lapCount * setup.courseLengthM : measuredDistance;
      setForm({ ...assessment, distanceWalkedM: partial });
    }
    catch { setError('Could not save the assessment. Your recording remains on this phone; try saving again.'); }
    finally { setSaving(false); }
  }
  const showDistance = protocol !== 'tug' && protocol !== '10mwt';
  return <Screen scrollKey={showReference ? 1 : 0} eyebrow="STEP 4 · SAVED" title="Recording saved" navigation={session?<Text style={ui.label}>{session.participantId?t('Participant: {0}').replace('{0}',session.participantLabel||session.participantId):t('Needs participant assignment')}</Text>:undefined} actions={<>
    {showReference&&<BigButton label="Save worker draft" variant="outline" disabled={!session||saving} onPress={()=>void saveDraft()}/>}
    {!showReference&&<><BigButton label="View summary & signals" onPress={() => navigation.navigate('Details', route.params)} />
    <BigButton label="Back to home" variant="outline" onPress={() => navigation.popToTop()} /></>}
  </>}>
    {session && !session.googleDistanceTrial && !session.cameraTrial && <Card><Text style={ui.label}>{session.protocolExecution?.end==='auto-stop-estimate'?'Test finish needs checking':'Saved on this phone'}</Text><Body>{session.protocolExecution?.end==='auto-stop-estimate'?'Saved after a pause. A worker needs to confirm the test finish.':'You can rest now. Your worker will review this recording.'}</Body></Card>}

    {session && !session.googleDistanceTrial && showReference && <Card>
      <Text style={ui.label}>Assessment record · {protocol.toUpperCase()}</Text>
      <Body>Enter observed test results from the marked course and stopwatch. These fields are stored locally with this participant and are separate from the phone sensor estimates.</Body>
      {session.participantId&&['research-walk','2mwt','6mwt'].includes(protocol)&&<Text style={ui.caption}>A suitable measured walk can calibrate this participant’s future device-only distance estimate. Calibration uses the sensor’s candidate step events; it is still experimental and needs checking against measured routes.</Text>}
      <Text style={ui.label}>Test measurements</Text>
      <Text style={ui.caption}>Test status</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{([['completed','Completed'],['modified','Modified'],['not-completed','Not completed']] as const).map(([value,label])=><Pressable accessibilityRole="radio" accessibilityLabel={label} accessibilityState={{selected:form.completionStatus===value}} onPress={()=>editForm(v=>({...v,completionStatus:value}))} key={value} style={[ui.choice,{minWidth:100},form.completionStatus===value&&ui.selected]}><Text>{label}</Text></Pressable>)}</View>
      {protocol==='10mwt'&&<Text style={ui.caption}>{t('Timed zone: {0} m of a {1} m course.').replace('{0}',String(session.assessmentSetup?.timedDistanceM ?? '?')).replace('{1}',String(session.assessmentSetup?.courseLengthM ?? '?'))}</Text>}
      {protocol === 'tug' ? <View style={{gap:6}}><Text style={ui.caption}>{t('Complete TUG time (seconds)')}</Text><Field accessibilityLabel={t('TUG total stopwatch seconds')} value={numberText(form.timedZoneSeconds)} onChangeText={(v:string)=>setNumber('timedZoneSeconds',v)} placeholder={t('Complete TUG time (seconds)')} keyboardType="decimal-pad" style={inputStyle}/></View> : <View style={{gap:6}}><Text style={ui.caption}>{t(protocol==='10mwt'?'10 m timed-zone time (seconds)':'Observed timed interval (seconds)')}</Text><Field accessibilityLabel={t('Timed interval seconds')} value={numberText(form.timedZoneSeconds)} onChangeText={(v:string)=>setNumber('timedZoneSeconds',v)} placeholder={t(protocol==='10mwt'?'10 m timed-zone time (seconds)':'Observed timed interval (seconds)')} keyboardType="decimal-pad" style={inputStyle}/></View>}
      {showDistance && <View style={{gap:6}}><Text style={ui.caption}>{t(protocol==='2mwt'||protocol==='6mwt'?'Additional partial distance after full laps (m)':'Total measured distance (m)')}</Text><Field accessibilityLabel={t('Measured distance metres')} value={numberText(form.distanceWalkedM)} onChangeText={(v:string)=>setNumber('distanceWalkedM',v)} placeholder={t(protocol==='2mwt'||protocol==='6mwt'?'Additional partial distance after full laps (m)':'Total measured distance (m)')} keyboardType="decimal-pad" style={inputStyle}/></View>}
      {(protocol==='2mwt'||protocol==='6mwt')&&<View style={{gap:6}}><Text style={ui.caption}>{t('Full laps of {0} m loop').replace('{0}',String(session.assessmentSetup?.courseLengthM ?? '?'))}</Text><Field accessibilityLabel={t('Completed course laps')} value={numberText(form.lapCount)} onChangeText={(v:string)=>setNumber('lapCount',v)} placeholder={t('Full laps of {0} m loop').replace('{0}',String(session.assessmentSetup?.courseLengthM ?? '?'))} keyboardType="number-pad" style={inputStyle}/></View>}
      {(protocol==='2mwt'||protocol==='6mwt')&&<View style={{gap:6}}><Text style={ui.caption}>{t('Number of rests')}</Text><Field accessibilityLabel={t('Rest count')} value={String(form.restCount)} onChangeText={(v:string)=>editForm(p=>({...p,restCount:Math.max(0,Math.floor(Number(v)||0))}))} placeholder={t('Number of rests')} keyboardType="number-pad" style={inputStyle}/></View>}
      <BigButton label={observationsOpen?'Hide optional observations':'Optional observations and notes'} variant="outline" onPress={()=>setObservationsOpen(v=>!v)}/>
      {observationsOpen&&<View style={{gap:12}}>      <View style={{gap:6}}><Text style={ui.caption}>{t('Perceived exertion score (optional)')}</Text><Field accessibilityLabel={t('Perceived exertion score')} value={numberText(form.perceivedExertion)} onChangeText={(v:string)=>setNumber('perceivedExertion',v)} placeholder={t('Perceived exertion score (optional)')} keyboardType="decimal-pad" style={inputStyle}/></View>

      <View style={{gap:6}}><Text style={ui.caption}>{t('Observed gait scale/name (optional)')}</Text><Field accessibilityLabel={t('Observed gait scale')} value={form.observedGaitScale} onChangeText={(v:string)=>editForm(p=>({...p,observedGaitScale:v}))} placeholder={t('Observed gait scale/name (optional)')} style={inputStyle}/></View>
      <View style={{gap:6}}><Text style={ui.caption}>{t('Observed gait score (optional)')}</Text><Field accessibilityLabel={t('Observed gait score')} value={numberText(form.observedGaitScore)} onChangeText={(v:string)=>setNumber('observedGaitScore',v)} placeholder={t('Observed gait score (optional)')} keyboardType="decimal-pad" style={inputStyle}/></View>
      <View style={{gap:6}}><Text style={ui.caption}>{t('Symptoms or reason for stopping (optional)')}</Text><Field accessibilityLabel={t('Symptoms')} value={form.symptoms} onChangeText={(v:string)=>editForm(p=>({...p,symptoms:v}))} placeholder={t('Symptoms or reason for stopping (optional)')} multiline style={[inputStyle,{minHeight:72}]}/></View>
      <View style={{gap:6}}><Text style={ui.caption}>{t('Worker observations and rehab notes')}</Text><Field accessibilityLabel={t('Clinician notes')} value={form.clinicianNotes} onChangeText={(v:string)=>editForm(p=>({...p,clinicianNotes:v}))} placeholder={t('Worker observations and rehab notes')} multiline style={[inputStyle,{minHeight:88}]}/></View>
</View>}
      <BigButton label="Open G.A.I.T. worker assessment" variant="outline" disabled={saving} onPress={()=>void saveDraft().then(saved=>{if(saved)navigation.navigate('Assessment',{sessionId:session.id});})}/>
      {draftSaved&&session.workerOutcomeDraft&&<Text accessibilityLiveRegion="polite" style={ui.caption}>Worker draft saved. Assessment is not complete.</Text>}
      {session.assessment && <Body>{session.assessment.completionStatus === 'completed' ? 'Saved worker outcome' : 'Saved partial test notes'}: {workerOutcome(session, session.assessment).distanceWalkedM ?? '—'} m · {session.assessment.timedZoneSeconds ?? '—'} s{workerOutcome(session, session.assessment).speedMps !== null ? ` · ${workerOutcome(session, session.assessment).speedMps!.toFixed(2)} m/s` : ''}</Body>}

      <BigButton label={saving?'Saving assessment…':'Save assessment to this phone'} loading={saving} onPress={()=>void saveAssessment()}/>
    </Card>}
    {!showReference && !session?.googleDistanceTrial && !session?.cameraTrial && (r ? <PatientSummary recording={r} previousRecording={previousRecording} /> : <Body>Loading recording details…</Body>)}
    {session?.cameraTrial&&<CameraTrialReview session={session}/>}
    {session?.cameraDistance&&<GaitDistanceReview session={session}/>}
    {session && !session.googleDistanceTrial && !session.cameraTrial && <Card>
      <Text style={ui.label}>Gait assessment form</Text>
      <Body>Record observed test results, symptoms and clinician notes for this recording. This is not an automatic G.A.I.T. score.</Body>
      <Text style={ui.caption}>{gaitReviewStatus(session).required?(gaitReviewStatus(session).complete?'G.A.I.T. assessment complete.':'Required G.A.I.T. assessment is unfinished.'):'Practice or provider experiment — assessment not required.'}</Text>
      <BigButton label={gaitReviewStatus(session).complete?'G.A.I.T. complete — review':'Complete required G.A.I.T. assessment'} onPress={()=>{if(showReference)void saveDraft().then(saved=>{if(saved)navigation.navigate('Assessment',{sessionId:session.id});});else navigation.navigate('Assessment',{sessionId:session.id});}}/>
      <BigButton label="Test outcomes and worker notes" variant="outline" onPress={()=>{if(showReference)void saveDraft().then(saved=>{if(saved)setShowReference(false);});else setShowReference(true);}}/>
    </Card>}

    {showReference&&session?.protocolExecution&&<Card><Text style={ui.label}>Protocol capture timing</Text><Body>Capture includes time before Go. The app timer is not a worker-verified clinical outcome.</Body><Text style={ui.caption}>{t('Seconds from Go: {0}').replace('{0}',session.protocolExecution.elapsedFromGoSeconds?.toFixed(1)??t('Not provided'))}</Text><Text style={ui.caption}>{t('Capture ended: {0}').replace('{0}',t(session.protocolExecution.end))}</Text></Card>}
    {r?.platform === 'web' && <Body>Browser recording: export before refreshing or closing this tab. Sensor timing and rates may differ from Android.</Body>}

    {showReference && phoneEstimate && !session?.cameraDistance && !session?.googleDistanceTrial && !session?.cameraTrial && <Card><Text style={ui.label}>Single-phone distance estimate · experimental</Text><Body>{phoneOutcome?.distanceM !== null ? `${phoneOutcome?.distanceM?.toFixed(1)} m · ${phoneOutcome?.meanSpeedMps?.toFixed(2) ?? '—'} m/s` : 'No estimate available from this recording.'}</Body>{session?.participantSnapshot?.distanceCalibration&&<Text style={ui.caption}>Using this participant’s reference walk: {session.participantSnapshot.distanceCalibration.referenceDistanceM.toFixed(1)} m across {session.participantSnapshot.distanceCalibration.referenceEventCount} candidate events.</Text>}<Text style={ui.caption}>{protocol==='2mwt'||protocol==='6mwt'?'Average speed includes the full timed interval and any rests.':protocol==='10mwt'?'This is whole-walk estimated speed, not speed in the central 10 m timed zone.':protocol==='tug'?'This is not a verified TUG time or walking distance.':''}</Text><Text style={ui.caption}>{phoneEstimate.reason ?? 'Heuristic based on height and candidate step peaks. Not a measured distance or validated clinical speed.'}</Text></Card>}
    {showReference && r?.locationDistance && <Card><Text style={ui.label}>{t('Outdoor GPS distance cross-check')}</Text><Body>{r.locationDistance.distanceM === null ? t('No usable location fixes were received.') : `${r.locationDistance.distanceM.toFixed(1)} m`}{r.locationDistance.medianAccuracyM !== null ? ` · ${t('median reported accuracy')} ${r.locationDistance.medianAccuracyM.toFixed(1)} m` : ''}</Body><Text style={ui.caption}>{t(r.locationDistance.status === 'usable-cross-check' ? 'Location signal supports a rough outdoor cross-check only.' : 'Location signal quality was too weak for a useful distance cross-check.')}{' '}{t(r.locationDistance.note)}</Text></Card>}
    {(showReference||session?.googleDistanceTrial) && r?.googleRecording && <Card>
      <Text style={ui.label}>Google distance test · experimental</Text>
      <Body>{t('Google reported distance: {0} m').replace('{0}',r.googleRecording.distanceM?.toFixed(2)??t('Not available'))}</Body>
      <Body>{t('Google reported steps: {0}').replace('{0}',r.googleRecording.steps?.toString()??t('Not available'))}</Body>
      <Text style={ui.caption}>{t('Google record status: {0}').replace('{0}',t(r.googleRecording.status))}</Text>
      <Text style={ui.caption}>These are Google fitness records, not a calibrated clinical distance. Missing records do not mean zero walking. JSON export includes record intervals and arrival times for checking delays.</Text>
    </Card>}
    {session?.googleDistanceTrial&&<Card>
      <Text style={ui.label}>Google distance trial</Text>
      <Body>{t('Measured reference route: {0} m').replace('{0}',String(session.googleDistanceTrial.referenceDistanceM))}</Body>
      {session.googleDistanceTrial.routePattern==='5m-out-and-back'&&<Body>Route: 5 m out, turn, then 5 m back. Total measured path: 10 m. This is not a 10MWT.</Body>}
      <Body>Did you reach the finish mark before stopping?</Body>
      <View style={ui.row}><BigButton style={ui.fill} label="Reached the finish" variant={session.googleDistanceTrial.completedMarkedRoute===true?'primary':'outline'} disabled={saving} onPress={()=>void confirmTrial(true)}/><BigButton style={ui.fill} label="Stopped before the finish" variant={session.googleDistanceTrial.completedMarkedRoute===false?'primary':'outline'} disabled={saving} onPress={()=>void confirmTrial(false)}/></View>
      {session.googleDistanceTrial.completedMarkedRoute===true&&r?.googleRecording?.status==='records-received'&&r.googleRecording.distanceM!=null&&<Body>{t('Google reported difference from the reference: {0} m').replace('{0}',(r.googleRecording.distanceM-session.googleDistanceTrial.referenceDistanceM).toFixed(2))}</Body>}
      {r?.googleRecording?.status!=='records-received'&&<Text style={ui.caption}>A full-route difference is unavailable because Google records are missing, incomplete or contain errors.</Text>}
      <Text style={ui.caption}>The reference is your measured route, not Google’s estimate. Confirm completion before exporting. This trial is excluded from rehabilitation progress trends.</Text>
      <BigButton label="Export trial JSON" disabled={saving||session.googleDistanceTrial.completedMarkedRoute==null} loading={saving} onPress={()=>void exportTrial()}/>
    </Card>}


    {issues.length > 0 && <Body muted>Saved with recording notes</Body>}
    {!!error && <Text style={ui.error}>{error}</Text>}
  </Screen>;
}
