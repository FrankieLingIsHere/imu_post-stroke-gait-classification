package expo.modules.gaitcalibration;

import java.util.ArrayDeque;

/** Serialized capture-thread handoff of real observations, never synthetic IMU. */
public final class VioBootstrap {
  private VioBootstrap() {}
  public interface SensorSink {
    void sensor(String name, long ns, double x, double y, double z) throws Exception;
  }
  public static final class PendingImu {
    private static final class Sample {
      final String name; final long ns; final double x,y,z;
      Sample(String name,long ns,double x,double y,double z) {
        this.name=name;this.ns=ns;this.x=x;this.y=y;this.z=z;
      }
    }
    private final ArrayDeque<Sample> pending=new ArrayDeque<>();
    private long firstNs=0;
    private int replayed=0;
    public void add(String name,long ns,double x,double y,double z) {
      if(!name.equals("accelerometer")&&!name.equals("gyroscope"))return;
      if(firstNs==0)firstNs=ns;
      if(pending.size()>=4096||ns-firstNs>10000000000L)
        throw new IllegalArgumentException("Camera did not become ready before the IMU startup buffer filled");
      pending.addLast(new Sample(name,ns,x,y,z));
    }
    public void replay(SensorSink sink)throws Exception {
      while(!pending.isEmpty()) {
        Sample s=pending.peekFirst();sink.sensor(s.name,s.ns,s.x,s.y,s.z);
        pending.removeFirst();replayed++;
      }
    }
    public int replayed(){return replayed;}
  }
  /** Same two-second history and readout window as the strict native solver. */
  public static final class CameraCoverage {
    private final ArrayDeque<Long> imu=new ArrayDeque<>();
    private boolean started=false;
    private int skipped=0;
    private long firstCameraNs=0;
    public void imu(long ns) {
      if(!imu.isEmpty()&&ns<=imu.peekLast())
        throw new IllegalArgumentException("IMU timestamp did not advance");
      imu.addLast(ns);
      while(ns-imu.peekFirst()>2000000000L)imu.removeFirst();
      if(imu.size()>4096)throw new IllegalArgumentException("IMU history exceeded its safety limit");
    }
    public boolean camera(long midpointNs,long skewNs,double offsetSeconds) {
      if(!Double.isFinite(offsetSeconds)||skewNs<0||skewNs>100000000L)
        throw new IllegalArgumentException("Camera timing is unavailable");
      double t=midpointNs/1e9,skew=skewNs/1e9,center=t+offsetSeconds;
      boolean covered=!imu.isEmpty()&&imu.peekFirst()/1e9<=center-skew/2&&imu.peekLast()/1e9>=center+skew/2;
      if(covered&&skewNs>0) {
        int count=0;
        for(long ns:imu)if(Math.abs(ns/1e9-center)<=skew/2+.005)count++;
        covered=count>=2;
      }
      if(covered){started=true;return true;}
      // Only bootstrap frames may be withheld. Later missing data is a failure.
      if(started)throw new IllegalArgumentException("Missing rolling shutter IMU coverage during tracking");
      if(firstCameraNs==0)firstCameraNs=midpointNs;
      if(++skipped>20||midpointNs-firstCameraNs>1000000000L)
        throw new IllegalArgumentException("Camera and IMU did not establish startup coverage");
      return false;
    }
    public int skipped(){return skipped;}
  }
}
