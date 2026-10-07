package expo.modules.gaitcalibration;

import java.util.*;
import org.json.*;
import org.opencv.core.*;
import org.opencv.calib3d.Calib3d;
import org.opencv.imgproc.Imgproc;
import org.opencv.objdetect.*;

/** Published Zhang/OpenCV lens solver. Selection/admission limits are provisional
 * engineering checks, not published accuracy guarantees or camera/IMU calibration.
 * Board coordinates use arbitrary units: uniform display scaling cancels in K/D.
 * The display must preserve the board's aspect ratio and remain flat. */
public final class GuidedLensCalibration implements AutoCloseable {
  public static final int MIN_VIEWS=24;
  private final int width,height;
  private final CharucoBoard board=new CharucoBoard(new Size(9,7),1f,.75f,Objdetect.getPredefinedDictionary(Objdetect.DICT_4X4_100));
  private final CharucoDetector detector=new CharucoDetector(board);
  private final List<View> views=new ArrayList<>();
  private long lastSample=Long.MIN_VALUE;
  private String hint="Point the front camera at the digital board.";
  private JSONObject report;
  private int lastFitCount=0;
  private static final class View {
    final MatOfPoint3f object;
    final MatOfPoint2f image;
    final double cx,cy,scale,px,py;
    final long timestamp;
    View(Point3[] o,Point[] p,double[] descriptor,long timestamp){
      object=new MatOfPoint3f(o);image=new MatOfPoint2f(p);
      cx=descriptor[0];cy=descriptor[1];scale=descriptor[2];px=descriptor[3];py=descriptor[4];this.timestamp=timestamp;
    }
    void close(){object.release();image.release();}
  }
  public GuidedLensCalibration(int width,int height){this.width=width;this.height=height;}
  public static CharucoBoard newBoard(){return new CharucoBoard(new Size(9,7),1f,.75f,Objdetect.getPredefinedDictionary(Objdetect.DICT_4X4_100));}
  public int acceptedViews(){return views.size();}
  public String hint(){return hint;}
  public boolean ready(){return report!=null;}
  public JSONObject report(){return report;}

