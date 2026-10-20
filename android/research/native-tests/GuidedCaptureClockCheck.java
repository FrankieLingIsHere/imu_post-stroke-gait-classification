package expo.modules.gaitcalibration;

/** Executes production timing logic with controlled boot times, not phone sensors. */
public final class GuidedCaptureClockCheck {
  static int assertions;
  static final long BASE=100000000000L;
  static void check(boolean condition){assertions++;if(!condition)throw new AssertionError("check "+assertions);}
  static void rejects(Runnable action){
    try{action.run();throw new AssertionError("Expected timing rejection");}
    catch(IllegalArgumentException expected){assertions++;}
  }
  public static void main(String[] args){
    GuidedCaptureClock clock=new GuidedCaptureClock(BASE);
    check(!clock.canBegin(BASE));
    check(!clock.canBegin(BASE+GuidedCaptureClock.QUIET_NS-1));
    check(clock.canBegin(BASE+GuidedCaptureClock.QUIET_NS));
    rejects(()->clock.remainingMovementMs(BASE));
    rejects(()->clock.begin(BASE+9000000000L,()->{throw new AssertionError("Early estimator call");}));
    long speechDone=BASE+20000000000L;
    int[] notifications={0};
    clock.begin(speechDone,()->{check(clock.movementStartedNs()==0);notifications[0]++;});
    check(notifications[0]==1);
    check(clock.movementStartedNs()==speechDone);
    check(!clock.canBegin(speechDone));
    rejects(()->clock.begin(speechDone+1,()->notifications[0]++));
    check(notifications[0]==1);
    check(clock.remainingMovementMs(speechDone)==50000);
    // The former generic 40-second deadline must leave 30 seconds of movement.
    check(clock.remainingMovementMs(BASE+40000000000L)==30000);
    check(clock.remainingMovementMs(speechDone+GuidedCaptureClock.MOVEMENT_NS-1000001L)==2);
    check(clock.remainingMovementMs(speechDone+GuidedCaptureClock.MOVEMENT_NS-1)==1);
    check(clock.remainingMovementMs(speechDone+GuidedCaptureClock.MOVEMENT_NS)==0);
    check(clock.remainingMovementMs(speechDone+GuidedCaptureClock.MOVEMENT_NS+1)==0);
    GuidedCaptureClock failed=new GuidedCaptureClock(BASE);
    try{failed.begin(speechDone,()->{throw new IllegalStateException("Estimator unavailable");});throw new AssertionError("Expected solver failure");}
    catch(IllegalStateException expected){check(expected.getMessage().equals("Estimator unavailable"));}
    check(failed.movementStartedNs()==0);
    rejects(()->failed.remainingMovementMs(speechDone));
    check(failed.canBegin(speechDone+1));
    failed.begin(speechDone+1,()->notifications[0]++);
    check(notifications[0]==2);
    check(failed.remainingMovementMs(speechDone+1)==50000);
    GuidedCaptureClock expired=new GuidedCaptureClock(BASE);
    check(expired.canBegin(BASE+GuidedCaptureClock.SAFETY_MS*1000000L-1));
    check(!expired.canBegin(BASE+GuidedCaptureClock.SAFETY_MS*1000000L));
    rejects(()->expired.begin(BASE+GuidedCaptureClock.SAFETY_MS*1000000L,()->{throw new AssertionError("Expired estimator call");}));
    // Regression: a 90-second baseline/voice delay formerly cut the requested
    // 50-second movement at the absolute 120-second capture deadline.
    GuidedCaptureClock slow=new GuidedCaptureClock(BASE);
    check(slow.remainingSafetyMs(BASE+120000000000L)==0);
    slow.begin(BASE+90000000000L,()->{});
    check(slow.remainingMovementMs(BASE+120000000000L)==20000);
    check(slow.remainingSafetyMs(BASE+120000000000L)==30000);
    check(slow.remainingSafetyMs(BASE+140000000000L)==10000);
    check(slow.remainingSafetyMs(BASE+150000000000L)==0);
    // Near-expired starts remain bounded; ordinary captures keep their limit.
    GuidedCaptureClock late=new GuidedCaptureClock(BASE);
    late.begin(BASE+119000000000L,()->{});
    check(late.remainingSafetyMs(BASE+120000000000L)==59000);
    check(late.remainingSafetyMs(BASE+179000000000L)==0);
    check(clock.remainingSafetyMs(BASE+120000000000L)==0);
    // Ordinary phone setup is quality-driven, including an elderly user's long pause.
    GuidedCaptureClock patient=new GuidedCaptureClock(BASE,true);
    check(patient.canBegin(BASE+900000000000L));
    check(patient.remainingSafetyMs(BASE+900000000000L)==Long.MAX_VALUE);
    patient.begin(BASE+900000000000L,()->{});
    check(patient.remainingMovementMs(BASE+900000000000L)==50000);
    check(patient.remainingMovementMs(BASE+960000000000L)==0);
    check(patient.remainingSafetyMs(BASE+3600000000000L)==Long.MAX_VALUE);
    check(!patient.canBegin(BASE+960000000000L));
    System.out.println("PASS: "+assertions+" guided capture clock assertions (software controls only)");
  }
}
