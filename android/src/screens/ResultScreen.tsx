import React, { useEffect, useState } from 'react';
import { Text } from '../i18n';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { getSession, SessionRecord } from '../store';
import { recordingIssues } from '../recording';
import PatientSummary from '../components/PatientSummary';
export default function ResultScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Result'>) {
  const [session, setSession] = useState<SessionRecord>();
  const [error, setError] = useState('');
  useEffect(() => { getSession(route.params.sessionId).then(setSession).catch(() => setError('Could not load details. Open My recordings to try again.')); }, [route.params.sessionId]);
  const r = session?.recording;
  const issues = r ? recordingIssues(r) : [];
  return <Screen eyebrow="STEP 4 · FINISHED" title="Your walk is saved" actions={<>
    <BigButton label="View summary & signals" onPress={() => navigation.navigate('Details', route.params)} />
    <BigButton label="Back to home" variant="outline" onPress={() => navigation.popToTop()} />
  </>}>
    {r?.platform === 'web' && <Body>Browser recording: export before refreshing or closing this tab. Sensor timing and rates may differ from Android.</Body>}
    {r ? <PatientSummary recording={r} /> : <Body>Loading recording details…</Body>}
    {issues.length > 0 && <Body muted>Saved with recording notes</Body>}
    {!!error && <Text style={ui.error}>{error}</Text>}
  </Screen>;
}
