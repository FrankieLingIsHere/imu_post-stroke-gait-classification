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
    intro:'Phone checks are complete. Stand at the start of the marked path. Stay still until you hear Go. Walk through the whole path, then stop and stand still. The phone will save automatically.',
    active:'Walk comfortably through the marked path. At the final marker, stop and stand still until the phone says the capture has ended.',
    finish:'The walk capture has ended. Rest comfortably. Phone distance and speed are estimates, not verified 10-metre timed-zone results.',
    start:'go',end:'worker',seconds:180,turnReminders:false,encouragement:'worker',
  },
  'tug':{
    title:'TUG',
    intro:'Phone checks are complete. Sit back in the chair and stay still. Wait for Go. Stand, walk to the three-metre mark, turn, return and sit. Stay still until the phone saves automatically.',
    active:'Stand, walk to the mark, turn, return and sit. Stay seated and still until the phone says capture has ended.',
    finish:'The chair-to-chair capture has ended. Stay comfortably seated. The phone endpoint is provisional; chair contact was not verified.',
    start:'go',end:'worker',seconds:180,turnReminders:false,encouragement:'worker',
  },
  '2mwt':{
    title:'2MWT',
    intro:'Phone checks are complete. Stand at the start and stay still until you hear Go. Walk comfortably for two minutes. You may rest; the clock continues. The phone stops and saves automatically.',
    active:'Follow the measured route and turn at its markers. Rest if needed; the two-minute clock keeps running.',
    finish:'Two minutes have finished. Stop safely. Your phone-based distance and speed estimates are saved with the recording.',
    start:'go',end:'duration',seconds:120,turnReminders:false,encouragement:'worker',
  },
  '6mwt':{
    title:'6MWT',
    intro:'Phone checks are complete. Stand at the start and stay still until you hear Go. Follow the clear route for six minutes. You may slow down or rest. The phone stops and saves automatically.',
    active:'Follow the measured route. Turns and standing rests are allowed. The worker gives the standard timed instructions; the clock keeps running.',
    finish:'Six minutes have finished. Stop safely. Your phone-based distance and speed estimates are saved with the recording.',
    start:'go',end:'duration',seconds:360,turnReminders:false,encouragement:'worker',
  },
};
export const assistedNotice='Prepare a clear marked path before starting. The phone captures without further taps, but its distance and endpoint estimates do not verify floor marks or chair contact.';
export const clinicalGo='Go.';
export const clinicalInterrupted='Capture stopped before the planned finish. Rest safely. The worker should record the reason.';
export const clinicalLimit='The capture time limit has been reached. Rest safely. This does not confirm that the test was completed.';
export interface ProtocolExecution {
  version:'protocol-flow-v1'; protocol:AssessmentProtocol; goOffsetMs:number|null;
  goSource:'speech-start-callback'|'worker-tap'|'automatic-silent-cue'; elapsedFromGoSeconds:number|null;
  end:'duration'|'worker-ended'|'auto-stop-estimate'|'interrupted'|'capture-limit'; clinicalOutcomeVerified:false;
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
