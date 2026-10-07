import expo.modules.gaitcalibration.ResearchDistanceTracker;
import org.json.*;
import org.opencv.core.*;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;

/** Executes application Java tracking/math with real desktop OpenCV JNI.
 * Known-answer synthetic inputs; never Android capture or physical distance validation. */
public final class NativeDistanceAlgorithmCheck {
  private static void require(boolean value,String message){if(!value)throw new AssertionError(message);}
  private static JSONObject profile() throws Exception {
    return new JSONObject("{\"lens\":{\"cameraMatrix\":[[500,0,320],[0,500,240],[0,0,1]],\"distortion\":[0,0,0,0,0]},\"rotationTiming\":{\"rotationImuToCamera\":[[1,0,0],[0,1,0],[0,0,1]],\"residualTimeOffsetSeconds\":0,\"gyroBiasRadS\":[0,0,0]}}");
  }
  private static Field field(Class<?> c,String name)throws Exception{Field f=c.getDeclaredField(name);f.setAccessible(true);return f;}
  private static Method method(String name,Class<?>...types)throws Exception{Method m=ResearchDistanceTracker.class.getDeclaredMethod(name,types);m.setAccessible(true);return m;}
  private static List<Point> project(double[][] world,double[] position,double yaw){
    List<Point> pixels=new ArrayList<>();double c=Math.cos(yaw),s=Math.sin(yaw);
    for(double[] v:world){double x=v[0]-position[0],y=v[1]-position[1],z=v[2]-position[2];double xx=c*x+s*z,zz=-s*x+c*z;pixels.add(new Point(500*xx/zz+320,500*y/zz+240));}return pixels;
  }
  private static double[] vector(JSONArray a)throws Exception{double[] v=new double[a.length()];for(int i=0;i<v.length;i++)v[i]=a.getDouble(i);return v;}
  private static double[][] matrix(JSONArray a)throws Exception{double[][] v=new double[a.length()][];for(int i=0;i<v.length;i++)v[i]=vector(a.getJSONArray(i));return v;}
  private static double[] lastPosition(ResearchDistanceTracker tracker)throws Exception{
    List<?> poses=(List<?>)field(ResearchDistanceTracker.class,"poses").get(tracker);Object p=poses.get(poses.size()-1);return (double[])field(p.getClass(),"p").get(p);
  }
  private static ResearchDistanceTracker scaleInputs(JSONObject fixture,boolean noTranslation)throws Exception{
    ResearchDistanceTracker tracker=new ResearchDistanceTracker(profile());JSONArray imu=fixture.getJSONArray("imu");
    for(int i=0;i<imu.length();i++){JSONObject row=imu.getJSONObject(i);double[] a=vector(row.getJSONArray("accel")),g=vector(row.getJSONArray("gyro"));long ns=(long)(row.getDouble("t")*1e9);tracker.sensor("accelerometer",ns,a[0],a[1],a[2]);tracker.sensor("gyroscope",ns,g[0],g[1],g[2]);}
    JSONArray poses=fixture.getJSONArray("poses");Method add=method("addPose",double.class,double[][].class,double[].class);
    for(int i=0;i<poses.length();i++){JSONObject row=poses.getJSONObject(i);double[][] Q=matrix(row.getJSONArray("Q"));double[] p=vector(row.getJSONArray("p")),tv=new double[3];double[][] R=new double[3][3];
      for(int j=0;j<3;j++)for(int k=0;k<3;k++){R[j][k]=Q[k][j];if(!noTranslation)tv[j]-=R[j][k]*p[k];}
      add.invoke(tracker,row.getDouble("t"),R,tv);
    }
    return tracker;
  }
  public static void main(String[] args)throws Exception{
    System.load(Paths.get(args[0]).toAbsolutePath().toString());require(Core.getVersionString().startsWith("4.12"),"JNI version mismatch");
    ResearchDistanceTracker noProfile=new ResearchDistanceTracker(null);require(noProfile.finish().getString("status").equals("unavailable"),"No profile must withhold distance");
    Random random=new Random(72);double[][] X=new double[180][3];for(double[] p:X){p[0]=random.nextDouble()*4-2;p[1]=random.nextDouble()*3-1.5;p[2]=random.nextDouble()*5+4;}
    List<Point> first=project(X,new double[]{0,0,0},0),second=project(X,new double[]{.6,0,0},0);
    ResearchDistanceTracker tracker=new ResearchDistanceTracker(profile());boolean initialized=(boolean)method("initialize",List.class,List.class,double.class).invoke(tracker,first,second,1.);
    require(initialized,"Known translation must initialize a consistent map");
    @SuppressWarnings("unchecked") List<Point> selected=(List<Point>)field(ResearchDistanceTracker.class,"pixels").get(tracker);
    List<Point> allLater=project(X,new double[]{1.2,.12,0},0),later=new ArrayList<>();for(Point pixel:selected){int best=0;double distance=Double.MAX_VALUE;for(int j=0;j<second.size();j++){double d=Math.hypot(pixel.x-second.get(j).x,pixel.y-second.get(j).y);if(d<distance){best=j;distance=d;}}later.add(allLater.get(best));}
    method("locate",List.class,double.class).invoke(tracker,later,2.);double[] position=lastPosition(tracker);
    require(Math.abs(position[0]-2)<.01&&Math.abs(position[1]-.2)<.01,"PnP changed map scale");
    double[][] freshWorld=new double[90][3];for(double[] v:freshWorld){v[0]=random.nextDouble()*4-2;v[1]=random.nextDouble()*3-1.5;v[2]=random.nextDouble()*5+4;}
    field(ResearchDistanceTracker.class,"candidateOrigins").set(tracker,project(freshWorld,new double[]{.6,0,0},0));
    field(ResearchDistanceTracker.class,"candidatePixels").set(tracker,project(freshWorld,new double[]{1.2,.12,0},0));
    field(ResearchDistanceTracker.class,"candidateRotation").set(tracker,new double[][]{{1,0,0},{0,1,0},{0,0,1}});
    field(ResearchDistanceTracker.class,"candidateTranslation").set(tracker,new double[]{-1,0,0});
    int oldCount=((List<?>)field(ResearchDistanceTracker.class,"landmarks").get(tracker)).size();method("triangulateCandidates").invoke(tracker);
    @SuppressWarnings("unchecked") List<Point3> growing=(List<Point3>)field(ResearchDistanceTracker.class,"landmarks").get(tracker);
    require(growing.size()>oldCount+20,"Map renewal did not add known translated landmarks");
    for(int i=oldCount;i<growing.size();i++){Point3 v=growing.get(i);double closest=Double.MAX_VALUE;
      for(double[] truth:freshWorld)closest=Math.min(closest,Math.sqrt(Math.pow(v.x-truth[0]/.6,2)+Math.pow(v.y-truth[1]/.6,2)+Math.pow(v.z-truth[2]/.6,2)));
      require(closest<.001,"Renewed map changed scale or coordinate frame");
    }
    tracker.finish();
    ResearchDistanceTracker rotation=new ResearchDistanceTracker(profile());require(!(boolean)method("initialize",List.class,List.class,double.class).invoke(rotation,first,project(X,new double[]{0,0,0},.15),1.),"Pure rotation fabricated translation");rotation.finish();
    JSONObject fixture=new JSONObject(Files.readString(Paths.get(args[1]))),result=new JSONObject();ResearchDistanceTracker scale=scaleInputs(fixture,false);
    method("estimateScale",JSONObject.class).invoke(scale,result);require(result.getString("status").equals("experimental-estimate"),"Known metric motion rejected: "+result);
    require(Math.abs(result.getDouble("metresPerMapUnit")-fixture.getDouble("expectedScale"))<.15,"Wrong known metric scale");scale.finish();
    ResearchDistanceTracker still=scaleInputs(fixture,true);boolean rejected=false;try{method("estimateScale",JSONObject.class).invoke(still,new JSONObject());}catch(InvocationTargetException e){rejected="scale-unobservable".equals(e.getCause().getMessage());}require(rejected,"Unobservable scale must be rejected");still.finish();
    System.out.println(new JSONObject().put("knownAnswerChecks",6).put("jniVersion",Core.getVersionString()).put("nativeMetricScale",result.getDouble("metresPerMapUnit")).put("expectedScale",fixture.getDouble("expectedScale")).put("heldOutRms",result.getDouble("heldOutCoordinateRmsMps2")).put("physicalDeviceValidation",false).put("androidCaptureExecuted",false).toString(2));
  }
}
