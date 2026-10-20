package expo.modules.gaitcalibration;
import org.json.*;
import java.io.*;
import java.nio.file.*;

/** Host artifact replay through production delivery; never physical phone evidence. */
public final class SelfCalibrationPipelineReplayCheck {
 public static void main(String[] args)throws Exception {
  JSONObject profile=OnDeviceProfile.read(new File(args[0])),manifest=OnDeviceProfile.read(new File(args[1]));
  if(!profile.getString("method").equals(OnDeviceProfile.METHOD)||!profile.getBoolean("numericalCalibrationReady")||profile.getBoolean("independentDistanceValidation"))throw new AssertionError("Not an unvalidated self-calibration candidate");
  if(!manifest.getString("status").equals("quiet-stop")||!manifest.isNull("error"))throw new AssertionError("Not a completed retained trial");
  String originalId=manifest.getString("captureId");
  manifest.put("sourceStatus",manifest.getString("status")).put("status","completed").put("kind","gait-camera-imu-distance-capture-v1").put("sessionId","self-calibrated-replay").put("captureId","gait-camera-self-calibrated-replay").put("protocol","research-walk").put("capturePipeline","native-camera-imu-v3").put("localReplay",true).put("physicalAndroidExecution",false).put("sourceCaptureId",originalId);
  // The v2-to-v3 staging adapter is explicit. No optics, route boundaries,
  // timestamps, IMU samples, or profile values are changed by this driver.
  OnDeviceProfile.validate(profile,manifest);
  Path root=Paths.get(args[3]),folder=root.resolve("gait-camera-captures/gait-camera-self-calibrated-replay");Files.createDirectories(folder);
  Files.writeString(folder.resolve("manifest.json"),manifest.toString());Files.writeString(folder.resolve("reference-calibration.json"),profile.toString());
  Files.copy(Paths.get(args[2]),folder.resolve("on-device-states.ndjson"),StandardCopyOption.REPLACE_EXISTING);
  Files.copy(Paths.get(args[4]),Paths.get(folder+".zip"),StandardCopyOption.REPLACE_EXISTING);
  Files.writeString(root.resolve("delivered-result.json"),OnDeviceResults.process(root.toFile(),"self-calibrated-replay"));
  JSONObject wrong=new JSONObject(profile.toString());wrong.getJSONObject("binding").put("cameraId","different-camera");Files.writeString(folder.resolve("reference-calibration.json"),wrong.toString());
  boolean rejected=false;try{OnDeviceResults.process(root.toFile(),"self-calibrated-replay");}catch(IllegalArgumentException expected){rejected=true;}finally{Files.writeString(folder.resolve("reference-calibration.json"),profile.toString());}
  if(!rejected)throw new AssertionError("Different-camera self-calibration accepted");
  System.out.println("PASS: self-calibration profile, actual saved-state delivery and different-camera rejection; host development replay only.");
 }
}
