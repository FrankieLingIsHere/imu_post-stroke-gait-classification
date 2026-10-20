package expo.modules.gaitcalibration;

import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Strict self-calibration admission; compatible references retain separate provenance. */
public final class OnDeviceProfile {
  public static final String METHOD="openvins-self-calibration-v1";
  public static final String COMMIT="69488123ed9362dd44b6f28e7f4680abbff1442b";
  public static final String[] KEYS={"installationId","cameraId","width","height","imageAxes","sensorOrientationDegrees","stabilizationRequested","capturePipeline","opticalSetup"};
  static void require(boolean v,String message){if(!v)throw new IllegalArgumentException(message);}
  static JSONObject read(File f)throws Exception{try(InputStream in=new FileInputStream(f);ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))>0)out.write(b,0,n);return new JSONObject(new String(out.toByteArray(),StandardCharsets.UTF_8));}}
  static String sha(File f)throws Exception{MessageDigest d=MessageDigest.getInstance("SHA-256");try(InputStream in=new FileInputStream(f)){byte[] b=new byte[65536];int n;while((n=in.read(b))>0)d.update(b,0,n);}StringBuilder s=new StringBuilder();for(byte b:d.digest())s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();}
  static double[] values(JSONArray a,int size)throws Exception{require(a.length()==size,"Invalid camera profile dimensions");double[] out=new double[size];for(int i=0;i<size;i++){out[i]=a.getDouble(i);require(Double.isFinite(out[i]),"Camera profile has a nonfinite parameter");}return out;}
  static JSONObject validate(JSONObject p,JSONObject binding)throws Exception{
    if(ReferenceTrackingProfile.METHOD.equals(p.optString("method")))return ReferenceTrackingProfile.validate(p,binding);
    require(p.getInt("schemaVersion")==1&&p.getString("kind").equals("phone-on-device-camera-imu-profile-v1")&&p.getString("method").equals(METHOD)&&p.getString("upstreamCommit").equals(COMMIT),"Unsupported on-phone profile");
    for(String k:KEYS)require(Objects.equals(p.getJSONObject("binding").get(k),binding.get(k)),"Camera setup changed; repeat phone setup");
    require(binding.getInt("width")==640&&binding.getInt("height")==480&&binding.getString("capturePipeline").equals("native-camera-imu-v3")&&binding.getString("imageAxes").equals("native-sensor-unrotated-unmirrored")&&binding.getString("stabilizationRequested").equals("off")&&binding.getString("opticalSetup").equals("waist-bag-window"),"Unsupported camera setup");
    require(!p.getBoolean("computerUsed")&&!p.getBoolean("groundTruthDistanceUsed")&&!p.getBoolean("independentDistanceValidation")&&p.getBoolean("numericalCalibrationReady")&&p.getString("sourceSha256").matches("[a-f0-9]{64}"),"Phone setup has not completed");
    checkFit(p.getJSONObject("fit"));require(p.getBoolean("stableTailAccepted"),"Phone setup has not settled");
    return p;
  }
  public static boolean fitReady(JSONObject r)throws Exception{try{checkFit(r);return true;}catch(IllegalArgumentException|JSONException e){return false;}}
  static void checkFit(JSONObject r)throws Exception{
    require(r.getBoolean("initialized"),"Phone tracking did not initialize");
    require(r.getBoolean("integrity"),"Camera and motion tracking lost integrity");
    require(r.getBoolean("numericalCalibrationReady"),"Phone calibration has not converged");
    require(r.getInt("updates")>=200,"Not enough initialized tracking updates");
    require(Double.isFinite(r.getDouble("positionStdMetres"))&&r.getDouble("positionStdMetres")>=0&&r.getDouble("positionStdMetres")<.15,"Tracking uncertainty is too high");
    double[] k=values(r.getJSONArray("cameraValues"),8),e=values(r.getJSONArray("imuToCamera"),7),sd=values(r.getJSONArray("calibrationStd"),15),motion=values(r.getJSONArray("axisMotionRadians"),3);
    require(k[0]>=150&&k[0]<=1600&&k[1]>=150&&k[1]<=1600&&k[2]>=160&&k[2]<=480&&k[3]>=120&&k[3]<=360,"Camera fit is outside physical bounds");
    for(int i=4;i<8;i++)require(Math.abs(k[i])<=1,"Distortion fit is outside physical bounds");
    require(Math.abs(e[0]*e[0]+e[1]*e[1]+e[2]*e[2]+e[3]*e[3]-1)<1e-5&&Math.sqrt(e[4]*e[4]+e[5]*e[5]+e[6]*e[6])<=.25,"Alignment fit is outside physical bounds");
    for(double s:sd)require(s>=0,"Invalid calibration uncertainty");
    require(sd[0]/k[0]<.04&&sd[1]/k[1]<.04&&sd[2]<6&&sd[3]<6&&sd[8]<.035&&sd[9]<.035&&sd[10]<.035&&sd[11]<.015&&sd[12]<.015&&sd[13]<.015&&sd[14]<.003,"Phone setup has not converged");
    for(double m:motion)require(m>=.5,"Tilt in all directions during phone setup");
    require(Double.isFinite(r.getDouble("timeOffsetSeconds"))&&Math.abs(r.getDouble("timeOffsetSeconds"))<=.15&&r.getDouble("readoutSeconds")>=0&&r.getDouble("readoutSeconds")<=.1,"Invalid timing fit");
  }
  /** The tail must pass for five real seconds, not just one fortuitous frame. */
  public static JSONObject finish(File files,String id)throws Exception{
    require(id.matches("calibration-[0-9]+"),"Invalid phone setup identifier");
    File dir=new File(files,"camera-calibration/"+id);JSONObject m=read(new File(dir,"manifest.json"));
    require(m.getString("kind").equals("phone-on-device-setup-capture-v1")&&m.getString("status").equals("completed")&&m.isNull("error")&&m.getString("timestampSource").equals("realtime")&&m.getLong("alignmentMovementStartedBootNs")>0,"Phone setup capture did not complete");
    List<JSONObject> tail=new ArrayList<>();try(BufferedReader r=new BufferedReader(new FileReader(new File(dir,"on-device-states.ndjson")))){String line;while((line=r.readLine())!=null){JSONObject row=new JSONObject(line);tail.add(row);double t=row.getDouble("timestampSeconds");while(tail.size()>1&&t-tail.get(0).getDouble("timestampSeconds")>5.5)tail.remove(0);}}
    checkStableTail(tail);
    JSONObject last=tail.get(tail.size()-1);
    JSONObject binding=new JSONObject();for(String key:KEYS)binding.put(key,m.get(key));
    JSONObject p=new JSONObject().put("schemaVersion",1).put("kind","phone-on-device-camera-imu-profile-v1").put("method",METHOD).put("upstreamCommit",COMMIT)
      .put("binding",binding).put("sourceSha256",sha(new File(dir.getPath()+".zip"))).put("sourceCaptureId",id).put("fit",last)
      .put("numericalCalibrationReady",true).put("stableTailAccepted",true).put("computerUsed",false).put("groundTruthDistanceUsed",false).put("independentDistanceValidation",false)
      .put("rollingShutterModel","measured-midpoint-gyro-rotational-row-compensation-v1").put("createdAtMillis",System.currentTimeMillis());
    validate(p,binding);File destination=new File(dir.getParentFile(),"on-device-profile.json"),temp=new File(destination.getPath()+".tmp");
    try{try(Writer w=new FileWriter(temp)){w.write(p.toString());}require(temp.renameTo(destination),"Could not save phone setup");}finally{temp.delete();}return p;
  }
  /** Shared by live completion and saved admission; never finish on a timer alone. */
  public static void checkStableTail(List<JSONObject> tail)throws Exception{
    require(tail.size()>=60&&tail.get(tail.size()-1).getDouble("timestampSeconds")-tail.get(0).getDouble("timestampSeconds")>=5,"Not enough stable tracking; repeat phone setup");
    double previous=Double.NaN;
    for(JSONObject row:tail){double time=row.getDouble("timestampSeconds");require(Double.isFinite(time)&&(Double.isNaN(previous)||(time>previous&&time-previous<=.2)),"Setup tracking has a gap");previous=time;}
    JSONObject last=tail.get(tail.size()-1);checkFit(last);
    double[] k=values(last.getJSONArray("cameraValues"),8),e=values(last.getJSONArray("imuToCamera"),7);
    for(JSONObject row:tail){checkFit(row);double[] a=values(row.getJSONArray("cameraValues"),8),b=values(row.getJSONArray("imuToCamera"),7);require(Math.abs(a[0]/k[0]-1)<.01&&Math.abs(a[1]/k[1]-1)<.01&&Math.abs(a[2]-k[2])<2&&Math.abs(a[3]-k[3])<2&&Math.abs(row.getDouble("timeOffsetSeconds")-last.getDouble("timeOffsetSeconds"))<.001,"Phone setup is still changing");double dot=0,pos=0;for(int i=0;i<4;i++)dot+=e[i]*b[i];for(int i=4;i<7;i++)pos+=Math.pow(e[i]-b[i],2);require(Math.abs(dot)>.99996&&Math.sqrt(pos)<.01,"Phone alignment is still changing");}
  }
}
