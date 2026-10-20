package expo.modules.gaitcalibration;
import java.util.*;
import org.json.JSONObject;

/** Production completion gate: same five-second checks as saved admission. */
public final class SetupConvergenceGate {
 private final List<JSONObject> tail=new ArrayList<>();
 private double last=Double.NEGATIVE_INFINITY;
 public void observe(JSONObject row)throws Exception{
  double time=row.getDouble("timestampSeconds");
  if(!Double.isFinite(time)||time<=last){tail.clear();last=Double.NEGATIVE_INFINITY;throw new IllegalArgumentException("Invalid setup tracking timestamps");}
  last=time;tail.add(row);
  while(tail.size()>1&&time-tail.get(0).getDouble("timestampSeconds")>5.5)tail.remove(0);
 }
 public boolean ready(){try{OnDeviceProfile.checkStableTail(tail);return true;}catch(Exception e){return false;}}
 public boolean readyAt(double nowSeconds){return Double.isFinite(nowSeconds)&&nowSeconds>=last&&nowSeconds-last<=.3&&ready();}
 /** Explain the existing gate; diagnostics never change its acceptance rules. */
 public JSONObject diagnostics(double nowSeconds)throws Exception{
  double span=tail.isEmpty()?0:last-tail.get(0).getDouble("timestampSeconds");
  String reason="collecting";
  if(!Double.isFinite(nowSeconds)||tail.isEmpty())reason="no-readings";
  else if(nowSeconds<last||nowSeconds-last>.3)reason="stale";
  else try{OnDeviceProfile.checkStableTail(tail);reason="ready";}
  catch(Exception e){String message=String.valueOf(e.getMessage());
   if(span>=5&&tail.size()<60)reason="slow-frames";
   else if(message.contains("has a gap"))reason="tracking-gap";
   else if(message.contains("still changing"))reason="fit-changing";
   else if(span>=5&&tail.size()>=60)reason="fit-quality";
  }
  return new JSONObject().put("reason",reason).put("frames",tail.size()).put("windowSeconds",span)
   .put("ageSeconds",Double.isFinite(nowSeconds)&&!tail.isEmpty()?nowSeconds-last:JSONObject.NULL);
 }
}
