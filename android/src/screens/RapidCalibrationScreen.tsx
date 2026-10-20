import React,{useEffect,useRef,useState} from 'react';
import {AppState,BackHandler,Image,Modal,Pressable,View} from 'react-native';
import {CameraView,useCameraPermissions} from 'expo-camera';
import {useKeepAwake} from 'expo-keep-awake';
import * as Sharing from 'expo-sharing';
import {Screen,Body,ui} from '../components/Screen';
import BigButton from '../components/BigButton';
import {Text,t} from '../i18n';
import {speakQueued,stopSpeaking} from '../audio';
import {calibrationBridge,retainCalibrationCapture,type CalibrationCapture} from '../cameraCalibration';
import {calibrationComputer,connectCalibrationComputer,createLensFeedback,type CalibrationComputer} from '../referenceCalibration';
import {activateRapid,exportRapid,latestRapid,pendingRapid,pollRapid,rapidReady,savedRapidResult,submitRapid} from '../rapidCalibration';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';

/** Researcher enrollment, separate from patient walking and from validated calibration. */
export default function RapidCalibrationScreen(props:NativeStackScreenProps<RootStackParamList,'RapidCalibration'>){
 useKeepAwake();const [permission,requestPermission]=useCameraPermissions();
 const b=useRef(calibrationBridge()),alive=useRef(true),running=useRef(false),cue=useRef(false),pairing=useRef(false);
 const voice=useRef<Promise<void>>(Promise.resolve()),feedback=useRef<ReturnType<typeof createLensFeedback>|null>(null);
 const [computer,setComputer]=useState<CalibrationComputer|null>(null),[scanning,setScanning]=useState(false),[busy,setBusy]=useState(false),[processing,setProcessing]=useState(false);
 const [capture,setCapture]=useState<CalibrationCapture|null>(null),[pending,setPending]=useState(false),[result,setResult]=useState<any>(null),[bag,setBag]=useState(true);
 const [hint,setHint]=useState('Connect your computer, then scan the room once.'),[image,setImage]=useState(''),[error,setError]=useState('');
 function say(message:string){const task=voice.current.then(async()=>{if(!running.current||!alive.current)return;let completed=false;await speakQueued(message,{onDone:()=>{completed=true;}});if(!completed&&running.current)throw new Error('Voice guidance could not finish. Please retry.');});voice.current=task;return task;}
 function cancel(){running.current=false;feedback.current?.close();feedback.current=null;stopSpeaking();void b.current?.stop();}
 useEffect(()=>{alive.current=true;void calibrationComputer().then(v=>{if(alive.current)setComputer(v);});void latestRapid().then(v=>{if(alive.current)setCapture(v);});void pendingRapid().then(v=>{if(alive.current)setPending(!!v);});void savedRapidResult().then(v=>{if(alive.current)setResult(v);});
  const listener=b.current?.addListener('progress',e=>{
   if(!running.current||!alive.current)return;setImage(e.imageUri);
   const message=e.phase==='alignment-move'?'Keep the scene in view. Capture stops automatically.':'Hold the bagged phone still, with the camera facing the room.';
   setHint(message);feedback.current?.send({acceptedViews:0,hint:t(message),status:'checking'},e.imageUri);
   if(e.phase==='alignment-cue'&&!cue.current){cue.current=true;setHint('Move in small loops; tilt left, right, up and down.');
    void say('Stillness captured. Now move the bagged phone in small loops. Tilt left, right, up and down. Keep furniture in view.').then(async()=>{if(running.current&&alive.current)await b.current?.beginAlignmentMovement?.();}).catch(()=>{setError('Voice guidance could not finish. Please retry.');cancel();});
   }
  });
  const back=BackHandler.addEventListener('hardwareBackPress',()=>running.current);
  const app=AppState.addEventListener('change',state=>{if(state!=='active'&&running.current)cancel();});
  return()=>{alive.current=false;cancel();listener?.remove();back.remove();app.remove();};
 },[]);
 function showError(e:unknown){const known=['Restart the computer helper for quick calibration.','Install the updated Android app for quick calibration.','Could not send the capture. It is saved on this phone.','Capture incomplete. Your previous profile is kept.','Quick calibration did not pass import checks.','Processing unavailable. Your previous profile is kept.','Retry in a brighter room with furniture in view.','Retry with gentle loops and tilts in all directions.','The views disagree. Retry with clearer scene views.','Processing could not finish. Export this attempt for review.'];const message=e instanceof Error?e.message:'';setError(known.includes(message)?message:'Could not finish. Your capture and previous profile are kept.');}
 async function scan(){try{const p=permission?.granted?permission:await requestPermission();if(!p.granted){setError('Camera permission is required for this trial.');return;}setScanning(true);}catch(e){showError(e);}}
 async function pair(code:string){if(pairing.current)return;pairing.current=true;try{const c=await connectCalibrationComputer(code);await rapidReady(c);setComputer(c);setError('');}catch(e){showError(e);}finally{setScanning(false);pairing.current=false;}}
 async function process(record?:CalibrationCapture){if(!computer)return;
  setProcessing(true);setImage('');setHint('Processing on your computer. You can put the phone down.');
  if(record){await submitRapid(computer,record);if(alive.current)setPending(true);}
  const value=await pollRapid(computer,()=>!running.current||!alive.current);if(value&&alive.current){setResult(value);setPending(false);setHint('Experimental profile ready. Check a measured walk before relying on distance.');await say('Capture checked. An experimental phone profile is ready.');}
 }
 async function run(mode:'new'|'retry'|'resume'){
  if(running.current||!computer)return;running.current=true;cue.current=false;voice.current=Promise.resolve();setBusy(true);setError('');setProcessing(false);
  try{
   await rapidReady(computer);
   if(mode!=='new'){await process(mode==='retry'?capture??undefined:undefined);return;}
   if(!b.current?.captureRapidCalibration||!b.current.beginAlignmentMovement)throw new Error('Install the updated Android app for quick calibration.');
   const p=permission?.granted?permission:await requestPermission();if(!p.granted){setError('Camera permission is required for this trial.');return;}
   setResult(null);feedback.current=createLensFeedback(computer,true);
   setHint('Hold the bagged phone still, with the camera facing the room.');await say('Hold the bagged phone still, with the camera facing the room. Follow the voice until capture finishes.');if(!running.current)return;
   const value=await b.current.captureRapidCalibration(bag?'waist-bag-window':'clear-lens');const record=await retainCalibrationCapture(value);if(alive.current)setCapture(record);
   await voice.current;if(!running.current||!alive.current)return;
   if(value.error||JSON.parse(value.metadata).status!=='completed')throw new Error('Capture incomplete. Your previous profile is kept.');
   await say('Capture finished. You can put the phone down while your computer checks it.');if(running.current)await process(record);
  }catch(e){if(alive.current)showError(e);}finally{running.current=false;feedback.current?.close();feedback.current=null;if(alive.current){setBusy(false);setProcessing(false);}}
 }
 async function useProfile(){if(busy||running.current||!result)return;setBusy(true);try{const info=await b.current?.phoneCalibrationInfo?.();if(!info)throw Error();await activateRapid(result,{...JSON.parse(info),captureId:result.binding.captureId,opticalSetup:result.binding.opticalSetup});setHint('Experimental profile selected. Walking tests run on this phone.');}catch(e){showError(e);}finally{setBusy(false);}}
 async function share(){if(!await Sharing.isAvailableAsync()){setError('File sharing is unavailable here.');return;}try{const uri=result?await exportRapid(result):capture?.uri;if(uri)await Sharing.shareAsync(uri,{mimeType:'application/zip',dialogTitle:t('Export enrollment bundle')});}catch(e){showError(e);}}
 return <Screen title="Quick phone setup" eyebrow="EXPERIMENTAL" actions={<>
  <BigButton label={busy?(processing?'Leave processing':'Cancel capture'):!computer?'Connect computer':pending?'Resume quick processing':'Capture scene and sensors'} onPress={busy?cancel:!computer?()=>void scan():()=>void run(pending?'resume':'new')} variant={busy?'outline':'primary'}/>
  {!busy&&result&&<BigButton label="Use experimental profile" variant="outline" onPress={()=>void useProfile()}/>}
  <BigButton label="Back to home" variant="ghost" disabled={busy} onPress={()=>props.navigation.goBack()}/>
 </>}>
  <Body>{hint}</Body>
  {!busy&&<><Body>About one minute of guided capture. No board. One-time computer processing.</Body>
   <Pressable accessibilityRole="checkbox" accessibilityState={{checked:bag}} style={ui.choice} onPress={()=>setBag(!bag)}><Text>{bag?'✓ ':''}{t('Capture through the usual waist-bag window')}</Text></Pressable>
   {computer&&<BigButton label="Reconnect computer" variant="ghost" onPress={()=>void scan()}/>}
   {capture&&!result&&<BigButton label="Retry saved capture" variant="outline" onPress={()=>void run('retry')}/>}
   {(capture||result)&&<BigButton label="Export enrollment bundle" variant="outline" onPress={()=>void share()}/>}
  </>}
  {busy&&!!image&&<Image source={{uri:image}} style={{width:'100%',height:220}} resizeMode="contain"/>}
  {!!error&&<Text style={ui.error}>{error}</Text>}
  <Modal visible={scanning} onRequestClose={()=>setScanning(false)}><View style={{flex:1,padding:20}}><Body>Point the front camera at the code on your computer.</Body><CameraView style={{flex:1}} facing="front" barcodeScannerSettings={{barcodeTypes:['qr']}} onBarcodeScanned={e=>void pair(e.data)}/><BigButton label="Cancel" variant="outline" onPress={()=>setScanning(false)}/></View></Modal>
 </Screen>;
}
