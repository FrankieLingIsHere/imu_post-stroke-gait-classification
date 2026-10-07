import React,{useEffect,useState} from 'react';
import {Card,Body,ui} from './Screen';
import {Text,t} from '../i18n';
import BigButton from './BigButton';
import type {SessionRecord} from '../store';
import {cameraVideoAvailable,shareCameraVideo} from '../cameraTrialStorage';
import {shareRecording} from '../export';
export default function CameraTrialReview({session}:{session:SessionRecord}){
  const [available,setAvailable]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
  const [details,setDetails]=useState(false);
  useEffect(()=>{let active=true;void cameraVideoAvailable(session).then(v=>{if(active)setAvailable(v);}).catch(()=>{if(active)setAvailable(false);});return()=>{active=false;};},[session]);
  async function share(video:boolean){if(busy)return;setBusy(true);setError('');try{if(video)await shareCameraVideo(session);else await shareRecording(session,'json');}catch(e){setError(e instanceof Error?e.message:String(e));}finally{setBusy(false);}}
  if(!session.cameraTrial)return null;
  return <Card><Text style={ui.label}>Camera + IMU trial</Text>
    <Text style={ui.caption}>{t('Video attachment: {0}').replace('{0}',t(available?'Saved on this phone':'Unavailable on this device'))}</Text>
    {session.cameraTrial.video.status==='failed'&&<Body>Video capture failed. The IMU JSON can still be exported for diagnostics.</Body>}
    <BigButton label="Export paired camera video" variant="outline" disabled={busy||!available} onPress={()=>void share(true)}/>
    <BigButton label="Export paired IMU and timing JSON" disabled={busy} onPress={()=>void share(false)}/>
    <BigButton label={details?'Close capture details':'Capture details'} variant="ghost" onPress={()=>setDetails(!details)}/>
    {details&&<>
      <Text selectable style={ui.caption}>{session.id}</Text>
      <Body>Camera-frame timestamps and camera/IMU clock calibration are unavailable. This is simultaneous capture, not validated distance or precise frame synchronization.</Body>
      {session.cameraTrial.referenceDistanceM!==null&&<Text style={ui.caption}>{t('Measured reference route: {0} m').replace('{0}',String(session.cameraTrial.referenceDistanceM))}</Text>}
      <Text style={ui.caption}>{t('Capture ended: {0}').replace('{0}',t(session.cameraTrial.end??'interrupted'))}</Text>
    </>}
    {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Card>;
}
