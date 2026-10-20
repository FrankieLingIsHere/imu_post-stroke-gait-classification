package expo.modules.gaitcalibration;
import org.json.*;
import java.nio.file.*;
import java.io.*;

/** Controlled software fixtures, not recordings or evidence of physical accuracy. */
public final class OnDeviceFlowCheck {
 static int assertions=0;
 static void check(boolean value){assertions++;if(!value)throw new AssertionError("check "+assertions);}
 static JSONObject state(double time,double x,double y,double z)throws Exception{
  return new JSONObject().put("initialized",true).put("integrity",true).put("positionStdMetres",.02)
   .put("timestampSeconds",time-.04).put("state",new JSONObject().put("imu_time_s",time).put("px",x).put("py",y).put("pz",z));
 }
 static JSONObject fit(double time)throws Exception{
  return state(time,0,0,0).put("numericalCalibrationReady",true).put("updates",500)
   .put("cameraValues",new JSONArray(new double[]{400,400,320,240,0,0,0,0}))
   .put("imuToCamera",new JSONArray(new double[]{0,0,0,1,0,0,0}))
   .put("calibrationStd",new JSONArray(new double[]{2,2,1,1,.01,.01,.001,.001,.01,.01,.01,.005,.005,.005,.0005}))
   .put("axisMotionRadians",new JSONArray(new double[]{1,1,1})).put("timeOffsetSeconds",.04).put("readoutSeconds",.02);
 }
 public static void main(String[] args)throws Exception{
  LiveDistanceGate gate=new LiveDistanceGate();gate.begin(1000000000L,state(1,0,0,0));
  for(int i=1;i<=500;i++){JSONObject s=gate.observe(state(1+i*.05,0,0,Math.sin(i)*.1));check(!s.getBoolean("complete")&&s.getDouble("distanceMetres")==0);}
  for(int i=1;i<=60;i++)gate.observe(state(26+i*.1,i*.1,0,0));
  for(int i=1;i<=100;i++)check(!gate.observe(state(32+i*.1,6,0,0)).getBoolean("complete"));
  JSONObject done=null;for(int i=1;i<=61;i++)done=gate.observe(state(42+i*.1,6+i*.1,0,0));
  check(done.getBoolean("complete"));check(Math.abs(gate.finishNs()/1e9-48)<1e-7);
  for(int mode=0;mode<4;mode++){
   gate=new LiveDistanceGate();gate.begin(1000000000L,state(1,0,0,0));
   gate.observe(state(1.1,.1,0,0));
   JSONObject bad=mode==0?state(2,.2,0,0):mode==1?state(1.2,4,0,0):mode==2?state(1.2,.2,0,0).put("integrity",false):state(1.2,.2,0,0).put("positionStdMetres",.3);
   check(!gate.observe(bad).getBoolean("usable"));check(!gate.observe(state(1.3,12,0,0)).getBoolean("complete"));
  }
  check(OnDeviceProfile.fitReady(fit(20)));check(!OnDeviceProfile.fitReady(fit(20).put("calibrationStd",new JSONArray(new double[15]).put(0,-1))));
  check(!OnDeviceProfile.fitReady(fit(20).put("axisMotionRadians",new JSONArray(new double[]{0,0,0}))));
  SetupConvergenceGate settling=new SetupConvergenceGate();check(!settling.ready());
  for(int i=0;i<100;i++)settling.observe(fit(40+i*.05));
  check(!settling.ready()); // A timer or one good row cannot replace five seconds.
  settling.observe(fit(45));check(settling.ready());
  settling.observe(fit(45.05).put("numericalCalibrationReady",false));check(!settling.ready());
  for(int i=0;i<109;i++)settling.observe(fit(45.1+i*.05));
  check(!settling.ready());settling.observe(fit(50.65));check(settling.ready());
  try{settling.observe(fit(50));throw new AssertionError("Backwards setup time accepted");}catch(IllegalArgumentException expected){check(!settling.ready());}
  SetupConvergenceGate gapped=new SetupConvergenceGate();gapped.observe(fit(60));
  for(int i=0;i<70;i++)gapped.observe(fit(62+i*.05));
  check(!gapped.ready()); // Enough rows and total span, but missing two seconds.
  Path root=Files.createTempDirectory("gait-on-device-contract-");File dir=root.resolve("camera-calibration/calibration-123").toFile();dir.mkdirs();
  JSONObject m=new JSONObject().put("kind","phone-on-device-setup-capture-v1").put("status","completed").put("error",JSONObject.NULL)
   .put("timestampSource","realtime").put("alignmentMovementStartedBootNs",1000000000L).put("installationId","fixture-phone").put("cameraId","1")
   .put("width",640).put("height",480).put("imageAxes","native-sensor-unrotated-unmirrored").put("sensorOrientationDegrees",270)
   .put("stabilizationRequested","off").put("capturePipeline","native-camera-imu-v3").put("opticalSetup","waist-bag-window");
  Files.write(dir.toPath().resolve("manifest.json"),m.toString().getBytes("UTF-8"));Files.write(root.resolve("camera-calibration/calibration-123.zip"),new byte[]{1,2,3});
  try(Writer w=new FileWriter(new File(dir,"on-device-states.ndjson"))){for(int i=0;i<=120;i++)w.write(fit(20+i*.05).toString()+"\n");}
  JSONObject saved=OnDeviceProfile.finish(root.toFile(),"calibration-123");check(!saved.getBoolean("computerUsed"));check(!saved.getBoolean("independentDistanceValidation"));
  byte[] before=Files.readAllBytes(root.resolve("camera-calibration/on-device-profile.json"));
  m.put("status","interrupted");Files.write(dir.toPath().resolve("manifest.json"),m.toString().getBytes("UTF-8"));
  boolean rejected=false;try{OnDeviceProfile.finish(root.toFile(),"calibration-123");}catch(IllegalArgumentException e){rejected=true;}check(rejected);
  check(java.util.Arrays.equals(before,Files.readAllBytes(root.resolve("camera-calibration/on-device-profile.json"))));
  System.out.println("PASS: "+assertions+" native contract assertions; controlled fixtures only; physical accuracy untested.");
 }
}
