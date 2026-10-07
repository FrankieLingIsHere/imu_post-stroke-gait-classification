import expo.modules.gaitcalibration.CaptureQueueBudget;
import java.util.*;

/** Real JVM concurrency/clock checks. No claim of Android hardware performance. */
public class CaptureQueueBudgetCheck {
  private static void check(boolean b){if(!b)throw new AssertionError();}
  public static void main(String[] args)throws Exception{
    CaptureQueueBudget q=new CaptureQueueBudget(4,10);
    for(int i=0;i<4;i++)check(q.reserveFrame());check(!q.reserveFrame());
    for(int i=0;i<4;i++)q.releaseFrame();
    for(int i=0;i<10;i++)check(q.reserveSensor());check(!q.reserveSensor());
    for(int i=0;i<10;i++)q.releaseSensor();
    List<Thread> threads=new ArrayList<>();
    for(int i=0;i<8;i++){Thread t=new Thread(()->{for(int k=0;k<10000;k++){
      if(q.reserveFrame())q.releaseFrame();if(q.reserveSensor())q.releaseSensor();
    }});threads.add(t);t.start();}
    for(Thread t:threads)t.join();
    for(int i=0;i<31;i++){long time=1_000_000_000L+i*100_000_000L;q.camera(time);if(i%2==0)q.saved(time);}
    q.timing(4_000_000,7_000_000,8_000_000);
    Map<String,Number> r=q.snapshot();
    check(r.get("pendingFrames").intValue()==0&&r.get("pendingSensors").intValue()==0);
    check(r.get("peakPendingFrames").intValue()<=4&&r.get("peakPendingSensors").intValue()<=10);
    check(r.get("droppedImageCallbacks").longValue()>=1&&r.get("rejectedSensorCallbacks").longValue()>=1);
    check(r.get("cameraMetadataHz").doubleValue()==10&&r.get("savedCameraHz").doubleValue()==5);
    check(r.get("maxQueueLatencyMs").doubleValue()==7);
    boolean rejected=false;try{q.saved(1_000_000_000L);}catch(IllegalArgumentException e){rejected=true;}check(rejected);
    System.out.println("CaptureQueueBudget: bounds, concurrent drain, hardware rates, delays and clock rejection PASS");
  }
}
