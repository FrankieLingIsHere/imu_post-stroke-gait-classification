import expo.modules.gaitcalibration.GaitDistanceFlow;
public final class GaitDistanceFlowCheck {
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 static void rejected(Runnable action){try{action.run();throw new AssertionError("Invalid boundary accepted");}catch(IllegalStateException|IllegalArgumentException expected){}}
 public static void main(String[] args){
  for(long seconds:new long[]{10,120,180,360}){
   GaitDistanceFlow f=new GaitDistanceFlow();rejected(()->f.end(5,"completed"));f.begin(1_000_000_000L);
   rejected(()->f.begin(2_000_000_000L));rejected(()->f.end(1_000_000_000L,"completed"));rejected(()->f.end(2_000_000_000L,"quiet-stop"));
   // The caller, not stillness or a research-trial timer, owns endurance time.
   check(f.endNs==0&&!f.finishing,"No implicit stop during a rest");
   f.end(1_000_000_000L+seconds*1_000_000_000L,"completed");check(f.completed(),"External completed boundary");
   long end=f.endNs;f.end(end+9,"interrupted");check(f.endNs==end&&f.completed(),"Idempotent end");
  }
  GaitDistanceFlow interrupted=new GaitDistanceFlow();interrupted.begin(1);interrupted.end(2,"interrupted");check(!interrupted.completed(),"Interrupted capture is not admitted");
  System.out.println("GaitDistanceFlow passed: external boundaries, 10/120/180/360 seconds, rests, invalid commands and interruption.");
 }
}
