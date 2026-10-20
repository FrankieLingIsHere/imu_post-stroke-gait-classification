package expo.modules.gaitcalibration;

/** Camera2 uses pixel-edge coordinates; OpenCV/OpenVINS use pixel centres at integers.
 * This transforms an unrotated, unmirrored, aspect-cropped stream only. It is a
 * factory prior, not evidence that the bag's optical geometry is calibrated.
 */
public final class CameraOpticalPrior {
  public static double[] stream(double fx,double fy,double cx,double cy,
      double left,double top,double right,double bottom,int width,int height) {
    double[] inputs={fx,fy,cx,cy,left,top,right,bottom};
    for(double v:inputs)if(!Double.isFinite(v))throw new IllegalArgumentException("Camera geometry is nonfinite");
    if(fx<=0||fy<=0||right<=left||bottom<=top||width<=0||height<=0)
      throw new IllegalArgumentException("Camera geometry is invalid");
    double cw=right-left,ch=bottom-top,ratio=(double)width/height;
    if(cw/ch>ratio)cw=ch*ratio;else ch=cw/ratio;
    double x=(left+right-cw)/2,y=(top+bottom-ch)/2;
    return new double[]{fx*width/cw,fy*height/ch,(cx-x)*width/cw-.5,(cy-y)*height/ch-.5,0,0,0,0};
  }
}
