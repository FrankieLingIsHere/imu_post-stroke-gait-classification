import type {Recording} from './recording';
import type {MotionWindow} from './movement';

export const CAMERA_TRIAL_VERSION='front-camera-imu-trial-v1';
export const cameraPlacementCue='Place the phone at your lower back, screen facing out. Stand still.';
export const cameraWalkCue='Walk to the finish and stand still. Begin walking now.';
export const cameraFinishCue='Finished. You can take the phone out.';
export type CameraStage='idle'|'placing'|'cue'|'waiting'|'walking'|'finishing'|'done';
export interface CameraTrial {
  version:typeof CAMERA_TRIAL_VERSION; walkingSeconds:15|30|60;
  referenceDistanceM:number|null;
  cameraFacing:'front';audioRecorded:false;requestedQuality:'720p';requestedMirror:false;
  mounting:'lower-back-landscape-screen-out';originalVideoUncropped:true;
  video:{status:'pending'|'saved'|'failed';fileName:string|null;error:string|null};
  timing:{basis:'js-monotonic-events-and-native-imu';captureStartedAt:string;
    nativeCameraFrameTimestampsAvailable:false;cameraImuClockCalibrationAvailable:false;
    actualVideoStartOffsetMs:null;alignmentUncertaintyMs:null;vioReady:false;
    events:{type:'camera-request'|'placement-instruction-end'|'walk-cue-end'|'movement-detected'|'stop-request'|'video-resolved';elapsedMs:number}[]};
  end:'duration'|'quiet-stop'|'user-stopped'|'interrupted'|'camera-ended'|'setup-limit'|null;
}
export function newCameraTrial(walkingSeconds:15|30|60,referenceDistanceM:number|null,startedAt:string):CameraTrial {
  return {version:CAMERA_TRIAL_VERSION,walkingSeconds,referenceDistanceM,cameraFacing:'front',audioRecorded:false,requestedQuality:'720p',requestedMirror:false,mounting:'lower-back-landscape-screen-out',originalVideoUncropped:true,
    video:{status:'pending',fileName:null,error:null},timing:{basis:'js-monotonic-events-and-native-imu',captureStartedAt:startedAt,nativeCameraFrameTimestampsAvailable:false,cameraImuClockCalibrationAvailable:false,actualVideoStartOffsetMs:null,alignmentUncertaintyMs:null,vioReady:false,events:[]},end:null};
}
export function validCameraTrial(value:unknown):value is CameraTrial {
  const f=value as CameraTrial;
  return !!f&&f.version===CAMERA_TRIAL_VERSION&&[15,30,60].includes(f.walkingSeconds)&&
    (f.referenceDistanceM===null||(Number.isFinite(f.referenceDistanceM)&&f.referenceDistanceM>0&&f.referenceDistanceM<=1000))&&
    f.cameraFacing==='front'&&f.audioRecorded===false&&f.requestedQuality==='720p'&&f.requestedMirror===false&&f.originalVideoUncropped===true&&f.mounting==='lower-back-landscape-screen-out'&&
    !!f.video&&['pending','saved','failed'].includes(f.video.status)&&(f.video.fileName===null||/^camera-[a-zA-Z0-9_-]+\.mp4$/.test(f.video.fileName))&&
    (f.video.error===null||(typeof f.video.error==='string'&&f.video.error.length<=2000))&&
    (f.video.status!=='saved'||f.video.fileName!==null)&&
    !!f.timing&&f.timing.basis==='js-monotonic-events-and-native-imu'&&typeof f.timing.captureStartedAt==='string'&&Number.isFinite(Date.parse(f.timing.captureStartedAt))&&
    f.timing.nativeCameraFrameTimestampsAvailable===false&&f.timing.cameraImuClockCalibrationAvailable===false&&f.timing.actualVideoStartOffsetMs===null&&f.timing.alignmentUncertaintyMs===null&&f.timing.vioReady===false&&
    Array.isArray(f.timing.events)&&f.timing.events.length<=20&&f.timing.events.every((e,i)=>!!e&&['camera-request','placement-instruction-end','walk-cue-end','movement-detected','stop-request','video-resolved'].includes(e.type)&&Number.isFinite(e.elapsedMs)&&e.elapsedMs>=0&&(i===0||e.elapsedMs>=f.timing.events[i-1].elapsedMs))&&
    [null,'duration','quiet-stop','user-stopped','interrupted','camera-ended','setup-limit'].includes(f.end);
}

type Engine={connect:()=>void;begin:()=>void;disconnect:()=>void;stop:(reason:Recording['stopReason'])=>Recording;
  readonly recordingClock:{monotonicMs:number;startedAt:string}|null;readonly allReceiving:boolean;readonly baselineReady:boolean;
  readonly motionStatus:MotionWindow;preserveSetupBaseline:()=>void;candidateStepsAfter:(since:number)=>number};
