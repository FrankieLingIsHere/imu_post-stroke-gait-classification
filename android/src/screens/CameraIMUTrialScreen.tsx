import React,{useEffect,useRef,useState} from 'react';
import {AppState,BackHandler,Platform,Pressable,TextInput,View} from 'react-native';
import {CameraView,useCameraPermissions} from 'expo-camera';
import {useKeepAwake} from 'expo-keep-awake';
import * as FileSystem from 'expo-file-system';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';
import {Screen,Card,Body,ui} from '../components/Screen';
import BigButton from '../components/BigButton';
import {Text,t} from '../i18n';
import {speakQueued,stopSpeaking} from '../audio';
import {SensorRecorder,checkSensors} from '../sensors';
import {recordingIssues,type Recording} from '../recording';
import {generateSessionId,saveSession,type SessionRecord} from '../store';
import {CameraTrialCapture,cameraFinishCue,type CameraStage,type CameraTrial} from '../cameraTrial';
import {saveCameraTrial} from '../cameraTrialStorage';
import CameraTrialReview from '../components/CameraTrialReview';
import {colours} from '../theme';

export default function CameraIMUTrialScreen({navigation}:NativeStackScreenProps<RootStackParamList,'CameraIMUTrial'>){
  useKeepAwake();
  const [permission,requestPermission]=useCameraPermissions();
  const camera=useRef<CameraView>(null),capture=useRef<CameraTrialCapture>(),alive=useRef(true),pending=useRef<SessionRecord>(),videoUri=useRef<string|null>(null),starting=useRef(false);
  const [ready,setReady]=useState(false),[stage,setStage]=useState<CameraStage>('idle'),[busy,setBusy]=useState(false),[seconds,setSeconds]=useState<15|30|60>(60),[reference,setReference]=useState(''),[error,setError]=useState(''),[saved,setSaved]=useState<SessionRecord>();
  const [options,setOptions]=useState(false);
  const [rawSaved,setRawSaved]=useState(false),[slowVideo,setSlowVideo]=useState(false);
  const active=['placing','cue','waiting','walking','finishing'].includes(stage);
  useEffect(()=>{if(stage!=='finishing')return;const timer=setTimeout(()=>setSlowVideo(true),15000);return()=>clearTimeout(timer);},[stage]);
  const say=(text:string)=>new Promise<void>((resolve,reject)=>{void speakQueued(text,{onDone:resolve,onStopped:()=>reject(new Error('Voice guidance failed. The partial capture will be saved.')),onError:()=>reject(new Error('Voice guidance failed. The partial capture will be saved.'))});});
  const warn=(message:string)=>{if(alive.current)setError(message);};
  async function saveFinal(){
    if(!pending.current)return;
    const result=await saveCameraTrial(pending.current,videoUri.current);pending.current=result;if(alive.current){setSaved(result);setError('');}
  }
  useEffect(()=>{
    alive.current=true;
    const interval=setInterval(()=>capture.current?.tick(),200);
    const listener=AppState.addEventListener('change',state=>{if(state!=='active'){capture.current?.finish('interrupted');stopSpeaking();}});
    const back=BackHandler.addEventListener('hardwareBackPress',()=>!!capture.current&&['placing','cue','waiting','walking','finishing'].includes(capture.current.stage));
    return()=>{alive.current=false;clearInterval(interval);listener.remove();back.remove();stopSpeaking();capture.current?.finish('interrupted');};
  },[]);
  async function allowCamera(){setError('');try{const p=await requestPermission();if(!p.granted)setError('Camera permission is required for this trial.');}catch{setError('Could not open the camera permission request.');}}
  async function start(){
    if(starting.current||!ready||!permission?.granted||active)return;
    const meters=reference.trim()?Number(reference):null;
    if(meters!==null&&(!Number.isFinite(meters)||meters<=0||meters>1000)){setError('Enter a positive measured reference distance, or leave it blank.');return;}
    starting.current=true;setBusy(true);setError('');
    try{
      await checkSensors();if(!alive.current||AppState.currentState!=='active')return;
      const free=await FileSystem.getFreeDiskStorageAsync();if(free<200*1024*1024)throw new Error('Free at least 200 MB of phone storage before this camera trial.');
      if(!camera.current)throw new Error('The front camera is not ready.');
      const view=camera.current,engine=new SensorRecorder({guidanceEnabled:false,voiceEnabled:true},()=>{}),id=generateSessionId();
      const sessionFor=(recording:Recording,trial:CameraTrial):SessionRecord=>({id,date:recording.startedAt,duration:seconds,isPractice:true,quality:recordingIssues(recording).length?'repeat':'good',windowCount:0,windows:[],recording,cameraTrial:trial});
      capture.current=new CameraTrialCapture({engine,camera:view,walkingSeconds:seconds,referenceDistanceM:meters,now:()=>performance.now(),say,
        onStage:next=>{if(alive.current)setStage(next);},onError:warn,
        onCaptureEnded:end=>{if(!alive.current||AppState.currentState!=='active'||end==='interrupted')return;stopSpeaking();void speakQueued(end==='quiet-stop'?cameraFinishCue:'Stop walking. Recording has stopped.',{onError:()=>warn('Capture stopped, but the stop instruction could not play.')});},
        onStopped:async(recording,trial)=>{pending.current=sessionFor(recording,trial);await saveSession(pending.current);if(alive.current)setRawSaved(true);},
        onDone:async(recording,trial,uri)=>{pending.current=sessionFor(recording,trial);videoUri.current=uri;await saveFinal();}});
      capture.current.start();
    }catch(e){warn(e instanceof Error?e.message:String(e));}
    finally{starting.current=false;if(alive.current)setBusy(false);}
  }
  async function retrySave(){setBusy(true);setError('');try{await saveFinal();}catch(e){warn(e instanceof Error?e.message:String(e));}finally{setBusy(false);}}
  function stop(){stopSpeaking();capture.current?.finish('user-stopped');}
  const captions:Record<CameraStage,string>={idle:'Mark a short route, then tap Start.',placing:'Place the phone. Stand still.',cue:'Wait for the start cue.',waiting:'Begin walking now.',walking:'Walk to the finish, then stand still.',finishing:'Saving your recording.',done:'Your recording is ready.'};
  return <Screen title="Camera + IMU trial" eyebrow="RESEARCH TOOL · NOT A CLINICAL TEST" actions={<>
    {!permission?.granted&&<BigButton label="Allow front camera" disabled={busy} onPress={()=>void allowCamera()}/>}
    {stage==='idle'&&permission?.granted&&<BigButton label="Start paired capture" loading={busy} disabled={!ready||busy} onPress={()=>void start()}/>}
    {['placing','cue','waiting','walking'].includes(stage)&&<BigButton label="Stop and save partial capture" variant="outline" onPress={stop}/>}
    {stage==='done'&&!saved&&pending.current&&<BigButton label="Retry save" loading={busy} onPress={()=>void retrySave()}/>}
    <BigButton label="Back to home" variant="ghost" disabled={(active&&!(stage==='finishing'&&rawSaved&&slowVideo))||busy} onPress={()=>navigation.goBack()}/>
  </>}>
    <Body>{captions[stage]}</Body>
    {permission?.granted&&Platform.OS==='android'&&stage!=='done'&&<View style={{height:210,borderRadius:16,overflow:'hidden'}}><CameraView ref={camera} style={{flex:1}} facing="front" mode="video" mute mirror={false} zoom={0} videoQuality="720p" onCameraReady={()=>setReady(true)} onMountError={()=>{setReady(false);warn('The front camera could not start.');capture.current?.finish('interrupted');}}/></View>}
    {stage==='idle'&&<>
      <BigButton label={options?'Close trial settings':'Trial settings'} variant="ghost" disabled={busy} onPress={()=>setOptions(!options)}/>
      {options&&<Card><Text style={ui.label}>Recording limit</Text><View style={ui.row}>{([15,30,60] as const).map(s=><Pressable key={s} accessibilityRole="radio" aria-checked={seconds===s} accessibilityState={{selected:seconds===s}} disabled={busy} style={[ui.choice,seconds===s&&ui.selected]} onPress={()=>{setSeconds(s);}}><Text>{s} s</Text></Pressable>)}</View><Text style={ui.caption}>Optional measured reference distance (m)</Text><TextInput accessibilityLabel={t('Optional measured reference distance (m)')} editable={!busy} value={reference} onChangeText={setReference} keyboardType="decimal-pad" style={{minHeight:48,borderWidth:1,borderColor:colours.border,borderRadius:12,padding:12,fontSize:18}}/></Card>}
    </>}
    {!!error&&<Text accessibilityRole="alert" style={ui.error}>{t(error)}</Text>}
    {stage==='finishing'&&rawSaved&&slowVideo&&<Body>Sensor data is saved. The video is still finalizing; you may return to recordings and check the attachment later.</Body>}
    {saved&&<CameraTrialReview session={saved}/>}
  </Screen>;
}
