import React,{useEffect,useRef,useState} from 'react';
import { View } from 'react-native';
import { Screen,Body,ui } from './Screen';
import BigButton from './BigButton';
import { Text,t } from '../i18n';
import type { AssessmentProtocol } from '../store';
import { ProtocolClock,protocolFlows,clinicalGo,type ProtocolExecution } from '../protocolFlow';
import type { MotionWindow } from '../movement';
import type { speak } from '../audio';

type Props={protocol:AssessmentProtocol;audioEnabled:boolean;
 say:(text:string,options?:Parameters<typeof speak>[1])=>Promise<void>;
 onBegin:()=>void;onGo?:(offsetMs:number)=>void;onFinish:(execution:ProtocolExecution)=>void;onCancel:()=>void;
 receiving:()=>boolean;motion:()=>MotionWindow;preview?:boolean};

export default function ClinicalCapture({protocol,audioEnabled,say,onBegin,onGo,onFinish,onCancel,receiving,motion,preview=false}:Props){
 const flow=protocolFlows[protocol];
 const [stage,setStage]=useState<'intro'|'ready'|'starting'|'active'|'done'>('intro');
 const stageRef=useRef(stage);stageRef.current=stage;
 const [elapsed,setElapsed]=useState(0),[remaining,setRemaining]=useState(flow.seconds??0),[error,setError]=useState('');
 const [armed,setArmed]=useState(false);
 const clock=useRef(new ProtocolClock(flow)),captureAt=useRef<number|null>(null),active=useRef(true),ended=useRef(false),starting=useRef(false);
 const readySince=useRef<number|null>(null),movementSince=useRef<number|null>(null),movementQualified=useRef(false),quietSince=useRef<number|null>(null),armUntil=useRef(0);
 const finish=(end:ProtocolExecution['end'])=>{
   if(ended.current||captureAt.current===null)return;
   ended.current=true;setStage('done');
   const now=performance.now(),go=clock.current.goAt;
   onFinish({version:'protocol-flow-v1',protocol,goOffsetMs:go===null?null:go-captureAt.current,
     goSource:audioEnabled?'speech-start-callback':'automatic-silent-cue',elapsedFromGoSeconds:go===null?null:(now-go)/1000,end,clinicalOutcomeVerified:false});
 };
 const finishRef=useRef(finish);finishRef.current=finish;
 const begin=()=>{
   if(starting.current||!receiving())return;
   starting.current=true;setError('');captureAt.current=performance.now();setStage('starting');onBegin();
   const go=()=>{if(!active.current||ended.current||clock.current.goAt!==null)return;clock.current.start(performance.now());onGo?.(clock.current.goAt!-captureAt.current!);setStage('active');};
   if(audioEnabled)void say(t(clinicalGo),{onStart:go}); else go();
 };
 const beginRef=useRef(begin);beginRef.current=begin;
 useEffect(()=>{
   active.current=true;
   void say(t(flow.intro)).finally(()=>{if(active.current)setStage('ready');});
   const timer=setInterval(()=>{
     if(!active.current||ended.current)return;
     const now=performance.now();
     if(now>armUntil.current)setArmed(false);
     if(captureAt.current===null){
       if(starting.current)return;
       const m=motion();
       if(stageRef.current==='intro'||!receiving()||!m.enough||!m.steady){readySince.current=null;return;}
       if(readySince.current===null)readySince.current=now;
       if(now-readySince.current>=3000)beginRef.current();
       return;
     }
     if(!receiving()){finishRef.current('interrupted');return;}
     if(clock.current.goAt===null){
       if(now-captureAt.current>=10000){setError(t('The start cue was not confirmed. No clinical time was recorded.'));finishRef.current('interrupted');}
       return;
     }
     const value=clock.current.read(now);setElapsed(value.elapsed);setRemaining(value.remaining??0);
     if(value.expired){finishRef.current(flow.end==='duration'?'duration':'capture-limit');return;}
     if(flow.end==='worker'){
       const m=motion();
       if(!m.enough){quietSince.current=null;return;}
       if(m.context==='movement'&&!m.steady){
         if(movementSince.current===null)movementSince.current=now;
         if(now-movementSince.current>=2000)movementQualified.current=true;
         quietSince.current=null;
       }else if(m.context==='rest-or-quiet'||m.steady){
         movementSince.current=null;
         if(quietSince.current===null)quietSince.current=now;
         // A long mid-test rest can still look like the endpoint: retain provisional provenance.
         if(movementQualified.current&&value.elapsed>=8&&now-quietSince.current>=8000)finishRef.current('auto-stop-estimate');
       }else{movementSince.current=null;quietSince.current=null;}
     }
   },100);
   return()=>{active.current=false;clearInterval(timer);};
 },[]);
 function stop(){
   if(!armed||performance.now()>armUntil.current){armUntil.current=performance.now()+5000;setArmed(true);return;}
   finish('interrupted');
 }
 return <Screen title={flow.title} eyebrow={preview?'PREVIEW — NO RECORDING SAVED':'HANDS-FREE TEST'} actions={<>
   {(stage==='active'||stage==='starting')&&<BigButton label={armed?'Confirm emergency stop':'Stop test early'} variant="danger" onPress={stop}/>}
   {preview&&stage==='active'&&<BigButton label="Preview finish event" variant="outline" onPress={()=>finish(flow.end==='duration'?'duration':'auto-stop-estimate')}/>}
   {(stage==='ready'||stage==='intro')&&<BigButton label="Back to setup" variant="outline" onPress={onCancel}/>}
 </>}>
   <Body>{stage==='intro'||stage==='ready'?flow.intro:flow.active}</Body>
   {stage==='ready'&&<Body>Move into the starting position and stay still. The phone will say Go when it settles. No button is needed.</Body>}
   {stage==='starting'&&<Body>Wait for Go before moving.</Body>}
   {stage==='active'&&<View><Text style={{fontSize:48,fontWeight:'700'}}>{flow.end==='duration'?remaining:Math.floor(elapsed)}</Text><Text style={ui.label}>{flow.end==='duration'?'seconds remaining':'seconds since Go — provisional'}</Text></View>}
   {flow.end==='worker'&&<Text style={ui.caption}>At the final marker, stop and stay still. For TUG, sit and remain still. The phone saves after a sustained stop. A long rest can end capture early, so this is not a verified clinical endpoint.</Text>}
   {flow.end==='duration'&&<Text style={ui.caption}>The phone stops automatically when time is up. Resting does not pause the clock.</Text>}
   {!audioEnabled&&<Body>Voice is off. Watch for the timer to start, or ask a helper for the Go cue.</Body>}
   {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
 </Screen>;
}
