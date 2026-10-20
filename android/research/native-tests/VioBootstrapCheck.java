package expo.modules.gaitcalibration;
import java.io.*;
import java.util.*;
import org.json.*;

/** Executes the real Java handoff/resampling with a controlled solver boundary.
 * Does not simulate Android hardware or establish physical distance accuracy. */
public final class VioBootstrapCheck {
  static int assertions=0;
  static final long BASE=100000000000L;
  static void check(boolean b){assertions++;if(!b)throw new AssertionError("check "+assertions);}
  interface Action{void run()throws Exception;}
  static void rejects(Action a,String message)throws Exception{
    try{a.run();throw new AssertionError("Expected rejection: "+message);}
    catch(IllegalArgumentException e){check(e.getMessage().contains(message));}
  }
  static final class SolverBoundary implements OnDeviceVio.Engine {
    final List<Long> times=new ArrayList<>();int frames=0,motionCalls=0,endCalls=0;boolean closed=false;
    double firstX=Double.NaN,routeX=0;
    public void imu(long ns,double ax,double ay,double az,double gx,double gy,double gz){
      if(times.isEmpty())firstX=ax;times.add(ns);
    }
    public String frame(long ns,String name,double skew){
      check(!times.isEmpty()&&times.get(0)/1e9<=ns/1e9-skew/2);
      check(times.get(times.size()-1)/1e9>=ns/1e9+skew/2);
      frames++;return "{\"timestampSeconds\":"+ns/1e9+",\"timeOffsetSeconds\":0,\"initialized\":true,\"integrity\":true,\"positionStdMetres\":0.02,\"state\":{\"imu_time_s\":"+ns/1e9+",\"px\":"+routeX+",\"py\":0,\"pz\":0}}";
    }
    public void beginMotion(){motionCalls++;} public void endMotion(){endCalls++;} public void close(){closed=true;}
  }
  static JSONObject timing()throws Exception{return new JSONObject().put("exposureNs",10000000).put("rollingShutterSkewNs",20000000);}
  static void samples(VioBootstrap.SensorSink sink,int start,int end)throws Exception{
    for(int i=start;i<=end;i++){
      long t=BASE+i*5000000L;
      sink.sensor("accelerometer",t,i,0,9.8);
      sink.sensor("gyroscope",t+1000000L,0,0,0);
    }
  }
  public static void main(String[] args)throws Exception{
    VioBootstrap.PendingImu early=new VioBootstrap.PendingImu();
    samples(early::add,0,39);early.add("magnetometer",BASE,1,2,3);
    SolverBoundary solver=new SolverBoundary();StringWriter states=new StringWriter();
    OnDeviceVio vio=new OnDeviceVio(solver,states,0);
    early.replay(vio::sensor);check(early.replayed()==80);check(solver.times.get(0)==BASE+1000000L);
    check(Math.abs(solver.firstX-.2)<1e-10); // Interpolated only between measured accelerometer points.
    vio.frame(BASE+10000000L,new File("fixture.jpg"),timing());check(solver.frames==0);
    samples(vio::sensor,40,60);check(solver.frames==1);
    early.replay(vio::sensor);check(early.replayed()==80);
    check(solver.motionCalls==0);
    vio.beginMotion();check(solver.motionCalls==1);
    vio.beginMotion();check(solver.motionCalls==1);
    vio.endMotion();check(solver.endCalls==1);vio.endMotion();check(solver.endCalls==1);
    vio.close();check(solver.closed);
    check(new JSONObject(states.toString().trim()).has("timestampSeconds"));

    // Controlled coordinate stream exercises the actual tracker lifecycle and
    // 1 m lead-in + 10 m timed zone + 1 m lead-out boundary attachment.
    solver=new SolverBoundary();states=new StringWriter();vio=new OnDeviceVio(solver,states,0);
    samples(vio::sensor,0,50);vio.frame(BASE+10000000L,new File("route-start.jpg"),timing());
    vio.endMotion();check(solver.endCalls==0);
    vio.begin(BASE+30000000L,true);check(solver.motionCalls==1);check(vio.finishNs()==0);
    for(int i=1;i<=121;i++){
      samples(vio::sensor,51+(i-1)*20,70+(i-1)*20);solver.routeX=i*.1;
      vio.frame(BASE+i*100000000L-15000000L,new File("route.jpg"),timing());
      if(i<120)check(vio.finishNs()==0&&solver.endCalls==0);
    }
    check(vio.finishNs()==BASE+12000000000L);check(solver.endCalls==1);
    check(vio.status().getJSONObject("walkProgress").getBoolean("complete"));
    vio.endMotion();check(solver.endCalls==1);vio.close();

    // Without the early readings the original first frame is uncovered. Withhold
    // that bootstrap frame, then accept a later fully measured frame.
    solver=new SolverBoundary();states=new StringWriter();vio=new OnDeviceVio(solver,states,0);
    samples(vio::sensor,20,90);
    vio.frame(BASE,new File("uncovered.jpg"),timing());check(solver.frames==0);
    check(vio.bootstrapDiagnostics().getInt("framesWithheld")==1);
    vio.frame(BASE+150000000L,new File("covered.jpg"),timing());check(solver.frames==1);
    // It must never silently skip missing history after tracking has begun.
    final OnDeviceVio active=vio;
    rejects(()->active.frame(BASE,new File("late-old.jpg"),timing()),"during tracking");
    vio.close();check(new JSONObject(states.toString().trim()).has("timestampSeconds"));

    VioBootstrap.CameraCoverage coverage=new VioBootstrap.CameraCoverage();
    for(int i=0;i<100;i++)coverage.imu(BASE+i*5000000L);
    check(!coverage.camera(BASE-50000000L,20000000L,.02));
    check(coverage.camera(BASE-10000000L,20000000L,.04)); // Saved profile offset applies at startup.
    final VioBootstrap.CameraCoverage tracked=coverage;
    rejects(()->tracked.camera(BASE-10000000L,20000000L,0),"during tracking");
    rejects(()->tracked.imu(BASE),"did not advance");
    coverage=new VioBootstrap.CameraCoverage();coverage.imu(BASE);coverage.imu(BASE+100000000L);
    check(!coverage.camera(BASE+50000000L,10000000L,0)); // Sparse readout must not pass.
    for(int i=1;i<20;i++)check(!coverage.camera(BASE+50000000L,10000000L,0));
    final VioBootstrap.CameraCoverage sparse=coverage;
    rejects(()->sparse.camera(BASE+50000000L,10000000L,0),"startup coverage");
    coverage=new VioBootstrap.CameraCoverage();check(!coverage.camera(BASE,10000000L,0));
    final VioBootstrap.CameraCoverage timeout=coverage;
    rejects(()->timeout.camera(BASE+1000000001L,10000000L,0),"startup coverage");
    rejects(()->timeout.camera(BASE,10000000L,Double.NaN),"timing");
    early=new VioBootstrap.PendingImu();
    for(int i=0;i<4096;i++)early.add("accelerometer",BASE+i,0,0,9.8);
    final VioBootstrap.PendingImu full=early;
    rejects(()->full.add("gyroscope",BASE+4096,0,0,0),"buffer filled");
    early=new VioBootstrap.PendingImu();early.add("accelerometer",BASE,0,0,9.8);
    final VioBootstrap.PendingImu late=early;
    rejects(()->late.add("gyroscope",BASE+10000000001L,0,0,0),"buffer filled");
    System.out.println("PASS: "+assertions+" Java bootstrap/transport assertions; controlled solver boundary, not physical validation.");
  }
}
