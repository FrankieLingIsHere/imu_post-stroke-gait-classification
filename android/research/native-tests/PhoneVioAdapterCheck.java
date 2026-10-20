import expo.modules.gaitcalibration.PhoneVio;
import java.io.File;
/** Desktop JVM execution of the actual Android input adapter, with retained data. */
public final class PhoneVioAdapterCheck {
  public static void main(String[] args)throws Exception {
    System.out.println(PhoneVio.prepare(new File(args[0]),args[1]).toString());
  }
}
