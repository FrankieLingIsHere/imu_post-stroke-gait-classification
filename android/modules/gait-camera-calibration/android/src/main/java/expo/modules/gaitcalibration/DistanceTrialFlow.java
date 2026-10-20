package expo.modules.gaitcalibration;

/** Sensor-driven research capture boundaries, not VIO initialization or gait diagnosis. */
public final class DistanceTrialFlow {
    public String phase = "placing";
    public long walkStartedNs, walkEndedNs;
    public boolean warmupCompleted;
    private long stillSince, lastSample, warmupMotion, lastMotion, waitingSince;
    private String stopReason;

    public void beginWarmup(long now) {
        if (!phase.equals("warmup-cue")) return;
        phase="warmup"; stillSince=0; lastSample=now; warmupMotion=0;
    }
    public void beginMeasured(long now) {
        if (!phase.equals("cue") || !warmupCompleted) return;
        phase="waiting"; waitingSince=now; stillSince=0; lastMotion=0;
    }
    public String observe(long now, boolean still, boolean moving, boolean fresh) {
        if (stopReason!=null) return stopReason;
        long dt=lastSample>0?Math.min(Math.max(0,now-lastSample),25_000_000L):0;
        lastSample=now;
        if (!fresh) { stillSince=0; return null; }
        if (still && !moving) { if(stillSince==0)stillSince=now; } else stillSince=0;
        if (phase.equals("placing") && stillSince>0 && now-stillSince>=2_000_000_000L)
            phase="warmup-cue";
        if (phase.equals("warmup")) {
            if(moving)warmupMotion+=dt;
            if(warmupMotion>=3_000_000_000L && stillSince>0 && now-stillSince>=2_000_000_000L) {
                warmupCompleted=true;phase="cue";
            }
        }
        if (phase.equals("waiting")) {
            if(moving) { phase="walking"; walkStartedNs=now;lastMotion=now; }
            else if(now-waitingSince>=25_000_000_000L)stopReason="no-walk";
        }
        if (phase.equals("walking")) {
            if(moving)lastMotion=now;
            if(now-walkStartedNs>=6_000_000_000L && now-lastMotion>=4_000_000_000L) {
                walkEndedNs=lastMotion;stopReason="quiet-stop";
            } else if(now-walkStartedNs>=60_000_000_000L) {
                walkEndedNs=now;stopReason="walk-time-limit";
            }
        }
        return stopReason;
    }
}
