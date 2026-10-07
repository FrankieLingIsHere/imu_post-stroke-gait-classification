package org.opencv.android;
/** Desktop test adapter only. The harness loads the matching real OpenCV DLL.
 * Android camera/permissions/loader are NOT tested by this adapter. */
public final class OpenCVLoader { public static boolean initLocal(){return true;} }
