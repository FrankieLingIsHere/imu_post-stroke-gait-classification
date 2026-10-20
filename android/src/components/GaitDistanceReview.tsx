import React,{useEffect,useState} from 'react';
import {Platform} from 'react-native';
import {Text,t} from '../i18n';
import {Card,Body,ui} from './Screen';
import BigButton from './BigButton';
import {getSessions,type SessionRecord} from '../store';
import {processGaitDistance,gaitDistanceArchive} from '../gaitDistance';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
export default function GaitDistanceReview({session}:{session:SessionRecord}){
 const [a,setAttachment]=useState(session.cameraDistance),[busy,setBusy]=useState(false),[error,setError]=useState('');
 useEffect(()=>{
  let active=true;
  const reload=()=>getSessions().then(rows=>{if(active)setAttachment(rows.find(s=>s.id===session.id)?.cameraDistance);}).catch(()=>{});
  const timer=setInterval(()=>void reload(),3000);void reload();
  if(Platform.OS==='android')void processGaitDistance(session.id).catch(()=>{});
  return()=>{active=false;clearInterval(timer);};
 },[session.id]);
 async function resume(){setBusy(true);setError('');try{await processGaitDistance(session.id);}catch(e){setError(e instanceof Error?t(e.message):t('Distance processing is unavailable. The recording stays on this phone.'));}finally{setBusy(false);}}
 async function shareCapture(){setBusy(true);setError('');try{const uri=gaitDistanceArchive(session.id);if(!(await FileSystem.getInfoAsync(uri)).exists)throw new Error('The camera archive is missing. Motion data is kept.');if(!await Sharing.isAvailableAsync())throw new Error('Sharing is unavailable on this device.');await Sharing.shareAsync(uri,{mimeType:'application/zip',dialogTitle:t('Export camera/IMU ZIP')});}catch(e){setError(e instanceof Error?t(e.message):t('Could not export. Please try again.'));}finally{setBusy(false);}}
 if(!a)return null;
 const live=a.binding.capturePipeline==='native-camera-imu-v3';
 const z=a.result?.testOutcome;
 return <Card><Text style={ui.label}>{live?'Phone distance':'Camera distance (experimental)'}</Text>
  <Body>{t(a.status==='capturing'?'Saving synchronized camera capture.':a.status==='processing'?'This phone is calculating distance. Keep the app open.':a.status==='saved'?'Saved on this phone. Distance can be calculated here without a computer.':a.status==='complete'?'Complete tracking passed the integrity checks.':'Camera tracking could not provide a complete distance. Motion data is kept.')}</Body>
  {a.distanceM!==null&&<Body>{t('Tracked course distance: {0} m').replace('{0}',a.distanceM.toFixed(2))}</Body>}
  {a.protocol==='10mwt'?<>
   <Text style={ui.caption}>12 m course: 1 m to build pace, 10 m for measurement, 1 m to slow down.</Text>
   {z?.status==='experimental'?<Body>{t('Estimated central 10 m: {0} s, {1} m/s').replace('{0}',z.timedZoneSeconds.toFixed(2)).replace('{1}',z.speedMps.toFixed(2))}</Body>:<Text style={ui.caption}>Central 10 m speed is unavailable until a complete estimated 12 m path is tracked.</Text>}
   <Text style={ui.caption}>{live?'The phone stops at its estimated 12 m crossing. Floor-mark timing still needs independent verification.':'Estimated crossings are calculated afterwards. They are not verified floor crossings or live stop triggers.'}</Text>
  </>:a.meanSpeedMps!==null&&<Body>{t('Whole-test mean speed: {0} m/s (rests included)').replace('{0}',a.meanSpeedMps.toFixed(2))}</Body>}
  <Text style={ui.caption}>One rule: complete tracking and integrity checks must pass. Otherwise distance is unavailable; no substitute estimate is shown.</Text>
  {a.status==='unavailable'&&<Text style={ui.caption}>{t('Tracking note: {0}').replace('{0}',t(a.reason))}</Text>}
  {Platform.OS==='android'&&['saved','processing'].includes(a.status)&&<BigButton label={a.status==='processing'?'Resume distance processing':'Calculate saved distance'} loading={busy} disabled={busy} variant="outline" onPress={()=>void resume()}/>}
  {Platform.OS==='android'&&a.status!=='capturing'&&<BigButton label="Export camera/IMU ZIP" variant="ghost" disabled={busy} onPress={()=>void shareCapture()}/>}
  <Text style={ui.caption}>Research estimate only. G.A.I.T. assessment and observed test outcomes remain separate.</Text>
  {!!error&&<Text style={ui.error}>{error}</Text>}
 </Card>;
}
