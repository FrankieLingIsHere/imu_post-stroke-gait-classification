package expo.modules.gaitcalibration;

/** External protocol boundaries on the native IMU/camera boot clock. Never a live distance stop. */
public final class GaitDistanceFlow {
  public long startNs, endNs;
  public String endReason = "interrupted";
  public boolean finishing;
  public void begin(long now) {
    if (now <= 0 || startNs != 0 || finishing) throw new IllegalStateException("Invalid distance start");
    startNs = now;
  }
  public void end(long now, String reason) {
    if (finishing) return;
    if (startNs == 0 || now <= startNs) throw new IllegalStateException("Distance has not started");
    if (!reason.equals("completed") && !reason.equals("interrupted") && !reason.equals("user-stopped"))
      throw new IllegalArgumentException("Invalid distance end");
    endNs = now; endReason = reason; finishing = true;
  }
  public boolean completed() { return finishing && endReason.equals("completed"); }
}
