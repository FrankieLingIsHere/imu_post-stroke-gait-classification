package expo.modules.gaitcalibration;
import org.json.*;
/** Exercises the production live monitor; software poses, not physical accuracy evidence. */
public final class TenMetreBoundaryReplayCheck {
 public static void main(String[] args)throws Exception{
  LiveDistanceGate gate=new LiveDistanceGate();
  gate.begin(1000000000L,OnDeviceFlowCheck.state(1,0,0,0));
  JSONArray rows=new JSONArray();
  for(int i=0;i<=344;i++){
   double t=i*.05,x=Math.max(0,Math.min(12,t-1)),y=x<1?0:Math.min(.15,(x-1)*.02);
   JSONObject frame=OnDeviceFlowCheck.state(t,x,y,0),s=frame.getJSONObject("state");
   s.put("initialized",1).put("position_std_m",.02).put("vx",x>0&&x<12?1:0).put("vy",0).put("vz",0)
    .put("ba_norm",.01).put("bg_norm",.001).put("tic_norm",.04).put("g_norm",9.80665).put("rotation_change_deg",0).put("reboot",0);
   rows.put(s);
   if(t>1&&gate.finishNs()==0)gate.observe(frame);
  }
  JSONObject q=gate.snapshot();
  if(!q.getBoolean("usable")||q.getLong("timedStartBootNs")!=2000000000L||q.getLong("timedEndBootNs")!=12000000000L||gate.finishNs()!=13000000000L)throw new AssertionError(q.toString());
  System.out.println(new JSONObject().put("states",rows).put("boundaries",q));
 }
}