  /** Work on the storage thread; never block the Camera2 or IMU callback thread. */
  public void observe(byte[] luma,long timestamp) throws JSONException {
    if(ready() || (lastSample!=Long.MIN_VALUE && timestamp-lastSample<250000000L))return;
    lastSample=timestamp;
    Mat gray=new Mat(height,width,CvType.CV_8UC1),corners=new Mat(),ids=new Mat(),lap=new Mat();
    MatOfDouble mean=new MatOfDouble(),sd=new MatOfDouble();
    try{
      gray.put(0,0,luma);detector.detectBoard(gray,corners,ids);
      if(ids.rows()<20){hint="Keep the whole board in view.";return;}
      // Measure board-region sharpness; bag edges/text outside the board must not
      // make a blurred board appear sharp.
      Point[] points=new Point[corners.rows()];int[] identifiers=new int[ids.rows()];
      for(int i=0;i<points.length;i++){double[] p=corners.get(i,0);points[i]=new Point(p[0],p[1]);identifiers[i]=(int)ids.get(i,0)[0];}
      MatOfPoint bounds=new MatOfPoint(points);Rect roi=Imgproc.boundingRect(bounds);bounds.release();
      roi.x=Math.max(0,roi.x);roi.y=Math.max(0,roi.y);roi.width=Math.min(width-roi.x,roi.width);roi.height=Math.min(height-roi.y,roi.height);
      Mat region=gray.submat(roi);
      try{Imgproc.Laplacian(region,lap,CvType.CV_64F);Core.meanStdDev(lap,mean,sd);}finally{region.release();}
      observePoints(points,identifiers,Math.pow(sd.toArray()[0],2),timestamp);
    }finally{gray.release();corners.release();ids.release();lap.release();mean.release();sd.release();}
  }
  /** Same admission/solver path used by native-image capture and JVM fixtures. */
  public boolean observePoints(Point[] points,int[] ids,double sharpness,long timestamp) throws JSONException {
    if(ready())return false;
    if(points.length!=ids.length || points.length<20 || !Double.isFinite(sharpness) || sharpness<40){hint="Hold the phone steady for a clear view.";return false;}
    MatOfPoint3f grid=board.getChessboardCorners();Point3[] all=grid.toArray(),objects=new Point3[points.length];grid.release();
    Set<Integer> unique=new HashSet<>();
    double minX=width,minY=height,maxX=0,maxY=0;
    for(int i=0;i<points.length;i++){
      if(ids[i]<0 || ids[i]>=all.length || !unique.add(ids[i]) || !Double.isFinite(points[i].x) || !Double.isFinite(points[i].y)
          || points[i].x<0 || points[i].x>=width || points[i].y<0 || points[i].y>=height){hint="Keep the whole board in view.";return false;}
      objects[i]=all[ids[i]];
      minX=Math.min(minX,points[i].x);maxX=Math.max(maxX,points[i].x);minY=Math.min(minY,points[i].y);maxY=Math.max(maxY,points[i].y);
    }
    if(maxX-minX<width*.20 || maxY-minY<height*.20){hint="Move a little closer to the board.";return false;}
    MatOfPoint2f source=new MatOfPoint2f(Arrays.stream(objects).map(p->new Point(p.x,p.y)).toArray(Point[]::new)),image=new MatOfPoint2f(points);
    Mat homography=Calib3d.findHomography(source,image,0);source.release();image.release();
    if(homography.empty()){homography.release();hint="Keep the whole board in view.";return false;}
    MatOfPoint2f quad=new MatOfPoint2f(new Point(1,1),new Point(8,1),new Point(8,6),new Point(1,6)),projected=new MatOfPoint2f();
    Point[] q;
    try{Core.perspectiveTransform(quad,projected,homography);q=projected.toArray();}finally{quad.release();projected.release();homography.release();}
    double top=distance(q[0],q[1]),bottom=distance(q[3],q[2]),left=distance(q[0],q[3]),right=distance(q[1],q[2]);
    if(Math.min(Math.min(top,bottom),Math.min(left,right))<5){hint="Keep the whole board in view.";return false;}
    double[] d={(minX+maxX)/2/width,(minY+maxY)/2/height,Math.sqrt((maxX-minX)*(maxY-minY)/(width*(double)height)),
      (left-right)/(left+right),(top-bottom)/(top+bottom)};
    for(View old:views)if(Math.hypot(old.cx-d[0],old.cy-d[1])<.05 && Math.abs(old.scale-d[2])<.055 && Math.hypot(old.px-d[3],old.py-d[4])<.055){
      hint=nextHint();return false;
    }
    views.add(new View(objects,points,d,timestamp));hint=nextHint();
    if(views.size()>=MIN_VIEWS && sufficientCoverage() && views.size()-lastFitCount>=4){
      lastFitCount=views.size();
      JSONObject candidate=fit();
      if(candidate.optBoolean("lensReady")){report=candidate;hint="Lens parameters saved. Sensor alignment is still needed.";}
      else hint="Try a clearer view from another angle.";
    }
    // Bound memory/optimizer cost while retaining early diverse views.
    if(views.size()>48){views.remove(views.size()-1).close();hint="Try a clearer view from another angle.";}
    return true;
  }
  private static double distance(Point a,Point b){return Math.hypot(a.x-b.x,a.y-b.y);}
  private double span(String value){
    double lo=Double.POSITIVE_INFINITY,hi=Double.NEGATIVE_INFINITY;
    for(View v:views){double n=value.equals("x")?v.cx:value.equals("y")?v.cy:value.equals("px")?v.px:v.py;lo=Math.min(lo,n);hi=Math.max(hi,n);}
    return views.isEmpty()?0:hi-lo;
  }
  private boolean sufficientCoverage(){return span("x")>=.25 && span("y")>=.20 && span("px")>=.12 && span("py")>=.12;}
  private String nextHint(){
    if(views.size()<4)return "Move slowly to show a different view.";
    if(span("px")<.12)return "Tilt the phone gently left and right.";
    if(span("py")<.12)return "Tilt the phone gently up and down.";
    if(span("x")<.25)return "Move the board toward the left and right of the view.";
    if(span("y")<.20)return "Move the board toward the top and bottom of the view.";
    return "Move slowly to show a different view.";
  }
  public JSONObject progress() throws JSONException {return new JSONObject().put("acceptedViews",acceptedViews()).put("targetViews",MIN_VIEWS)
    .put("hint",hint).put("coverageReady",sufficientCoverage()).put("lensReady",ready());}
  private JSONObject fit() throws JSONException {
    JSONObject r=new JSONObject().put("schemaVersion",1).put("kind","phone-camera-lens-calibration-v1")
      .put("method","opencv-zhang-2000").put("methodDoi","10.1109/34.888718").put("opencvVersion",Core.VERSION)
      .put("lensReady",false).put("fullCalibrationReady",false).put("distanceReady",false).put("independentDistanceValidation",false)
      .put("boardUnits","arbitrary-uniform-units-not-metres").put("acceptedViews",views.size());
    Mat K=Mat.eye(3,3,CvType.CV_64F),D=new Mat(),subsetK=Mat.eye(3,3,CvType.CV_64F),subsetD=new Mat();
    List<Mat> obj=new ArrayList<>(),img=new ArrayList<>(),rot=new ArrayList<>(),trans=new ArrayList<>(),rot2=new ArrayList<>(),trans2=new ArrayList<>();
    List<View> held=new ArrayList<>();
    try{
      for(int i=0;i<views.size();i++){View v=views.get(i);if(i%4==3)held.add(v);else{obj.add(v.object);img.add(v.image);}}
      double rms=Calib3d.calibrateCamera(obj,img,new Size(width,height),K,D,rot,trans,0,new TermCriteria(TermCriteria.COUNT+TermCriteria.EPS,60,1e-8));
      double[] k=new double[9],d=new double[(int)D.total()];K.get(0,0,k);D.get(0,0,d);
      if(!finite(k)||!finite(d)||d.length!=5 || !validMatrix(k,width,height) || !monotonic(k,d,width,height))throw new IllegalArgumentException("implausible-lens-parameters");
      List<Double> residuals=new ArrayList<>();MatOfDouble distortion=new MatOfDouble(d);
      try{for(View v:held){
        Mat rv=new Mat(),tv=new Mat();MatOfPoint2f predictions=new MatOfPoint2f();
        try{
          if(!Calib3d.solvePnP(v.object,v.image,K,distortion,rv,tv))throw new IllegalArgumentException("held-out-pose-failed");
          Calib3d.projectPoints(v.object,rv,tv,K,distortion,predictions);
          Point[] p=predictions.toArray(),actual=v.image.toArray();for(int i=0;i<p.length;i++)residuals.add(distance(p[i],actual[i]));
        }finally{rv.release();tv.release();predictions.release();}
      }}finally{distortion.release();}
      Collections.sort(residuals);double p90=residuals.get(Math.min(residuals.size()-1,(int)Math.ceil(residuals.size()*.9)-1));
      // Sensitivity to dropping recent training views catches weak/overfit geometry.
      Calib3d.calibrateCamera(obj.subList(0,obj.size()-3),img.subList(0,img.size()-3),new Size(width,height),subsetK,subsetD,rot2,trans2,0,new TermCriteria(TermCriteria.COUNT+TermCriteria.EPS,60,1e-8));
      double drift=Math.max(Math.abs(subsetK.get(0,0)[0]/k[0]-1),Math.abs(subsetK.get(1,1)[0]/k[4]-1));
      double principalDrift=Math.hypot(subsetK.get(0,2)[0]-k[2],subsetK.get(1,2)[0]-k[5])/Math.hypot(width,height);
      if(!Double.isFinite(rms)||!Double.isFinite(p90)||!Double.isFinite(drift)||!Double.isFinite(principalDrift)||rms>1 || p90>1.5 || drift>.05 || principalDrift>.02)throw new IllegalArgumentException("lens-validation-failed");
      JSONArray matrix=new JSONArray();for(int i=0;i<3;i++)matrix.put(new JSONArray(Arrays.copyOfRange(k,i*3,i*3+3)));
      r.put("lensReady",true).put("status","lens-candidate").put("errors",new JSONArray())
        .put("lens",new JSONObject().put("cameraMatrix",matrix).put("distortion",new JSONArray(d)).put("model","opencv-pinhole-radtan5")
          .put("trainingRmsPixels",rms).put("heldOutP90Pixels",p90).put("heldOutViews",held.size()).put("focalSubsetDriftFraction",drift).put("principalSubsetDriftFraction",principalDrift));
    }catch(RuntimeException e){r.put("status","rejected").put("errors",new JSONArray().put(e.getMessage()));}
    finally{K.release();D.release();subsetK.release();subsetD.release();for(List<Mat> list:Arrays.asList(rot,trans,rot2,trans2))for(Mat m:list)m.release();}
    return r;
  }
  private static boolean finite(double[] v){for(double n:v)if(!Double.isFinite(n))return false;return true;}
  public static boolean validMatrix(double[] k,int w,int h){double dim=Math.max(w,h);return k.length==9&&finite(k)&&k[0]>.25*dim&&k[0]<3*dim&&k[4]>.25*dim&&k[4]<3*dim
    &&k[0]/k[4]>.67&&k[0]/k[4]<1.5&&k[2]>.2*w&&k[2]<.8*w&&k[5]>.2*h&&k[5]<.8*h&&Math.abs(k[8]-1)<1e-9;}
  private static boolean monotonic(double[] k,double[] d,int w,int h){
    double maxR=0;for(int x:new int[]{0,w})for(int y:new int[]{0,h})maxR=Math.max(maxR,Math.hypot((x-k[2])/k[0],(y-k[5])/k[4]));
    for(int i=0;i<=100;i++){double r=maxR*i/100,r2=r*r;double derivative=1+3*d[0]*r2+5*d[1]*r2*r2+7*d[4]*r2*r2*r2;if(!Double.isFinite(derivative)||derivative<=.1)return false;}
    return true;
  }
  public void close(){for(View v:views)v.close();views.clear();}
}
