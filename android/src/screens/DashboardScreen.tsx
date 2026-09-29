import React, { useCallback, useState } from 'react';
import { Pressable, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { Text } from '../i18n';
import { getParticipants, getSessions, ParticipantProfile, SessionRecord } from '../store';
import { formatSessionDate } from '../store';
import Svg, { Circle, Polyline } from 'react-native-svg';
import { colours } from '../theme';
export default function DashboardScreen({ navigation }: NativeStackScreenProps<RootStackParamList,'Dashboard'>) {
  const [profiles,setProfiles]=useState<ParticipantProfile[]>([]); const [sessions,setSessions]=useState<SessionRecord[]>([]); const [selected,setSelected]=useState<string|null>(null); const [error,setError]=useState('');
  const load=useCallback(()=>{let active=true;Promise.all([getParticipants(),getSessions()]).then(([p,s])=>{if(active){setProfiles(p.filter(x=>!x.archived));setSessions(s);if(!selected&&p.length)setSelected(p[0].id);}}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[selected]);
  useFocusEffect(load);
  const person=profiles.find(p=>p.id===selected); const rows=sessions.filter(s=>s.participantId===selected&&!s.isPractice);
  const protocolName=(s:SessionRecord)=>s.assessmentSetup?.protocol?.toUpperCase()??'RESEARCH WALK';
  const score=(s:SessionRecord)=>{const a=s.assessment;if(!a)return null;const speed=a.speedMps,dist=a.distanceWalkedM;return [speed!==null?`${speed.toFixed(2)} m/s`:null,dist!==null?`${dist.toFixed(1)} m`:null,a.timedZoneSeconds!==null?`${a.timedZoneSeconds.toFixed(2)} s`:null].filter(Boolean).join(' · ')||null;};
  const latestSession=[...rows].sort((a,b)=>b.date.localeCompare(a.date))[0];
  const latestProtocol=latestSession?.assessmentSetup?.protocol;
  const latestAid=latestSession?.participantSnapshot?.clinical.assistiveDevice;
  const speeds=rows.filter(s=>s.assessmentSetup?.protocol===latestProtocol&&s.assessmentSetup?.courseLengthM===latestSession?.assessmentSetup?.courseLengthM&&s.participantSnapshot?.clinical.assistiveDevice===latestAid&&s.assessment?.distanceSource==='measured-course'&&s.assessment.speedMps!==null).sort((a,b)=>a.date.localeCompare(b.date)).slice(-12);
  const values=speeds.map(s=>s.assessment!.speedMps!); const min=Math.min(...values), max=Math.max(...values), span=Math.max(max-min,0.05);
  const points=values.map((v,i)=>`${16+i*(268/Math.max(values.length-1,1))},${94-((v-min)/span)*76}`).join(' ');
  return <Screen title="Progress dashboard" eyebrow="LOCAL PARTICIPANT HISTORY" actions={<><BigButton label="Manage participants" variant="outline" onPress={()=>navigation.navigate('Participants')}/><BigButton label="Back to home" variant="ghost" onPress={()=>navigation.popToTop()}/></>}>
    <Body>Choose a participant to review their recorded assessments and clinician-entered outcomes.</Body>
    {profiles.length>0&&<View style={[ui.row,{flexWrap:'wrap'}]}>{profiles.map(p=><Pressable key={p.id} style={[ui.choice,selected===p.id&&ui.selected]} onPress={()=>setSelected(p.id)}><Text>{p.label}{p.favorite?' ★':''}</Text></Pressable>)}</View>}
    {!!error&&<Text style={ui.error}>{error}</Text>}
    {person&&<><Card><Text style={ui.label}>{person.label}</Text><Body>{person.demographics.ageYears??'—'} y · {person.demographics.heightCm??'—'} cm · Usual aid: {person.clinical.assistiveDevice.replace(/-/g,' ')}</Body><Body>{rows.length} assessment{rows.length===1?'':'s'} saved on this device.</Body></Card>
      {rows.map(s=><Pressable key={s.id} onPress={()=>navigation.navigate('Details',{sessionId:s.id})}><Card><Text style={ui.label}>{protocolName(s)} · {formatSessionDate(s.date)}</Text><Body>{score(s)??'No clinician-entered distance/time outcome yet'}</Body><Text style={ui.caption}>{s.assessment?.completionStatus??'Assessment form incomplete'} · {s.assessment?.restCount??0} rests</Text></Card></Pressable>)}
      {!rows.length&&<Body>No assessments linked to this participant yet. Select them in Participants before starting.</Body>}
    </>}
    {person&&speeds.length>=2&&<Card><Text style={ui.label}>Measured speed trend · {latestProtocol?.toUpperCase()}</Text><Svg width="100%" height={120} viewBox="0 0 300 110" accessibilityLabel="Measured walking speed history"><Polyline points={points} fill="none" stroke={colours.primary} strokeWidth={3}/>{values.map((v,i)=><Circle key={`${i}-${v}`} cx={16+i*(268/Math.max(values.length-1,1))} cy={94-((v-min)/span)*76} r={4} fill={colours.primary}/>)}</Svg><Body>{values[0].toFixed(2)} m/s → {values[values.length-1].toFixed(2)} m/s. Descriptive only; course and aid must also be considered.</Body></Card>}
    {!person&&<Body>Add a participant profile before using the dashboard.</Body>}
  </Screen>;
}
