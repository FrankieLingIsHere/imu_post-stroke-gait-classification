import React,{useEffect,useRef,useState} from 'react';
import {AppState,BackHandler,Image,View,Pressable} from 'react-native';
import {useCameraPermissions} from 'expo-camera';
import {useKeepAwake} from 'expo-keep-awake';
import * as Sharing from 'expo-sharing';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import {Screen,Body,ui} from '../components/Screen';
import {colours as c} from '../theme';
import BigButton from '../components/BigButton';
import {Text,t} from '../i18n';
import {speakQueued,stopSpeaking} from '../audio';
import {calibrationBridge,latestCalibrationCapture,retainCalibrationCapture,retainCalibrationReport,hasCalibrationGeometry,latestNoiseCapture,retainNoiseCapture,type CalibrationCapture} from '../cameraCalibration';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';

export default function CameraCalibrationScreen({navigation}:NativeStackScreenProps<RootStackParamList,'CameraCalibration'>){
 useKeepAwake();const [permission,requestPermission]=useCameraPermissions();
 const bridge=useRef(calibrationBridge()),alive=useRef(true),running=useRef(false),lastPhase=useRef('');
 const [busy,setBusy]=useState(false),[image,setImage]=useState(''),[phase,setPhase]=useState('ready'),[seconds,setSeconds]=useState(40),[error,setError]=useState(''),[saved,setSaved]=useState<CalibrationCapture|null>(null);
 const [geometry,setGeometry]=useState(false);
 const [mode,setMode]=useState<'board'|'noise'>('board'),[bag,setBag]=useState(true),[noise,setNoise]=useState<CalibrationCapture|null>(null);
 const activeMode=useRef<'board'|'noise'>('board');
 useEffect(()=>{alive.current=true;void latestCalibrationCapture().then(async v=>{if(alive.current)setSaved(v);if(v){const valid=await hasCalibrationGeometry(v);if(alive.current)setGeometry(valid);}}).catch(e=>{if(alive.current)setError(String(e));});
  void latestNoiseCapture().then(v=>{if(alive.current)setNoise(v);}).catch(e=>{if(alive.current)setError(String(e));});
  const progress=bridge.current?.addListener('progress',e=>{if(!alive.current||!running.current)return;setImage(e.imageUri);setSeconds(Math.max(0,Math.ceil((activeMode.current==='noise'?300:40)-e.elapsedSeconds)));setPhase(e.phase);
   if(e.phase!==lastPhase.current){lastPhase.current=e.phase;if(e.phase==='move')void speakQueued('Slowly tilt and move the phone. Keep the board in view.');}
  });
  const app=AppState.addEventListener('change',state=>{if(state!=='active'&&running.current){running.current=false;stopSpeaking();void bridge.current?.stop();}});
  const back=BackHandler.addEventListener('hardwareBackPress',()=>running.current);
  return()=>{alive.current=false;progress?.remove();app.remove();back.remove();stopSpeaking();if(running.current)void bridge.current?.stop();};
 },[]);
 async function sayComplete(text:string){let completed=false;await speakQueued(text,{onDone:()=>{completed=true;}});if(!completed&&running.current)throw new Error('Voice guidance did not finish. Please try again.');}
 async function start(){if(running.current)return;setError('');if(!bridge.current){setError('Camera calibration needs the new Android APK.');return;}
  activeMode.current=mode;running.current=true;setBusy(true);setImage('');setSeconds(mode==='noise'?300:40);
  try{
   if(mode==='noise'){
    if(!bridge.current.captureNoise)throw new Error('Sensor noise capture needs the new Android APK.');
    setPhase('starting');await sayComplete('Leave the phone flat on a firm table. Do not touch it until the sound.');
    if(!running.current)return;
    const result=await bridge.current.captureNoise();const record=await retainNoiseCapture(result);
    if(alive.current){setNoise(record);setPhase('done');setError(result.error??'');await sayComplete('Sensor noise capture saved.');}
   }else{
    if(!bridge.current.captureWithOptics)throw new Error('Camera calibration needs the new Android APK.');
    const p=permission?.granted?permission:await requestPermission();if(!p.granted)throw new Error('Camera permission is required for this trial.');
    lastPhase.current='';setPhase('starting');
    await sayComplete('Hold the phone still, facing the board.');if(!running.current)return;
    const result=await bridge.current.captureWithOptics(bag?'waist-bag-window':'clear-lens');const record=await retainCalibrationCapture(result);
    if(alive.current){setSaved(record);setGeometry(false);setPhase('done');setError(result.error??'');await sayComplete('Capture saved. Calibration must be processed before use.');}
   }
  }catch(e){if(alive.current){setError(e instanceof Error?e.message:String(e));setPhase('ready');}}
  finally{running.current=false;if(alive.current)setBusy(false);}
 }
 function cancel(){running.current=false;stopSpeaking();void bridge.current?.stop();}
 async function share(){const record=mode==='noise'?noise:saved;if(!record)return;try{if(!await Sharing.isAvailableAsync())throw new Error('File sharing is unavailable here.');await Sharing.shareAsync(record.uri,{mimeType:'application/zip',dialogTitle:t(mode==='noise'?'Export sensor noise':'Export calibration capture')});}catch(e){setError(e instanceof Error?e.message:String(e));}}
 async function importReport(){if(!saved)return;try{
  const pick=await DocumentPicker.getDocumentAsync({type:['application/json','text/plain','application/octet-stream'],copyToCacheDirectory:true});if(pick.canceled)return;
  const asset=pick.assets[0];const info=await FileSystem.getInfoAsync(asset.uri);
  if(!info.exists||('size'in info&&info.size>256000))throw new Error('This calibration report did not pass processing.');
  const report=JSON.parse(await FileSystem.readAsStringAsync(asset.uri));await retainCalibrationReport(report,saved);setGeometry(true);setError('');
 }catch(e){setError(e instanceof Error?e.message:String(e));}}
 const captions:Record<string,string>={ready:mode==='noise'?'Leave the phone on a firm table for five minutes.':'Show the digital board on a fixed tablet or monitor.',starting:'Preparing capture.',still:'Hold still. Keep the board visible.',move:'Tilt and move slowly. Keep the board visible.',noise:'Keep the phone untouched on the table.',done:'Capture saved. Processing required.'};
 return <Screen title="Phone calibration" eyebrow="RESEARCHER SETUP" actions={<>
  {!busy&&<BigButton label={mode==='noise'?'Measure sensor noise (5 min)':'Capture calibration'} onPress={()=>void start()}/>}
  {busy&&<BigButton label="Cancel capture" variant="outline" onPress={cancel}/>}
  {!!(mode==='noise'?noise:saved)&&!busy&&<BigButton label={mode==='noise'?'Export sensor noise':'Export calibration capture'} onPress={()=>void share()}/>}
  {mode==='board'&&!!saved&&!busy&&<BigButton label="Import processed calibration" variant="outline" onPress={()=>void importReport()}/>}
  <BigButton label="Back to home" variant="ghost" disabled={busy} onPress={()=>navigation.goBack()}/>
 </>}>{!busy&&<View accessibilityRole="tablist" style={{flexDirection:'row',gap:8}}>{(['board','noise'] as const).map(value=><Pressable key={value} accessibilityRole="tab" accessibilityState={{selected:mode===value}} onPress={()=>{setMode(value);setPhase('ready');setError('');}} style={{flex:1,padding:14,borderRadius:12,borderWidth:2,borderColor:c.primary,backgroundColor:mode===value?c.primary:c.surface}}><Text style={{color:mode===value?'white':c.textPrimary,fontWeight:'700'}}>{value==='board'?'Camera board':'Sensor noise'}</Text></Pressable>)}</View>}
 <Body>{captions[phase]}</Body>
 {!busy&&mode==='board'&&<Pressable accessibilityRole="checkbox" accessibilityState={{checked:bag}} onPress={()=>setBag(!bag)} style={{padding:12,borderWidth:2,borderRadius:12,borderColor:c.primary}}><Text>{bag?'☑ ':'☐ '}{t('Capture through the usual waist-bag window')}</Text></Pressable>}
  {image&&busy&&<Image source={{uri:image}} style={{width:'100%',height:230}} resizeMode="contain"/>}
  {busy&&<Text style={ui.label}>{seconds} s</Text>}
  {phase==='ready'&&<Body>This belongs to the phone, not the participant.</Body>}
  {mode==='board'&&saved&&!busy&&<Body>{geometry?'Geometry saved. Walking-distance validation is still needed.':'No distance calibration is active yet.'}</Body>}
  {!!error&&<Text style={ui.error}>{t(error)}</Text>}
 </Screen>;
}
