import React,{useEffect,useState} from 'react';
import { BackHandler } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Text,t } from '../i18n';
import { Screen,Card,Body,ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { checkGoogleApi,type GoogleApiCheck } from '../googleApiCheck';
import { checkGoogleRecordingPermission,googleRecordingBridge } from '../googleRecordingBridge';

export default function GoogleApiCheckScreen({navigation}:NativeStackScreenProps<RootStackParamList,'GoogleApiCheck'>){
  const [busy,setBusy]=useState(false),[result,setResult]=useState<GoogleApiCheck>(),[error,setError]=useState('');
  useEffect(()=>{const back=BackHandler.addEventListener('hardwareBackPress',()=>busy);return()=>back.remove();},[busy]);
  async function run(){
    if(busy)return;setBusy(true);setResult(undefined);setError('');
    try{
      await checkGoogleRecordingPermission();const bridge=googleRecordingBridge();
      if(!bridge)throw new Error('Google distance test needs the new Android APK. Turn it off to continue.');
      const value=await checkGoogleApi(bridge);setResult(value);
      // Technical diagnostics only: no profile, coordinates or gait recording.
      console.info('GaitGoogleApiCheck',JSON.stringify(value));
    }catch(e){setError(e instanceof Error?e.message:String(e));}
    finally{setBusy(false);}
  }
  return <Screen title="Quick Google API check" eyebrow="RESEARCH TOOL · NOT A CLINICAL TEST" actions={<>
    <BigButton label={busy?'Checking Google API…':'Run API check'} loading={busy} disabled={busy} onPress={()=>void run()}/>
    <BigButton label="Back to home" variant="outline" disabled={busy} onPress={()=>navigation.goBack()}/>
  </>}>
    <Body>Keep the phone connected. No walking, placement check or participant profile is needed.</Body>
    <Body>This checks subscription, read requests and cleanup. There is no countdown or deliberate waiting period. Each request has a timeout.</Body>
    <Body>You may move the phone gently, but waving is not walking. It cannot validate distance or step accuracy.</Body>
    {result&&<Card>
      <Text style={ui.label}>{result.apiAccess==='passed'?'API access passed':'API access check failed'}</Text>
      <Body>{result.recordsAvailable?'Google returned context records. These are not the distance of a walking test.':'No records returned. An empty successful response does not mean API access failed or zero walking.'}</Body>
      <Text style={ui.caption}>{t('Subscription: {0}').replace('{0}',t(result.subscription))}</Text>
      {result.reads.map((read,i)=><Text key={i} style={ui.caption}>{t('Last {0} seconds: {1} records · {2}').replace('{0}',String(read.windowSeconds)).replace('{1}',read.recordCount===null?t('Not available'):String(read.recordCount)).replace('{2}',t(read.error?'failed':'passed'))}</Text>)}
      <Text style={ui.caption}>{t('Cleanup: {0}').replace('{0}',t(result.cleanup))}</Text>
      {result.errors.map((detail,i)=><Text key={i} style={ui.caption}>{detail}</Text>)}
    </Card>}
    <Body muted>This check does not save a gait recording, score movement or prove that Google can measure a short walk.</Body>
    {!!error&&<Text accessibilityRole="alert" style={ui.error}>{t(error)}</Text>}
  </Screen>;
}
