package expo.modules.gaitcalibration;

import org.json.*;
import java.util.Objects;

/** An earlier same-phone calibration seeds live tracking; its review status remains unchanged. */
public final class ReferenceTrackingProfile {
  public static final String METHOD="ikalibr-reference-reuse-v2";
  private static final String BASE="ulong2/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c";
  private static void check(boolean ok){OnDeviceProfile.require(ok,"Saved reference does not match this phone or camera setup");}
  private static JSONObject object(JSONObject p,String section,String key,String topic)throws Exception{return (JSONObject)param(p,section,key,topic);}
  private static Object param(JSONObject p,String section,String key,String topic)throws Exception{
    JSONArray a=p.getJSONObject(section).getJSONArray(key);Object value=null;int count=0;
    for(int i=0;i<a.length();i++)if(topic.equals(a.getJSONObject(i).getString("key"))){value=a.getJSONObject(i).get("value");count++;}
    check(count==1);return value;
  }
  private static double scalar(JSONObject p,String key,String topic)throws Exception{double v=((Number)param(p,"TEMPORAL",key,topic)).doubleValue();check(Double.isFinite(v));return v;}
  public static JSONObject fit(JSONObject r,JSONObject binding)throws Exception{
    check(r.getInt("schemaVersion")==1&&r.getString("kind").equals("phone-reference-camera-imu-calibration-v1")&&r.getString("method").equals("ikalibr-tro-2025")&&r.getString("status").equals("reference-solved-review-required"));
    for(String key:new String[]{"cameraImuCandidateReady","fullCalibrationReady","distanceReady","independentDistanceValidation"})check(!r.getBoolean(key));
    check(r.getJSONArray("reviewRequired").length()>0&&r.getString("sourceSha256").matches("[a-f0-9]{64}"));
    JSONObject s=r.getJSONObject("software");check(s.getString("executableSha256").matches("[a-f0-9]{64}"));
    check(s.getString("image").equals(BASE)||(s.getString("image").equals("sha256:e6b2e0e5dd4e88831560e1d3d3012d69673c00f2e58f0c6b0c85e3ba610f1b91")&&s.getString("executableSha256").equals("b01cdfb24f098e6be0a35ead8b55932f6899cd892c07d4c1ac09738ae690b429")&&s.optString("baseImage").equals(BASE)&&(s.optString("experimentalBackend").equals("cpu")||s.optString("experimentalBackend").equals("cuda"))));
    JSONObject b=r.getJSONObject("binding"),l=r.getJSONObject("lensProfile"),lb=l.getJSONObject("binding");
    check(!binding.getString("installationId").isEmpty());
    for(String key:OnDeviceProfile.KEYS)if(!key.equals("capturePipeline")){check(Objects.equals(b.get(key),binding.get(key)));check(Objects.equals(lb.get(key),b.get(key)));}
    check(b.getString("capturePipeline").equals("native-camera-imu-v2")&&lb.getString("capturePipeline").equals("native-camera-imu-v2")&&binding.getString("capturePipeline").equals("native-camera-imu-v3"));
    check(binding.getInt("width")==640&&binding.getInt("height")==480&&binding.getString("imageAxes").equals("native-sensor-unrotated-unmirrored")&&binding.getString("opticalSetup").equals("waist-bag-window")&&binding.getString("stabilizationRequested").equals("off"));
    int orientation=binding.getInt("sensorOrientationDegrees");check(orientation==0||orientation==90||orientation==180||orientation==270);
    check(l.getString("method").equals("opencv-zhang-2000")&&l.getBoolean("lensReady"));
    JSONObject lens=l.getJSONObject("lens");check(lens.getString("model").equals("opencv-pinhole-radtan5"));JSONArray matrix=lens.getJSONArray("cameraMatrix");check(matrix.length()==3);
    double[] row0=OnDeviceProfile.values(matrix.getJSONArray(0),3),row1=OnDeviceProfile.values(matrix.getJSONArray(1),3),row2=OnDeviceProfile.values(matrix.getJSONArray(2),3),d=OnDeviceProfile.values(lens.getJSONArray("distortion"),5);
    check(row0[1]==0&&row1[0]==0&&row2[0]==0&&row2[1]==0&&row2[2]==1);
    double[] k={row0[0],row1[1],row0[2],row1[2],d[0],d[1],d[2],d[3]};
    check(k[0]>=150&&k[0]<=1600&&k[1]>=150&&k[1]<=1600&&k[2]>=160&&k[2]<=480&&k[3]>=120&&k[3]<=360);for(double value:d)check(Math.abs(value)<=1);
    JSONObject p=r.getJSONObject("upstreamParameters").getJSONObject("CalibParam"),q=object(p,"EXTRI","SO3_CmToBr","/gaittrace/camera"),t=object(p,"EXTRI","POS_CmInBr","/gaittrace/camera");
    double[] e=OnDeviceProfile.values(new JSONArray(new double[]{q.getDouble("qx"),q.getDouble("qy"),q.getDouble("qz"),q.getDouble("qw"),t.getDouble("r0c0"),t.getDouble("r1c0"),t.getDouble("r2c0")}),7);
    double x=e[0],y=e[1],z=e[2],w=e[3];check(Math.abs(x*x+y*y+z*z+w*w-1)<1e-5&&Math.sqrt(e[4]*e[4]+e[5]*e[5]+e[6]*e[6])<=.25);
    JSONObject iq=object(p,"EXTRI","SO3_BiToBr","/gaittrace/imu"),it=object(p,"EXTRI","POS_BiInBr","/gaittrace/imu");
    for(String key:new String[]{"qx","qy","qz","qw"}){double v=iq.getDouble(key);check(Double.isFinite(v)&&Math.abs(v-(key.equals("qw")?1:0))<1e-8);}
    for(String key:new String[]{"r0c0","r1c0","r2c0"}){double v=it.getDouble(key);check(Double.isFinite(v)&&Math.abs(v)<1e-8);}check(Math.abs(scalar(p,"TO_BiToBr","/gaittrace/imu"))<1e-8);
    double td=scalar(p,"TO_CmToBr","/gaittrace/camera"),rs=scalar(p,"RS_READOUT","/gaittrace/camera");check(Math.abs(td)<=.15&&rs>=0&&rs<=.1);
    double[][] R={{1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)},{2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)},{2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)}};
    double[] v={e[4],e[5],e[6]};for(int i=0;i<3;i++){e[4+i]=0;for(int j=0;j<3;j++)e[4+i]-=R[j][i]*v[j];}
    return new JSONObject().put("cameraValues",new JSONArray(k)).put("fixedLensK3",d[4]).put("imuToCamera",new JSONArray(e)).put("timeOffsetSeconds",td).put("readoutSeconds",rs);
  }
  public static JSONObject create(JSONObject reference,JSONObject binding)throws Exception{
    JSONObject p=new JSONObject().put("schemaVersion",1).put("kind","phone-on-device-camera-imu-profile-v1").put("method",METHOD).put("upstreamCommit",OnDeviceProfile.COMMIT)
      .put("binding",binding).put("sourceSha256",reference.getString("sourceSha256")).put("sourceReference",reference).put("fit",fit(reference,binding))
      .put("computerUsed",true).put("groundTruthDistanceUsed",false).put("independentDistanceValidation",false).put("numericalCalibrationReady",false).put("trackingSeedReady",true)
      .put("geometryConversion","radtan5-fixed-k3-v2");return validate(p,binding);
  }
  public static JSONObject validate(JSONObject p,JSONObject binding)throws Exception{
    check(p.getInt("schemaVersion")==1&&p.getString("kind").equals("phone-on-device-camera-imu-profile-v1")&&p.getString("method").equals(METHOD)&&p.getString("upstreamCommit").equals(OnDeviceProfile.COMMIT));
    for(String key:OnDeviceProfile.KEYS)check(Objects.equals(p.getJSONObject("binding").get(key),binding.get(key)));
    check(p.getBoolean("computerUsed")&&!p.getBoolean("groundTruthDistanceUsed")&&!p.getBoolean("independentDistanceValidation")&&!p.getBoolean("numericalCalibrationReady")&&p.getBoolean("trackingSeedReady")&&p.getString("geometryConversion").equals("radtan5-fixed-k3-v2"));
    JSONObject r=p.getJSONObject("sourceReference"),expected=fit(r,binding),actual=p.getJSONObject("fit");check(p.getString("sourceSha256").equals(r.getString("sourceSha256")));
    for(String key:new String[]{"cameraValues","imuToCamera"}){int n=key.equals("cameraValues")?8:7;double[] a=OnDeviceProfile.values(actual.getJSONArray(key),n),b=OnDeviceProfile.values(expected.getJSONArray(key),n);for(int i=0;i<n;i++)check(Math.abs(a[i]-b[i])<=1e-10);}
    for(String key:new String[]{"timeOffsetSeconds","readoutSeconds","fixedLensK3"})check(actual.getDouble(key)==expected.getDouble(key));return p;
  }
}
