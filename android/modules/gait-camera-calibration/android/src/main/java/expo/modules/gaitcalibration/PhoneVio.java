package expo.modules.gaitcalibration;

import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

import java.security.MessageDigest;
import java.util.*;

/** Saved native capture -> calibrated on-device VINS. Never contacts a server. */
public final class PhoneVio {
  private static native int nativeProcess(String directory);
  public static final String REVISION="android-vins-fixed-rows-quiet-v1";
  private static final String[] BINDING={"installationId","cameraId","width","height","imageAxes","sensorOrientationDegrees","stabilizationRequested","capturePipeline","opticalSetup"};
  private static JSONObject json(File f)throws Exception{try(InputStream in=new FileInputStream(f);ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] buffer=new byte[8192];int n;while((n=in.read(buffer))>0)out.write(buffer,0,n);return new JSONObject(new String(out.toByteArray(),StandardCharsets.UTF_8));}}
  private static List<JSONObject> rows(File f)throws Exception{List<JSONObject> a=new ArrayList<>();try(BufferedReader r=new BufferedReader(new InputStreamReader(new FileInputStream(f),StandardCharsets.UTF_8))){String s;while((s=r.readLine())!=null)if(!s.trim().isEmpty())a.add(new JSONObject(s));}return a;}
  private static String sha(File f)throws Exception{MessageDigest d=MessageDigest.getInstance("SHA-256");try(InputStream in=new FileInputStream(f)){byte[] b=new byte[65536];int n;while((n=in.read(b))>0)d.update(b,0,n);}StringBuilder s=new StringBuilder();for(byte b:d.digest())s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();}
  private static void require(boolean v,String message){if(!v)throw new IllegalArgumentException(message);}
  private static double finite(double v){require(Double.isFinite(v),"Nonfinite sensor/calibration value");return v;}
  private static double norm(double[] v){return Math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);}
  private static double[] vector(JSONObject v)throws Exception{return new double[]{finite(v.getDouble("x")),finite(v.getDouble("y")),finite(v.getDouble("z"))};}
  private static final class Sample {long t;double[] v;Sample(JSONObject r)throws Exception{t=r.getLong("timestampNs");v=vector(r);}}
  private static List<Sample> stream(List<JSONObject> all,String name)throws Exception{List<Sample>a=new ArrayList<>();long prev=0;for(JSONObject r:all)if(name.equals(r.getString("sensor"))){Sample s=new Sample(r);require(s.t>prev,"Nonmonotonic IMU");prev=s.t;a.add(s);}require(a.size()>100,"Not enough IMU samples");return a;}
  private static JSONObject parameter(JSONObject p,String section,String key,String topic)throws Exception{JSONArray a=p.getJSONObject(section).getJSONArray(key);JSONObject out=null;for(int i=0;i<a.length();i++)if(topic.equals(a.getJSONObject(i).getString("key"))){require(out==null,"Ambiguous calibration");out=a.getJSONObject(i);}require(out!=null,"Missing calibration: "+key);return out;}
  private static JSONObject objectParam(JSONObject p,String section,String key,String topic)throws Exception{return parameter(p,section,key,topic).getJSONObject("value");}
  private static double scalarParam(JSONObject p,String key,String topic)throws Exception{return finite(parameter(p,"TEMPORAL",key,topic).getDouble("value"));}
  private static void matrix(Writer w,String name,int r,int c,double[] values)throws Exception{w.write(name+": !!opencv-matrix\n   rows: "+r+"\n   cols: "+c+"\n   dt: d\n   data: [");for(int i=0;i<values.length;i++)w.write((i==0?"":", ")+finite(values[i]));w.write("]\n");}
  private static double[] flatten(JSONArray a)throws Exception{List<Double>v=new ArrayList<>();for(int i=0;i<a.length();i++){Object x=a.get(i);if(x instanceof JSONArray){JSONArray row=(JSONArray)x;for(int j=0;j<row.length();j++)v.add(finite(row.getDouble(j)));}else v.add(finite(a.getDouble(i)));}double[] out=new double[v.size()];for(int i=0;i<out.length;i++)out[i]=v.get(i);return out;}
  private static long quiet(List<Sample>a,List<Sample>g,long boundary,double sigma){
    for(int i=0;i<a.size();i+=10){long end=a.get(i).t,start=end-2000000000L;if(end>=boundary)break;if(start<Math.max(a.get(0).t,g.get(0).t))continue;
      List<Sample> aw=new ArrayList<>(),gw=new ArrayList<>();for(int j=i;j>=0&&a.get(j).t>=start;j--)aw.add(0,a.get(j));for(Sample s:g){if(s.t>end)break;if(s.t>=start)gw.add(s);}
      if(!continuous(aw,start,end)||!continuous(gw,start,end))continue;
      double mean=0,var=0,maxG=0;for(Sample s:aw)mean+=norm(s.v);mean/=aw.size();for(Sample s:aw)var+=Math.pow(norm(s.v)-mean,2);for(Sample s:gw)maxG=Math.max(maxG,norm(s.v));
      if(Math.sqrt(var/aw.size())<=3*sigma&&maxG<.08)return start;
    }throw new IllegalArgumentException("No continuous quiet baseline before walking");
  }
  private static boolean continuous(List<Sample>a,long start,long end){if(a.size()<=100||a.get(0).t-start>20000000L||end-a.get(a.size()-1).t>20000000L)return false;for(int i=1;i<a.size();i++)if(a.get(i).t-a.get(i-1).t>20000000L)return false;return true;}

  public static JSONObject refinedLens(JSONObject reference)throws Exception{
    JSONObject c=objectParam(reference.getJSONObject("upstreamParameters").getJSONObject("CalibParam"),"INTRI","Camera","/gaittrace/camera").getJSONObject("ptr_wrapper").getJSONObject("data");
    double[] f=flatten(c.getJSONArray("focal_length")),p=flatten(c.getJSONArray("principal_point")),d=flatten(c.getJSONArray("disto_param"));
    require(f.length==2&&p.length==2&&d.length==5&&c.getInt("img_width")==640&&c.getInt("img_height")==480,"Invalid refined camera dimensions");
    require(f[0]>=150&&f[0]<=1600&&f[1]>=150&&f[1]<=1600&&p[0]>=160&&p[0]<=480&&p[1]>=120&&p[1]<=360,"Refined camera outside research bounds");
    for(double value:d)require(Math.abs(value)<=5,"Refined distortion outside research bounds");
    return new JSONObject().put("model","opencv-pinhole-radtan5").put("cameraMatrix",new JSONArray().put(new JSONArray(new double[]{f[0],0,p[0]})).put(new JSONArray(new double[]{0,f[1],p[1]})).put(new JSONArray(new double[]{0,0,1})))
      .put("distortion",new JSONArray(new double[]{d[0],d[1],d[3],d[4],d[2]})).put("origin","ikalibr-refined-candidate").put("independentLensValidation",false);
  }

  /** Public input adapter is also exercised on retained captures by the JVM test. */
  public static JSONObject prepare(File files,String id)throws Exception{
    require(id.matches("[a-zA-Z0-9_-]{1,160}"),"Invalid recording identifier");
    File folder=new File(files,"gait-camera-captures/gait-camera-"+id), archive=new File(folder.getPath()+".zip");
    require(folder.isDirectory()&&archive.isFile(),"The camera archive is missing. Motion data is kept.");
    JSONObject meta=json(new File(folder,"manifest.json")),ref=json(new File(folder,"reference-calibration.json"));
    require("gait-camera-imu-distance-capture-v1".equals(meta.getString("kind"))&&id.equals(meta.getString("sessionId"))&&("gait-camera-"+id).equals(meta.getString("captureId")),"Capture does not match this recording");
    require("completed".equals(meta.getString("status"))&&meta.isNull("error")&&meta.getJSONObject("diagnostics").getBoolean("placementCompleted"),"Incomplete camera capture");
    require("realtime".equals(meta.getString("timestampSource")),"Unverified camera/IMU clock");
    require("m/s2".equals(meta.getJSONObject("units").getString("accelerometer"))&&"rad/s".equals(meta.getJSONObject("units").getString("gyroscope")),"IMU units mismatch");
    require("phone-reference-camera-imu-calibration-v1".equals(ref.getString("kind"))&&"ikalibr-tro-2025".equals(ref.getString("method"))&&"reference-solved-review-required".equals(ref.getString("status")),"Unsupported calibration");
    JSONObject binding=ref.getJSONObject("binding"), lensProfile=ref.getJSONObject("lensProfile"), lens=lensProfile.getJSONObject("lens");
    for(String k:BINDING)require(Objects.equals(meta.get(k),binding.get(k))&&Objects.equals(meta.get(k),lensProfile.getJSONObject("binding").get(k)),"Calibration binding mismatch: "+k);
    if("phone-learned-lens-seed-v1".equals(lensProfile.optString("kind"))){
      JSONObject learned=lensProfile.getJSONObject("learned");
      require("geocalib-eccv2024-seed".equals(lensProfile.optString("method"))&&!lensProfile.getBoolean("lensReady")&&lensProfile.getBoolean("calibrationSeedReady")
        &&learned.getBoolean("qualityAccepted")&&learned.getInt("supportViews")==5&&learned.getInt("queryViews")==5&&learned.getBoolean("disjointViews")
        &&!learned.getBoolean("neuralWeightsUpdated")&&!learned.getBoolean("fullLensValidated")&&!learned.getBoolean("internalUncertaintyValidated")
        &&finite(learned.getDouble("viewConsistencyFraction"))>=0&&learned.getDouble("viewConsistencyFraction")<=.08
        &&"97b8968e7798a66bf04fcf791fb535624241bda7".equals(learned.getString("sourceCommit"))
        &&"13cc505928e3ff4eb26c00bff73861ab2b11b804a546323456cf5462e1f8f447".equals(learned.getString("checkpointSha256")),"Experimental lens seed needs review");
      double[] k=flatten(lens.getJSONArray("cameraMatrix")),d=flatten(lens.getJSONArray("distortion"));
      require(k.length==9&&d.length==5&&k[0]>=150&&k[0]<=1600&&k[4]>=150&&k[4]<=1600&&k[2]==320&&k[5]==240&&Math.abs(d[0])<=.3,"Invalid experimental lens seed");
      require(k[1]==0&&k[3]==0&&k[6]==0&&k[7]==0&&k[8]==1,"Invalid experimental camera matrix");
      for(int i=1;i<5;i++)require(d[i]==0,"Unexpected learned distortion model");
      lens=refinedLens(ref);
    }else require(lensProfile.getBoolean("lensReady")&&finite(lens.getDouble("heldOutP90Pixels"))<=1.5,"Lens profile needs review");
    require(meta.getInt("width")==640&&meta.getInt("height")==480,"Unsupported calibrated camera dimensions");
    for(String k:new String[]{"distanceReady","fullCalibrationReady","independentDistanceValidation","cameraImuCandidateReady"})require(!ref.getBoolean(k),"Unexpected calibration admission");
    List<JSONObject> raw=rows(new File(folder,"imu.ndjson"));List<Sample>a=stream(raw,"accelerometer"),g=stream(raw,"gyroscope");
    long start=meta.getJSONObject("diagnostics").getLong("walkStartedBootNs"),end=meta.getJSONObject("diagnostics").getLong("walkEndedBootNs");require(end>start&&end-start<=600000000000L,"Invalid walking boundaries");
    double accN=.08,gyrN=.004;String noiseSource="provisional-vins-defaults";String noiseHash=null;
    File[] reports=new File(files,"camera-imu-noise").listFiles((d,n)->n.endsWith("-report.json"));
    if(reports!=null){Arrays.sort(reports,Comparator.comparing(File::getName).reversed());for(File report:reports){JSONObject n=json(report),b=n.getJSONObject("binding");if(!Objects.equals(b.opt("installationId"),meta.opt("installationId"))||!Objects.equals(b.opt("capturePipeline"),meta.opt("capturePipeline"))||!b.getJSONObject("device").toString().equals(meta.getJSONObject("device").toString())||!n.optBoolean("whiteNoiseCandidateReady")||n.optBoolean("biasRandomWalkReady"))continue;
      double[] values=new double[2];int k=0;for(String sensor:new String[]{"accelerometer","gyroscope"}){JSONObject s=n.getJSONObject("sensors").getJSONObject(sensor);double rate=s.getDouble("sampleRateHz");require(rate>=150&&rate<=250,"Noise sample rate mismatch");double[] axes=flatten(s.getJSONArray("stdAxes"));require(axes.length==3,"Invalid noise axes");for(double v:axes){require(v>0&&v<=(k==0?.15:.02),"Noise candidate outside bounds");values[k]=Math.max(values[k],v);}k++;}accN=values[0];gyrN=values[1];noiseSource="saved-phone-noise-candidate-random-walk-provisional";noiseHash=sha(report);break;}}
    long baseline=quiet(a,g,start,accN);File replay=new File(folder,"phone-vio");require(replay.isDirectory()||replay.mkdirs(),"Cannot prepare phone processing");
    List<double[]> blocks=new ArrayList<>();for(int b=0;b<10;b++){double[] mean=new double[3];int count=0;long from=baseline+b*200000000L,to=from+200000000L;for(Sample s:g)if(s.t>=from&&s.t<to){for(int k=0;k<3;k++)mean[k]+=s.v[k];count++;}require(count>10,"Sparse quiet gyro block");for(int k=0;k<3;k++)mean[k]/=count;blocks.add(mean);}
    double[] learnedBias=ShortBaselineModel.fit(blocks);
    boolean biasCertain=ShortBaselineModel.accept(learnedBias);
    JSONObject adaptation=new JSONObject().put("version",ShortBaselineModel.VERSION).put("observations",blocks.size()).put("quietSeconds",2).put("gyroBiasRadPerSecond",new JSONArray(Arrays.copyOfRange(learnedBias,0,3))).put("posteriorStdRadPerSecond",new JSONArray(Arrays.copyOfRange(learnedBias,3,6))).put("appliedToInitialization",biasCertain).put("replacesCameraCalibration",false).put("groundTruthDistanceUsed",false);
    try(Writer w=new BufferedWriter(new FileWriter(new File(replay,"imu.csv")))){w.write("timestamp_ns,gx,gy,gz,ax,ay,az\n");int j=1;for(Sample s:g){if(s.t<a.get(0).t||s.t>a.get(a.size()-1).t)continue;while(j<a.size()-1&&a.get(j).t<=s.t)j++;Sample l=a.get(j-1),r=a.get(j);require(r.t-l.t<=20000000L,"Acceleration gap exceeds 20 ms");double q=(double)(s.t-l.t)/(r.t-l.t);w.write(s.t+","+s.v[0]+","+s.v[1]+","+s.v[2]);for(int k=0;k<3;k++)w.write(","+(l.v[k]*(1-q)+r.v[k]*q));w.write("\n");}}
    Map<Long,JSONObject> timing=new HashMap<>();for(JSONObject r:rows(new File(folder,"capture-results.ndjson")))timing.put(r.getLong("timestampNs"),r);
    long last=0,captureEnd=0;try(Writer w=new BufferedWriter(new FileWriter(new File(replay,"frames.csv")))){w.write("timestamp_ns,file\n");for(JSONObject r:rows(new File(folder,"frames.ndjson"))){long t=r.getLong("timestampNs");JSONObject info=timing.get(t);require(info!=null,"Missing camera timing");long exposure=info.getLong("exposureNs"),skew=info.getLong("rollingShutterSkewNs");require(exposure>=0&&skew>=0,"Invalid camera timing");long midpoint=t+(exposure+skew)/2;require(midpoint>last,"Nonmonotonic camera clock");last=midpoint;captureEnd=t;String name=r.getString("file");require(name.matches("frames/[A-Za-z0-9_-]+\\.jpg")&&new File(folder,name).isFile(),"Invalid frame path");w.write(midpoint+","+name+"\n");}}
    require(start<end&&end<=captureEnd,"Walk boundary outside capture");
    JSONObject p=ref.getJSONObject("upstreamParameters").getJSONObject("CalibParam"),q=objectParam(p,"EXTRI","SO3_CmToBr","/gaittrace/camera"),t=objectParam(p,"EXTRI","POS_CmInBr","/gaittrace/camera");
    double x=q.getDouble("qx"),y=q.getDouble("qy"),z=q.getDouble("qz"),qw=q.getDouble("qw");require(Math.abs(x*x+y*y+z*z+qw*qw-1)<1e-5,"Invalid calibration rotation");
    double[] rotation={1-2*(y*y+z*z),2*(x*y-z*qw),2*(x*z+y*qw),2*(x*y+z*qw),1-2*(x*x+z*z),2*(y*z-x*qw),2*(x*z-y*qw),2*(y*z+x*qw),1-2*(x*x+y*y)};
    double[] translation={t.getDouble("r0c0"),t.getDouble("r1c0"),t.getDouble("r2c0")};require(norm(translation)<=.25,"Invalid camera translation");
    JSONObject iq=objectParam(p,"EXTRI","SO3_BiToBr","/gaittrace/imu"),it=objectParam(p,"EXTRI","POS_BiInBr","/gaittrace/imu");for(String k:new String[]{"qx","qy","qz","qw"})require(Math.abs(iq.getDouble(k)-(k.equals("qw")?1:0))<1e-8,"Nonidentity IMU frame");for(String k:new String[]{"r0c0","r1c0","r2c0"})require(Math.abs(it.getDouble(k))<1e-8,"Nonidentity IMU origin");require(Math.abs(scalarParam(p,"TO_BiToBr","/gaittrace/imu"))<1e-8,"Nonzero IMU reference clock");
    double td=scalarParam(p,"TO_CmToBr","/gaittrace/camera"),tr=scalarParam(p,"RS_READOUT","/gaittrace/camera");require(Math.abs(td)<=.15&&tr>=0&&tr<=.1,"Invalid camera timing calibration");
    try(Writer w=new FileWriter(new File(replay,"reference.yaml"))){w.write("%YAML:1.0\n---\n");matrix(w,"extrinsicRotation",3,3,rotation);matrix(w,"extrinsicTranslation",3,1,translation);matrix(w,"cameraMatrix",3,3,flatten(lens.getJSONArray("cameraMatrix")));matrix(w,"distortion",1,5,flatten(lens.getJSONArray("distortion")));matrix(w,"initialGyroBias",3,1,Arrays.copyOfRange(learnedBias,0,3));w.write("td: "+td+"\nreadout: "+tr+"\nacc_n: "+accN+"\ngyr_n: "+gyrN+"\nacc_w: 0.00004\ngyr_w: 0.000002\nestimate_extrinsic: 0\nestimate_td: 0\nfixed_time_row_correction: 1\nreplay_start_ns: \""+baseline+"\"\n");}
    return new JSONObject().put("manifest",meta).put("reference",ref).put("sourceSha256",sha(archive)).put("captureEndSeconds",captureEnd/1e9).put("initializationStartNs",baseline).put("baselineAdaptation",adaptation).put("noiseSource",noiseSource).put("noiseProfileSha256",noiseHash==null?JSONObject.NULL:noiseHash).put("processingRevision",REVISION);
  }
  public static synchronized String process(File files,String id)throws Exception{
    require(id.matches("[a-zA-Z0-9_-]{1,160}"),"Invalid recording identifier");
    File profile=new File(files,"gait-camera-captures/gait-camera-"+id+"/reference-calibration.json");
    if(profile.isFile()&&"phone-on-device-camera-imu-profile-v1".equals(json(profile).optString("kind")))return OnDeviceResults.process(files,id);
    JSONObject result=prepare(files,id);File replay=new File(files,"gait-camera-captures/gait-camera-"+id+"/phone-vio");
    System.loadLibrary("gait_phone_vio");long began=System.nanoTime();int code=nativeProcess(replay.getAbsolutePath());require(code==0||code==6,"Phone estimator did not complete");
    JSONArray states=new JSONArray();try(BufferedReader r=new BufferedReader(new FileReader(new File(replay,"reference-states.csv")))){String[] keys=r.readLine().split(",");String line;while((line=r.readLine())!=null){String[] values=line.split(",");require(values.length==keys.length,"Invalid estimator state");JSONObject state=new JSONObject();for(int i=0;i<keys.length;i++){double value=Double.parseDouble(values[i]);state.put(keys[i],Double.isFinite(value)?value:JSONObject.NULL);}states.put(state);}}
    result.put("states",states).put("processingSeconds",(System.nanoTime()-began)/1e9).put("processingLocation","phone");
    return result.toString();
  }
}
