package expo.modules.gaitcalibration;
import org.json.*;
import java.io.*;

/** Result delivery uses the saved live states, not a second scaled estimator. */
public final class OnDeviceResults {
 public static String process(File files,String id)throws Exception{
  OnDeviceProfile.require(id.matches("[a-zA-Z0-9_-]{1,160}"),"Invalid recording identifier");
  File folder=new File(files,"gait-camera-captures/gait-camera-"+id),archive=new File(folder.getPath()+".zip");
  JSONObject m=OnDeviceProfile.read(new File(folder,"manifest.json")),p=OnDeviceProfile.read(new File(folder,"reference-calibration.json"));
  OnDeviceProfile.validate(p,m);
  OnDeviceProfile.require(m.getString("kind").equals("gait-camera-imu-distance-capture-v1")&&m.getString("sessionId").equals(id)&&m.getString("status").equals("completed")&&m.isNull("error")&&m.getString("timestampSource").equals("realtime"),"Camera capture did not complete");
  JSONArray states=new JSONArray();double last=0,processing=0;
  boolean fullLens=ReferenceTrackingProfile.METHOD.equals(p.optString("method"));
  try(BufferedReader r=new BufferedReader(new FileReader(new File(folder,"on-device-states.ndjson")))){String line;while((line=r.readLine())!=null){JSONObject row=new JSONObject(line);if(fullLens)OnDeviceProfile.require(!row.isNull("fixedLensK3")&&row.getDouble("fixedLensK3")==p.getJSONObject("fit").getDouble("fixedLensK3"),"Tracker did not use the saved full lens model");double t=row.getJSONObject("state").getDouble("imu_time_s");OnDeviceProfile.require(t>last&&states.length()<30000,"Invalid live tracking timestamps");last=t;processing+=row.getDouble("processingSeconds");states.put(row.getJSONObject("state"));}}
  return new JSONObject().put("manifest",m).put("reference",p).put("sourceSha256",OnDeviceProfile.sha(archive)).put("captureEndSeconds",last).put("states",states)
   .put("processingRevision","android-openvins-live-v1").put("processingLocation","phone").put("processingSeconds",processing)
   .put("noiseSource","provisional-continuous-time-density").put("noiseProfileSha256",JSONObject.NULL)
   .put("initializationStartNs",states.length()==0?JSONObject.NULL:(long)(states.getJSONObject(0).getDouble("imu_time_s")*1e9)).put("baselineAdaptation",JSONObject.NULL).toString();
 }
}
