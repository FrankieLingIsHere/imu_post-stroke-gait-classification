import React,{useEffect,useState} from 'react';
import {UNSTABLE_usePreventRemove as usePreventRemove,CommonActions,type NavigationAction} from '@react-navigation/native';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';
import GaitAssessmentForm from '../components/GaitAssessmentForm';
import {Screen,ui} from '../components/Screen';
import BigButton from '../components/BigButton';
import {Text} from 'react-native';
import {getSession,saveSession,type SessionRecord} from '../store';
import {newGaitAssessment,validGaitAssessment,gaitAssessmentSummary,type GaitAssessment} from '../gaitAssessment';

export default function AssessmentScreen({route,navigation}:NativeStackScreenProps<RootStackParamList,'Assessment'>){
  const [session,setSession]=useState<SessionRecord>(),[form,setForm]=useState<GaitAssessment>(newGaitAssessment);
  const [saving,setSaving]=useState(false),[error,setError]=useState('');
  const [notice,setNotice]=useState('');
  const [dirty,setDirty]=useState(false),[exitAction,setExitAction]=useState<NavigationAction>();
  useEffect(()=>{let active=true;void getSession(route.params.sessionId).then(s=>{if(!active)return;if(!s){setError('Recording not found.');return;}setSession(s);setForm(s.assessment?.gaitAssessment??newGaitAssessment());}).catch(()=>setError('Could not load this recording.'));return()=>{active=false;};},[route.params.sessionId]);
  async function save():Promise<boolean>{
    if(!session||saving)return false;
    if(!validGaitAssessment(form)){setError('Invalid ratings or notes. Review the form before saving.');return false;}
    setSaving(true);setError('');setNotice('');
    try{
      // Re-read so a worker draft cannot overwrite another saved outcome field.
      const latest=await getSession(session.id);if(!latest)throw new Error('Recording not found.');
      const assessment=latest.assessment??{completed:false,completionStatus:'not-completed' as const,timedZoneSeconds:null,distanceWalkedM:null,lapCount:null,restCount:0,perceivedExertion:null,symptoms:'',clinicianNotes:'',observedGaitScore:null,observedGaitScale:'',speedMps:null,distanceSource:'unavailable' as const};
      const updated={...latest,assessment:{...assessment,gaitAssessment:form}};
      await saveSession(updated);setSession(updated);setDirty(false);setNotice(gaitAssessmentSummary(form).complete?'Complete assessment saved on this phone.':'Draft saved on this phone.');return true;
    }catch{setError('Could not save the assessment. Your raw recording remains saved. Please try again.');return false;}
    finally{setSaving(false);}
  }
  usePreventRemove(dirty,({data})=>{void save().then(ok=>{if(ok)setExitAction(data.action);});});
  useEffect(()=>{if(exitAction&&!dirty){setExitAction(undefined);navigation.dispatch(exitAction);}},[exitAction,dirty,navigation]);
  if(!session)return <Screen title="Worker assessment" translateTitle={false}><Text style={ui.caption}>Loading recording…</Text>{!!error&&<><Text style={ui.error}>{error}</Text><BigButton label="Back to recording" translateLabel={false} onPress={()=>navigation.goBack()}/></>}</Screen>;
  return <GaitAssessmentForm key={session.id} value={form} onChange={v=>{setNotice('');setDirty(true);setForm(v);}} saving={saving} error={error} notice={notice} onSave={save} onBack={()=>setExitAction(CommonActions.goBack())}/>;
}
