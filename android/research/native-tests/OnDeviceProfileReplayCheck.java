package expo.modules.gaitcalibration;
import java.io.File;
/** Runs the actual admission code on an explicitly labelled host-control folder. */
public final class OnDeviceProfileReplayCheck {
 public static void main(String[] args)throws Exception {
  System.out.println(OnDeviceProfile.finish(new File(args[0]),args[1]).toString());
 }
}
