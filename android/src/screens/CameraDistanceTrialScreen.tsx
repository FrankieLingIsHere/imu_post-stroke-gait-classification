import React,{useEffect,useRef,useState} from 'react';
import {AppState,BackHandler,Image,View} from 'react-native';
import {useCameraPermissions} from 'expo-camera';
import {useKeepAwake} from 'expo-keep-awake';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {RootStackParamList} from '../../App';
import {Screen,Body,ui} from '../components/Screen';
import BigButton from '../components/BigButton';
import {Text,t} from '../i18n';
import {speakQueued,stopSpeaking} from '../audio';
import {latestCalibrationCapture,type CalibrationCapture} from '../cameraCalibration';
import {releaseInfo} from '../releaseInfo';
import {distanceBridge,loadDistanceResearchProfile,saveDistanceResearchProfile,retainDistanceTrial,latestDistanceTrial,distanceTrialSummary,type DistanceProgress} from '../cameraDistanceTrial';

export default function CameraDistanceTrialScreen({navigation}:NativeStackScreenProps<RootStackParamList,'CameraDistanceTrial'>){
 useKeepAwake();const [permission,requestPermission]=useCameraPermissions();
 const bridge=useRef(distanceBridge()),alive=useRef(true),running=useRef(false),cueStarted=useRef(false),cancelled=useRef(false);
 const [busy,setBusy]=useState(false),[phase,setPhase]=useState('ready'),[image,setImage]=useState(''),[error,setError]=useState('');
 const [profile,setProfile]=useState<any>(null),[saved,setSaved]=useState<CalibrationCapture|null>(null),[tracking,setTracking]=useState<any>(null),[details,setDetails]=useState(false);
 const say=(text:string)=>new Promise<void>((resolve,reject)=>{void speakQueued(text,{onDone:resolve,onStopped:()=>reject(new Error('Voice guidance failed. The partial capture will be saved.')),onError:()=>reject(new Error('Voice guidance failed. The partial capture will be saved.'))});});
 useEffect(()=>{
  alive.current=true;
  void Promise.all([latestCalibrationCapture().then(loadDistanceResearchProfile),latestDistanceTrial()]).then(([p,s])=>{if(alive.current){setProfile(p);setSaved(s);}}).catch(e=>{if(alive.current)setError(String(e));});
  const listener=bridge.current?.addListener('progress',(e:DistanceProgress)=>{
   if(!alive.current||!running.current)return;setPhase(e.phase);setImage(e.imageUri);
   try{setTracking(e.tracking?JSON.parse(e.tracking):null);}catch{setTracking(null);}
   if(e.phase==='cue'&&!cueStarted.current){cueStarted.current=true;
    void say('Phone ready. Walk to your finish mark, then stand still. Begin walking now.').then(async()=>{if(running.current&&alive.current&&!cancelled.current)await bridge.current?.beginDistance();}).catch(e=>{if(alive.current)setError(e.message);void bridge.current?.stop();});
   }
  });
  const app=AppState.addEventListener('change',state=>{if(state!=='active'&&running.current){cancelled.current=true;stopSpeaking();void bridge.current?.stop();}});
  const back=BackHandler.addEventListener('hardwareBackPress',()=>running.current);
  return()=>{alive.current=false;listener?.remove();app.remove();back.remove();stopSpeaking();if(running.current)void bridge.current?.stop();};
 },[]);
 async function start(){
  if(running.current)return;setError('');if(!bridge.current){setError('Camera distance trial needs the new Android APK.');return;}
  if(!profile){setError('Import the phone research profile before starting.');return;}
  setBusy(true);try{
   const permissionResult=permission?.granted?permission:await requestPermission();if(!permissionResult.granted)throw new Error('Camera permission is required for this trial.');
   running.current=true;cancelled.current=false;cueStarted.current=false;setPhase('placing');setSaved(null);setTracking(null);
   await say('Place the phone at your lower back, screen facing out. Stand still.');
   if(!alive.current||cancelled.current)return;
   const result=await bridge.current.captureDistance(profile?JSON.stringify(profile):null,JSON.stringify(releaseInfo()));
   const record=await retainDistanceTrial(result);
   if(alive.current){setSaved(record);setPhase('done');if(result.error)setError(result.error);}
   if(alive.current)await say('Finished. You can take the phone out.');
  }catch(e){if(alive.current){setError(e instanceof Error?e.message:String(e));setPhase('ready');}}
  finally{running.current=false;if(alive.current)setBusy(false);}
 }
 async function importProfile(){try{
  const result=await DocumentPicker.getDocumentAsync({type:['application/json','text/plain','application/octet-stream'],copyToCacheDirectory:true});if(result.canceled)return;
  const info=await FileSystem.getInfoAsync(result.assets[0].uri);if(!info.exists||info.isDirectory||info.size>256000)throw new Error('Invalid research profile.');
  const capture=await latestCalibrationCapture();if(!capture)throw new Error('A phone calibration capture is needed to match this profile.');
  const p=JSON.parse(await FileSystem.readAsStringAsync(result.assets[0].uri));await saveDistanceResearchProfile(p,capture);setProfile(p);setError('');
 }catch(e){setError(e instanceof Error?e.message:String(e));}}
 async function share(){if(!saved)return;try{if(!await Sharing.isAvailableAsync())throw new Error('File sharing is unavailable here.');await Sharing.shareAsync(saved.uri,{mimeType:'application/zip',dialogTitle:t('Export distance trial')});}catch(e){setError(e instanceof Error?e.message:String(e));}}
 const summary=distanceTrialSummary(saved);
 const captions:Record<string,string>={ready:'Mark a short route, then tap Start.',placing:'Place the phone. Stand still.',cue:'Wait for the start cue.',waiting:'Begin walking now.',walking:'Walk to the finish, then stand still.',done:'Distance trial saved.'};
 const reasons:Record<string,string>={'needs-profile':'Import the phone research profile to calculate experimental distance.','low-texture':'The camera could not find enough scene detail.','insufficient-parallax':'There was not enough clear forward movement.','initial-features-lost':'The camera lost its scene features.','mapped-features-lost':'The camera lost its scene features.','inconsistent-map-pose':'The camera lost its scene features.','reprojection-error':'The camera lost its scene features.','camera-gap':'Camera timing had a gap.','imu-coverage-gap':'Sensor timing had a gap.','missing-camera-timing':'Camera timing data was unavailable.','gyro-visual-disagreement':'Camera motion did not agree with the IMU.','scale-unobservable':'This trial could not determine metric scale.','scale-physical-check-failed':'This trial did not pass the distance consistency checks.','insufficient-continuous-motion':'There was not enough continuous tracking to calculate distance.'};
 return <Screen title="Camera distance trial" eyebrow="RESEARCH TRIAL" actions={<>
  {!busy&&profile&&<BigButton label="Start camera distance trial" onPress={()=>void start()}/>}
  {busy&&<BigButton label="Stop trial" variant="outline" onPress={()=>{cancelled.current=true;stopSpeaking();void bridge.current?.stop();}}/>}
  {!busy&&saved&&<BigButton label="Export distance trial" onPress={()=>void share()}/>}
  {!busy&&<BigButton label="Import phone research profile" variant={profile?"outline":"primary"} onPress={()=>void importProfile()}/>}
  <BigButton label="Back to home" variant="ghost" disabled={busy} onPress={()=>navigation.goBack()}/>
 </>}>
  <Body>{captions[phase]??captions.ready}</Body>
  {busy&&image&&<Image source={{uri:image}} style={{width:'100%',height:150}} resizeMode="contain"/>}
  {!busy&&<Body muted>{profile?'Phone research profile loaded.':'Import the phone research profile before starting.'}</Body>}
  {!busy&&!saved&&<Body>Walk a marked short route in a bright, textured room. Stand still at the finish until the voice says finished.</Body>}
  {summary&&<View><Text style={ui.label}>{summary.available?'Experimental camera travel':'Distance unavailable'}</Text>
   {summary.available?<Text style={ui.label}>{summary.metres.toFixed(2)} m</Text>:<Body>{reasons[summary.reason]??'The trial could not provide a distance estimate. Export it for review.'}</Body>}
   <Body muted>Research only. This does not stop or score a clinical walking test.</Body></View>}
  {tracking&&busy&&<Body>{tracking.state==='tracking'?'Camera tracking active.':tracking.state==='tracking-lost'?'Camera tracking lost. Raw capture continues.':'Collecting camera and sensor data.'}</Body>}
  {!busy&&saved&&<BigButton label={details?'Hide trial diagnostics':'Show trial diagnostics'} variant="ghost" onPress={()=>setDetails(!details)}/>}
  {details&&summary&&<Body muted>{JSON.stringify({state:summary.diagnostics?.state,reason:summary.reason,frames:summary.diagnostics?.framesProcessed,poses:summary.diagnostics?.poseFrames,features:summary.diagnostics?.features,reprojectionRms:summary.diagnostics?.reprojectionRmsPixels,rank:summary.diagnostics?.fitRank,condition:summary.diagnostics?.scaledCondition},null,2)}</Body>}
  {!!error&&<Text style={ui.error}>{t(error)}</Text>}
 </Screen>;
}
