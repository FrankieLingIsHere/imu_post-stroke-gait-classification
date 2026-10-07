import expo.modules.gaitcalibration.GuidedLensCalibration;
import org.json.*;
import org.opencv.core.*;
import org.opencv.imgcodecs.Imgcodecs;
import java.nio.file.*;
import java.util.*;
import java.util.zip.ZipFile;

/** Real OpenCV 4.12 JNI and the actual app solver. Not Android hardware validation. */
public final class GuidedLensCalibrationCheck {
  private static void check(boolean ok,String reason){if(!ok)throw new AssertionError(reason);}
  private static Point[] points(JSONObject row){JSONArray p=row.getJSONArray("points");Point[] v=new Point[p.length()];for(int i=0;i<v.length;i++)v[i]=new Point(p.getJSONArray(i).getDouble(0),p.getJSONArray(i).getDouble(1));return v;}
  private static int[] ids(JSONObject row){JSONArray a=row.getJSONArray("ids");int[] v=new int[a.length()];for(int i=0;i<v.length;i++)v[i]=a.getInt(i);return v;}
  public static void main(String[] args)throws Exception{
    System.load(Paths.get(args[0]).toAbsolutePath().toString());check(Core.getVersionString().startsWith("4.12"),"JNI version mismatch");
    if(args.length>2 && args[2].equals("replay")){
      GuidedLensCalibration solver=new GuidedLensCalibration(640,480);
      try(ZipFile zip=new ZipFile(args[1])){
       String rows=new String(zip.getInputStream(zip.getEntry("frames.ndjson")).readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);
       for(String line:rows.split("\\n")){if(line.isBlank())continue;JSONObject f=new JSONObject(line);
        byte[] encoded=zip.getInputStream(zip.getEntry(f.getString("file"))).readAllBytes();MatOfByte input=new MatOfByte(encoded);
        Mat image=Imgcodecs.imdecode(input,Imgcodecs.IMREAD_GRAYSCALE);input.release();
        check(image.cols()==640&&image.rows()==480,"Replay image dimensions");
        byte[] b=new byte[(int)image.total()];image.get(0,0,b);solver.observe(b,f.getLong("timestampNs"));image.release();if(solver.ready())break;
       }
      }
      JSONObject out=solver.progress().put("source","retained-phone-artifact-replay-not-new-capture").put("report",solver.report()==null?JSONObject.NULL:solver.report());System.out.println(out);solver.close();return;
    }
    JSONObject fixture=new JSONObject(Files.readString(Paths.get(args[1])));JSONArray views=fixture.getJSONArray("views");
    GuidedLensCalibration still=new GuidedLensCalibration(640,480);JSONObject first=views.getJSONObject(0);
    for(int i=0;i<100;i++)still.observePoints(points(first),ids(first),100,i*300000000L);
    check(still.acceptedViews()==1&&!still.ready(),"Repeated still views must not pass");still.close();
    GuidedLensCalibration blurred=new GuidedLensCalibration(640,480);
    for(int i=0;i<views.length();i++)blurred.observePoints(points(views.getJSONObject(i)),ids(views.getJSONObject(i)),2,i*300000000L);
    check(blurred.acceptedViews()==0&&!blurred.ready(),"Blur must not pass");blurred.close();
    GuidedLensCalibration solver=new GuidedLensCalibration(640,480);
    for(int i=0;i<views.length()&&!solver.ready();i++){JSONObject row=views.getJSONObject(i);solver.observePoints(points(row),ids(row),100,row.getLong("timestampNs"));}
    check(solver.ready(),"Diverse known geometry must solve: "+solver.progress());
    JSONObject report=solver.report();JSONArray K=report.getJSONObject("lens").getJSONArray("cameraMatrix"),expected=fixture.getJSONArray("expectedCameraMatrix");
    for(int i=0;i<2;i++)for(int j:new int[]{i,2})check(Math.abs(K.getJSONArray(i).getDouble(j)-expected.getJSONArray(i).getDouble(j))<2,"Known focal/principal point recovery");
    check(!report.getBoolean("fullCalibrationReady")&&!report.getBoolean("distanceReady"),"Lens calibration cannot grant distance readiness");
    check(report.getJSONObject("lens").getDouble("heldOutP90Pixels")<.3,"Held-out prediction quality");
    check(!GuidedLensCalibration.validMatrix(new double[]{Double.NaN,0,320,0,500,240,0,0,1},640,480),"NaN intrinsics must fail");
    JSONObject out=new JSONObject().put("knownAnswer",report).put("checks",new JSONArray(Arrays.asList("same-view-rejection","blur-rejection","known-lens-recovery","held-out-views","lens-not-distance","nonfinite-rejection")));
    System.out.println(out);solver.close();
  }
}
