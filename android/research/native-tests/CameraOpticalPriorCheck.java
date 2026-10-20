package expo.modules.gaitcalibration;
public final class CameraOpticalPriorCheck {
  static void near(double a,double b){if(Math.abs(a-b)>1e-9)throw new AssertionError(a+" != "+b);}
  public static void main(String[] args){
    double[] k=CameraOpticalPrior.stream(2000,2000,2000,1500,0,0,4000,3000,640,480);
    near(k[0],320);near(k[1],320);near(k[2],319.5);near(k[3],239.5);
    // Off-centre crop, odd boundaries and aspect crop: never truncate half pixels.
    k=CameraOpticalPrior.stream(1600,1700,1500,1200,101,201,2102,1802,640,480);
    near(k[0],1600*640./2001);near(k[1],1700*480./1500.75);
    near(k[2],(1500-101)*640./2001-.5);near(k[3],(1200-251.125)*480./1500.75-.5);
    // Projection of any source point must equal scale/crop followed by the centre shift.
    for(double x:new double[]{-.5,0,.2})for(double y:new double[]{-.3,0,.4}){
      near(k[0]*x+k[2],(1600*x+1500-101)*640./2001-.5);
      near(k[1]*y+k[3],(1700*y+1200-251.125)*480./1500.75-.5);
    }
    try{CameraOpticalPrior.stream(400,400,320,240,0,0,0,480,640,480);throw new AssertionError("Invalid crop accepted");}
    catch(IllegalArgumentException expected){}
    System.out.println("PASS: Camera2/OpenCV pixel centres, odd/off-centre/aspect crop and projection agreement");
  }
}
