import React,{useCallback,useState} from 'react';
import {Alert,Platform} from 'react-native';
import {useFocusEffect} from '@react-navigation/native';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';
import {Screen,Body,ui} from '../components/Screen';
import BigButton from '../components/BigButton';
import {Text,t,useLanguage} from '../i18n';
import {clearRecordedData,getSessions} from '../store';
import {recordingStorageBytes} from '../recordingStorage';

export default function StorageScreen({navigation}:NativeStackScreenProps<RootStackParamList,'Storage'>){
 useLanguage();const [count,setCount]=useState(0),[bytes,setBytes]=useState(0),[busy,setBusy]=useState(false),[error,setError]=useState(''),[done,setDone]=useState(false);
 const refresh=useCallback(()=>{let alive=true;void Promise.all([getSessions(),recordingStorageBytes()]).then(([s,b])=>{if(alive){setCount(s.length);setBytes(b);}}).catch(()=>{if(alive)setError('Could not read storage.');});return()=>{alive=false;};},[]);
 useFocusEffect(refresh);
 async function remove(){setBusy(true);setError('');setDone(false);try{await clearRecordedData();setCount(0);setBytes(await recordingStorageBytes());setDone(true);}catch{setError('Deletion did not finish. Please retry; some files may remain.');}finally{setBusy(false);}}
 function confirm(){const body=t('Permanently delete all recordings, videos, research captures and app export copies? There is no undo.');
  if(Platform.OS==='web'){if(window.confirm(body))void remove();}
  else Alert.alert(t('Delete recorded data?'),body,[{text:t('Cancel'),style:'cancel'},{text:t('Delete permanently'),style:'destructive',onPress:()=>void remove()}]);}
 return <Screen title="Storage" actions={<><BigButton label={busy?'Deleting...':'Delete all recorded data'} variant="outline" disabled={busy} onPress={confirm}/><BigButton label="Back to home" variant="ghost" disabled={busy} onPress={()=>navigation.popToTop()}/></>}>
  <Body>{t('{0} recordings').replace('{0}',String(count))}</Body>
  {Platform.OS!=='web'&&<Body>{t('Recording files: {0} MB').replace('{0}',(bytes/1048576).toFixed(1))}</Body>}
  <Body>Participant profiles and saved phone calibration are kept.</Body>
  <Body muted>Files already shared to Downloads, other apps or your computer must be deleted there separately.</Body>
  {done&&<Body>Recorded data deleted. No app backup was kept.</Body>}
  {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
 </Screen>;
}
