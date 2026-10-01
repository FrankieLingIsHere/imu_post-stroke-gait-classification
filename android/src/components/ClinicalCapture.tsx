import React,{useEffect,useRef,useState} from 'react';
import { View } from 'react-native';
import { Screen,Body,ui } from './Screen';
import BigButton from './BigButton';
import { Text } from '../i18n';
import type { AssessmentProtocol } from '../store';
import { ProtocolClock,protocolFlows,assistedNotice,clinicalGo,type ProtocolExecution } from '../protocolFlow';
import type { speak } from '../audio';

type Props={
 protocol:AssessmentProtocol;audioEnabled:boolean;
 say:(text:string,options?:Parameters<typeof speak>[1])=>Promise<void>;
 onBegin:()=>void;onGo?:(offsetMs:number)=>void;onFinish:(execution:ProtocolExecution)=>void;onCancel:()=>void;
 receiving:()=>boolean;preview?:boolean;
};
export default function ClinicalCapture({protocol,audioEnabled,say,onBegin,onGo,onFinish,onCancel,receiving,preview=false}:Props){
 const flow=protocolFlows[protocol];
 const [stage,setStage]=useState<'intro'|'ready'|'starting'|'active'|'done'>('intro');
 const [elapsed,setElapsed]=useState(0),[remaining,setRemaining]=useState(flow.seconds??0),[error,setError]=useState('');
 const [armed,setArmed]=useState(false);
 const clock=useRef(new ProtocolClock(flow)),captureAt=useRef<number|null>(null),active=useRef(true),ended=useRef(false),starting=useRef(false);
 const armUntil=useRef(0);
 const finish=(end:ProtocolExecution['end'])=>{
   if(ended.current||captureAt.current===null)return;
   ended.current=true;setStage('done');
   const now=performance.now(),go=clock.current.goAt;
   onFinish({version:'protocol-flow-v1',protocol,goOffsetMs:go===null?null:go-captureAt.current,
     goSource:audioEnabled?'speech-start-callback':'worker-tap',elapsedFromGoSeconds:go===null?null:(now-go)/1000,end,clinicalOutcomeVerified:false});
 };
 const finishRef=useRef(finish);finishRef.current=finish;
 useEffect(()=>{
   active.current=true;
   void say(flow.intro).finally(()=>{if(active.current)setStage('ready');});
   const timer=setInterval(()=>{
     if(!active.current||ended.current)return;
     const now=performance.now();
     if(now>armUntil.current)setArmed(false);
     if(captureAt.current===null)return;
     if(!receiving()){finishRef.current('interrupted');return;}
     if(clock.current.goAt===null){
       if(now-captureAt.current>=10000){setError('The start cue was not confirmed. No clinical time was recorded.');finishRef.current('interrupted');}
       return;
     }
     const value=clock.current.read(now);
     setElapsed(value.elapsed);setRemaining(value.remaining??0);
     if(value.expired)finishRef.current(flow.end==='duration'?'duration':'capture-limit');
   },100);
   return()=>{active.current=false;clearInterval(timer);};
 },[]);
 function begin(){
   if(stage!=='ready'||starting.current)return;
   if(!receiving()){setError('Live sensor readings are missing. Wait or return to setup.');return;}
   starting.current=true;setError('');captureAt.current=performance.now();setStage('starting');onBegin();
   const go=()=>{if(!active.current||ended.current||clock.current.goAt!==null)return;clock.current.start(performance.now());onGo?.(clock.current.goAt!-captureAt.current!);setStage('active');};
   if(audioEnabled)void say(clinicalGo,{onStart:go});
   else go();
 }
 function stop(){
   if(!armed||performance.now()>armUntil.current){armUntil.current=performance.now()+5000;setArmed(true);return;}
   finish(flow.end==='worker'?'worker-ended':'interrupted');
 }
 return <Screen title={flow.title} eyebrow={preview?'PREVIEW — NO RECORDING SAVED':'WORKER-ASSISTED TEST'} actions={<>
   {stage==='ready'&&<BigButton label="Worker: ready to start" onPress={begin}/>}
   {(stage==='active'||stage==='starting')&&<BigButton label={armed?'Confirm stop and save':flow.end==='worker'?'Worker: finish capture':'Stop test early'} variant="danger" onPress={stop}/>}
   {preview&&stage==='active'&&<BigButton label="Preview finish event" variant="outline" onPress={()=>finish(flow.end==='duration'?'duration':'worker-ended')}/>}
   {(stage==='ready'||stage==='intro')&&<BigButton label="Back to setup" variant="outline" onPress={onCancel}/>}
 </>}>
   <Body>{stage==='intro'||stage==='ready'?flow.intro:flow.active}</Body>
   {stage==='ready'&&<Body>{protocol==='tug'?'Worker: confirm the participant is seated and ready. Use a separate stopwatch from Go until seated again.':'Worker: confirm the marked course is ready. Use the protocol stopwatch and record the measured outcome.'}</Body>}
   {stage==='starting'&&<Body>Waiting for the spoken Go. Do not start yet.</Body>}
   {stage==='active'&&<View><Text style={{fontSize:48,fontWeight:'700'}}>{flow.end==='duration'?remaining:Math.floor(elapsed)}</Text><Text style={ui.label}>{flow.end==='duration'?'seconds remaining':'seconds since Go — not the clinical result'}</Text></View>}
   <Text style={ui.caption}>{assistedNotice}</Text>
   {flow.end==='worker'&&<Text style={ui.caption}>Capture has a three-minute limit. The worker must stop the clinical stopwatch at the actual test endpoint.</Text>}
   {stage==='active'&&<Text style={ui.caption}>{protocol==='6mwt'?'App coaching is off. The worker gives the standard timed encouragement.':'No extra coaching during the measured test. Follow the worker’s protocol instructions.'}</Text>}
   {!audioEnabled&&<Body>Voice is off. The worker says Go when pressing the start button.</Body>}
   {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
 </Screen>;
}
