import React, { useMemo, useState } from 'react';
import { View, Pressable } from 'react-native';
import type { Recording } from '../recording';
import { describeMovement } from '../movement';
import { patientSummary } from '../patientSummary';
import { Text, t } from '../i18n';
import { Card, Body, ui } from './Screen';

export default function PatientSummary({ recording }: { recording: Recording }) {
  const [page, setPage] = useState(0);
  const observations = useMemo(() => patientSummary(describeMovement(recording), recording.guidanceEvents.some(e => e.type === 'possible-placement-shift')), [recording]);
  const selected = Math.min(page, observations.length - 1);
  return <>
    <Text style={ui.label}>What this walk tells you</Text>
    {observations.length > 1 && <View style={ui.row}>{observations.map((item, index) => <Pressable key={item.title} accessibilityRole="tab" accessibilityLabel={t(item.title)} accessibilityState={{ selected: index === selected }} onPress={() => setPage(index)} style={[ui.choice, index === selected && ui.selected]}><Text style={ui.label}>{['Pauses', 'Rhythm', 'Changes'][index]}</Text></Pressable>)}</View>}
    <Card><Text style={ui.label}>{observations[selected].title}</Text><Body>{observations[selected].text}</Body></Card>
    <Text style={ui.caption}>These observations describe movement, not a diagnosis or a score of your walking ability.</Text>
    <Text style={ui.label}>For your next review</Text>
    <Text style={ui.caption}>Share this recording together with how the walk felt: any rests, turns, discomfort, or help you used. The phone cannot confirm these experiences.</Text>
  </>;
}
