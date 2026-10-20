package expo.modules.gaitcalibration;
import org.json.JSONObject;
public final class SetupBaselineGateCheck {
 static int assertions;static final long BASE=100000000000L;
 static void check(boolean yes){assertions++;if(!yes)throw new AssertionError("Baseline assertion "+assertions);}
 static JSONObject status(long ns)throws Exception{return new JSONObject().put("initialized",true).put("integrity",true).put("positionStdMetres",.02).put("state",new JSONObject().put("imu_time_s",ns/1e9).put("vx",0).put("vy",0).put("vz",0));}
 static SetupBaselineGate filled(boolean moving,boolean shaking){SetupBaselineGate g=new SetupBaselineGate();for(int i=0;i<=420;i++){long ns=BASE+i*5000000L;g.sensor("accelerometer",ns,0,0,9.80665+(shaking?(i%2==0?1:-1):0));g.sensor("gyroscope",ns,moving?.2:0,0,0);}return g;}
 public static void main(String[] args)throws Exception {
  long end=BASE+2100000000L;JSONObject s=status(end);
  SetupBaselineGate empty=new SetupBaselineGate();check(!empty.ready(end,s));check(!filled(false,false).ready(end,null));
  JSONObject uninitialized=status(end).put("initialized",false);check(!filled(false,false).ready(end,uninitialized));
  check(!filled(true,false).ready(end,s));check(!filled(false,true).ready(end,s));
  check(!filled(false,false).ready(end+1000000000L,status(end+1000000000L)));
  JSONObject stale=status(end-1000000000L);check(!filled(false,false).ready(end,stale));
  JSONObject speed=status(end);speed.getJSONObject("state").put("vx",.2);check(!filled(false,false).ready(end,speed));
  check(!filled(false,false).ready(end,status(end).put("integrity",false)));
  check(!filled(false,false).ready(end,status(end).put("positionStdMetres",.2)));
  SetupBaselineGate gap=filled(false,false);gap.sensor("gyroscope",end+100000000L,0,0,0);check(!gap.ready(end+100000000L,status(end+100000000L)));
  SetupBaselineGate backwards=filled(false,false);backwards.sensor("accelerometer",end-1,0,0,9.80665);check(!backwards.ready(end,s));
  SetupBaselineGate quiet=filled(false,false);check(quiet.ready(end,s));check(!quiet.accepted());quiet.accept(end,s);check(quiet.accepted());
  // The movement instruction can be completed without resetting its already
  // measured baseline when the person begins to pick the phone up.
  quiet.sensor("gyroscope",end+10000000L,1,0,0);check(quiet.ready(end+10000000L,null));
  try{empty.accept(end,s);throw new AssertionError("Timer-only advance accepted");}catch(IllegalArgumentException expected){assertions++;}
  System.out.println("PASS: "+assertions+" measured baseline assertions; software controls only.");
 }
}
