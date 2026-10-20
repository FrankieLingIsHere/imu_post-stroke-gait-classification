package expo.modules.gaitcalibration;

import android.app.Instrumentation;
import android.os.Bundle;
import java.io.*;
import java.util.*;
import org.json.*;

/** Emulator-only numerical replay. Never linked into the patient APK.
 * Uses unchanged production Java sources and native libraries extracted from
 * the recorded lab APK. Camera2, speech and real hardware are not simulated here.
 */
public final class CalibrationReplayInstrumentation extends Instrumentation {
  private Bundle arguments;
  @Override public void onCreate(Bundle args){arguments=args;start();}
  @Override public void onStart(){
    Bundle reply=new Bundle();
    try {
      JSONObject report=replay(new File(arguments.getString("fixture")));
      File result=new File(getTargetContext().getFilesDir(),"replay-result.json");
      try(Writer w=new OutputStreamWriter(new FileOutputStream(result),"UTF-8")){w.write(report.toString(2));}
      reply.putString("result",report.toString());finish(report.getBoolean("passed")?-1:0,reply);
    } catch(Throwable e){reply.putString("failure",android.util.Log.getStackTraceString(e));finish(0,reply);}
  }
  private JSONObject replay(File fixture)throws Exception {
    JSONObject spec=OnDeviceProfile.read(new File(fixture,"fixture.json"));
    JSONArray prior=spec.getJSONArray("priorValues");
    JSONObject camera=new JSONObject().put("opticalPrior",new JSONObject()
      .put("cameraValues",prior).put("imuToCamera",new JSONArray(new double[]{0,0,0,1,0,0,0})));
    File files=getTargetContext().getFilesDir(),root=new File(files,"camera-calibration");root.mkdirs();
    String id="calibration-"+System.currentTimeMillis();File dir=new File(root,id);dir.mkdirs();
    File profile=new File(root,"on-device-profile.json");
    // Sentinel verifies rejection does not erase an earlier profile. Lab data only.
    String sentinel="{\"labPreviousProfile\":true}";
    try(Writer w=new FileWriter(profile)){w.write(sentinel);}
    List<String[]> frames=new ArrayList<>();
    try(BufferedReader r=new BufferedReader(new FileReader(new File(fixture,"frames.csv")))){
      r.readLine();String line;while((line=r.readLine())!=null)frames.add(line.split(","));
    }
    long first=Long.parseLong(frames.get(0)[0]),movement=first+(long)(spec.getDouble("quietSeconds")*1e9);
    GuidedCaptureClock clock=new GuidedCaptureClock(first,true);SetupBaselineGate baseline=new SetupBaselineGate();
    int fi=0,initialized=0,ready=0;long complete=0;double wall=System.nanoTime()/1e9;JSONObject last=null;String processingFailure=null;
    try(OnDeviceVio vio=new OnDeviceVio(dir,camera,null);
        BufferedReader r=new BufferedReader(new FileReader(new File(fixture,"imu.csv")))){
      r.readLine();String line;
      while((line=r.readLine())!=null){String[] a=line.split(",");long ns=Long.parseLong(a[0]);
        double gx=Double.parseDouble(a[1]),gy=Double.parseDouble(a[2]),gz=Double.parseDouble(a[3]);
        double ax=Double.parseDouble(a[4]),ay=Double.parseDouble(a[5]),az=Double.parseDouble(a[6]);
        baseline.sensor("accelerometer",ns,ax,ay,az);baseline.sensor("gyroscope",ns,gx,gy,gz);
        vio.sensor("accelerometer",ns,ax,ay,az);vio.sensor("gyroscope",ns,gx,gy,gz);
        while(fi<frames.size()&&Long.parseLong(frames.get(fi)[0])<=ns){String[] f=frames.get(fi++);
          vio.frame(Long.parseLong(f[0]),new File(fixture,"frames/"+new File(f[1].replace('\\','/')).getName()),
            new JSONObject().put("exposureNs",0).put("rollingShutterSkewNs",0));
        }
        if(clock.movementStartedNs()==0&&ns>=movement){
          if(!baseline.ready(ns,vio.status()))throw new IllegalStateException("Quiet baseline not established before fixture movement");
          baseline.accept(ns,vio.status());clock.begin(ns,()->vio.beginMotion());
        }
        JSONObject status=vio.status();if(status!=last&&status!=null){last=status;
          if(status.optBoolean("initialized"))initialized++;if(status.optBoolean("numericalCalibrationReady"))ready++;
        }
        if(clock.movementStartedNs()>0&&clock.remainingMovementMs(ns)==0&&vio.setupSettled(ns)){
          complete=ns;break;
        }
      }
    }catch(Exception e){processingFailure=e.getMessage();}
    JSONObject manifest=new JSONObject().put("kind","phone-on-device-setup-capture-v1")
      .put("status",complete>0?"completed":"pending").put("error",JSONObject.NULL)
      .put("timestampSource","realtime").put("alignmentMovementStartedBootNs",clock.movementStartedNs())
      .put("installationId","emulator-numerical-control").put("cameraId","analytic-front")
      .put("width",640).put("height",480).put("imageAxes","native-sensor-unrotated-unmirrored")
      .put("sensorOrientationDegrees",270).put("stabilizationRequested","off")
      .put("capturePipeline","native-camera-imu-v3").put("opticalSetup","waist-bag-window");
    try(Writer w=new FileWriter(new File(dir,"manifest.json"))){w.write(manifest.toString());}
    // Archive the executed input identity and actual output; not physical capture.
    try(java.util.zip.ZipOutputStream out=new java.util.zip.ZipOutputStream(new FileOutputStream(new File(root,id+".zip")))){
      for(File source:new File[]{new File(fixture,"fixture.json"),new File(dir,"manifest.json"),new File(dir,"on-device-states.ndjson")}){
        out.putNextEntry(new java.util.zip.ZipEntry(source.getName()));
        try(InputStream in=new FileInputStream(source)){byte[] buffer=new byte[4096];int n;while((n=in.read(buffer))>0)out.write(buffer,0,n);}
        out.closeEntry();
      }
    }
    boolean accepted=false;String rejection=null;JSONObject saved=null;
    try{saved=OnDeviceProfile.finish(files,id);accepted=true;}catch(Exception e){rejection=e.getMessage();}
    boolean preserved=accepted||OnDeviceProfile.read(profile).optBoolean("labPreviousProfile");
    boolean expected=arguments.getString("expect","accept").equals("accept");
    boolean legitimateProcessing=processingFailure==null||(!expected&&spec.optBoolean("blank")&&"Quiet baseline not established before fixture movement".equals(processingFailure));
    return new JSONObject().put("kind","android-production-jni-calibration-control")
      .put("syntheticInput",true).put("physicalPhoneValidation",false).put("fullAppUiReplay",false)
      .put("expectedAcceptance",expected).put("accepted",accepted).put("previousPreserved",preserved)
      .put("passed",accepted==expected&&preserved&&legitimateProcessing).put("rejection",rejection==null?JSONObject.NULL:rejection)
      .put("processingFailure",processingFailure==null?JSONObject.NULL:processingFailure)
      .put("baselineAccepted",baseline.accepted()).put("initializedFrames",initialized).put("numericallyReadyFrames",ready)
      .put("completionSeconds",complete==0?JSONObject.NULL:(complete-first)/1e9)
      .put("wallSeconds",System.nanoTime()/1e9-wall).put("captureDirectory",dir.getAbsolutePath())
      .put("lastState",last==null?JSONObject.NULL:last).put("savedProfile",saved==null?JSONObject.NULL:saved);
  }
}
