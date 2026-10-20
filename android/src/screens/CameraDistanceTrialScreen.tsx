import React,{useEffect,useRef,useState} from 'react';
import {AppState,BackHandler,Image,Pressable,View} from 'react-native';
import {CameraView,useCameraPermissions} from 'expo-camera';
import {useKeepAwake} from 'expo-keep-awake';
import * as Sharing from 'expo-sharing';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';
import {Screen,Body,ui} from '../components/Screen';
import BigButton from '../components/BigButton';
import {Text,t,useLanguage} from '../i18n';
import {speakQueued,stopSpeaking} from '../audio';
import type {CalibrationCapture} from '../cameraCalibration';
import {calibrationComputer,connectCalibrationComputer,type CalibrationComputer} from '../referenceCalibration';
import {distanceReference,distanceComputerReady,pendingDistanceValidation,savedDistanceValidation,submitDistanceValidation,pollDistanceValidation,retainValidationRoute,validationRoute,validationGeometry,distanceResultFile} from '../distanceValidation';
import {releaseInfo} from '../releaseInfo';
import {distanceBridge,retainDistanceTrial,latestDistanceTrial,type DistanceProgress} from '../cameraDistanceTrial';

export default function CameraDistanceTrialScreen({navigation}:NativeStackScreenProps<RootStackParamList,'CameraDistanceTrial'>){
 useKeepAwake();useLanguage();const [permission,requestPermission]=useCameraPermissions();
 const bridge=useRef(distanceBridge()),alive=useRef(true),running=useRef(false),cueStarted=useRef(false),warmupCueStarted=useRef(false),cancelled=useRef(false),scanBusy=useRef(false);
 const [busy,setBusy]=useState(false),[phase,setPhase]=useState('ready'),[image,setImage]=useState(''),[error,setError]=useState('');
 const [reference,setReference]=useState<any>(null),[computer,setComputer]=useState<CalibrationComputer|null>(null),[scanning,setScanning]=useState(false);
 const [saved,setSaved]=useState<CalibrationCapture|null>(null),[result,setResult]=useState<any>(null),[pending,setPending]=useState(false),[metres,setMetres]=useState(3);
 const [geometry,setGeometry]=useState('straight');
 const say=(text:string)=>new Promise<void>((resolve,reject)=>{void speakQueued(text,{onDone:resolve,onStopped:()=>reject(new Error('Voice guidance failed. The partial capture will be saved.')),onError:()=>reject(new Error('Voice guidance failed. The partial capture will be saved.'))});});
 useEffect(()=>{
  alive.current=true;
  void Promise.all([distanceReference(),calibrationComputer(),latestDistanceTrial(),pendingDistanceValidation()]).then(async([r,c,s,p])=>{
   const report=await savedDistanceValidation(s),route=await validationRoute(s),shape=await validationGeometry(s);if(alive.current){setReference(r);setComputer(c);setSaved(s);setResult(report);setPending(!!p);setMetres(report?.referenceDistanceMetres??p?.referenceMetres??route);setGeometry(report?.routeGeometry??p?.routeGeometry??shape);}
  }).catch(()=>{if(alive.current)setError('Could not read the distance trial setup.');});
  const listener=bridge.current?.addListener('progress',(e:DistanceProgress)=>{
   if(!alive.current||!running.current)return;setPhase(e.phase);setImage(e.imageUri);
   if(e.phase==='warmup-cue'&&!warmupCueStarted.current){warmupCueStarted.current=true;
    void say('Take a few comfortable practice steps, turn and return to your start mark. Then stand still. This is practice, not the measured walk.').then(async()=>{if(running.current&&alive.current&&!cancelled.current)await bridge.current?.beginDistanceWarmup?.();}).catch(e=>{if(alive.current)setError(e.message);void bridge.current?.stop();});
   }
   if(e.phase==='cue'&&!cueStarted.current){cueStarted.current=true;
    void say('Practice complete. The measured walk starts after this instruction. Walk to your finish mark, then stand still. Begin walking now.').then(async()=>{if(running.current&&alive.current&&!cancelled.current)await bridge.current?.beginDistance();}).catch(e=>{if(alive.current)setError(e.message);void bridge.current?.stop();});
   }
  });
  const app=AppState.addEventListener('change',state=>{if(state!=='active'&&running.current){cancelled.current=true;stopSpeaking();void bridge.current?.stop();}});
  const back=BackHandler.addEventListener('hardwareBackPress',()=>running.current);
  return()=>{alive.current=false;cancelled.current=true;listener?.remove();app.remove();back.remove();stopSpeaking();if(running.current)void bridge.current?.stop();};
 },[]);
 async function process(record:CalibrationCapture|null=saved,resume=false){
  if(!computer||!reference||!record)return;setBusy(true);setError('');setPhase('processing');cancelled.current=false;
  try{if(!resume)await submitDistanceValidation(computer,record,reference,metres,geometry);if(alive.current)setPending(true);
   const report=await pollDistanceValidation(computer,()=>cancelled.current||!alive.current);
   if(report&&alive.current){setResult(report);setPending(false);setPhase('done');}
  }catch(e){if(alive.current){setPending(!!await pendingDistanceValidation());setError(e instanceof Error?e.message:String(e));setPhase('done');}}
  finally{if(alive.current)setBusy(false);}
 }
 async function start(){
  if(running.current||busy)return;setError('');
  if(!bridge.current?.captureReferenceDistance||!bridge.current?.beginDistanceWarmup){setError('Install the updated APK for this distance trial.');return;}
  if(!reference||!computer)return;setBusy(true);
  try{
   await distanceComputerReady(computer);
   const granted=permission?.granted?permission:await requestPermission();if(!granted.granted)throw new Error('Camera permission is required for this trial.');
   if(!alive.current)return;
   running.current=true;cancelled.current=false;cueStarted.current=false;warmupCueStarted.current=false;setPhase('placing');setSaved(null);setResult(null);setImage('');
   await say('Place the phone at your lower back, screen facing out. Stand still.');
   if(!alive.current||cancelled.current)return;
   const capture=await bridge.current.captureReferenceDistance(JSON.stringify(reference),JSON.stringify(releaseInfo()));
   const record=await retainDistanceTrial(capture);await retainValidationRoute(record,metres,geometry);running.current=false;
   if(alive.current){setSaved(record);setPhase('done');if(capture.error)setError(capture.error);}
   if(alive.current&&!cancelled.current){
    if(JSON.parse(record.metadata).status==='no-walk'){await say('No walking was detected. The trial is saved.');}
    else{await say('Finished. You can take the phone out.');await process(record);}
   }
  }catch(e){if(alive.current){setError(e instanceof Error?e.message:String(e));setPhase('ready');}}
  finally{running.current=false;if(alive.current)setBusy(false);}
 }
 async function scan(data:string){if(scanBusy.current)return;scanBusy.current=true;try{const c=await connectCalibrationComputer(data);await distanceComputerReady(c);if(alive.current){setComputer(c);setScanning(false);setError('');}}catch(e){if(alive.current)setError(e instanceof Error?e.message:String(e));}finally{scanBusy.current=false;}}
 async function showScanner(){const p=permission?.granted?permission:await requestPermission();if(p.granted){setScanning(true);setError('');}}
 async function share(){if(!saved)return;try{if(!await Sharing.isAvailableAsync())throw new Error('File sharing is unavailable here.');await Sharing.shareAsync(saved.uri,{mimeType:'application/zip',dialogTitle:t('Export distance trial')});}catch(e){setError(e instanceof Error?e.message:String(e));}}
 async function shareResult(){if(!saved)return;try{if(!await Sharing.isAvailableAsync())throw new Error('File sharing is unavailable here.');await Sharing.shareAsync(await distanceResultFile(saved),{mimeType:'application/json',dialogTitle:t('Export result JSON')});}catch(e){setError(e instanceof Error?e.message:String(e));}}
 const completeCapture=!!saved&&['quiet-stop','walk-time-limit','time-limit'].includes(JSON.parse(saved.metadata).status)&&!saved.error;
 const captions:Record<string,string>={ready:'Mark a short route, then tap Start.',placing:'Place the phone. Stand still.','warmup-cue':'Wait for the practice cue.',warmup:'Practice, return to the start, then stand still.',cue:'Wait for the start cue.',waiting:'Begin walking now.',walking:'Walk to the finish, then stand still.',processing:'Your computer is checking the walk.',done:'Distance trial saved.'};
 return <Screen title="Distance validation" eyebrow="RESEARCH TRIAL" actions={<>
  {scanning?<BigButton label="Cancel" variant="outline" onPress={()=>setScanning(false)}/>:<>
   {!busy&&!pending&&!saved&&reference&&computer&&<BigButton label="Start distance trial" onPress={()=>void start()}/>}
   {!busy&&pending&&<BigButton label="Resume distance processing" onPress={()=>void process(saved,true)}/>}
   {!busy&&completeCapture&&!pending&&!result&&<BigButton label="Retry distance processing" onPress={()=>void process()}/>}
   {busy&&running.current&&<BigButton label="Stop trial" variant="outline" onPress={()=>{cancelled.current=true;stopSpeaking();void bridge.current?.stop();}}/>}
   {!busy&&!reference&&<BigButton label="Phone calibration" onPress={()=>navigation.replace('CameraCalibration')}/>}
   {!busy&&<BigButton label="Connect computer" variant="outline" onPress={()=>void showScanner()}/>}
   {!busy&&saved&&<BigButton label="Export distance trial" variant="outline" onPress={()=>void share()}/>}
  </>}
  <BigButton label="Back to home" variant="ghost" disabled={running.current} onPress={()=>navigation.goBack()}/>
 </>}>
  {scanning?<><Body>Scan the setup code on your computer.</Body><CameraView style={{height:240}} facing="back" barcodeScannerSettings={{barcodeTypes:['qr']}} onBarcodeScanned={event=>void scan(event.data)}/></>:<>
   <Body>{captions[phase]??captions.ready}</Body>
   {!busy&&<>
    <Body>Choose the marked route length</Body>
    <View accessibilityRole="radiogroup" style={ui.row}>{[2,3,5].map(m=><Pressable key={m} accessibilityRole="radio" accessibilityState={{selected:metres===m}} style={[ui.choice,metres===m&&ui.selected]} disabled={!!saved||pending} onPress={()=>setMetres(m)}><Text>{m} m {metres===m?'✓':''}</Text></Pressable>)}</View>
    <Body>Route shape</Body>
    <View accessibilityRole="radiogroup" style={ui.row}>{[['straight','Straight route'],['with-turns','Route with turns']].map(([value,label])=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:geometry===value}} style={[ui.choice,geometry===value&&ui.selected]} disabled={!!saved||pending} onPress={()=>setGeometry(value)}><Text>{t(label)}</Text></Pressable>)}</View>
    {!!saved&&!pending&&<BigButton label="New trial" variant="ghost" onPress={()=>{setSaved(null);setResult(null);setPhase('ready');}}/>}
    <Body muted>{reference?'Saved phone calibration loaded.':'Complete phone calibration once before this trial.'}</Body>
    <Body muted>Stand still at the finish until you hear Finished.</Body>
   </>}
   {busy&&image&&phase!=='processing'&&<Image source={{uri:image}} style={{width:'100%',height:150}} resizeMode="contain"/>}
   {result&&<View style={{gap:8}}>
    <Text style={ui.label}>{result.fullRouteCovered?'Experimental route estimate':'Full distance unavailable'}</Text>
    {result.fullRouteCovered?<><Text style={ui.label}>{result.completeRouteEstimateMetres.toFixed(2)} m</Text><Body>{t('Marked route: {0} m').replace('{0}',String(result.referenceDistanceMetres))}</Body><Body>{t('Difference: {0} m').replace('{0}',result.errorMetres.toFixed(2))}</Body></>:<Body>{result.reason==='partial-route'?'Tracking began after walking started. This is not a complete distance measurement.':'The tracker could not follow this whole walk reliably.'}</Body>}
    <Body muted>Research only. This does not stop or score a clinical walking test.</Body>
    <BigButton label="Export result JSON" variant="outline" onPress={()=>void shareResult()}/>
   </View>}
  </>}
  {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
 </Screen>;
}
