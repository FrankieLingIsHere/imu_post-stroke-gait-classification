package expo.modules.gaitcalibration;
import org.json.*;
import java.io.*;
/** Actual production live completion gate on synthetic/retained host states. */
public final class SetupConvergenceReplayCheck {
 public static void main(String[] args)throws Exception{
  SetupConvergenceGate gate=new SetupConvergenceGate();double minimum=Double.parseDouble(args[1]);
  double first=-1;int eligible=0;
  try(BufferedReader r=new BufferedReader(new FileReader(args[0]))){String line;
   while((line=r.readLine())!=null){JSONObject row=new JSONObject(line);gate.observe(row);double time=row.getDouble("timestampSeconds");
    if(time>=minimum&&gate.ready()){if(first<0)first=time;eligible++;}}
  }
  System.out.println(new JSONObject().put("firstEligibleCompletionSeconds",first<0?JSONObject.NULL:first).put("eligibleFrames",eligible).put("physicalAndroidExecution",false));
 }
}
