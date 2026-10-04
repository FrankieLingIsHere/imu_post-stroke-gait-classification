import {gaitAssessmentSummary} from '../gaitAssessment';
import React, { useCallback, useState } from 'react';
import { Pressable, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { Text, t } from '../i18n';
import { getParticipants, getSessions, getSession, ParticipantProfile, SessionRecord } from '../store';
import { formatSessionDate } from '../store';
import Svg, { Circle, Polyline } from 'react-native-svg';
import { colours } from '../theme';
export default function DashboardScreen({ navigation }: NativeStackScreenProps<RootStackParamList,'Dashboard'>) {
  const [profiles,setProfiles]=useState<ParticipantProfile[]>([]); const [sessions,setSessions]=useState<SessionRecord[]>([]); const [selected,setSelected]=useState<string|null>(null); const [error,setError]=useState('');
  const load=useCallback(()=>{
    let active=true;
    void (async()=>{
      try{
        const [p,s]=await Promise.all([getParticipants(),getSessions()]);
        const summaries:SessionRecord[]=[];
        for(const row of s){
          if(!active)return;
          // Older indexes omitted the raw-recording flag. Read one file at a time;
          // retain only summaries so six-minute streams do not accumulate in memory.
          const device=row.hasDeviceRecording??(row.recording?row.recording.source==='device':(await getSession(row.id))?.recording?.source==='device');
          const {recording,windows,...summary}=row;
          summaries.push({...summary,windows:[],hasDeviceRecording:device});
        }
        if(active){setProfiles(p);setSessions(summaries);setError('');}
      }catch(e){if(active)setError(e instanceof Error?e.message:'Could not load the recording. Please try again.');}
    })();
    return()=>{active=false;};
  },[]);

  useFocusEffect(load);
  const person=profiles.find(p=>p.id===selected); const rows=sessions.filter(s=>selected ? s.participantId===selected : !s.participantId||!profiles.some(p=>p.id===s.participantId));
  const protocolName=(s:SessionRecord)=>s.assessmentSetup?.protocol?.toUpperCase()??'RESEARCH WALK';
  const score=(s:SessionRecord)=>{const a=s.assessment;if(!a)return null;const speed=a.speedMps,dist=a.distanceWalkedM,g=a.gaitAssessment?gaitAssessmentSummary(a.gaitAssessment):null;return [g?.total!=null?t('G.A.I.T. total: {0} / 62').replace('{0}',String(g.total)):null,speed!==null?`${speed.toFixed(2)} m/s`:null,dist!==null?`${dist.toFixed(1)} m`:null,a.timedZoneSeconds!==null?`${a.timedZoneSeconds.toFixed(2)} s`:null].filter(Boolean).join(' · ')||null;};
  const latestSession=rows.filter(s=>!s.isPractice&&s.hasDeviceRecording===true).sort((a,b)=>b.date.localeCompare(a.date))[0];
  const latestProtocol=latestSession?.assessmentSetup?.protocol;
  const latestAid=latestSession?.participantSnapshot?.clinical.assistiveDevice;
  const speeds=rows.filter(s=>!!latestProtocol&&!!latestAid&&!!latestSession?.assessmentSetup?.courseLengthM&&!s.isPractice&&s.hasDeviceRecording===true&&s.assessmentSetup?.protocol===latestProtocol&&s.assessmentSetup?.courseLengthM===latestSession?.assessmentSetup?.courseLengthM&&s.participantSnapshot?.clinical.assistiveDevice===latestAid&&s.assessment?.distanceSource==='measured-course'&&s.assessment.speedMps!==null).sort((a,b)=>a.date.localeCompare(b.date)).slice(-12);
  const values=speeds.map(s=>s.assessment!.speedMps!); const min=Math.min(...values), max=Math.max(...values), span=Math.max(max-min,0.05);
  const points=values.map((v,i)=>`${16+i*(268/Math.max(values.length-1,1))},${94-((v-min)/span)*76}`).join(' ');
  return <Screen title="Progress dashboard" eyebrow="LOCAL PARTICIPANT HISTORY" actions={<><BigButton label="Manage participants" variant="outline" onPress={()=>navigation.navigate('Participants')}/><BigButton label="Back to home" variant="ghost" onPress={()=>navigation.popToTop()}/></>}>
    <Body>Choose a participant to review their recorded assessments and clinician-entered outcomes.</Body>
    <BigButton label="Needs participant assignment" variant={selected===null?'primary':'outline'} onPress={()=>setSelected(null)}/>
    <Text style={ui.caption}>All recordings remain visible. Practice and simulated recordings are excluded from measured progress trends.</Text>
    {profiles.length>0&&<View style={[ui.row,{flexWrap:'wrap'}]}>{profiles.map(p=><Pressable key={p.id} accessibilityRole="radio" accessibilityState={{selected:selected===p.id}} style={[ui.choice,{flexBasis:120},selected===p.id&&ui.selected]} onPress={()=>setSelected(p.id)}><Text>{selected===p.id?'● ':'○ '}{p.label}{p.archived?' ('+t('Archived')+')':''}{p.favorite?' ★':''}</Text></Pressable>)}</View>}
    {!!error&&<Text style={ui.error}>{error}</Text>}
    {(person||selected===null)&&<>{person&&<Card><Text style={ui.label}>{person.label}</Text><Body>{person.demographics.ageYears??'—'} y · {person.demographics.heightCm??'—'} cm · Usual aid: {person.clinical.assistiveDevice.replace(/-/g,' ')}</Body><Body>{rows.length} assessment{rows.length===1?'':'s'} saved on this device.</Body></Card>}
      {rows.map(s=><Pressable key={s.id} onPress={()=>navigation.navigate('Details',{sessionId:s.id})}><Card><Text style={ui.label}>{s.googleDistanceTrial?t('Google distance trial'):protocolName(s)} · {formatSessionDate(s.date)}</Text><Text style={ui.caption}>{s.isPractice?'Practice':!s.hasDeviceRecording?'Legacy simulation':'Assessment'}</Text><Body>{score(s)??'No clinician-entered distance/time outcome yet'}</Body><Text style={ui.caption}>{s.assessment?.completionStatus??'Assessment form incomplete'} · {s.assessment?.restCount??0} rests</Text></Card></Pressable>)}
      {!rows.length&&<Body>No recordings in this selection.</Body>}
    </>}
    {person&&speeds.length>=2&&<Card><Text style={ui.label}>Measured speed trend · {latestProtocol?.toUpperCase()}</Text><Svg width="100%" height={120} viewBox="0 0 300 110" accessibilityLabel="Measured walking speed history"><Polyline points={points} fill="none" stroke={colours.primary} strokeWidth={3}/>{values.map((v,i)=><Circle key={`${i}-${v}`} cx={16+i*(268/Math.max(values.length-1,1))} cy={94-((v-min)/span)*76} r={4} fill={colours.primary}/>)}</Svg><Body>{values[0].toFixed(2)} m/s → {values[values.length-1].toFixed(2)} m/s. Descriptive only; course and aid must also be considered.</Body></Card>}
    {selected===null&&<Body>Open an unassigned recording to confirm its participant. Create a profile first if needed.</Body>}
  </Screen>;
}
