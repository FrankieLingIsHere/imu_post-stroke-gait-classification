import React, { useEffect, useState } from 'react';
import { View, Pressable, Modal } from 'react-native';
import { Text, t, useLanguage } from '../i18n';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import SignalChart from '../components/SignalChart';
import { getSession, SessionRecord, formatSessionDate } from '../store';
import { recordingIssues, SENSOR_NAMES, SENSOR_UNITS, SensorName, streamStats, Sample } from '../recording';
import { shareRecording } from '../export';
import RecordingParticipant from '../components/RecordingParticipant';
import PatientSummary from '../components/PatientSummary';
import {useFocusEffect} from '@react-navigation/native';
import {gaitReviewStatus} from '../gaitAssessment';
import CameraTrialReview from '../components/CameraTrialReview';
import GaitDistanceReview from '../components/GaitDistanceReview';
const labels = { accelerometer: 'Acceleration', gyroscope: 'Rotation', magnetometer: 'Magnetic field' };
export default function DetailsScreen({ route, navigation }: NativeStackScreenProps<RootStackParamList, 'Details'>) {
  useLanguage();
  const [session, setSession] = useState<SessionRecord>();
  const [tab, setTab] = useState('Summary');
  const [sensor, setSensor] = useState<SensorName>('accelerometer');
  const [page, setPage] = useState(0),[overview,setOverview]=useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [exportOpen,setExportOpen]=useState(false);
  const [attempt, setAttempt] = useState(0);
  useFocusEffect(React.useCallback(() => { let active = true; setError(''); setLoading(true);
    getSession(route.params.sessionId).then(s => { if (active) { setSession(s); if (!s) setError('This recording could not be found.'); } }).catch(() => { if (active) setError('Could not load the recording. Please try again.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [route.params.sessionId, attempt]));
  const r = session?.recording;
  const legacy: Sample[] = session?.windows.map(s => ({ x: s.x, y: s.y, z: s.z, elapsedMs: s.timestamp - (session.windows[0]?.timestamp ?? 0), receivedAtUnixMs: s.timestamp, sensorTimestampSeconds: null })) ?? [];
  const samples = r ? r.streams[sensor] : sensor === 'accelerometer' ? legacy : [];
  const seconds = r?.elapsedSeconds ?? (legacy.length ? legacy[legacy.length - 1].elapsedMs / 1000 : 0);
  const pages = Math.max(1, Math.ceil(seconds / 5));
  const currentPage = Math.min(page, pages - 1);
  async function share(format: 'csv' | 'json' | 'features') {
    if (!session || busy) return;
    setBusy(true); setError('');
    try { const current=await getSession(session.id);if(!current)throw new Error('This recording could not be found.');await shareRecording(current, format); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not export. Please try again.'); }
    finally { setBusy(false); }
  }
  return <Screen navigation={<View style={{gap:8}}><View style={[ui.row, { flexWrap: 'wrap' }]}>{['Summary', 'Signals', 'Sensors', 'Notes'].map(t => <Pressable key={t} accessibilityRole="tab" accessibilityState={{ selected: tab === t }} style={[ui.choice, { flexBasis: '44%',minHeight:48,padding:8 }, tab === t && ui.selected]} onPress={() => setTab(t)}><Text style={ui.caption}>{t}</Text></Pressable>)}</View></View>} scrollKey={tab} title={session?tab:'Recording details'} actions={<BigButton label="Export recording" labelStyle={{fontSize:18}} variant="outline" disabled={!session||busy} onPress={()=>setExportOpen(true)}/>}>
    {session&&<Text style={ui.label}>{session.participantId?t('Participant: {0}').replace('{0}',session.participantLabel||session.participantId):t('Needs participant assignment')}</Text>}
    {session&&<Text style={ui.caption}>{formatSessionDate(session.date)}</Text>}
    <Modal visible={exportOpen} animationType="slide" onRequestClose={()=>{if(!busy)setExportOpen(false);}}>
      <Screen fullScreen title="Export recording" actions={<BigButton label="Done" disabled={busy} onPress={()=>setExportOpen(false)}/>}>
        <Body>Choose a file format.</Body>
        <BigButton label="Export CSV" disabled={busy} onPress={()=>share('csv')}/>
        <BigButton label="Export JSON" variant="outline" disabled={busy} onPress={()=>share('json')}/>
        <BigButton label="Export features CSV" variant="outline" disabled={busy} onPress={()=>share('features')}/>
        {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
      </Screen>
    </Modal>

    {loading && <Body>Loading recording…</Body>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
    {!loading && !session && <BigButton label="Retry loading" onPress={() => setAttempt(attempt + 1)} />}
    {session && !r && <Text style={ui.error}>Older simulated recording · not patient sensor data</Text>}
    {session && tab === 'Summary' && <>
    {!session.googleDistanceTrial&&!session.cameraTrial&&<Card>
      <Text style={ui.label}>Gait assessment form</Text>
      <Body>{session.assessment?'Assessment saved with this recording.':'No assessment has been saved for this recording yet.'}</Body>
      <Text style={ui.caption}>{gaitReviewStatus(session).required?(gaitReviewStatus(session).complete?'G.A.I.T. assessment complete.':'Required G.A.I.T. assessment is unfinished.'):'Practice or provider experiment — assessment not required.'}</Text>
      <BigButton label={session.assessment?.gaitAssessment?'Review G.A.I.T. worker assessment':'Open G.A.I.T. worker assessment'} variant={gaitReviewStatus(session).status==='pending'?'primary':'outline'} onPress={()=>navigation.navigate('Assessment',{sessionId:session.id})}/>
      <BigButton label="Test outcomes and worker notes" variant="outline" onPress={()=>navigation.navigate('Result',{sessionId:session.id,openAssessment:true})}/>
    </Card>}
    {session.cameraTrial ? <CameraTrialReview session={session}/> : session.googleDistanceTrial ? <Card><Text style={ui.label}>Google distance trial</Text><Body>{t('Measured reference route: {0} m').replace('{0}',String(session.googleDistanceTrial.referenceDistanceM))}</Body>{session.googleDistanceTrial.routePattern==='5m-out-and-back'&&<Body>5 m out + 5 m back, with one turn.</Body>}<Body>This is a distance experiment, not a rehabilitation assessment.</Body><BigButton label="Open trial result" variant="outline" onPress={()=>navigation.navigate('Result',{sessionId:session.id})}/></Card> : r ? <PatientSummary recording={r} /> : <Body>No gait summary is calculated from older simulated recordings.</Body>}
    {session?.protocolExecution?.end==='auto-stop-estimate'&&<Card><Text style={ui.label}>Test finish needs checking</Text><Body>The recording saved after a pause. This does not confirm that you reached the finish. A worker should review the test before using its result.</Body></Card>}


      <RecordingParticipant session={session} onLinked={setSession} onCreate={()=>navigation.navigate('Participants')}/>
      {session.cameraDistance&&<GaitDistanceReview session={session}/>}
      {r?.platform === 'web' && <Body>Browser recording: export before refreshing or closing this tab. Sensor timing and rates may differ from Android.</Body>}

    {session.demographics && <Card><Text style={ui.label}>Participant information</Text><Body>{t('Age')}: {session.demographics.ageYears ?? t('Not provided')} · {t('Sex')}: {t(session.demographics.sex === 'prefer-not-to-say' ? 'Prefer not to say' : session.demographics.sex[0].toUpperCase() + session.demographics.sex.slice(1))}</Body><Text style={ui.caption}>Self-reported research metadata; not used for diagnosis.</Text></Card>}

    </>}
    {session && tab === 'Signals' && <>
      <View style={ui.row}>{SENSOR_NAMES.map((n, i) => <Pressable key={n} accessibilityRole="tab" accessibilityLabel={t(n)} accessibilityState={{ selected: sensor === n }} onPress={() => { setSensor(n); setPage(0); }} style={[ui.choice,{minHeight:48,padding:8}, sensor === n && ui.selected]}><Text style={ui.caption}>{['Accel', 'Gyro', 'Mag'][i]}</Text></Pressable>)}</View>
      <View style={ui.row}><BigButton style={{...ui.fill,minHeight:48,paddingVertical:8}} labelStyle={{fontSize:16}} label="Whole recording" variant={overview?'primary':'outline'} onPress={()=>setOverview(true)}/><BigButton style={{...ui.fill,minHeight:48,paddingVertical:8}} labelStyle={{fontSize:16}} label="5-second detail" variant={overview?'outline':'primary'} onPress={()=>setOverview(false)}/></View>
      {overview&&<Text style={ui.caption}>Tap the graph to zoom.</Text>}
      <Card><Text style={ui.label}>{labels[sensor]} · {SENSOR_UNITS[sensor]}</Text><Text style={ui.caption}>Showing {overview?0:currentPage * 5}–{(overview?seconds:Math.min((currentPage + 1) * 5, seconds)).toFixed(1)} seconds after recording started</Text><SignalChart samples={samples} start={overview?0:currentPage * 5} end={overview?Math.max(seconds,.001):Math.min((currentPage + 1) * 5, seconds)} onSelectTime={overview?time=>{setPage(Math.min(pages-1,Math.floor(time/5)));setOverview(false);}:undefined} units={SENSOR_UNITS[sensor]} /></Card>
      {!overview&&<View style={ui.row}><BigButton style={ui.fill} label="Previous 5 sec" variant="outline" disabled={currentPage === 0} onPress={() => setPage(currentPage - 1)} /><BigButton style={ui.fill} label="Next 5 sec" variant="outline" disabled={currentPage + 1 >= pages} onPress={() => setPage(currentPage + 1)} /></View>}
      <Text style={ui.caption}>Movement signals, not a step or stroke assessment. Export contains every saved reading.</Text>
    </>}
    {session && tab === 'Sensors' && <>
      {SENSOR_NAMES.map(n => { const stat = streamStats(r ? r.streams[n] : n === 'accelerometer' ? legacy : [], seconds);
        return <Card key={n}><Text style={ui.label}>{n.charAt(0).toUpperCase() + n.slice(1)} · X / Y / Z</Text><Text style={ui.caption}>{stat.count ? `${stat.count} readings · ${stat.hz.toFixed(1)} Hz observed · ${SENSOR_UNITS[n]}` : 'No saved readings'}</Text>
          <Text style={ui.caption}>{n === 'accelerometer' ? 'Acceleration including gravity' : n === 'gyroscope' ? 'Angular velocity around each device axis' : 'OS-calibrated magnetic field; accuracy unverified'}</Text></Card>;
      })}
      <Text style={ui.caption}>Device axes: X across the screen, Y toward the top, Z out of the screen. Independent streams; no alignment or resampling applied.</Text>
    </>}
    {session && tab === 'Notes' && <>
    {session?.protocolExecution&&<Card><Text style={ui.label}>Protocol capture timing</Text><Body>Capture includes time before Go. The app timer is not a worker-verified clinical outcome.</Body><Text style={ui.caption}>{t('Seconds from Go: {0}').replace('{0}',session.protocolExecution.elapsedFromGoSeconds?.toFixed(1)??t('Not provided'))}</Text><Text style={ui.caption}>{t('Capture ended: {0}').replace('{0}',t(session.protocolExecution.end))}</Text></Card>}
      <Card><Text style={ui.label}>{seconds.toFixed(1)} seconds captured</Text><Body>{session.duration} seconds planned · {r ? r.stopReason.replace(/-/g, ' ') : 'Legacy simulation'}</Body><Text style={ui.caption}>Time includes any standing or pauses.</Text></Card>
      {r ? <><Body>{recordingIssues(r).length ? recordingIssues(r).join('\n') : 'All streams received; no gaps above 0.25 seconds detected.'}</Body><Text style={ui.caption}>Requested: acceleration 100 Hz, rotation 100 Hz, magnetic field 50 Hz. Actual rates depend on the phone. No clinical quality validation.</Text><Text style={ui.caption}>Lower-back placement is user instructed, not verified. Direction reminders: {r.guidanceEnabled ? 'on' : 'off'} · {r.guidanceEvents.filter(e => e.type === 'possible-turn').length} possible-turn cues · {r.guidanceEvents.filter(e => e.type === 'possible-handling').length} possible-handling cues · {r.guidanceEvents.filter(e => e.type === 'strong-motion').length} legacy strong-motion cues.</Text>{r.fitCheck && <Text style={ui.caption}>Pre-walk fit motion saved in JSON. Contact, tightness and step count unverified. 10 Hz high-pass acceleration RMS: {r.fitCheck.highPass10HzRmsG === null ? 'unavailable (timing/coverage)' : `${r.fitCheck.highPass10HzRmsG.toFixed(3)} g (research descriptor only)`}.</Text>}<Text style={ui.caption}>{r.baseline ? 'Stationary reference saved separately in JSON. Walking readings are uncorrected.' : 'No saved stationary reference in this recording.'}</Text></> : <Body>This older app generated acceleration. Gyroscope and magnetometer were not recorded.</Body>}
      <Card><Text style={ui.label}>About clinical gait assessment</Text><Body>The G.A.I.T. form needs a trained observer to assess limb and trunk movement during different walking phases. This phone cannot score arm swing, knee or ankle angles, foot clearance or a total G.A.I.T. score.</Body><Text style={ui.caption}>Daly et al., 2009 · doi:10.1016/j.jneumeth.2008.12.016. Phone tilt is not a clinical trunk-angle measurement.</Text></Card>
      <Body muted>Files include recording times and movement data. Choose a trusted recipient in the share menu. JSON includes full metadata and guidance events.</Body>
    </>}
  </Screen>;
}