type Camera={recordAsync:(options:{maxDuration:number;maxFileSize:number})=>Promise<{uri:string}|undefined>;stopRecording:()=>void};
/** Concurrent research capture. Expo's recording request is NOT a camera-frame timestamp. */
export class CameraTrialCapture {
  stage:CameraStage='idle'; trial:CameraTrial|null=null; recording:Recording|null=null;
  private origin=0;private instructionsDone=false;private steadyAt:number|null=null;private walkAt:number|null=null;private motionArmedAt=0;
  private videoTask:Promise<void>|null=null;private videoUri:string|null=null;private videoError:string|null=null;private ended=false;
  private doneSent=false;
  private quietAt:number|null=null;
  constructor(private options:{engine:Engine;camera:Camera;walkingSeconds:15|30|60;referenceDistanceM:number|null;
    now:()=>number;say:(text:string)=>Promise<void>;onStage:(stage:CameraStage)=>void;onCaptureEnded?:(end:NonNullable<CameraTrial['end']>)=>void;
    onStopped:(recording:Recording,trial:CameraTrial)=>Promise<void>;
    onDone:(recording:Recording,trial:CameraTrial,uri:string|null)=>Promise<void>;onError:(message:string)=>void}){}
  private stageTo(stage:CameraStage){this.stage=stage;this.options.onStage(stage);}
  private event(type:CameraTrial['timing']['events'][number]['type']){this.trial!.timing.events.push({type,elapsedMs:Math.max(0,this.options.now()-this.origin)});}
  start(){
    if(this.stage!=='idle')return;
    const o=this.options;
    try{
      o.engine.connect();o.engine.begin();const clock=o.engine.recordingClock;if(!clock)throw new Error('Sensor capture did not start.');
      this.origin=clock.monotonicMs;this.trial=newCameraTrial(o.walkingSeconds,o.referenceDistanceM,clock.startedAt);this.stageTo('placing');this.event('camera-request');
      this.videoTask=o.camera.recordAsync({maxDuration:600,maxFileSize:150*1024*1024}).then(video=>{
        if(!video?.uri)throw new Error('No video file was returned.');this.videoUri=video.uri;
      }).catch(error=>{this.videoError=String(error instanceof Error?error.message:error).slice(0,2000);}).then(()=>{
        if(!this.ended){this.finish('camera-ended');}this.event('video-resolved');return this.deliver();
      });
      void o.say(cameraPlacementCue).then(()=>{if(!this.ended){this.instructionsDone=true;this.event('placement-instruction-end');}}).catch(()=>{if(this.ended)return;o.onError('Voice guidance failed. The partial capture will be saved.');this.finish('interrupted');});
    }catch(error){o.engine.disconnect();o.onError(String(error instanceof Error?error.message:error));if(this.trial)this.finish('interrupted');else this.stageTo('done');}
  }
  tick(){
    if(this.ended||!this.trial)return;
    const o=this.options,now=o.now(),m=o.engine.motionStatus;
    if(now-this.origin>=595000){this.finish('setup-limit');return;}
    if(this.stage==='placing'){
      const settled=this.instructionsDone&&o.engine.allReceiving&&o.engine.baselineReady&&m.enough&&m.upright&&m.steady;
      if(!settled){this.steadyAt=null;return;}
      this.steadyAt??=now;if(now-this.steadyAt<5000)return;
      o.engine.preserveSetupBaseline();this.stageTo('cue');
      void o.say(cameraWalkCue).then(()=>{if(this.ended)return;this.event('walk-cue-end');this.motionArmedAt=o.now();this.stageTo('waiting');}).catch(()=>{if(this.ended)return;o.onError('Voice guidance failed. The partial capture will be saved.');this.finish('interrupted');});
    }else if(this.stage==='waiting'){
      if(o.engine.allReceiving&&m.enough&&!m.steady&&m.context==='movement'&&o.engine.candidateStepsAfter(this.motionArmedAt)>=1){this.walkAt=now;this.event('movement-detected');this.stageTo('walking');}
    }else if(this.stage==='walking'&&this.walkAt!==null){
      // Engineering route trial only: quiet ends capture, not proof of a measured finish.
      const quiet=o.engine.allReceiving&&m.enough&&m.steady&&m.context==='rest-or-quiet';
      if(!quiet)this.quietAt=null;else this.quietAt??=now;
      if(this.quietAt!==null&&now-this.quietAt>=4000){this.finish('quiet-stop');return;}
      if(now-this.walkAt>=this.trial.walkingSeconds*1000)this.finish('duration');
    }
  }
  get walkingRemaining(){return this.walkAt===null?this.options.walkingSeconds:Math.max(0,this.options.walkingSeconds-(this.options.now()-this.walkAt)/1000);}
  finish(end:NonNullable<CameraTrial['end']>){
    if(this.ended||!this.trial)return;this.ended=true;this.trial.end=end;this.event('stop-request');this.stageTo('finishing');
    this.recording=this.options.engine.stop(end==='duration'||end==='quiet-stop'?'completed':end==='user-stopped'?'user-stopped':'interrupted');
    // Preserve raw sensors immediately, even if the camera takes time to finalize.
    this.stoppedTask=this.options.onStopped(this.recording,JSON.parse(JSON.stringify(this.trial))).catch(error=>this.options.onError(String(error)));
    try{this.options.camera.stopRecording();}catch(error){this.videoError=String(error);}
    this.options.onCaptureEnded?.(end);
    if(!this.videoTask){this.videoError??='Video did not start.';void this.deliver();}
  }
  private stoppedTask:Promise<void>=Promise.resolve();
  private async deliver(){
    if(this.doneSent||!this.recording||!this.trial)return;this.doneSent=true;await this.stoppedTask;
    this.trial.video={status:this.videoUri?'pending':'failed',fileName:null,error:this.videoError};
    try{await this.options.onDone(this.recording,this.trial,this.videoUri);this.stageTo('done');}
    catch(error){this.options.onError(String(error));this.stageTo('done');}
  }
}
