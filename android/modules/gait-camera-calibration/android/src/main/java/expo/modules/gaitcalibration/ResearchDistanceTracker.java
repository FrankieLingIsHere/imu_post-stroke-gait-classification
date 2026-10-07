package expo.modules.gaitcalibration;

import org.json.*;
import org.opencv.android.OpenCVLoader;
import org.opencv.core.*;
import org.opencv.calib3d.Calib3d;
import org.opencv.imgproc.Imgproc;
import org.opencv.video.Video;
import org.apache.commons.math3.linear.*;
import java.util.*;

/** Research-only growing-map front camera tracking. No clinical distance/stop output. */
public final class ResearchDistanceTracker {
  private final JSONObject profile;
  private Mat K,D,previous;
  private List<Point> initialPixels,pixels;
  private List<Point3> landmarks;
  private List<Point> candidateOrigins,candidatePixels;
  private double[][] candidateRotation,currentRotation;
  private double[] candidateTranslation,currentTranslation;
  private double candidateTime;
  private int mapPointsAdded=0,keyframes=0;
  private final List<Pose> poses=new ArrayList<>();
  private final List<Imu> acceleration=new ArrayList<>(),gyroscope=new ArrayList<>();
  private final List<JSONObject> events=new ArrayList<>();
  private String state="needs-profile",failure="";
  private double firstTime=-1,lastTime=-1,offset=0;
  private double[][] Rci;
  private int features=0,processed=0;
  private double lastRms=0;
  private static final class Pose {double t;double[] p;double[][] q;Pose(double t,double[] p,double[][] q){this.t=t;this.p=p;this.q=q;}}
  private static final class Imu {double t;double[] v;Imu(double t,double[] v){this.t=t;this.v=v;}}
  public ResearchDistanceTracker(JSONObject profile) throws Exception {
    this.profile=profile;
    if(profile==null)return;
    if(!OpenCVLoader.initLocal())throw new IllegalStateException("OpenCV could not load");
    K=new Mat(3,3,CvType.CV_64F);K.put(0,0,flatten(matrix(profile.getJSONObject("lens").getJSONArray("cameraMatrix"))));
    JSONArray distortion=profile.getJSONObject("lens").getJSONArray("distortion");D=new Mat(1,distortion.length(),CvType.CV_64F);
    double[] values=new double[distortion.length()];for(int i=0;i<values.length;i++)values[i]=distortion.getDouble(i);D.put(0,0,values);
    JSONObject rotation=profile.getJSONObject("rotationTiming");Rci=matrix(rotation.getJSONArray("rotationImuToCamera"));
    offset=rotation.getDouble("residualTimeOffsetSeconds");state="initializing";
  }
  public void sensor(String name,long timestamp,double x,double y,double z){
    if(name.equals("accelerometer"))acceleration.add(new Imu(timestamp/1e9,new double[]{x,y,z}));
    if(name.equals("gyroscope"))gyroscope.add(new Imu(timestamp/1e9,new double[]{x,y,z}));
  }
  public JSONObject process(byte[] luma,int width,int height,long timestamp,JSONObject capture) throws JSONException {
    processed++;
    if(profile==null||!failure.isEmpty())return snapshot();
    Mat image=new Mat(height,width,CvType.CV_8UC1);image.put(0,0,luma);
    try {
      if(capture.isNull("exposureNs")||capture.isNull("rollingShutterSkewNs"))throw new Exception("missing-camera-timing");
      double t=(timestamp+capture.getDouble("exposureNs")/2+capture.getDouble("rollingShutterSkewNs")/2)/1e9+offset;
      if(lastTime>=0&&(t<=lastTime||t-lastTime>.3))throw new Exception("camera-gap");
      if(previous==null){
        MatOfPoint corners=new MatOfPoint();Imgproc.goodFeaturesToTrack(image,corners,800,.01,8);
        pixels=new ArrayList<>(corners.toList());corners.release();initialPixels=new ArrayList<>(pixels);
        if(pixels.size()<80)throw new Exception("low-texture");firstTime=t;
      }else{
        MatOfPoint2f before=new MatOfPoint2f();before.fromList(pixels);
        MatOfPoint2f after=new MatOfPoint2f(),back=new MatOfPoint2f();MatOfByte ok=new MatOfByte(),backOk=new MatOfByte();MatOfFloat err=new MatOfFloat();
        List<Point> current=new ArrayList<>(),orig=new ArrayList<>();List<Point3> points=new ArrayList<>();
        try {
          Video.calcOpticalFlowPyrLK(previous,image,before,after,ok,err);
          Video.calcOpticalFlowPyrLK(image,previous,after,back,backOk,err);
          Point[] a=after.toArray(),b=back.toArray();byte[] valid=ok.toArray(),reverse=backOk.toArray();
          for(int i=0;i<a.length;i++)if(valid[i]!=0&&reverse[i]!=0&&distance(b[i],pixels.get(i))<1){
            current.add(a[i]);if(landmarks==null)orig.add(initialPixels.get(i));else points.add(landmarks.get(i));
          }
        }finally{before.release();after.release();back.release();ok.release();backOk.release();err.release();}
        if(landmarks==null){
          initialPixels=orig;if(current.size()<80)throw new Exception("initial-features-lost");
          double[] displacement=new double[current.size()];for(int i=0;i<current.size();i++)displacement[i]=distance(current.get(i),orig.get(i));
          Arrays.sort(displacement);
          if(displacement[displacement.length/2]>12){
            if(!initialize(orig,current,t)&&t-firstTime>8)throw new Exception("insufficient-parallax");
            if(landmarks!=null)current=pixels;
          }
        }else{
          landmarks=points;current=locate(current,t);
        }
        pixels=current;
      }
      if(landmarks!=null)renewMap(image,t);
      features=pixels.size();if(previous!=null)previous.release();previous=image;image=null;lastTime=t;
    }catch(Exception e){state="tracking-lost";failure=e.getMessage()==null?"tracking-error":e.getMessage();}
    finally{if(image!=null)image.release();}
    JSONObject result=snapshot();events.add(result);return result;
  }
  private boolean initialize(List<Point> a,List<Point> b,double time)throws Exception{
    MatOfPoint2f pa=new MatOfPoint2f();pa.fromList(a);MatOfPoint2f pb=new MatOfPoint2f();pb.fromList(b);
    MatOfPoint2f na=new MatOfPoint2f(),nb=new MatOfPoint2f();Mat mask=new Mat(),R=new Mat(),T=new Mat(),E=null,X=new Mat();
    Mat eye=Mat.eye(3,3,CvType.CV_64F),P0=Mat.zeros(3,4,CvType.CV_64F),P1=Mat.zeros(3,4,CvType.CV_64F),at=new Mat(),bt=new Mat();
    try{
      Calib3d.undistortPoints(pa,na,K,D);Calib3d.undistortPoints(pb,nb,K,D);
      Point[] aa=na.toArray(),bb=nb.toArray();
      if(rotationOnly(aa,bb))return false;
      E=Calib3d.findEssentialMat(na,nb,eye,Calib3d.RANSAC,.999,.002,1000,mask);
      if(E.rows()!=3||E.cols()!=3)return false;
      Calib3d.recoverPose(E,na,nb,eye,R,T,mask);
      for(int i=0;i<3;i++){P0.put(i,i,1.);for(int j=0;j<3;j++)P1.put(i,j,R.get(i,j)[0]);P1.put(i,3,T.get(i,0)[0]);}
      Mat flatA=na.reshape(1),flatB=nb.reshape(1),transposedA=flatA.t(),transposedB=flatB.t();
      transposedA.copyTo(at);transposedB.copyTo(bt);flatA.release();flatB.release();transposedA.release();transposedB.release();
      Calib3d.triangulatePoints(P0,P1,at,bt,X);
      List<Point3> selected=new ArrayList<>();List<Point> observed=new ArrayList<>();double[][] r=matrix(R);double[] tv=vector(T);
      for(int i=0;i<aa.length;i++){
        double w=X.get(3,i)[0];if(Math.abs(w)<1e-10)continue;
        double[] point={X.get(0,i)[0]/w,X.get(1,i)[0]/w,X.get(2,i)[0]/w};
        double[] rayA=unit(new double[]{aa[i].x,aa[i].y,1}),rayB=multiply(transpose(r),unit(new double[]{bb[i].x,bb[i].y,1}));
        double angle=Math.acos(Math.max(-1,Math.min(1,dot(rayA,rayB))));
        if(mask.get(i,0)[0]!=0&&point[2]>.05&&multiply(r,point)[2]+tv[2]>.05&&angle>Math.PI/180&&finite(point)){
          selected.add(new Point3(point[0],point[1],point[2]));observed.add(b.get(i));
        }
      }
      if(selected.size()<40)return false;
      landmarks=selected;pixels=observed;state="tracking";addPose(time,r,tv);return true;
    }finally{for(Mat m:new Mat[]{pa,pb,na,nb,mask,R,T,X,eye,P0,P1,at,bt})m.release();if(E!=null)E.release();}
  }
  private List<Point> locate(List<Point> current,double t)throws Exception{
    if(landmarks.size()<30)throw new Exception("mapped-features-lost");
    MatOfPoint3f world=new MatOfPoint3f();world.fromList(landmarks);MatOfPoint2f image=new MatOfPoint2f();image.fromList(current);
    Mat rv=new Mat(),tv=new Mat(),inliers=new Mat();MatOfDouble distortion=new MatOfDouble(D);
    try{
      boolean ok=Calib3d.solvePnPRansac(world,image,K,distortion,rv,tv,false,150,2f,.999,inliers);
      if(!ok||inliers.rows()<30||inliers.rows()<landmarks.size()*.65)throw new Exception("inconsistent-map-pose");
      List<Point3> selected=new ArrayList<>();List<Point> observed=new ArrayList<>();
      for(int i=0;i<inliers.rows();i++){int index=(int)inliers.get(i,0)[0];selected.add(landmarks.get(index));observed.add(current.get(index));}
      world.fromList(selected);image.fromList(observed);Calib3d.solvePnPRefineLM(world,image,K,distortion,rv,tv);
      MatOfPoint2f projected=new MatOfPoint2f();Mat R=new Mat();
      try{
        Calib3d.projectPoints(world,rv,tv,K,distortion,projected);Point[] predicted=projected.toArray();double squared=0;
        for(int i=0;i<predicted.length;i++)squared+=Math.pow(distance(predicted[i],observed.get(i)),2);
        lastRms=Math.sqrt(squared/(predicted.length*2));if(lastRms>1.5)throw new Exception("reprojection-error");
        Calib3d.Rodrigues(rv,R);addPose(t,matrix(R),vector(tv));
      }finally{projected.release();R.release();}
      landmarks=selected;return observed;
    }finally{world.release();image.release();rv.release();tv.release();inliers.release();distortion.release();}
  }
  /** New landmarks use two already accepted world-camera poses. No essential-matrix
   * reinitialization, scale reset or stitching after loss is permitted. */
  private void renewMap(Mat image,double time)throws Exception{
    if(candidatePixels!=null&&previous!=null){
      MatOfPoint2f before=new MatOfPoint2f();before.fromList(candidatePixels);
      MatOfPoint2f after=new MatOfPoint2f(),back=new MatOfPoint2f();MatOfByte ok=new MatOfByte(),reverse=new MatOfByte();MatOfFloat error=new MatOfFloat();
      try{
        Video.calcOpticalFlowPyrLK(previous,image,before,after,ok,error);
        Video.calcOpticalFlowPyrLK(image,previous,after,back,reverse,error);
        Point[] a=after.toArray(),b=back.toArray();byte[] good=ok.toArray(),reversed=reverse.toArray();
        List<Point> origins=new ArrayList<>(),now=new ArrayList<>();
        for(int i=0;i<a.length;i++)if(good[i]!=0&&reversed[i]!=0&&distance(b[i],candidatePixels.get(i))<1){origins.add(candidateOrigins.get(i));now.add(a[i]);}
        candidateOrigins=origins;candidatePixels=now;
        if(now.size()>=40&&time-candidateTime>=.3)triangulateCandidates();
      }finally{before.release();after.release();back.release();ok.release();reverse.release();error.release();}
      if(candidatePixels.size()<40||time-candidateTime>1.5){candidatePixels=null;candidateOrigins=null;}
    }
    if(candidatePixels==null&&pixels.size()<350){
      Mat mask=new Mat(image.rows(),image.cols(),CvType.CV_8UC1,new Scalar(255));MatOfPoint corners=new MatOfPoint();
      try{
        Imgproc.rectangle(mask,new Point(0,0),new Point(image.cols()-1,image.rows()-1),new Scalar(0),16);
        for(Point pixel:pixels)Imgproc.circle(mask,pixel,10,new Scalar(0),-1);
        Imgproc.goodFeaturesToTrack(image,corners,600,.01,8,mask);
        if(corners.rows()>=40){candidatePixels=new ArrayList<>(corners.toList());candidateOrigins=new ArrayList<>(candidatePixels);candidateRotation=currentRotation;candidateTranslation=currentTranslation;candidateTime=time;keyframes++;}
      }finally{mask.release();corners.release();}
    }
  }
  private void triangulateCandidates()throws Exception{
    MatOfPoint2f a=new MatOfPoint2f(),b=new MatOfPoint2f(),na=new MatOfPoint2f(),nb=new MatOfPoint2f();
    Mat P0=Mat.zeros(3,4,CvType.CV_64F),P1=Mat.zeros(3,4,CvType.CV_64F),X=new Mat(),at=new Mat(),bt=new Mat();
    try{
      a.fromList(candidateOrigins);b.fromList(candidatePixels);Calib3d.undistortPoints(a,na,K,D);Calib3d.undistortPoints(b,nb,K,D);
      for(int i=0;i<3;i++){for(int j=0;j<3;j++){P0.put(i,j,candidateRotation[i][j]);P1.put(i,j,currentRotation[i][j]);}P0.put(i,3,candidateTranslation[i]);P1.put(i,3,currentTranslation[i]);}
      Mat flatA=na.reshape(1),flatB=nb.reshape(1),ta=flatA.t(),tb=flatB.t();ta.copyTo(at);tb.copyTo(bt);flatA.release();flatB.release();ta.release();tb.release();
      Calib3d.triangulatePoints(P0,P1,at,bt,X);Point[] aa=na.toArray(),bb=nb.toArray();
      List<Point3> world=new ArrayList<>();List<Integer> indices=new ArrayList<>();
      for(int i=0;i<aa.length;i++){
        double w=X.get(3,i)[0];if(Math.abs(w)<1e-10)continue;double[] point={X.get(0,i)[0]/w,X.get(1,i)[0]/w,X.get(2,i)[0]/w};
        double[] ca=multiply(candidateRotation,point),cb=multiply(currentRotation,point);
        double[] rayA=multiply(transpose(candidateRotation),unit(new double[]{aa[i].x,aa[i].y,1})),rayB=multiply(transpose(currentRotation),unit(new double[]{bb[i].x,bb[i].y,1}));
        double angle=Math.acos(Math.max(-1,Math.min(1,dot(rayA,rayB))));
        if(finite(point)&&ca[2]+candidateTranslation[2]>.05&&cb[2]+currentTranslation[2]>.05&&angle>Math.PI/180){world.add(new Point3(point[0],point[1],point[2]));indices.add(i);}
      }
      if(world.isEmpty())return;
      MatOfPoint3f wp=new MatOfPoint3f();wp.fromList(world);MatOfPoint2f pa=new MatOfPoint2f(),pb=new MatOfPoint2f();MatOfDouble distortion=new MatOfDouble(D);
      Mat ra=new Mat(3,3,CvType.CV_64F),rb=new Mat(3,3,CvType.CV_64F),rva=new Mat(),rvb=new Mat(),tva=new Mat(3,1,CvType.CV_64F),tvb=new Mat(3,1,CvType.CV_64F);
      try{
        ra.put(0,0,flatten(candidateRotation));rb.put(0,0,flatten(currentRotation));Calib3d.Rodrigues(ra,rva);Calib3d.Rodrigues(rb,rvb);tva.put(0,0,candidateTranslation);tvb.put(0,0,currentTranslation);
        Calib3d.projectPoints(wp,rva,tva,K,distortion,pa);Calib3d.projectPoints(wp,rvb,tvb,K,distortion,pb);Point[] old=pa.toArray(),now=pb.toArray();Set<Integer> accepted=new HashSet<>();
        for(int j=0;j<world.size();j++){int i=indices.get(j);Point pixel=candidatePixels.get(i);
          boolean near=false;for(Point known:pixels)if(distance(known,pixel)<8){near=true;break;}
          if(!near&&distance(old[j],candidateOrigins.get(i))<2&&distance(now[j],pixel)<2){landmarks.add(world.get(j));pixels.add(pixel);accepted.add(i);mapPointsAdded++;}
        }
        List<Point> remainOrigins=new ArrayList<>(),remainPixels=new ArrayList<>();
        for(int i=0;i<candidatePixels.size();i++)if(!accepted.contains(i)){remainOrigins.add(candidateOrigins.get(i));remainPixels.add(candidatePixels.get(i));}
        candidateOrigins=remainOrigins;candidatePixels=remainPixels;
      }finally{wp.release();pa.release();pb.release();distortion.release();ra.release();rb.release();rva.release();rvb.release();tva.release();tvb.release();}
    }finally{a.release();b.release();na.release();nb.release();P0.release();P1.release();X.release();at.release();bt.release();}
  }
  private void addPose(double t,double[][] Rcw,double[] tv){currentRotation=Rcw;currentTranslation=tv;double[][] Rwc=transpose(Rcw);double[] p=multiply(Rwc,tv);for(int i=0;i<3;i++)p[i]=-p[i];poses.add(new Pose(t,p,multiply(Rwc,Rci)));}
  public JSONObject snapshot() throws JSONException {return new JSONObject().put("state",state).put("reason",failure).put("framesProcessed",processed).put("features",features).put("poseFrames",poses.size()).put("reprojectionRmsPixels",lastRms).put("distanceReady",false).put("mapPointsAdded",mapPointsAdded).put("keyframes",keyframes);}
  public JSONObject finish() throws JSONException {
    JSONObject result=snapshot().put("schemaVersion",1).put("kind","front-camera-distance-research-v1").put("method","native-growing-map-scale-v2")
      .put("independentDistanceValidation",false).put("fullCalibrationReady",false)
      .put("limitations",new JSONArray(Arrays.asList("Research only; not a clinical boundary","Conservative map renewal; no loop closure or relocalization","Rolling shutter not corrected in visual tracking","Camera path may include body sway","Full acceleration calibration not established")));
    try{
      if(profile==null)result.put("status","unavailable").put("reason","needs-profile");
      else if(!failure.isEmpty())result.put("status","rejected");
      else estimateScale(result);
    }catch(Exception e){result.put("status","rejected").put("reason",e.getMessage()==null?"scale-error":e.getMessage());}
    JSONArray trajectory=new JSONArray();for(Pose p:poses)trajectory.put(new JSONObject().put("timeSeconds",p.t).put("positionMap",new JSONArray(p.p)).put("rotationWorldImu",new JSONArray(p.q)));
    result.put("trajectoryMapUnits",trajectory).put("frameDiagnostics",new JSONArray(events));
    if(previous!=null)previous.release();if(K!=null)K.release();if(D!=null)D.release();return result;
  }
  private void estimateScale(JSONObject report)throws Exception{
    if(poses.size()<80||poses.get(poses.size()-1).t-poses.get(0).t<6)throw new Exception("insufficient-continuous-motion");
    // Local least-squares quadratic derivatives, rather than raw three-frame differences.
    List<double[]> rows=new ArrayList<>();List<Double> targets=new ArrayList<>();List<Integer> rowPose=new ArrayList<>();
    for(int i=4;i<poses.size()-4;i++){
      Pose center=poses.get(i);double[][] design=new double[9][3];double[][] positions=new double[9][3];double[][] rotations=new double[9][9];
      for(int j=0;j<9;j++){Pose p=poses.get(i+j-4);double dt=p.t-center.t;design[j]=new double[]{1,dt,dt*dt};positions[j]=p.p;rotations[j]=flatten(p.q);}
      DecompositionSolver solver=new QRDecomposition(new Array2DRowRealMatrix(design)).getSolver();
      double[] pdd=solver.solve(new Array2DRowRealMatrix(positions)).getRow(2);double[][] rdd=reshape(solver.solve(new Array2DRowRealMatrix(rotations)).getRow(2));
      for(int k=0;k<3;k++){pdd[k]*=2;for(int j=0;j<3;j++)rdd[k][j]*=2;}
      double[] force=interpolate(acceleration,center.t);double[] world=multiply(center.q,force);
      if(i>4){Pose before=poses.get(i-1);double[] rates=interpolate(gyroscope,(center.t+before.t)/2);
        JSONArray b=profile.getJSONObject("rotationTiming").getJSONArray("gyroBiasRadS");for(int k=0;k<3;k++)rates[k]-=b.getDouble(k);
        double[][] relative=multiply(transpose(before.q),center.q);Mat rm=new Mat(3,3,CvType.CV_64F),rv=new Mat();
        try{rm.put(0,0,flatten(relative));Calib3d.Rodrigues(rm,rv);double[] rotation=vector(rv);double error=0;for(int k=0;k<3;k++)error+=Math.pow(rotation[k]-rates[k]*(center.t-before.t),2);if(Math.sqrt(error)>Math.toRadians(5))throw new Exception("gyro-visual-disagreement");}finally{rm.release();rv.release();}
      }
      for(int k=0;k<3;k++){double[] row=new double[10];row[0]=pdd[k];for(int j=0;j<3;j++){row[1+j]=center.q[k][j];row[4+j]=k==j?-1:0;row[7+j]=-rdd[k][j];}rows.add(row);targets.add(world[k]);rowPose.add(i);}
    }
    int train=(rows.size()/3*4/5)*3;double[][] raw=rows.subList(0,train).toArray(new double[0][]);double[] y=new double[train];for(int i=0;i<train;i++)y[i]=targets.get(i);
    double[] norms=new double[10];for(double[] row:raw)for(int j=0;j<10;j++)norms[j]+=row[j]*row[j];for(int j=0;j<10;j++)norms[j]=Math.sqrt(norms[j]);
    double[][] scaled=new double[train][10];for(int i=0;i<train;i++)for(int j=0;j<10;j++)scaled[i][j]=raw[i][j]/Math.max(norms[j],1e-12);
    SingularValueDecomposition svd=new SingularValueDecomposition(new Array2DRowRealMatrix(scaled));double[] singular=svd.getSingularValues();int rank=0;for(double v:singular)if(v>1e-6)rank++;
    double condition=singular[0]/Math.max(singular[singular.length-1],1e-12);report.put("fitRank",rank).put("scaledCondition",condition);
    if(rank<10||condition>1e4)throw new Exception("scale-unobservable");
    double[] coefficients=svd.getSolver().solve(new ArrayRealVector(y)).toArray();for(int j=0;j<10;j++)coefficients[j]/=norms[j];
    double sum=0;for(int i=train;i<rows.size();i++)sum+=Math.pow(dot(rows.get(i),coefficients)-targets.get(i),2);double rms=Math.sqrt(sum/(rows.size()-train));
    double residual=0;for(int i=0;i<train;i++)residual+=Math.pow(dot(raw[i],coefficients)-y[i],2);
    RealMatrix A=new Array2DRowRealMatrix(raw),inverse=new SingularValueDecomposition(A).getSolver().getInverse();
    double scaleStd=Math.sqrt(inverse.multiply(inverse.transpose()).getEntry(0,0)*residual/Math.max(train-10,1));
    double scale=coefficients[0];double[] bias=Arrays.copyOfRange(coefficients,1,4),gravity=Arrays.copyOfRange(coefficients,4,7),lever=Arrays.copyOfRange(coefficients,7,10);
    report.put("heldOutCoordinateRmsMps2",rms).put("metresPerMapUnit",scale).put("scaleLinearizedStd",scaleStd).put("accelerometerBiasMps2",new JSONArray(bias)).put("gravityWorldMps2",new JSONArray(gravity)).put("leverArmMetres",new JSONArray(lever));
    if(!(scale>0&&scaleStd/scale<.15&&rms<.6&&Math.abs(norm(gravity)-9.80665)<.5&&norm(bias)<1.5&&norm(lever)<.2))throw new Exception("scale-physical-check-failed");
    double length=0;double[] vertical=unit(gravity);
    // Smoothed camera positions, not raw jitter accumulated as distance.
    double[] previousPosition=null;
    for(int i=4;i<poses.size()-4;i++){double[] p=new double[3];for(int j=i-4;j<=i+4;j++)for(int k=0;k<3;k++)p[k]+=poses.get(j).p[k]/9;
      if(previousPosition!=null){double[] d=new double[3];for(int k=0;k<3;k++)d[k]=(p[k]-previousPosition[k])*scale;double along=dot(d,vertical);for(int k=0;k<3;k++)d[k]-=along*vertical[k];length+=norm(d);}previousPosition=p;}
    double duration=poses.get(poses.size()-5).t-poses.get(4).t;
    report.put("status","experimental-estimate").put("reason","").put("experimentalHorizontalCameraPathMetres",length).put("experimentalElapsedSeconds",duration).put("experimentalMeanCameraSpeedMps",length/duration);
  }
  private static double[] interpolate(List<Imu> list,double t)throws Exception{
    if(list.size()<2||t<list.get(0).t||t>list.get(list.size()-1).t)throw new Exception("imu-coverage-gap");
    int lo=0,hi=list.size()-1;while(hi-lo>1){int mid=(lo+hi)/2;if(list.get(mid).t<t)lo=mid;else hi=mid;}
    Imu a=list.get(lo),b=list.get(hi);if(b.t-a.t>.15)throw new Exception("imu-coverage-gap");double f=(t-a.t)/(b.t-a.t);double[] v=new double[3];for(int k=0;k<3;k++)v[k]=a.v[k]*(1-f)+b.v[k]*f;return v;
  }
  private static boolean rotationOnly(Point[] a,Point[] b){
    double[][] H=new double[3][3];for(int i=0;i<a.length;i++){double[] aa=unit(new double[]{a[i].x,a[i].y,1}),bb=unit(new double[]{b[i].x,b[i].y,1});for(int j=0;j<3;j++)for(int k=0;k<3;k++)H[j][k]+=bb[j]*aa[k];}
    SingularValueDecomposition s=new SingularValueDecomposition(new Array2DRowRealMatrix(H));RealMatrix U=s.getU(),Vt=s.getVT();RealMatrix correction=MatrixUtils.createRealIdentityMatrix(3);correction.setEntry(2,2,new LUDecomposition(U.multiply(Vt)).getDeterminant()<0?-1:1);double[][] R=U.multiply(correction).multiply(Vt).getData();double[] angles=new double[a.length];for(int i=0;i<a.length;i++){double[] aa=multiply(R,unit(new double[]{a[i].x,a[i].y,1})),bb=unit(new double[]{b[i].x,b[i].y,1});angles[i]=Math.acos(Math.max(-1,Math.min(1,dot(aa,bb))));}Arrays.sort(angles);return angles[angles.length/2]<Math.toRadians(.15);
  }
  private static double distance(Point a,Point b){return Math.hypot(a.x-b.x,a.y-b.y);}
  private static boolean finite(double[] a){for(double v:a)if(!Double.isFinite(v))return false;return true;}
  private static double dot(double[] a,double[] b){double x=0;for(int i=0;i<a.length;i++)x+=a[i]*b[i];return x;}
  private static double norm(double[] a){return Math.sqrt(dot(a,a));}
  private static double[] unit(double[] a){double n=norm(a);double[] b=a.clone();for(int i=0;i<b.length;i++)b[i]/=n;return b;}
  private static double[][] transpose(double[][] a){double[][] b=new double[3][3];for(int i=0;i<3;i++)for(int j=0;j<3;j++)b[i][j]=a[j][i];return b;}
  private static double[] multiply(double[][] a,double[] b){double[] c=new double[3];for(int i=0;i<3;i++)for(int j=0;j<3;j++)c[i]+=a[i][j]*b[j];return c;}
  private static double[][] multiply(double[][] a,double[][] b){double[][] c=new double[3][3];for(int i=0;i<3;i++)for(int j=0;j<3;j++)for(int k=0;k<3;k++)c[i][j]+=a[i][k]*b[k][j];return c;}
  private static double[] flatten(double[][] a){double[] b=new double[9];for(int i=0;i<3;i++)for(int j=0;j<3;j++)b[i*3+j]=a[i][j];return b;}
  private static double[][] reshape(double[] a){double[][] b=new double[3][3];for(int i=0;i<3;i++)for(int j=0;j<3;j++)b[i][j]=a[i*3+j];return b;}
  private static double[][] matrix(JSONArray a)throws JSONException{double[][] b=new double[3][3];for(int i=0;i<3;i++)for(int j=0;j<3;j++)b[i][j]=a.getJSONArray(i).getDouble(j);return b;}
  private static double[][] matrix(Mat a){double[][] b=new double[3][3];for(int i=0;i<3;i++)for(int j=0;j<3;j++)b[i][j]=a.get(i,j)[0];return b;}
  private static double[] vector(Mat a){double[] b=new double[3];for(int i=0;i<3;i++)b[i]=a.get(i,0)[0];return b;}
}
