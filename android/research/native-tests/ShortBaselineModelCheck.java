import expo.modules.gaitcalibration.ShortBaselineModel;
import java.util.*;
public final class ShortBaselineModelCheck {
  public static void main(String[] args){
    List<double[]> rows=new ArrayList<>();for(int i=0;i<10;i++)rows.add(new double[]{.012+(i%2==0?.0001:-.0001),-.006,.003});
    double[] p=ShortBaselineModel.fit(rows);if(Math.abs(p[0]-.012)>.0001||p[3]<=0||p[3]>.001)throw new AssertionError("Bias posterior");
    if(!ShortBaselineModel.accept(p)||ShortBaselineModel.accept(new double[]{0,0,0,.008,.004,.003}))throw new AssertionError("Uncertainty gating");
    rows.set(0,new double[]{.2,0,0});try{ShortBaselineModel.fit(rows);throw new AssertionError("Movement accepted");}catch(IllegalArgumentException expected){}
    rows.set(0,new double[]{Double.NaN,0,0});try{ShortBaselineModel.fit(rows);throw new AssertionError("NaN accepted");}catch(IllegalArgumentException expected){}
    try{ShortBaselineModel.fit(rows.subList(0,3));throw new AssertionError("Sparse capture accepted");}catch(IllegalArgumentException expected){}
    System.out.println("Short baseline: known bias recovered; moving/nonfinite/sparse data rejected. Synthetic controls only.");
  }
}
