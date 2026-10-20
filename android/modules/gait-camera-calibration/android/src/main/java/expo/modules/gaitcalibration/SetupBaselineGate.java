package expo.modules.gaitcalibration;
import java.util.ArrayDeque;
import org.json.JSONObject;

/** Measured quiet baseline before the first-setup movement cue. No timer fallback. */
public final class SetupBaselineGate {
 private static final long WINDOW=2000000000L,MAX_GAP=50000000L,FRESH=500000000L;
 private final ArrayDeque<double[]> acceleration=new ArrayDeque<>(),rotation=new ArrayDeque<>();
 private volatile boolean accepted=false;
 public void sensor(String name,long ns,double x,double y,double z){
  ArrayDeque<double[]> rows=name.equals("accelerometer")?acceleration:name.equals("gyroscope")?rotation:null;
  if(rows==null||accepted)return;
  double norm=Math.sqrt(x*x+y*y+z*z);
  if(!Double.isFinite(norm)||ns<=0){rows.clear();return;}
  if(!rows.isEmpty()&&(ns<=(long)rows.peekLast()[0]||ns-(long)rows.peekLast()[0]>MAX_GAP))rows.clear();
  rows.addLast(new double[]{ns,norm});
  while(rows.size()>1&&ns-(long)rows.peekFirst()[0]>WINDOW+MAX_GAP)rows.removeFirst();
 }
 public boolean ready(long nowNs,JSONObject status){
  if(accepted)return true;
  if(status==null||!status.optBoolean("initialized")||!status.optBoolean("integrity"))return false;
  JSONObject state=status.optJSONObject("state");if(state==null)return false;
  double age=nowNs/1e9-state.optDouble("imu_time_s",Double.NaN),uncertainty=status.optDouble("positionStdMetres",Double.NaN);
  if(!Double.isFinite(age)||age<0||age>.5||!Double.isFinite(uncertainty)||uncertainty<0||uncertainty>=.15)return false;
  double velocity=0;for(String key:new String[]{"vx","vy","vz"}){double v=state.optDouble(key,Double.NaN);if(!Double.isFinite(v))return false;velocity+=v*v;}
  if(velocity>.05*.05)return false;
  if(!fresh(acceleration,nowNs)||!fresh(rotation,nowNs))return false;
  double mean=0;for(double[] row:acceleration)mean+=row[1];mean/=acceleration.size();
  double variance=0;for(double[] row:acceleration)variance+=(row[1]-mean)*(row[1]-mean);
  if(mean<9.3||mean>10.3||Math.sqrt(variance/acceleration.size())>=.05*9.80665)return false;
  for(double[] row:rotation)if(row[1]>=.08)return false;
  return true;
 }
 private static boolean fresh(ArrayDeque<double[]> rows,long nowNs){return rows.size()>=30&&nowNs-(long)rows.peekLast()[0]>=0&&nowNs-(long)rows.peekLast()[0]<=FRESH&&(long)rows.peekLast()[0]-(long)rows.peekFirst()[0]>=WINDOW;}
 /** Latch at the cue; movement may start while its completed audio is playing. */
 public void accept(long nowNs,JSONObject status){if(!ready(nowNs,status))throw new IllegalArgumentException("Quiet phone baseline is not ready");accepted=true;}
 public boolean accepted(){return accepted;}
}
