import expo.modules.gaitcalibration.DistanceTrialFlow;

/** Executes the app's actual boundary state machine with controlled sensor classifications. */
public final class DistanceTrialFlowCheck {
    static long now=1_000_000_000L;
    static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    static String samples(DistanceTrialFlow f,double seconds,boolean still,boolean moving,boolean fresh){
        String result=null;for(int i=0;i<(int)(seconds*200);i++){now+=5_000_000L;String r=f.observe(now,still,moving,fresh);if(r!=null)result=r;}return result;
    }
    static DistanceTrialFlow prepared(){
        DistanceTrialFlow f=new DistanceTrialFlow();samples(f,2.1,true,false,true);check(f.phase.equals("warmup-cue"),"Still placement should request practice audio");
        samples(f,3,false,true,true);check(f.phase.equals("warmup-cue"),"Motion during speech must not begin practice");
        f.beginWarmup(now);samples(f,4,true,false,true);check(!f.warmupCompleted,"Standing cannot pass practice");
        samples(f,3.1,true,true,true);check(!f.warmupCompleted,"Motion cannot also count as stillness");
        samples(f,2.1,true,false,true);check(f.phase.equals("cue"),"Practice plus stillness should request measured cue");
        samples(f,2,false,true,true);check(f.walkStartedNs==0,"Measured timer cannot start during speech");
        f.beginMeasured(now);return f;
    }
    public static void main(String[] args){
        DistanceTrialFlow f=prepared();samples(f,2,true,false,true);check(f.walkStartedNs==0,"Standing must not start measured walk");
        samples(f,3,false,true,true);long end=now;check(f.walkStartedNs>0,"First fresh motion should start walk");
        String stop=samples(f,4.1,true,false,true);check("quiet-stop".equals(stop),"Quiet finish should stop automatically");check(f.walkEndedNs==end,"End must exclude finishing pause");
        DistanceTrialFlow idle=prepared();check("no-walk".equals(samples(idle,25.1,true,false,true)),"No-walk timeout");check(idle.walkStartedNs==0&&idle.walkEndedNs==0,"Idle cannot fabricate walk boundaries");
        DistanceTrialFlow stale=new DistanceTrialFlow();samples(stale,10,true,false,false);check(stale.phase.equals("placing"),"Stale sensors cannot verify placement");
        DistanceTrialFlow gap=prepared();samples(gap,3,false,true,true);samples(gap,10,true,false,false);check(gap.walkEndedNs==0,"Missing sensors cannot masquerade as a quiet finish");
        DistanceTrialFlow limit=prepared();check("walk-time-limit".equals(samples(limit,61,false,true,true)),"Walk safety cap");
        System.out.println("DistanceTrialFlow: placement, audio barriers, practice, first motion, quiet-stop, no-walk, stale sensors and time limit passed.");
    }
}
