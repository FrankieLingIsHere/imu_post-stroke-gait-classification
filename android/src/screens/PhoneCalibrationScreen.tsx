import React,{useEffect,useRef,useState} from 'react';
import {AppState,BackHandler,Image,Pressable,Modal,View} from 'react-native';
import {useCameraPermissions,CameraView} from 'expo-camera';
import * as FileSystem from 'expo-file-system';
import {useKeepAwake} from 'expo-keep-awake';
import * as Sharing from 'expo-sharing';
import {Screen,Body,ui} from '../components/Screen';
import {colours as c} from '../theme';
import BigButton from '../components/BigButton';
import {Text,t} from '../i18n';
import {speakQueued,stopSpeaking} from '../audio';
import {calibrationBridge,currentLensReport,recoverLensReport,retainCalibrationCapture} from '../cameraCalibration';
import {calibrationComputer,connectCalibrationComputer,showComputerBoard,createLensFeedback,submitAlignment,pollReference,pendingReference,savedReference,type CalibrationComputer} from '../referenceCalibration';
import {lensGuidance,lensPreparation,tabletLensPreparation,type LensMode} from '../lensGuidance';
import CameraCalibrationScreen from './CameraCalibrationScreen';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';

/** Phone-only published lens calibration. Never equates a lens fit with VIO readiness. */
export default function PhoneCalibrationScreen(props:NativeStackScreenProps<RootStackParamList,'CameraCalibration'>){
 useKeepAwake();const [permission,requestPermission]=useCameraPermissions();
 const bridge=useRef(calibrationBridge()),alive=useRef(true),running=useRef(false);
 const [busy,setBusy]=useState(false),[image,setImage]=useState(''),[error,setError]=useState(''),[ready,setReady]=useState(false);
 const [views,setViews]=useState(0),[hint,setHint]=useState('Point the front camera at the digital board.'),[bag,setBag]=useState(true),[legacy,setLegacy]=useState(false);
 const voiceBusy=useRef(false),voicePromise=useRef<Promise<void>|null>(null),lastVoice=useRef(''),lastVoiceTime=useRef(0);
 const [computer,setComputer]=useState<CalibrationComputer|null>(null),[scanning,setScanning]=useState(false),[processing,setProcessing]=useState(false),[pending,setPending]=useState(false),[referenceSaved,setReferenceSaved]=useState(false);
 const stage=useRef<'lens'|'alignment'|'processing'>('lens'),alignmentCue=useRef(false),pairing=useRef(false);
 const feedback=useRef<ReturnType<typeof createLensFeedback>|null>(null),viewCount=useRef(0);
 const [mode,setMode]=useState<LensMode>('computer'),modeRef=useRef<LensMode>('computer');
 const [configuring,setConfiguring]=useState(false);
 useEffect(()=>{alive.current=true;
  void calibrationComputer().then(v=>{if(alive.current)setComputer(v);});void pendingReference().then(v=>{if(alive.current)setPending(!!v);});
  const progress=bridge.current?.addListener('progress',e=>{
   if(!alive.current||!running.current)return;
   if(stage.current==='alignment'){
    setImage(e.imageUri);
    if(e.phase==='alignment-still')setHint('Hold the phone still in its bag.');
    if(e.phase==='alignment-cue'&&!alignmentCue.current){alignmentCue.current=true;setHint('Move the phone gently in small loops and tilt it in different directions.');
     voicePromise.current=sayComplete('Move the phone gently in small loops and tilt it in different directions.').then(async()=>{if(running.current&&alive.current)await bridge.current?.beginAlignmentMovement?.();}).catch(e=>{setError(e.message);void bridge.current?.stop();});
    }
    if(e.phase==='alignment-move')setHint('Continue gentle loops and tilts. The app will stop automatically.');
    return;
   }
   if(e.phase!=='lens'||!e.lens)return;
   try{const p=JSON.parse(e.lens),cue=lensGuidance(p.hint,modeRef.current);setImage(e.imageUri);setViews(p.acceptedViews);viewCount.current=p.acceptedViews;setHint(cue);
    feedback.current?.send({acceptedViews:p.acceptedViews,hint:t(cue),status:'checking'},e.imageUri);
    if(!p.lensReady&&!voiceBusy.current&&cue!==lastVoice.current&&Date.now()-lastVoiceTime.current>8000){
     voiceBusy.current=true;lastVoice.current=cue;lastVoiceTime.current=Date.now();
     voicePromise.current=speakQueued(cue).finally(()=>{voiceBusy.current=false;});
    }
   }catch{setError('Could not read calibration progress.');}
  });
  const app=AppState.addEventListener('change',state=>{if(state!=='active'&&running.current){running.current=false;stopSpeaking();void bridge.current?.stop();}});
  const back=BackHandler.addEventListener('hardwareBackPress',()=>running.current);
  return()=>{alive.current=false;feedback.current?.close();progress?.remove();app.remove();back.remove();stopSpeaking();if(running.current)void bridge.current?.stop();};
 },[]);
 useEffect(()=>{let cancelled=false;setReady(false);setReferenceSaved(false);
  void bridge.current?.phoneCalibrationInfo?.().then(async value=>{
   const binding={...JSON.parse(value),opticalSetup:bag?'waist-bag-window':'clear-lens'};
   const report=await currentLensReport(binding),reference=await savedReference(report);if(!cancelled&&alive.current){setReady(!!report);setReferenceSaved(!!reference);}
  }).catch(()=>{/* Optional factory values never imply a verified profile. */});
  return()=>{cancelled=true;};
 },[bag]);
 async function sayComplete(text:string){let completed=false;await speakQueued(text,{onDone:()=>{completed=true;}});if(!completed&&running.current)throw new Error('Voice guidance did not finish. Please try again.');}
 async function start(){if(running.current)return;setError('');
  if(!bridge.current?.captureGuidedLens){setError('Camera calibration needs the new Android APK.');return;}
  running.current=true;setBusy(true);setImage('');setViews(0);viewCount.current=0;
  feedback.current?.close();feedback.current=computer?createLensFeedback(computer):null;
  try{
   const p=permission?.granted?permission:await requestPermission();if(!p.granted)throw new Error('Camera permission is required for this trial.');
   stage.current='lens';
   if(mode==='computer'&&!computer)throw new Error('Connect the computer before starting the lens check.');
   modeRef.current=mode;
   if(computer&&bridge.current.digitalCalibrationBoard){const uri=await bridge.current.digitalCalibrationBoard();await showComputerBoard(computer,await FileSystem.readAsStringAsync(uri),mode);}
   setHint('Preparing capture.');
   const preparation=mode==='computer'?lensPreparation:tabletLensPreparation;
   feedback.current?.send({acceptedViews:0,hint:t(preparation),status:'checking'});
   await sayComplete(preparation);
   if(!running.current)return;
   lastVoice.current='';lastVoiceTime.current=Date.now();
   const result=await bridge.current.captureGuidedLens(bag?'waist-bag-window':'clear-lens');
   const record=await retainCalibrationCapture(result);
   // The native solver saves atomically; a failed attempt keeps the prior profile.
   const report=await recoverLensReport(record);
   if(!alive.current)return;
   if(voicePromise.current)await voicePromise.current;
   setError(result.error??'');
   const finished=report?'Lens parameters saved. Sensor alignment is still needed.':'This attempt was not completed. Your previous lens profile is kept.';
   setHint(finished);if(report){setReady(true);setReferenceSaved(false);}
   feedback.current?.send({acceptedViews:viewCount.current,hint:t(finished),status:report?'completed':'failed'});
   if(running.current)await sayComplete(finished);
  }catch(e){feedback.current?.send({acceptedViews:viewCount.current,hint:t('This attempt was not completed. Your previous lens profile is kept.'),status:'failed'});if(alive.current)setError(e instanceof Error?e.message:String(e));}
  finally{running.current=false;if(alive.current)setBusy(false);}
 }
 function cancel(){running.current=false;if(stage.current==='lens')feedback.current?.send({acceptedViews:viewCount.current,hint:t('Capture stopped.'),status:'stopped'});stopSpeaking();void bridge.current?.stop();}
 async function openScanner(){setError('');try{const p=permission?.granted?permission:await requestPermission();if(!p.granted)throw new Error('Camera permission is required for this trial.');setScanning(true);}catch(e){setError(e instanceof Error?e.message:String(e));}}
 async function pair(code:string){if(pairing.current)return;pairing.current=true;try{
  const value=await connectCalibrationComputer(code);setComputer(value);setScanning(false);setError('');
  if(bridge.current?.digitalCalibrationBoard){const uri=await bridge.current.digitalCalibrationBoard();await showComputerBoard(value,await FileSystem.readAsStringAsync(uri),mode);}
  await speakQueued('Calibration computer connected.');
 }catch(e){setError(e instanceof Error?e.message:String(e));setScanning(false);}finally{pairing.current=false;}}
 async function processSaved(){if(!computer||running.current)return;running.current=true;setBusy(true);setProcessing(true);stage.current='processing';setHint('Processing calibration on your computer.');setError('');setImage('');
  try{const result=await pollReference(computer,()=>!running.current||!alive.current);if(result&&alive.current){setReferenceSaved(true);setPending(false);setHint('Reference parameters saved. Research review is still needed.');if(running.current)await sayComplete('Reference parameters saved. Research review is still needed.');}}
  catch(e){if(alive.current)setError(e instanceof Error?e.message:String(e));}
  finally{running.current=false;if(alive.current){setBusy(false);setProcessing(false);}}
 }
 async function align(){if(running.current||!computer)return;setError('');
  if(!bridge.current?.captureAlignment||!bridge.current.beginAlignmentMovement){setError('Camera calibration needs the new Android APK.');return;}
  running.current=true;stage.current='alignment';alignmentCue.current=false;setBusy(true);setProcessing(false);setImage('');
  try{
   const p=permission?.granted?permission:await requestPermission();if(!p.granted)throw new Error('Camera permission is required for this trial.');
   await sayComplete('Hold the phone still in its bag, with the front camera facing the room.');if(!running.current)return;
   const result=await bridge.current.captureAlignment(bag?'waist-bag-window':'clear-lens');const record=await retainCalibrationCapture(result);
   if(!alive.current)return;if(voicePromise.current)await voicePromise.current;
   if(!running.current)return;
   stage.current='processing';setProcessing(true);setImage('');setHint('Transferring calibration to your computer.');
   await sayComplete('Movement capture finished. You can put the phone down.');
   if(!running.current)return;await submitAlignment(computer,record);setPending(true);setHint('Processing calibration on your computer.');
   const report=await pollReference(computer,()=>!running.current||!alive.current);
   if(report&&alive.current){setReferenceSaved(true);setPending(false);setHint('Reference parameters saved. Research review is still needed.');if(running.current)await sayComplete('Reference parameters saved. Research review is still needed.');}
  }catch(e){if(alive.current)setError(e instanceof Error?e.message:String(e));}
  finally{running.current=false;if(alive.current){setBusy(false);setProcessing(false);}}
 }
 async function shareBoard(){try{
  if(!bridge.current?.digitalCalibrationBoard)throw new Error('Camera calibration needs the new Android APK.');
  if(!await Sharing.isAvailableAsync())throw new Error('File sharing is unavailable here.');
  await Sharing.shareAsync(await bridge.current.digitalCalibrationBoard(),{mimeType:'text/html',dialogTitle:t('Share digital board')});
 }catch(e){setError(e instanceof Error?e.message:String(e));}}
 async function changeMode(){if(configuring||running.current)return;const next=mode==='computer'?'tablet':'computer';setMode(next);modeRef.current=next;setError('');setConfiguring(true);
  try{if(computer&&bridge.current?.digitalCalibrationBoard){const uri=await bridge.current.digitalCalibrationBoard();await showComputerBoard(computer,await FileSystem.readAsStringAsync(uri),next);}}
  catch(e){if(alive.current)setError(e instanceof Error?e.message:String(e));}finally{if(alive.current)setConfiguring(false);}
 }
 if(legacy)return <CameraCalibrationScreen {...props} navigation={{...props.navigation,goBack:()=>setLegacy(false)}}/>;
 return <Screen title="Phone calibration" eyebrow="RESEARCHER SETUP" actions={<>
  <BigButton label={busy?(processing?'Leave processing':'Cancel capture'):pending&&computer?'Resume calibration processing':ready&&computer?'Align camera and sensors':ready?'Repeat lens check':'Calibrate camera lens'} disabled={configuring} variant={busy?'outline':'primary'} onPress={busy?cancel:pending&&computer?()=>void processSaved():ready&&computer?()=>void align():()=>void start()}/>
  <BigButton label="Back to home" variant="ghost" disabled={busy} onPress={()=>props.navigation.goBack()}/>
 </>}>
  <Body>{busy?hint:referenceSaved?'Reference parameters saved. Research review is still needed.':ready?'Lens parameters are saved on this phone.':mode==='computer'?'Use your computer screen as the board. No tablet is needed.':'Rest the bagged phone securely. Face the tablet board toward its front camera.'}</Body>
  {!busy&&<>
   <Body>{mode==='computer'?'Watch the framing on your computer while moving the phone. Saved views are kept if the board leaves view.':'Move the tablet, not the phone. If the board leaves view, bring it back; saved views are kept.'}</Body>
   {!computer&&<BigButton label="Connect calibration computer" variant="outline" onPress={()=>void openScanner()}/>}
   <BigButton label={mode==='computer'?'Use a tablet instead':'Use computer screen instead'} disabled={configuring} variant="ghost" onPress={()=>void changeMode()}/>
   {mode==='tablet'&&<BigButton label="Share digital board" variant="ghost" onPress={()=>void shareBoard()}/>}
   {ready&&computer&&<BigButton label="Repeat lens check" variant="outline" disabled={configuring} onPress={()=>void start()}/>}
   {computer&&<Body>Calibration computer connected. Walking tests stay on your phone.</Body>}
   <Pressable accessibilityRole="checkbox" accessibilityState={{checked:bag}} onPress={()=>setBag(!bag)} style={{padding:12,borderWidth:2,borderRadius:12,borderColor:c.primary}}><Text>{bag?'[x] ':'[ ] '}{t('Capture through the usual waist-bag window')}</Text></Pressable>
   <Body>{ready?'Sensor alignment is still needed before camera distance can be measured.':'The app chooses clear views and saves the lens parameters automatically.'}</Body>
  </>}
  {!!image&&busy&&<Image source={{uri:image}} style={{width:'100%',height:230}} resizeMode="contain"/>}
  {busy&&stage.current==='lens'&&<Text style={ui.label}>{`Clear views saved: ${views}`}</Text>}
  {!busy&&<Pressable accessibilityRole="button" onPress={()=>setLegacy(true)} style={{padding:14}}><Text>Research capture tools</Text></Pressable>}
  {!!error&&<Text style={ui.error}>{t(error)}</Text>}
  {!!error&&!busy&&computer&&<BigButton label="Reconnect computer" variant="outline" onPress={()=>void openScanner()}/>}
  <Modal visible={scanning} onRequestClose={()=>setScanning(false)}><View style={{flex:1,backgroundColor:c.surface,padding:20}}><Body>Point the front camera at the code on your computer.</Body><CameraView style={{flex:1}} facing="front" barcodeScannerSettings={{barcodeTypes:['qr']}} onBarcodeScanned={e=>{void pair(e.data);}}/><BigButton label="Cancel" variant="outline" onPress={()=>setScanning(false)}/></View></Modal>
 </Screen>;
}
