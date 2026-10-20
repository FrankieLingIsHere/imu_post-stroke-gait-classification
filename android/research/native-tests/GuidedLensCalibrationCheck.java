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
    check(still.acceptedViews()==1&&!still.ready(),"Repeated still views must not pass");
    check(still.progress().getString("frameStatus").equals("duplicate-view"),"Duplicate reason must be visible");
    check(still.failureMessage().equals("Not enough different clear views were collected."),"Count failure reason");still.close();
    GuidedLensCalibration blurred=new GuidedLensCalibration(640,480);
    for(int i=0;i<views.length();i++)blurred.observePoints(points(views.getJSONObject(i)),ids(views.getJSONObject(i)),2,i*300000000L);
    check(blurred.acceptedViews()==0&&!blurred.ready(),"Blur must not pass");blurred.close();
    GuidedLensCalibration frontOnly=new GuidedLensCalibration(640,480);
    for(int zoom=0;zoom<2;zoom++)for(int x=0;x<5;x++)for(int y=0;y<3;y++){
      Point[] plane=new Point[48];int[] cornerIds=new int[48];int at=0;double scale=zoom==0?22:35;
      for(int row=1;row<=6;row++)for(int col=1;col<=8;col++){
        plane[at]=new Point(160+x*80+(col-4.5)*scale,120+y*120+(row-3.5)*scale);cornerIds[at]=at++;
      }
      frontOnly.observePoints(plane,cornerIds,100,(zoom*15+x*3+y)*300000000L);
    }
    check(frontOnly.acceptedViews()==4&&!frontOnly.ready(),"Front-on translations must not count during the angle round");
    check(frontOnly.failureMessage().equals("Left and right viewing angles are still missing."),"Name missing coverage despite sufficient view count");frontOnly.close();
    GuidedLensCalibration bounded=new GuidedLensCalibration(640,480);
    int attempts=0;
    for(int zoom=0;zoom<3;zoom++)for(int x=0;x<9;x++)for(int y=0;y<5;y++){
      Point[] plane=new Point[48];int[] cornerIds=new int[48];int at=0;double scale=23+zoom*7;
      for(int row=1;row<=6;row++)for(int col=1;col<=8;col++){
        plane[at]=new Point(165+x*38+(col-4.5)*scale,140+y*50+(row-3.5)*scale);cornerIds[at]=at++;
      }
      bounded.observePoints(plane,cornerIds,100,attempts++*300000000L);
      check(bounded.acceptedViews()<=GuidedLensCalibration.MAX_VIEWS,"Memory bound must hold");
    }
    check(bounded.acceptedViews()==4&&!bounded.ready(),"Irrelevant poses stop inflating the initial count");
    check(bounded.activeRound().equals("side-angles"),"First missing angle is explicitly selected");
    int revision=bounded.progress().getInt("acceptedRevision");
    for(int i=0;i<views.length();i++){
      JSONObject row=views.getJSONObject(i);bounded.observePoints(points(row),ids(row),100,attempts++*300000000L);
      check(bounded.acceptedViews()<=48,"Replacement stays bounded");if(bounded.ready())break;
    }
    check(bounded.progress().getInt("acceptedRevision")>revision,"Useful new poses must enter after the pool fills");

    check(bounded.progress().getBoolean("coverageReady"),"Missing angles can be acquired after 48 views");bounded.close();
    // Deliberately noisy observations must stay rejected but can keep collecting
    // better poses without exceeding the memory pool. Real solver, no fitted success.
    GuidedLensCalibration noisy=new GuidedLensCalibration(640,480);Random rng=new Random(7);
    boolean reachedPool=false;
    for(int repeat=0;repeat<8;repeat++)for(int i=0;i<views.length();i++){
      JSONObject row=views.getJSONObject(i);Point[] observed=points(row);
      double shiftX=(repeat%3-1)*12,shiftY=(repeat%4-1.5)*10;
      for(Point point:observed){point.x+=shiftX+rng.nextGaussian()*2;point.y+=shiftY+rng.nextGaussian()*2;}
      noisy.observePoints(observed,ids(row),100,attempts++*300000000L);
      check(noisy.acceptedViews()<=48,"Noisy replacement pool stays bounded");
      if(noisy.acceptedViews()==48)reachedPool=true;
    }
    check(reachedPool&&!noisy.ready(),"48 retained noisy views never force success");
    check(noisy.progress().getInt("replacedViews")>0,"New views replace old redundant views after 48");noisy.close();
    GuidedLensCalibration partial=new GuidedLensCalibration(640,480);
    Point[] flat=new Point[48];int[] allIds=new int[48];int at=0;
    for(int row=1;row<=6;row++)for(int col=1;col<=8;col++){flat[at]=new Point(320+(col-4.5)*32,240+(row-3.5)*32);allIds[at]=at++;}
    partial.observePoints(flat,allIds,100,0);
    List<Point> crop=new ArrayList<>();List<Integer> cropIds=new ArrayList<>();
    for(int i=0;i<48;i++)if(i%8<5){crop.add(flat[i]);cropIds.add(i);}
    partial.observePoints(crop.toArray(Point[]::new),cropIds.stream().mapToInt(Integer::intValue).toArray(),100,300000000L);
    check(partial.acceptedViews()==1,"Changing partial corner visibility must not invent another pose");partial.close();
    GuidedLensCalibration solver=new GuidedLensCalibration(640,480);
    final int[] fittingEvents={0};
    solver.setFitListener(()->{fittingEvents[0]++;check(solver.progress().getString("frameStatus").equals("fitting"),"Preview must announce fitting before optimizer blocks");});
    for(int i=0;i<views.length()&&!solver.ready();i++){JSONObject row=views.getJSONObject(i);solver.observePoints(points(row),ids(row),100,row.getLong("timestampNs"));}
    check(solver.ready(),"Diverse known geometry must solve: "+solver.progress());
    check(fittingEvents[0]>0,"Fitting progress callback must run");
    check(solver.progress().getBoolean("coverageReady"),"Same coverage gates required");
    JSONObject report=solver.report();JSONArray K=report.getJSONObject("lens").getJSONArray("cameraMatrix"),expected=fixture.getJSONArray("expectedCameraMatrix");
    for(int i=0;i<2;i++)for(int j:new int[]{i,2})check(Math.abs(K.getJSONArray(i).getDouble(j)-expected.getJSONArray(i).getDouble(j))<2,"Known focal/principal point recovery");
    check(!report.getBoolean("fullCalibrationReady")&&!report.getBoolean("distanceReady"),"Lens calibration cannot grant distance readiness");
    check(report.getJSONObject("lens").getDouble("heldOutP90Pixels")<.3,"Held-out prediction quality");
    check(!GuidedLensCalibration.validMatrix(new double[]{Double.NaN,0,320,0,500,240,0,0,1},640,480),"NaN intrinsics must fail");
    JSONObject out=new JSONObject().put("knownAnswer",report).put("checks",new JSONArray(Arrays.asList("same-view-rejection","blur-rejection","known-lens-recovery","held-out-views","lens-not-distance","nonfinite-rejection","specific-coverage-failure","fitting-status-before-optimizer","stage-specific-view-admission","bounded-pool-replacement","partial-corner-pose-invariance")));
    System.out.println(out);solver.close();
  }
}
