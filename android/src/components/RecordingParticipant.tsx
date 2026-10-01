import React, { useState } from 'react';
import { Modal, TextInput } from 'react-native';
import { Screen, Body, ui } from './Screen';
import BigButton from './BigButton';
import { Text, t } from '../i18n';
import { getParticipants, linkSessionParticipant, type ParticipantProfile, type SessionRecord } from '../store';

export default function RecordingParticipant({session,onLinked,onCreate}:{session:SessionRecord;onLinked:(s:SessionRecord)=>void;onCreate:()=>void}) {
  const [open,setOpen]=useState(false),[profiles,setProfiles]=useState<ParticipantProfile[]>([]);
  const [search,setSearch]=useState(''),[selected,setSelected]=useState<ParticipantProfile|null>(null);
  const [error,setError]=useState(''),[busy,setBusy]=useState(false);
  async function show(){
    setError('');setSelected(null);setSearch('');setBusy(true);
    try{setProfiles((await getParticipants()).filter(p=>!p.archived));setOpen(true);}
    catch{setError('Could not load participants. Try again.');}finally{setBusy(false);}
  }
  async function confirm(){
    if(!selected||busy)return;setBusy(true);setError('');
    try{onLinked(await linkSessionParticipant(session.id,selected.id));setOpen(false);}
    catch{setError('Could not link recording. Try again.');}finally{setBusy(false);}
  }
  return <>
    <Text style={ui.label}>{session.participantId ? t('Participant: {0}').replace('{0}',session.participantLabel||session.participantId):t('Needs participant assignment')}</Text>
    {!session.participantId&&<BigButton label="Assign recording to participant" variant="outline" loading={busy} onPress={()=>void show()}/>}
    {!!error&&!open&&<Text style={ui.error}>{error}</Text>}
    <Modal visible={open} animationType="slide" onRequestClose={()=>{if(!busy)setOpen(false);}}>
      <Screen fullScreen title="Assign recording to participant" actions={<>
        <BigButton label="Confirm participant" disabled={!selected} loading={busy} onPress={()=>void confirm()}/>
        <BigButton label="Cancel" variant="outline" disabled={busy} onPress={()=>setOpen(false)}/>
      </>}>
        <Body>Choose only if you know whose recording this is. Age and sex do not identify a person. Original recording measurements stay unchanged.</Body>
        <TextInput accessibilityLabel={t('Search saved participants')} placeholder={t('Search saved participants')} value={search} onChangeText={setSearch} style={{minHeight:52,fontSize:18,borderWidth:1,borderRadius:12,padding:12}}/>
        {profiles.filter(p=>p.label.toLocaleLowerCase().includes(search.toLocaleLowerCase())).map(p=><BigButton key={p.id} label={p.label} icon={selected?.id===p.id?'●':'○'} variant={selected?.id===p.id?'primary':'outline'} disabled={busy} onPress={()=>setSelected(p)}/>)}
        <BigButton label="Create participant, then return here" variant="outline" disabled={busy} onPress={()=>{setOpen(false);onCreate();}}/>
        {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
      </Screen>
    </Modal>
  </>;
}
