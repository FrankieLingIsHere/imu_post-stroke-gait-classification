export interface GoogleDistanceTrial {
  version:'google-distance-trial-v1'; referenceDistanceM:2|3|5;
  end?:'quiet-stop'|'time-limit'|'user-stopped'|'interrupted';
  completedMarkedRoute?:boolean|null;
}
export const GOOGLE_TRIAL_LIMIT_SECONDS=60;
export const googleTrialIntro='Phone checks are complete. Return to your start mark and stand still. Wait until you hear begin. Walk to your short finish mark, then stop and stand still. The trial will finish automatically.';
export const googleTrialFinish='The short trial has finished. You can rest. I will check for delayed Google records before saving. You do not need to walk again.';
export const googleTrialLimit='The trial time limit has been reached. Stop safely and rest. This trial does not confirm that you reached the finish mark.';
/** Only arm after the existing fresh-step gate; quiet stopping is not distance detection. */
export class GoogleTrialStopGate {
  private started:number|null=null;
  private quietSince:number|null=null;
  begin(now:number){this.started=now;this.quietSince=null;}
  update(now:number,receiving:boolean,enough:boolean,steady:boolean):GoogleDistanceTrial['end']|null {
    if(this.started===null)return null;
    if(!receiving)return 'interrupted';
    if(now-this.started>=GOOGLE_TRIAL_LIMIT_SECONDS*1000)return 'time-limit';
    if(!enough||!steady){this.quietSince=null;return null;}
    if(this.quietSince===null)this.quietSince=now;
    return now-this.quietSince>=4000?'quiet-stop':null;
  }
}
