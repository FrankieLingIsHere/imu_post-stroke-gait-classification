import React, { useEffect, useState } from 'react';
import { View, Pressable } from 'react-native';
import { Text, t, useLanguage } from '../i18n';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import SignalChart from '../components/SignalChart';
import { getSession, SessionRecord, formatSessionDate } from '../store';
import { recordingIssues, SENSOR_NAMES, SENSOR_UNITS, SensorName, streamStats, Sample } from '../recording';
import { shareRecording } from '../export';
import PatientSummary from '../components/PatientSummary';
const labels = { accelerometer: 'Acceleration', gyroscope: 'Rotation', magnetometer: 'Magnetic field' };
export default function DetailsScreen({ route }: NativeStackScreenProps<RootStackParamList, 'Details'>) {
  useLanguage();
  const [session, setSession] = useState<SessionRecord>();
  const [tab, setTab] = useState('Summary');
  const [sensor, setSensor] = useState<SensorName>('accelerometer');
  const [page, setPage] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => { let active = true; setError(''); setLoading(true);
    getSession(route.params.sessionId).then(s => { if (active) { setSession(s); if (!s) setError('This recording could not be found.'); } }).catch(() => { if (active) setError('Could not load the recording. Please try again.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [route.params.sessionId, attempt]);
  const r = session?.recording;
  const legacy: Sample[] = session?.windows.map(s => ({ x: s.x, y: s.y, z: s.z, elapsedMs: s.timestamp - (session.windows[0]?.timestamp ?? 0), receivedAtUnixMs: s.timestamp, sensorTimestampSeconds: null })) ?? [];
  const samples = r ? r.streams[sensor] : sensor === 'accelerometer' ? legacy : [];
  const seconds = r?.elapsedSeconds ?? (legacy.length ? legacy[legacy.length - 1].elapsedMs / 1000 : 0);
  const pages = Math.max(1, Math.ceil(seconds / 5));
  const currentPage = Math.min(page, pages - 1);
  async function share(format: 'csv' | 'json' | 'features') {
    if (!session || busy) return;
    setBusy(true); setError('');
    try { await shareRecording(session, format); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not export. Please try again.'); }
    finally { setBusy(false); }
  }
  return <Screen eyebrow={session ? session.isPractice ? 'PRACTICE RECORDING' : 'YOUR RECORDING' : 'YOUR RECORDING'} title={session ? formatSessionDate(session.date) : 'Recording details'} actions={<><View style={ui.row}>
    <BigButton style={ui.fill} label="Export CSV" disabled={!session || busy} onPress={() => share('csv')} />
    <BigButton style={ui.fill} label="Export JSON" variant="outline" disabled={!session || busy} onPress={() => share('json')} />
  </View><BigButton label="Export features CSV" variant="outline" disabled={!session || busy} onPress={() => share('features')} /></>}>
    <View style={[ui.row, { flexWrap: 'wrap' }]}>{['Summary', 'Signals', 'Sensors', 'Notes'].map(t => <Pressable key={t} accessibilityRole="tab" accessibilityState={{ selected: tab === t }} style={[ui.choice, { flexBasis: '44%' }, tab === t && ui.selected]} onPress={() => setTab(t)}><Text style={ui.caption}>{t}</Text></Pressable>)}</View>
    {loading && <Body>Loading recording…</Body>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
    {!loading && !session && <BigButton label="Retry loading" onPress={() => setAttempt(attempt + 1)} />}
    {session && !r && <Text style={ui.error}>Older simulated recording · not patient sensor data</Text>}
    {session && tab === 'Summary' && <>
      {r ? <PatientSummary recording={r} /> : <Body>No gait summary is calculated from older simulated recordings.</Body>}
    </>}
    {session && tab === 'Signals' && <>
      <View style={ui.row}>{SENSOR_NAMES.map((n, i) => <Pressable key={n} accessibilityRole="tab" accessibilityLabel={t(n)} accessibilityState={{ selected: sensor === n }} onPress={() => { setSensor(n); setPage(0); }} style={[ui.choice, sensor === n && ui.selected]}><Text style={ui.caption}>{['Accel', 'Gyro', 'Mag'][i]}</Text></Pressable>)}</View>
      <Card><Text style={ui.label}>{labels[sensor]} · {SENSOR_UNITS[sensor]}</Text><Text style={ui.caption}>Showing {currentPage * 5}–{Math.min((currentPage + 1) * 5, seconds).toFixed(1)} seconds after recording started</Text><SignalChart samples={samples} start={currentPage * 5} end={Math.min((currentPage + 1) * 5, seconds)} units={SENSOR_UNITS[sensor]} /></Card>
      <View style={ui.row}><BigButton style={ui.fill} label="Previous 5 sec" variant="outline" disabled={currentPage === 0} onPress={() => setPage(currentPage - 1)} /><BigButton style={ui.fill} label="Next 5 sec" variant="outline" disabled={currentPage + 1 >= pages} onPress={() => setPage(currentPage + 1)} /></View>
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
      <Card><Text style={ui.label}>{seconds.toFixed(1)} seconds captured</Text><Body>{session.duration} seconds planned · {r ? r.stopReason.replace(/-/g, ' ') : 'Legacy simulation'}</Body><Text style={ui.caption}>Time includes any standing or pauses.</Text></Card>
      {r ? <><Body>{recordingIssues(r).length ? recordingIssues(r).join('\n') : 'All streams received; no gaps above 0.25 seconds detected.'}</Body><Text style={ui.caption}>Requested: acceleration 100 Hz, rotation 100 Hz, magnetic field 50 Hz. Actual rates depend on the phone. No clinical quality validation.</Text><Text style={ui.caption}>Lower-back placement is user instructed, not verified. Direction reminders: {r.guidanceEnabled ? 'on' : 'off'} · {r.guidanceEvents.filter(e => e.type === 'possible-turn').length} possible-turn cues · {r.guidanceEvents.filter(e => e.type === 'possible-handling').length} possible-handling cues · {r.guidanceEvents.filter(e => e.type === 'strong-motion').length} legacy strong-motion cues.</Text>{r.fitCheck && <Text style={ui.caption}>Pre-walk fit motion saved in JSON. Contact, tightness and step count unverified. 10 Hz high-pass acceleration RMS: {r.fitCheck.highPass10HzRmsG === null ? 'unavailable (timing/coverage)' : `${r.fitCheck.highPass10HzRmsG.toFixed(3)} g (research descriptor only)`}.</Text>}<Text style={ui.caption}>{r.baseline ? 'Stationary reference saved separately in JSON. Walking readings are uncorrected.' : 'No saved stationary reference in this recording.'}</Text></> : <Body>This older app generated acceleration. Gyroscope and magnetometer were not recorded.</Body>}
      <Card><Text style={ui.label}>About clinical gait assessment</Text><Body>The G.A.I.T. form needs a trained observer to assess limb and trunk movement during different walking phases. This phone cannot score arm swing, knee or ankle angles, foot clearance or a total G.A.I.T. score.</Body><Text style={ui.caption}>Daly et al., 2009 · doi:10.1016/j.jneumeth.2008.12.016. Phone tilt is not a clinical trunk-angle measurement.</Text></Card>
      <Body muted>Files include recording times and movement data. Choose a trusted recipient in the share menu. JSON includes full metadata and guidance events.</Body>
    </>}
  </Screen>;
}
