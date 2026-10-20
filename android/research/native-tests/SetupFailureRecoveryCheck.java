package expo.modules.gaitcalibration;
import org.json.*;

/** Production gate under delayed, incomplete and interrupted setup states.
 * Invented estimator states: not proof of camera or physical convergence. */
public final class SetupFailureRecoveryCheck {
 static int assertions;
 static void check(boolean value){assertions++;if(!value)throw new AssertionError("Setup recovery check "+assertions);}
 static JSONObject row(double t,boolean enoughTilt,boolean integrity)throws Exception{
  return new JSONObject().put("timestampSeconds",t).put("initialized",true).put("integrity",integrity)
   .put("numericalCalibrationReady",true).put("updates",200+(int)(t*20)).put("positionStdMetres",.02)
   .put("cameraValues",new JSONArray(new double[]{400,400,320,240,0,0,0,0}))
   .put("imuToCamera",new JSONArray(new double[]{0,0,0,1,0,0,0}))
   .put("calibrationStd",new JSONArray(new double[15]))
   .put("axisMotionRadians",new JSONArray(new double[]{.6,enoughTilt?.6:.1,.6}))
   .put("timeOffsetSeconds",0).put("readoutSeconds",.01);
 }
 public static void main(String[] args)throws Exception{
  SetupConvergenceGate gate=new SetupConvergenceGate();
  // Equivalent of many retained frames with one missing motion direction.
  for(int i=0;i<=940;i++){gate.observe(row(i*.05,false,true));check(!gate.ready());}
  check(!gate.ready()); // 47 seconds or a large count must not force completion.
  // Supplying the missing direction later recovers in the SAME attempt.
  for(int i=941;i<=1100;i++)gate.observe(row(i*.05,true,true));
  check(gate.ready());
  check(gate.readyAt(55.1));check(gate.diagnostics(55.1).getString("reason").equals("ready"));check(gate.diagnostics(56).getString("reason").equals("stale"));check(!gate.readyAt(56));check(!gate.readyAt(Double.NaN));
  gate.observe(row(55.05,true,false));check(!gate.ready());
  for(int i=1102;i<=1260;i++)gate.observe(row(i*.05,true,true));check(gate.ready());
  // A freeze/gap cannot remain ready; continuing healthy data recovers.
  gate.observe(row(65,true,true));check(!gate.ready());
  for(int i=1;i<=130;i++)gate.observe(row(65+i*.05,true,true));check(gate.ready());
  try{gate.observe(row(71.5,true,true));throw new AssertionError("Duplicate timestamp accepted");}
  catch(IllegalArgumentException expected){assertions++;}
  check(!gate.ready());
  for(int i=1;i<=130;i++)gate.observe(row(72+i*.05,true,true));check(gate.ready());
  SetupConvergenceGate sparse=new SetupConvergenceGate();
  for(int i=0;i<=55;i++)sparse.observe(row(i*.1,true,true));check(!sparse.ready());check(sparse.diagnostics(5.5).getString("reason").equals("slow-frames"));
  SetupConvergenceGate changing=new SetupConvergenceGate();for(int i=0;i<=130;i++){JSONObject r=row(i*.05,true,true);r.getJSONArray("cameraValues").put(2,320+(i%2==0?3:-3));changing.observe(r);}check(!changing.ready());check(changing.diagnostics(6.5).getString("reason").equals("fit-changing"));
  System.out.println("PASS: "+assertions+" setup failure/recovery assertions; software states only.");
 }
}
