package expo.modules.gaitcalibration;
import org.json.*;
import java.io.*;
import java.nio.file.*;

/** Retained development replay: no camera hardware, no clinical validation claim. */
public final class ReferencePipelineReplayCheck {
 static void rejects(JSONObject p,JSONObject b)throws Exception{boolean failed=false;try{OnDeviceProfile.validate(p,b);}catch(Exception e){failed=true;}if(!failed)throw new AssertionError("Incompatible profile accepted");}
 public static void main(String[] args)throws Exception{
  JSONObject ref=OnDeviceProfile.read(new File(args[0])),manifest=OnDeviceProfile.read(new File(args[1]));
  JSONObject binding=new JSONObject();for(String key:OnDeviceProfile.KEYS)binding.put(key,manifest.get(key));binding.put("capturePipeline","native-camera-imu-v3");
  JSONObject profile=ReferenceTrackingProfile.create(ref,binding);OnDeviceProfile.validate(profile,binding);
  for(String key:new String[]{"installationId","cameraId","imageAxes","opticalSetup","capturePipeline"}){JSONObject b=new JSONObject(binding.toString());b.put(key,"incompatible");rejects(profile,b);}
  for(String key:new String[]{"width","height","sensorOrientationDegrees"}){JSONObject b=new JSONObject(binding.toString());b.put(key,1);rejects(profile,b);}
  JSONObject mutated=new JSONObject(profile.toString());mutated.getJSONObject("fit").getJSONArray("imuToCamera").put(4,.2);rejects(mutated,binding);
  mutated=new JSONObject(profile.toString());mutated.put("numericalCalibrationReady",true);rejects(mutated,binding);
  mutated=new JSONObject(profile.toString());mutated.put("method",OnDeviceProfile.METHOD);rejects(mutated,binding);
  mutated=new JSONObject(profile.toString());mutated.getJSONObject("sourceReference").put("distanceReady",true);rejects(mutated,binding);
  mutated=new JSONObject(profile.toString());mutated.getJSONObject("fit").put("fixedLensK3",0);rejects(mutated,binding);
  mutated=new JSONObject(profile.toString());mutated.getJSONObject("fit").remove("fixedLensK3");rejects(mutated,binding);
  mutated=new JSONObject(profile.toString());mutated.put("geometryConversion","radtan5-to-radtan4-k3-omitted-v1");rejects(mutated,binding);
  Path root=Paths.get(args[3]),folder=root.resolve("gait-camera-captures/gait-camera-retained-replay");Files.createDirectories(folder);
  if(!manifest.optString("status").equals("quiet-stop")||!manifest.isNull("error"))throw new AssertionError("Not a completed retained research trial");
  manifest.put("sourceStatus",manifest.getString("status")).put("status","completed").put("kind","gait-camera-imu-distance-capture-v1").put("sessionId","retained-replay").put("captureId","gait-camera-retained-replay").put("protocol","research-walk").put("capturePipeline","native-camera-imu-v3");
  // Staging metadata records adapter identity; original capture stays untouched.
  manifest.put("localReplay",true).put("sourceCaptureId",OnDeviceProfile.read(new File(args[1])).getString("captureId"));
  Files.writeString(folder.resolve("manifest.json"),manifest.toString());Files.writeString(folder.resolve("reference-calibration.json"),profile.toString());
  Files.copy(Paths.get(args[2]),folder.resolve("on-device-states.ndjson"),StandardCopyOption.REPLACE_EXISTING);
  Files.copy(Paths.get(args[4]),Paths.get(folder+".zip"),StandardCopyOption.REPLACE_EXISTING);
  String delivered=OnDeviceResults.process(root.toFile(),"retained-replay");Files.writeString(root.resolve("delivered-result.json"),delivered);
  Path stateFile=folder.resolve("on-device-states.ndjson");String original=Files.readString(stateFile);int newline=original.indexOf('\n');
  for(boolean missing:new boolean[]{true,false}){
    JSONObject first=new JSONObject(original.substring(0,newline));if(missing)first.remove("fixedLensK3");else first.put("fixedLensK3",0);
    boolean rejected=false;
    try{Files.writeString(stateFile,first.toString()+original.substring(newline));OnDeviceResults.process(root.toFile(),"retained-replay");}catch(IllegalArgumentException error){rejected=true;}finally{Files.writeString(stateFile,original);}
    if(!rejected)throw new AssertionError("Inconsistent live lens model accepted");
  }
  Files.writeString(root.resolve("reference-profile.json"),profile.toString());
  if(profile.getBoolean("numericalCalibrationReady")||!profile.getBoolean("computerUsed")||profile.getBoolean("independentDistanceValidation"))throw new AssertionError("Provenance changed");
  System.out.println("PASS: full-lens reference conversion, 15 profile rejection controls, 2 live-model rejection controls and native result delivery; retained development replay only.");
 }
}
