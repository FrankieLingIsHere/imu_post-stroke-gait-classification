import React,{useEffect,useRef,useState} from 'react';
import {AppState,BackHandler,ActivityIndicator,Image,View} from 'react-native';
import {CameraView} from 'expo-camera';
import {useKeepAwake} from 'expo-keep-awake';
import {Screen,Body,ui} from '../components/Screen';
import {Text,t} from '../i18n';
import BigButton from '../components/BigButton';
import {speakQueued,stopSpeaking} from '../audio';
import {calibrationBridge} from '../cameraCalibration';
import {phoneSetupPermission,completePhoneSetup,phoneDistanceProfile} from '../onDeviceSetup';
import {phoneSetupFeedback,setupBeforeInstruction,setupViewInstruction,setupStartInstruction,setupMovementInstruction,setupWaitingMessage,setupRequestedAxis,setupMovementConfirmation,setupMovementsComplete,setupLongWaitInstruction,type SetupFeedback} from '../phoneSetupGuidance';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';

export default function PhoneSetupScreen({navigation}:NativeStackScreenProps<RootStackParamList,'PhoneSetup'>){
 useKeepAwake();const alive=useRef(true),running=useRef(false),motion=useRef(false),cue=useRef<Promise<void>>(Promise.resolve());
 const nativeStarted=useRef(false),nativeCompleted=useRef(false);
 const attempt=useRef(0),capturing=useRef(false),halting=useRef(false),stopping=useRef<Promise<void>>(Promise.resolve());
 const permissionsPending=useRef(false),appState=useRef(AppState.currentState??'active'),resume=useRef<(()=>void)|null>(null);
 const [stage,setStage]=useState<'ready'|'preview'|'capture'|'checking'|'saved'|'failed'|'cancelling'>('ready');
 const [error,setError]=useState('');
 const [announced,setAnnounced]=useState(false);
 const [checkingSaved,setCheckingSaved]=useState(true),[hasSaved,setHasSaved]=useState(false);
 const [stopFailed,setStopFailed]=useState(false);
 const [previewReady,setPreviewReady]=useState(false),[voiceChecking,setVoiceChecking]=useState(false),[captureRetained,setCaptureRetained]=useState(false);
 const [imageUri,setImageUri]=useState(''),[feedback,setFeedback]=useState<SetupFeedback>(()=>phoneSetupFeedback(null,false));
 const guidancePending=useRef(false),lastGuidance=useRef({hint:'',at:0});
 const confirmedAxes=useRef(new Set<number>());
 const movementDone=useRef(false),spokenHints=useRef(new Map<string,number>());
 const lastFeedback=useRef<SetupFeedback>(phoneSetupFeedback(null,false));
 async function sayComplete(text:string){
  let completed=false;
  await speakQueued(text,{onDone:()=>{completed=true;}});
  if(!completed)throw new Error('The voice instruction could not finish. Check your phone voice and try again.');
  console.info('[phone-setup] spoken instruction completed:',text);
 }
 function stopAttempt(){
  const cancelled=++attempt.current;running.current=false;capturing.current=false;permissionsPending.current=false;halting.current=true;resume.current?.();resume.current=null;stopSpeaking();
  stopping.current=Promise.resolve().then(()=>calibrationBridge()?.stop()).then(()=>{}).finally(()=>{if(cancelled===attempt.current)halting.current=false;});
  return {cancelled,task:stopping.current};
 }
 async function interrupt(){
  setStage('cancelling');const {cancelled,task}=stopAttempt();
  try{await task;if(alive.current&&cancelled===attempt.current){setStage('failed');setError('Phone setup was interrupted.');}}
  catch{if(alive.current&&cancelled===attempt.current){setStage('failed');setStopFailed(true);setError('Phone capture could not stop. Close and reopen the app before trying again.');}}
 }
 async function failGuidance(e:unknown,id:number){
  if(id!==attempt.current||!alive.current||!running.current)return;
  setStage('cancelling');const {cancelled,task}=stopAttempt();
  try{await task;if(alive.current&&cancelled===attempt.current){setStage('failed');setError(e instanceof Error?e.message:'Phone setup could not finish.');}}
  catch{if(alive.current&&cancelled===attempt.current){setStage('failed');setStopFailed(true);setError('Phone capture could not stop. Close and reopen the app before trying again.');}}
 }
 useEffect(()=>{alive.current=true;const b=calibrationBridge();const sub=b?.addListener('progress',e=>{
  if(!running.current||!capturing.current||!alive.current)return;
  if(e.imageUri)setImageUri(e.imageUri.replace(/^file:\/(?!\/)/,'file:///'));
  const current=phoneSetupFeedback(e.setupTracking,e.phase==='alignment-move',e.setupSettled,e.setupMovementRemainingMs,e.setupFinalCheck);lastFeedback.current=current;setFeedback(current);
  // Do not overlap the required baseline/movement cue or queue a backlog.
  // New actions follow completed speech; repeat an unchanged action only every 25 seconds.
  const requested=setupRequestedAxis(lastGuidance.current.hint);
  const completed=requested!==null&&current.roomReady&&current.axisReady[requested]&&!confirmedAxes.current.has(requested)?requested:null;
  const allDirections=current.roomReady&&current.movementReady&&!current.fitReady&&!movementDone.current;
  const seen=spokenHints.current.get(current.hint);
  const changed=current.hint!==lastGuidance.current.hint;
  // No endless 25-second repeat: a new blocker is announced immediately,
  // with one later reminder. Coverage completion is a separate one-time cue.
  const shouldSpeak=completed!==null||allDirections||(!current.fitReady&&changed&&e.elapsedSeconds-lastGuidance.current.at>=3 );
  const longWait=!current.fitReady&&seen!==undefined&&e.elapsedSeconds-seen>=60&&e.elapsedSeconds-lastGuidance.current.at>=60&&!spokenHints.current.has('reminder:'+current.reason);
  if(e.phase!=='alignment-cue'&&!guidancePending.current&&(shouldSpeak||longWait)){
   const id=attempt.current;guidancePending.current=true;lastGuidance.current={hint:current.hint,at:e.elapsedSeconds};
   if(seen===undefined)spokenHints.current.set(current.hint,e.elapsedSeconds);
   if(longWait)spokenHints.current.set('reminder:'+current.reason,e.elapsedSeconds);
   cue.current=cue.current.then(async()=>{
    if(id!==attempt.current||!alive.current||!running.current)return;
    if(completed!==null){await sayComplete(setupMovementConfirmation(completed));confirmedAxes.current.add(completed);}
    if(allDirections&&!movementDone.current&&!nativeCompleted.current&&!lastFeedback.current.fitReady){await sayComplete(setupMovementsComplete);movementDone.current=true;}
    if(id===attempt.current&&alive.current&&running.current&&!nativeCompleted.current&&!lastFeedback.current.fitReady){
     if(longWait)await sayComplete(setupLongWaitInstruction);
     if(!nativeCompleted.current&&!lastFeedback.current.fitReady){const fresh=lastFeedback.current;lastGuidance.current.hint=fresh.hint;spokenHints.current.set(fresh.hint,e.elapsedSeconds);await sayComplete(fresh.hint);}
    }
   }).catch(e=>failGuidance(e,id)).finally(()=>{if(id===attempt.current)guidancePending.current=false;});
  }
  if(e.phase==='alignment-cue'&&!motion.current){motion.current=true;
   const id=attempt.current;
   cue.current=sayComplete(setupMovementInstruction).then(async()=>{
    if(id===attempt.current&&running.current&&alive.current){await b?.beginAlignmentMovement?.();lastGuidance.current={hint:'',at:e.elapsedSeconds-25};}
   }).catch(async e=>{
    if(id!==attempt.current||!alive.current)return;
    setStage('cancelling');const {cancelled,task}=stopAttempt();
    try{await task;if(alive.current&&cancelled===attempt.current){setStage('failed');setError(e instanceof Error?e.message:'Phone setup could not finish. Your previous setup is kept.');}}
    catch{if(alive.current&&cancelled===attempt.current){setStage('failed');setStopFailed(true);setError('Phone capture could not stop. Close and reopen the app before trying again.');}}
   });
  }
 });
 void phoneDistanceProfile().then(p=>{if(alive.current)setHasSaved(!!p);}).catch(()=>{if(alive.current)setError('Could not check saved phone setup. Try again.');}).finally(()=>{if(alive.current)setCheckingSaved(false);});
 const app=AppState.addEventListener('change',value=>{
  appState.current=value;
  if(value==='active'){resume.current?.();resume.current=null;}
  // Android's permission activity also pauses our activity. Wait for its return,
  // rather than treating the system prompt as an interrupted camera capture.
  else if(running.current&&!permissionsPending.current)void interrupt();
 });
 const back=BackHandler.addEventListener('hardwareBackPress',()=>{if(halting.current)return true;if(running.current){void interrupt();return true;}return false;});
 return()=>{alive.current=false;sub?.remove();app.remove();back.remove();stopSpeaking();if(running.current)void stopAttempt().task.catch(()=>{});};
 },[]);
 async function start(fromPreview=false){if(running.current||checkingSaved||stopFailed||voiceChecking||stage==='cancelling'||(fromPreview&&!previewReady))return;const id=++attempt.current;running.current=true;permissionsPending.current=true;motion.current=false;movementDone.current=false;spokenHints.current.clear();confirmedAxes.current.clear();cue.current=Promise.resolve();guidancePending.current=false;lastGuidance.current={hint:'',at:0};nativeStarted.current=false;nativeCompleted.current=false;setCaptureRetained(false);setPreviewReady(false);setImageUri('');setFeedback(phoneSetupFeedback(null,false));setError('');setAnnounced(false);setStage('capture');
  try{await stopping.current;if(id!==attempt.current||!alive.current)return;
   const b=fromPreview?calibrationBridge():await phoneSetupPermission();if(!b)throw new Error('Install the updated Android app for on-phone setup.');if(id!==attempt.current||!alive.current||!running.current)return;
   if(appState.current!=='active')await new Promise<void>(resolve=>{resume.current=resolve;});
   if(id!==attempt.current||!alive.current||!running.current)return;permissionsPending.current=false;
   if(!fromPreview){setStage('preview');return;}
   console.info('[phone-setup] permissions ready; app active');
   await sayComplete(setupStartInstruction);
   if(id!==attempt.current||!alive.current||!running.current)return;capturing.current=true;nativeStarted.current=true;
   console.info('[phone-setup] native capture starting');
   const capture=await b.captureOnDeviceSetup!();if(id!==attempt.current||!alive.current||!running.current)return;
   nativeCompleted.current=true;
   await cue.current;
   // The native fit may finish while the requested movement instruction is
   // still speaking. Acknowledge its measured completion before saving too.
   const requested=setupRequestedAxis(lastGuidance.current.hint),finished=lastFeedback.current;
   if(id===attempt.current&&alive.current&&running.current&&requested!==null&&finished.roomReady&&finished.axisReady[requested]&&!confirmedAxes.current.has(requested)){
    guidancePending.current=true;await sayComplete(setupMovementConfirmation(requested));confirmedAxes.current.add(requested);guidancePending.current=false;
   }
   if(id!==attempt.current||!alive.current||!running.current)return;capturing.current=false;setCaptureRetained(!!capture.uri);const m=JSON.parse(capture.metadata);
   console.info('[phone-setup] capture finished',{captureId:m.captureId,status:m.status,frames:m.frames,sensorCounts:m.sensorCounts,startedBootNs:m.startedBootNs,endedBootNs:m.endedBootNs,alignmentMovementStartedBootNs:m.alignmentMovementStartedBootNs,vioBootstrap:m.vioBootstrap});
   if(capture.error||m.status!=='completed'){
    console.warn('[phone-setup] native capture failed',JSON.stringify({captureId:m.captureId,status:m.status,error:capture.error??m.error??null,frames:m.frames,sensorCounts:m.sensorCounts}));
    throw new Error('Phone setup could not finish. Your previous setup is kept.');
   }
   setStage('checking');await completePhoneSetup(m.captureId);
   if(id!==attempt.current||!alive.current||!running.current)return;setHasSaved(true);setStage('saved');await sayComplete('Phone setup saved. You can use it for every participant on this phone.');if(id===attempt.current&&alive.current)setAnnounced(true);
  }catch(e){if(id===attempt.current&&alive.current){console.warn('[phone-setup] setup failed',e instanceof Error?e.message:String(e));setStage(nativeStarted.current?'failed':fromPreview?'preview':'failed');setError((e instanceof Error&&['Install the updated Android app for on-phone setup.','Camera permission is needed for on-phone setup.','The voice instruction could not finish. Check your phone voice and try again.','A quiet baseline was not established. Your saved setup is kept.','Phone tracking did not initialize','Camera and motion tracking lost integrity','Phone calibration has not converged','Tracking uncertainty is too high'].includes(e.message)?e.message:'Phone setup could not finish.').replace(!hasSaved?/ Your (?:previous|saved) setup is kept\./g:/$^/,''));}}
  finally{if(id===attempt.current){running.current=false;capturing.current=false;permissionsPending.current=false;}}
 }
 async function checkVoice(){if(voiceChecking||running.current)return;setVoiceChecking(true);setError('');const id=attempt.current;try{await sayComplete('Listen for this voice during setup.');}catch{if(alive.current&&id===attempt.current)setError('Voice is unavailable. Keep the phone reachable and try the voice sample again.');}finally{if(alive.current&&id===attempt.current)setVoiceChecking(false);}}
 async function cancel(){setStage('cancelling');const {task}=stopAttempt();try{await task;if(alive.current)navigation.goBack();}catch{if(alive.current){setStage('failed');setStopFailed(true);setError('Phone capture could not stop. Close and reopen the app before trying again.');}}}
 return <Screen scrollKey={stage+'-'+!!error} title={stage==='preview'?'Camera and voice':'One-time camera setup'} actions={stage==='preview'?<><BigButton label="Start calibration" disabled={!previewReady||voiceChecking} onPress={()=>void start(true)}/><BigButton label="Back" variant="outline" onPress={()=>{attempt.current++;stopSpeaking();setVoiceChecking(false);setStage('ready');}}/></>:stage==='cancelling'?<BigButton label="Stopping phone capture..." disabled/>:stage==='capture'||stage==='checking'?<BigButton label="Cancel" variant="outline" onPress={()=>void cancel()}/>:stage==='saved'?<BigButton label="Continue" disabled={!announced} onPress={()=>{if(announced)navigation.goBack();}}/>:<>{hasSaved&&<BigButton label="Use saved phone setup" disabled={stopFailed} onPress={()=>navigation.goBack()}/>}<BigButton label={hasSaved?'Set up this phone again':stage==='failed'?'Try again':'Start phone setup'} variant={hasSaved?'outline':'primary'} disabled={checkingSaved||stopFailed} onPress={()=>void start()}/><BigButton label="Back" variant="outline" onPress={()=>navigation.goBack()}/></>}>
  {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  {(stage==='failed'||stage==='preview')&&!!error&&!stopFailed&&<Body>{captureRetained?'This attempt was kept for review.':'Calibration has not been saved.'}</Body>}
  {(stage==='failed'||stage==='preview')&&!!error&&hasSaved&&<Body>Your saved phone setup is still available.</Body>}
  {stage==='ready'&&<>{checkingSaved?<ActivityIndicator/>:hasSaved?<Body>Saved setup matches this phone. Reuse it unless the holder or camera window has changed.</Body>:<><Body>{setupBeforeInstruction}</Body><Body>{setupViewInstruction}</Body></>}</>}
  {stage==='preview'&&<>
   {!error&&<Body>Hold the bagged phone where you can see its screen.</Body>}
   <CameraView facing="front" mute style={{width:'100%',height:180,borderRadius:16}} onCameraReady={()=>setPreviewReady(true)} onMountError={()=>{setPreviewReady(false);setError('Camera preview could not start. Check camera permission and try again.');}} accessibilityLabel={t('Live front camera view')}/>
   <Body>{setupViewInstruction}</Body>
   <BigButton label={voiceChecking?'Playing voice sample…':'Play voice sample'} variant="outline" disabled={voiceChecking} onPress={()=>void checkVoice()}/>
   {!error&&<Text style={ui.caption}>Start when the view is clear and you can hear the voice.</Text>}
  </>}
  {stage==='capture'&&<>
   {!!imageUri&&<Image source={{uri:imageUri}} style={{width:'100%',height:140,borderRadius:16}} resizeMode="contain" accessibilityLabel={t('Live front camera view')}/>}
   <Text style={ui.label}>{t(feedback.movementReady?'Final camera and sensor check':'Follow the voice')}</Text>
   <Body>{feedback.hint}</Body>
   <View>{[['Room tracking',feedback.roomReady],['Gentle movements',feedback.movementReady],['Final check',feedback.fitReady]].map(([label,ready])=><Text key={String(label)} style={ui.caption}>{ready?'✓':'○'} {t(String(label))}: {t(ready?'Complete':'Waiting')}</Text>)}</View>
   <Text style={ui.caption}>{t(setupWaitingMessage)}</Text>
  </>}
  {stage==='checking'&&<><ActivityIndicator size="large"/><Body>Checking this phone. No computer is needed.</Body></>}
  {stage==='cancelling'&&<ActivityIndicator size="large"/>}
  {stage==='saved'&&<Body>Phone setup saved. You can use it for every participant on this phone.</Body>}
 </Screen>;
}
