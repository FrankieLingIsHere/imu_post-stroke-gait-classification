import type { AssessmentProtocol } from './store';

export interface ProtocolFlow {
  title:string; intro:string; active:string; finish:string;
  start:'first-step'|'go'; end:'duration'|'worker';
  seconds:number|null; turnReminders:boolean; encouragement:'behaviour'|'worker';
}
export const protocolFlows:Record<AssessmentProtocol,ProtocolFlow>={
  'research-walk':{
    title:'Research walk',intro:'Wait for the start cue. Walk at your comfortable pace. Recording waits for your first detected step.',
    active:'Follow your clear path. Keep your eyes ahead.',finish:'Recording stopped. Check your phone when safely settled.',
    start:'first-step',end:'duration',seconds:null,turnReminders:true,encouragement:'behaviour',
  },
  '10mwt':{
    title:'10MWT',
    intro:'Phone checks are complete. Stand at the start of the marked path. Walk past both timing marks at your comfortable pace, then slow down. Wait for Go.',
    active:'Walk through the marked path. The worker times the middle section and ends capture after you have slowed down.',
    finish:'The walk capture has ended. Rest comfortably. The worker will enter the marked-zone stopwatch time.',
    start:'go',end:'worker',seconds:180,turnReminders:false,encouragement:'worker',
  },
  'tug':{
    title:'TUG',
    intro:'Phone checks are complete. Sit back in the chair. On Go, stand, walk to the three-metre mark, turn, return and sit. Wait for the worker.',
    active:'Stand, walk to the mark, turn, return and sit. The worker times from Go until you are seated again.',
    finish:'The chair-to-chair capture has ended. Stay comfortably seated. The worker will enter the stopwatch time.',
    start:'go',end:'worker',seconds:180,turnReminders:false,encouragement:'worker',
  },
  '2mwt':{
    title:'2MWT',
    intro:'Phone checks are complete. Follow the measured route for two minutes from Go. Rest if needed; the clock keeps running. The worker measures your distance.',
    active:'Follow the measured route and turn at its markers. Rest if needed; the two-minute clock keeps running.',
    finish:'Two minutes have finished. Stop safely and stay where you are while the worker measures the remaining distance.',
    start:'go',end:'duration',seconds:120,turnReminders:false,encouragement:'worker',
  },
  '6mwt':{
    title:'6MWT',
    intro:'Phone checks are complete. Follow the measured route for six minutes from Go. You may slow down or rest. Listen to the worker for the timed instructions.',
    active:'Follow the measured route. Turns and standing rests are allowed. The worker gives the standard timed instructions; the clock keeps running.',
    finish:'Six minutes have finished. Stop safely and stay where you are while the worker measures the remaining distance.',
    start:'go',end:'duration',seconds:360,turnReminders:false,encouragement:'worker',
  },
};
export const assistedNotice='This test needs a worker to prepare the course, give protocol instructions and confirm the outcome. The phone does not detect distance markers or chair contact.';
export const clinicalGo='Go.';
export const clinicalInterrupted='Capture stopped before the planned finish. Rest safely. The worker should record the reason.';
export const clinicalLimit='The capture time limit has been reached. Rest safely. This does not confirm that the test was completed.';
export interface ProtocolExecution {
  version:'protocol-flow-v1'; protocol:AssessmentProtocol; goOffsetMs:number|null;
  goSource:'speech-start-callback'|'worker-tap'; elapsedFromGoSeconds:number|null;
  end:'duration'|'worker-ended'|'interrupted'|'capture-limit'; clinicalOutcomeVerified:false;
}
/** Independent protocol clock: rests and candidate step detections never alter it. */
export class ProtocolClock {
  goAt:number|null=null;
  constructor(readonly flow:ProtocolFlow){}
  start(now:number){if(this.goAt===null)this.goAt=now;}
  read(now:number){
    const elapsed=this.goAt===null?0:Math.max(0,(now-this.goAt)/1000);
    const remaining=this.flow.seconds===null?null:Math.max(0,Math.ceil(this.flow.seconds-elapsed));
    return {elapsed,remaining,expired:this.goAt!==null&&this.flow.seconds!==null&&elapsed>=this.flow.seconds};
  }
}
