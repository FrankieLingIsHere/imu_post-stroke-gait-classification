package expo.modules.gaitcalibration;

import java.util.List;

/** Small Bayesian adaptation from quiet gyro blocks, not a learned camera calibration.
 * Ten short observations update a zero-mean bias prior. Raw IMU remains unchanged.
 * The model is device/session-specific; it cannot infer lens geometry or metric scale.
 */
public final class ShortBaselineModel {
  public static final String VERSION="bayesian-quiet-gyro-bias-v1";
  public static boolean accept(double[] posterior){
    if(posterior.length!=6)return false;
    for(double v:posterior)if(!Double.isFinite(v))return false;
    for(int k=3;k<6;k++)if(posterior[k]<=0||posterior[k]>.002)return false;
    return Math.sqrt(posterior[0]*posterior[0]+posterior[1]*posterior[1]+posterior[2]*posterior[2])<.02;
  }
  public static double[] fit(List<double[]> blocks) {
    if(blocks.size()<5||blocks.size()>20)throw new IllegalArgumentException("Need 5 to 20 quiet blocks");
    double[] mean=new double[3],variance=new double[3],posterior=new double[6];
    for(double[] row:blocks){if(row.length!=3)throw new IllegalArgumentException("Three gyro axes required");double magnitude=0;for(int k=0;k<3;k++){if(!Double.isFinite(row[k]))throw new IllegalArgumentException("Nonfinite gyro");magnitude+=row[k]*row[k];mean[k]+=row[k]/blocks.size();}if(Math.sqrt(magnitude)>=.08)throw new IllegalArgumentException("Motion is not a stationary bias label");}
    for(double[] row:blocks)for(int k=0;k<3;k++)variance[k]+=Math.pow(row[k]-mean[k],2)/(blocks.size()-1);
    for(int k=0;k<3;k++){
      // Conservative block-level floor; no false precision from ~400 correlated samples.
      double observationVariance=Math.max(variance[k],.002*.002),priorVariance=.02*.02;
      double postVariance=1/(1/priorVariance+blocks.size()/observationVariance);
      posterior[k]=postVariance*blocks.size()*mean[k]/observationVariance;
      posterior[k+3]=Math.sqrt(postVariance);
    }
    return posterior;
  }
}
