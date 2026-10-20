package expo.modules.gaitcalibration;

/** Boot-clock timing for full guided capture; speech completion triggers begin. */
public final class GuidedCaptureClock {
  public static final long QUIET_NS=10000000000L;
  public static final long MOVEMENT_NS=50000000000L;
  public static final long SAFETY_MS=120000L;
  private final long captureStartedNs;
  private final boolean waitForQuality;
  private volatile long movementStartedNs=0;
  public GuidedCaptureClock(long captureStartedNs){this(captureStartedNs,false);}
  public GuidedCaptureClock(long captureStartedNs,boolean waitForQuality){this.captureStartedNs=captureStartedNs;this.waitForQuality=waitForQuality;}
  public boolean canBegin(long nowNs){return movementStartedNs==0&&nowNs-captureStartedNs>=QUIET_NS&&(waitForQuality||nowNs-captureStartedNs<SAFETY_MS*1000000L);}
  public void begin(long nowNs,Runnable notifyEstimator){
    if(!canBegin(nowNs))throw new IllegalArgumentException("Guided movement cannot start yet");
    // A failed estimator transition must never start a successful finish timer.
    notifyEstimator.run();movementStartedNs=nowNs;
  }
  public long movementStartedNs(){return movementStartedNs;}
  /** Slow baseline/speech must not consume the promised movement window.
   * Still bounded: one movement start, plus ten seconds to settle. */
  public long remainingSafetyMs(long nowNs){
    if(waitForQuality)return Long.MAX_VALUE;
    long deadline=captureStartedNs+SAFETY_MS*1000000L;
    if(movementStartedNs>0)deadline=Math.max(deadline,movementStartedNs+MOVEMENT_NS+10000000000L);
    long remaining=deadline-nowNs;
    return remaining<=0?0:(remaining+999999L)/1000000L;
  }
  public long remainingMovementMs(long nowNs){
    if(movementStartedNs==0)throw new IllegalArgumentException("Guided movement has not started");
    long remaining=movementStartedNs+MOVEMENT_NS-nowNs;
    return remaining<=0?0:(remaining+999999L)/1000000L;
  }
}
