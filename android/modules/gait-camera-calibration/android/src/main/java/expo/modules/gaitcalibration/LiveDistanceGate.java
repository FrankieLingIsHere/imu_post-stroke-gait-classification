package expo.modules.gaitcalibration;
import org.json.*;

/** Monotonic 1 + 10 + 1 m boundaries from accepted live poses, never step counts. */
public final class LiveDistanceGate {
 private double[] origin,axis;private double previousTime,previousAlong;
 private boolean begun=false,failed=false,complete=false;private long started=0,end=0,timedStart=0,timedEnd=0;
 public long finishNs(){return end;}
 public JSONObject snapshot()throws Exception{
  return new JSONObject().put("version","ten-metre-boundaries-v1").put("usable",begun&&!failed&&complete&&timedStart>started&&timedEnd>timedStart)
   .put("startBootNs",started).put("timedStartBootNs",timedStart).put("timedEndBootNs",timedEnd).put("finishBootNs",end)
   .put("origin",origin==null?JSONObject.NULL:new JSONArray(origin)).put("axis",axis==null?JSONObject.NULL:new JSONArray(axis));
 }
 public void begin(long ns,JSONObject status)throws Exception{
  OnDeviceProfile.require(!begun&&valid(status)&&time(status)<=ns/1e9&&ns/1e9-time(status)<=.2,"Live tracking is not ready to begin");
  origin=position(status);started=ns;previousTime=ns/1e9;previousAlong=0;begun=true;
 }
 private static double time(JSONObject r)throws Exception{return r.getJSONObject("state").getDouble("imu_time_s");}
 private static double[] position(JSONObject r)throws Exception{JSONObject s=r.getJSONObject("state");return new double[]{s.getDouble("px"),s.getDouble("py")};}
 private static boolean valid(JSONObject r)throws Exception{return r!=null&&r.getBoolean("initialized")&&r.getBoolean("integrity")&&Double.isFinite(r.getDouble("positionStdMetres"))&&r.getDouble("positionStdMetres")>=0&&r.getDouble("positionStdMetres")<=.15;}
 public JSONObject observe(JSONObject r)throws Exception{
  if(!begun)return new JSONObject().put("usable",false).put("zone","waiting").put("complete",false);
  if(!valid(r))failed=true;
  double t=time(r);double[] p=position(r);double dx=p[0]-origin[0],dy=p[1]-origin[1],distance=Math.hypot(dx,dy);
  if(t<=previousTime)return new JSONObject().put("usable",!failed).put("zone",failed?"unavailable":"approach").put("complete",false);
  if(t-previousTime>.2||!Double.isFinite(distance))failed=true;
  if(axis==null&&distance>=.8)axis=new double[]{dx/distance,dy/distance};
  double along=axis==null?distance:dx*axis[0]+dy*axis[1];
  if(axis!=null&&(Math.abs(dx*axis[1]-dy*axis[0])>Math.max(.25,.15*distance)||along<previousAlong-.2))failed=true;
  if(Math.abs(along-previousAlong)/(t-previousTime)>3)failed=true;
  if(!failed&&!complete){
   if(timedStart==0&&previousAlong<1&&along>=1)timedStart=crossing(1,t,along);
   if(timedEnd==0&&previousAlong<11&&along>=11)timedEnd=crossing(11,t,along);
   if(previousAlong<12&&along>=12){end=crossing(12,t,along);complete=true;}
  }
  previousTime=t;previousAlong=along;
  return new JSONObject().put("usable",!failed).put("zone",failed?"unavailable":complete?"complete":along<1?"approach":along<11?"timed":"finish")
    .put("distanceMetres",Math.max(0,along)).put("complete",complete&&!failed).put("finishBootNs",end==0?JSONObject.NULL:end)
    .put("startBootNs",started).put("targetMetres",12).put("boundarySource","on-device-estimated-trajectory-crossing");
 }
 private long crossing(double mark,double time,double along){return (long)((previousTime+(mark-previousAlong)/(along-previousAlong)*(time-previousTime))*1e9);}
}
