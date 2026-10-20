package expo.modules.gaitcalibration;

import org.json.*;
import java.io.*;
import java.util.*;

/** All calls are serialized on the capture processing thread. No network code. */
public final class OnDeviceVio implements AutoCloseable {
  private static native long nativeStart(String file);
  private static native void nativeImu(long handle,long ns,double ax,double ay,double az,double gx,double gy,double gz);
  private static native String nativeFrame(long handle,long ns,String filename,double skew);
  private static native void nativeStop(long handle);
  private static native void nativeBeginMotion(long handle);
  private static native void nativeEndMotion(long handle);
  interface Engine {
    void imu(long ns,double ax,double ay,double az,double gx,double gy,double gz);
    String frame(long ns,String filename,double skew);
    void beginMotion(); void endMotion(); void close();
  }
  private boolean motionStarted=false,motionEnded=false;
  public void beginMotion(){if(!motionStarted){engine.beginMotion();motionStarted=true;}}
  public void endMotion(){if(motionStarted&&!motionEnded){engine.endMotion();motionEnded=true;}}
  private final Engine engine;
  private final BufferedWriter output;
  private final List<double[]> accel=new ArrayList<>(),gyro=new ArrayList<>();
  private final ArrayDeque<Frame> frames=new ArrayDeque<>();
  private final VioBootstrap.CameraCoverage coverage=new VioBootstrap.CameraCoverage();
  private final double initialOffsetSeconds;
  private int displayRotationDegrees=0;
  private long lastImu=0;private boolean closed=false;
  private volatile JSONObject latest=null;
  private final SetupConvergenceGate convergence=new SetupConvergenceGate();
  public boolean setupSettled(long nowNs){return convergence.readyAt(nowNs/1e9);}
  public JSONObject setupCheck(long nowNs)throws Exception{return convergence.diagnostics(nowNs/1e9);}
  private LiveDistanceGate boundary=null;
  public void begin(long ns,boolean tenMetre)throws Exception{beginMotion();if(tenMetre){boundary=new LiveDistanceGate();boundary.begin(ns,latest);}}
  public long finishNs(){return boundary==null?0:boundary.finishNs();}
  public JSONObject tenMetreBoundaries()throws Exception{return boundary==null?null:boundary.snapshot();}
  private static final class Frame{long time;File file;JSONObject timing;Frame(long t,File f,JSONObject r){time=t;file=f;timing=r;}}
  public OnDeviceVio(File dir,JSONObject camera,JSONObject profile)throws Exception{
    System.loadLibrary("gait_openvins");
    displayRotationDegrees=camera.optInt("displayRotationDegrees",0);
    OnDeviceProfile.require(displayRotationDegrees==0||displayRotationDegrees==90||displayRotationDegrees==180||displayRotationDegrees==270,"Invalid guidance screen rotation");
    JSONObject seed=profile==null?camera.getJSONObject("opticalPrior"):profile.getJSONObject("fit");
    initialOffsetSeconds=profile==null?0:seed.getDouble("timeOffsetSeconds");
    double[] k=OnDeviceProfile.values(seed.getJSONArray("cameraValues"),8),e=OnDeviceProfile.values(seed.getJSONArray("imuToCamera"),7);
    File config=new File(dir,"on-device-config.yaml");
    try(Writer w=new FileWriter(config)){w.write("%YAML:1.0\n---\ncalibrating: "+(profile==null?1:0)+"\n");matrix(w,"intrinsics",k);matrix(w,"extrinsics",e);if(profile!=null&&ReferenceTrackingProfile.METHOD.equals(profile.optString("method")))w.write("reference_lens_k3: "+seed.getDouble("fixedLensK3")+"\n");w.write("td: "+(profile==null?0:seed.getDouble("timeOffsetSeconds"))+"\nacc_noise_density: 0.0057\ngyro_noise_density: 0.000283\n");}
    output=new BufferedWriter(new FileWriter(new File(dir,"on-device-states.ndjson")));
    final long handle=nativeStart(config.getAbsolutePath());OnDeviceProfile.require(handle>0,"On-phone tracking did not start");
    engine=new Engine(){
      public void imu(long ns,double ax,double ay,double az,double gx,double gy,double gz){nativeImu(handle,ns,ax,ay,az,gx,gy,gz);}
      public String frame(long ns,String filename,double skew){return nativeFrame(handle,ns,filename,skew);}
      public void beginMotion(){nativeBeginMotion(handle);}public void endMotion(){nativeEndMotion(handle);}public void close(){nativeStop(handle);}
    };
  }
  // Host transport controls inject only the solver boundary; production always uses JNI.
  OnDeviceVio(Engine engine,Writer output,double offset){this.engine=engine;this.output=new BufferedWriter(output);initialOffsetSeconds=offset;}
  private static void matrix(Writer w,String name,double[] a)throws Exception{w.write(name+": !!opencv-matrix\n   rows: "+a.length+"\n   cols: 1\n   dt: d\n   data: [");for(int i=0;i<a.length;i++)w.write((i==0?"":", ")+a[i]);w.write("]\n");}
  public void sensor(String name,long ns,double x,double y,double z)throws Exception{
    if(closed)return;
    if(name.equals("accelerometer"))accel.add(new double[]{ns,x,y,z});else if(name.equals("gyroscope"))gyro.add(new double[]{ns,x,y,z});else return;
    while(!gyro.isEmpty()&&accel.size()>=2&&accel.get(accel.size()-1)[0]>=gyro.get(0)[0]){
      double[] g=gyro.remove(0);while(accel.size()>2&&accel.get(1)[0]<=g[0])accel.remove(0);
      double[] a=accel.get(0),b=accel.get(1);if(g[0]<a[0])continue;
      OnDeviceProfile.require(b[0]>a[0]&&b[0]-a[0]<=20000000,"Acceleration stream has a gap");
      double f=(g[0]-a[0])/(b[0]-a[0]);engine.imu((long)g[0],a[1]*(1-f)+b[1]*f,a[2]*(1-f)+b[2]*f,a[3]*(1-f)+b[3]*f,g[1],g[2],g[3]);lastImu=(long)g[0];coverage.imu(lastImu);
    }
    OnDeviceProfile.require(accel.size()<100&&gyro.size()<100,"One motion sensor stopped responding");drain();
  }
  public void frame(long timestamp,File image,JSONObject timing)throws Exception{
    if(closed)return;OnDeviceProfile.require(frames.size()<8,"This phone could not keep up with camera tracking");
    frames.add(new Frame(timestamp,image,timing));drain();
  }
  private void drain()throws Exception{
    while(!frames.isEmpty()){
      Frame f=frames.peek();long exposure=f.timing.getLong("exposureNs"),skew=f.timing.getLong("rollingShutterSkewNs");
      OnDeviceProfile.require(exposure>=0&&skew>=0&&skew<=100000000,"Camera timing is unavailable");
      long midpoint=f.time+(exposure+skew)/2;
      double offset=latest==null?initialOffsetSeconds:latest.optDouble("timeOffsetSeconds",initialOffsetSeconds);
      if(lastImu<midpoint+Math.max(200000000L,(long)((Math.abs(offset)+skew/2e9+.01)*1e9)))return;
      if(!coverage.camera(midpoint,skew,offset)) {
        frames.remove();continue;
      }
      frames.remove();long processingAt=System.nanoTime();JSONObject next=new JSONObject(engine.frame(midpoint,f.file.getAbsolutePath(),skew/1e9));next.put("processingSeconds",(System.nanoTime()-processingAt)/1e9);next.put("displayRotationDegrees",displayRotationDegrees);convergence.observe(next);if(boundary!=null){JSONObject progress=boundary.observe(next);next.put("walkProgress",progress);if(progress.optBoolean("complete"))endMotion();}output.write(next.toString()+"\n");latest=next;
    }
  }
  public JSONObject status(){return latest;}
  public JSONObject bootstrapDiagnostics()throws JSONException{return new JSONObject().put("framesWithheld",coverage.skipped()).put("syntheticImuUsed",false);}
  public boolean trackingReady(long nowNs){JSONObject s=latest;if(s==null||s.optJSONObject("state")==null)return false;double age=nowNs/1e9-s.optJSONObject("state").optDouble("imu_time_s",0);return age>=0&&age<=.3&&s.optBoolean("initialized")&&s.optBoolean("integrity")&&s.optDouble("positionStdMetres",100)<.15;}
  @Override public void close()throws Exception{if(closed)return;closed=true;try{output.close();}finally{engine.close();}}
}
