package expo.modules.gaitcalibration;
import java.io.*;
import java.util.*;
import org.json.JSONObject;

/** Baseline admission on paired real replay readings or labelled analytic controls. */
public final class SetupBaselineReplayCheck {
 public static void main(String[] args)throws Exception {
  List<double[]> imu=new ArrayList<>();try(BufferedReader input=new BufferedReader(new FileReader(args[0]))){input.readLine();String line;while((line=input.readLine())!=null){String[] parts=line.split(",");double[] row=new double[7];for(int i=0;i<7;i++)row[i]=Double.parseDouble(parts[i]);imu.add(row);}}
  long cue=Long.parseLong(args[2]),firstReady=0;int index=0,states=0,before=0,eligibleBefore=0,initializedBefore=0;
  SetupBaselineGate gate=new SetupBaselineGate();
  try(BufferedReader input=new BufferedReader(new FileReader(args[1]))){String line;while((line=input.readLine())!=null){JSONObject status=new JSONObject(line);long ns=(long)(status.getDouble("timestampSeconds")*1e9);
   while(index<imu.size()&&(long)imu.get(index)[0]<ns+200000000L){double[] r=imu.get(index++);gate.sensor("gyroscope",(long)r[0],r[1],r[2],r[3]);gate.sensor("accelerometer",(long)r[0],r[4],r[5],r[6]);}
   long now=(long)imu.get(Math.max(0,index-1))[0];boolean ready=gate.ready(now,status);states++;
   if(ready&&firstReady==0)firstReady=now;
   if(ns<cue){before++;if(ready)eligibleBefore++;if(status.optBoolean("initialized"))initializedBefore++;}
  }}
  if(states==0)throw new AssertionError("No replay states");
  System.out.println(new JSONObject().put("states",states).put("oldMovementCueBootNs",cue).put("statesBeforeOldCue",before).put("initializedBeforeOldCue",initializedBefore).put("eligibleBeforeOldCue",eligibleBefore).put("firstEligibleBaselineBootNs",firstReady==0?JSONObject.NULL:firstReady).put("oldCueWouldBeBlocked",eligibleBefore==0).put("physicalAndroidExecution",false).toString());
 }
}
