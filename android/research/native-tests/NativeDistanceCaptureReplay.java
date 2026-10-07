import expo.modules.gaitcalibration.ResearchDistanceTracker;
import org.json.*;
import org.opencv.core.*;
import org.opencv.imgcodecs.Imgcodecs;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;

/** Explicit artifact replay of the application tracker, not live Android capture.
 * All IMU samples are available before frames: this cannot validate live latency. */
public final class NativeDistanceCaptureReplay {
  private static String read(ZipFile zip,String name)throws Exception {
    ZipEntry entry=zip.getEntry(name);if(entry==null||entry.getSize()>128L*1024*1024)throw new IllegalArgumentException("Missing/oversize ZIP entry");
    try(java.io.InputStream stream=zip.getInputStream(entry)){return new String(stream.readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);}
  }
  public static void main(String[] args)throws Exception {
    System.load(Paths.get(args[0]).toAbsolutePath().toString());
    JSONObject profile=new JSONObject(Files.readString(Paths.get(args[2]))),report;
    try(ZipFile zip=new ZipFile(args[1])){
      JSONObject manifest=new JSONObject(read(zip,"manifest.json"));JSONObject binding=profile.getJSONObject("binding");
      for(String key:new String[]{"installationId","cameraId","width","height","imageAxes","sensorOrientationDegrees","stabilizationRequested"})if(!Objects.equals(binding.opt(key),manifest.opt(key)))throw new IllegalArgumentException("Profile/capture binding mismatch: "+key);
      ResearchDistanceTracker tracker=new ResearchDistanceTracker(profile);
      for(String line:read(zip,"imu.ndjson").split("\n")){if(line.isBlank())continue;JSONObject row=new JSONObject(line);tracker.sensor(row.getString("sensor"),row.getLong("timestampNs"),row.getDouble("x"),row.getDouble("y"),row.getDouble("z"));}
      Map<Long,JSONObject> capture=new HashMap<>();for(String line:read(zip,"capture-results.ndjson").split("\n")){if(!line.isBlank()){JSONObject row=new JSONObject(line);capture.put(row.getLong("timestampNs"),row);}}
      long cutoff=manifest.optJSONObject("diagnostics")!=null?manifest.getJSONObject("diagnostics").optLong("walkStartedBootNs",0):manifest.getLong("startedBootNs")+5000000000L;
      if(manifest.optJSONObject("diagnostics")!=null&&cutoff<=0)throw new IllegalArgumentException("Trial never entered walking; no route replay");
      boolean nativeTrackingCutoff=false;
      if(zip.getEntry("tracking.ndjson")!=null){
        for(String line:read(zip,"tracking.ndjson").split("\n"))if(!line.isBlank()){
          cutoff=new JSONObject(line).getLong("timestampNs");nativeTrackingCutoff=true;break;
        }
      }
      int replayed=0;
      for(String line:read(zip,"frames.ndjson").split("\n")){
        if(line.isBlank())continue;JSONObject row=new JSONObject(line);long timestamp=row.getLong("timestampNs");if(timestamp<cutoff)continue;
        JSONObject metadata=capture.get(timestamp);if(metadata==null)continue;String name=row.getString("file");if(!name.matches("frames/[0-9]+\\.jpg"))throw new IllegalArgumentException("Invalid frame path");
        byte[] jpg;try(java.io.InputStream stream=zip.getInputStream(zip.getEntry(name))){jpg=stream.readAllBytes();}
        MatOfByte bytes=new MatOfByte(jpg);Mat image=Imgcodecs.imdecode(bytes,Imgcodecs.IMREAD_GRAYSCALE);
        try{if(image.cols()!=manifest.getInt("width")||image.rows()!=manifest.getInt("height"))throw new IllegalArgumentException("Pixel pipeline mismatch");byte[] luma=new byte[image.rows()*image.cols()];image.get(0,0,luma);tracker.process(luma,image.cols(),image.rows(),timestamp,metadata);replayed++;}finally{bytes.release();image.release();}
      }
      report=tracker.finish();report.put("artifactReplay",true).put("allImuAvailableBeforeFrames",true).put("androidCaptureExecuted",false).put("independentDistanceValidation",false).put("replayedFrames",replayed).put("replayFirstFrameBootNs",cutoff).put("replayStartsFromNativeTrackingLog",nativeTrackingCutoff);
    }
    Files.writeString(Paths.get(args[3]),report.toString(2));JSONObject summary=new JSONObject();for(String key:new String[]{"status","reason","framesProcessed","poseFrames","features","reprojectionRmsPixels","artifactReplay","androidCaptureExecuted"})summary.put(key,report.opt(key));System.out.println(summary.toString(2));
  }
}
