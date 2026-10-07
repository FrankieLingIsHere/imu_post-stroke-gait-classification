# One-time phone calibration

This is researcher preparation for a particular phone, native camera pipeline
and optical setup. Patients do not repeat it before their walking tests.

1. On this computer, double-click `android/Start phone calibration.cmd`. Keep the
   page and processor open. The free WSL/Linux Docker reference environment is
   installed on Frankie's computer. Other computers need that environment first.
2. Use the same private Wi-Fi. On the new Android app, open **Research tools →
   Phone calibration → Connect calibration computer** and scan the code. The
   computer switches to the board and a live framing diagram. **No tablet is
   needed.** Keep that computer board still.
3. Tap **Calibrate camera lens**. Hold the phone in its usual bag, front camera
   toward the computer. Watch the outline/dots beside the board on the computer
   while slowly moving/tilting the phone. Follow the voice and pause between
   positions. Briefly losing the board does not reset saved views. No ruler,
   physical print or manual ZIP transfer is needed. A saved profile also offers
   **Repeat lens check**, preserving the prior profile if the new attempt fails.
4. Tap **Align camera and sensors**. Hold the phone in its bag, front camera
   facing a textured room. Follow the stillness and gentle loops/tilts prompts.
   After the movement cue finishes, the phone records 50 seconds and stops
   automatically. Keep the lens unobstructed and the room lighting stable.
   This is research-team handling of the device, not an exercise for a patient.
5. The app uploads the capture locally and retrieves the reference result. Keep
   the computer running while it processes. **Leave processing** does not delete
   the computer job; **Resume calibration processing** retrieves its result.
   Restarting the processor creates a new pairing code: reconnect first.

Published on 7 October 2026 from commit `2cce693`. GitHub's three publication
workflows passed. The first functional Android update is
`01a115df-b6e0-7bf6-9760-2c02061813e8` on channel `preview`, runtime
`e1383287be615da4c75a7a9ce08b9260cfd2cfb3`. Expo's client endpoint serves that
manifest for build 15. Later documentation-only updates may have a newer ID.
If build 15 is installed, open the app online, let the update download, then
fully close and reopen it. Older builds need the build-15 APK for the new native
APIs. Restart the computer launcher so it runs the current companion source.

The computer shows a mirrored framing diagram detected from actual phone JPEGs,
not another coded board/video image. That prevents a duplicate target appearing
in the same camera view. Up to one frame/second is sent to this computer over
private Wi-Fi, decoded in memory and discarded. Only outline/corner coordinates
and native accepted-view count reach the computer page; no camera preview is
saved or sent to a cloud service. Framing is optional display feedback and cannot
admit a calibration or change raw pixels. Failed/absent/stale frames show waiting
or paused feedback. The native phone solver still controls quality and lens save.

**Use a tablet instead** remains an explicit optional mode: the computer gives a
board-only tablet link, the phone stays supported and the tablet moves. Switch
modes before starting. The default always uses the computer board. The target
display must remain flat with unchanged proportions; digital perspective warping
does not replace physical relative viewpoints.

The transfer uses a session token over private-LAN HTTP. It is not encrypted.
The QR code grants access to this temporary calibration service. No cloud
camera upload or paid distance service is used. If Windows shows a firewall
prompt for this Python processor, allow the private home/research network.
Public/guest Wi-Fi and networks that isolate devices will not work.

The app deliberately distinguishes **lens saved**, **reference result saved**
and **validated metric tracking**. A reference result is retained for review,
not automatically admitted to the live distance tracker. Parameter conventions,
physical bounds, residuals, repeatability, complete IMU noise and independent
distance accuracy still need review. Ordinary waist walking does not supply all
the movement required for full calibration. Changing phone, camera dimensions,
capture pipeline or bag-window optics invalidates reuse. An app reinstall that
clears device storage also loses this binding.

## Methods and provenance

- Lens: Zhang's published planar calibration, through OpenCV 4.12
  `calibrateCamera`, with ChArUco detections. Uniform board-size scale is irrelevant
  for lens intrinsics; the pattern must remain planar and retain its aspect ratio.
  Automatic view selection, held-out reprojection, subset stability and radial
  mapping checks are provisional engineering admission gates, not clinical limits.
  Zhang allows either the camera or the target to move. ChArUco permits partial
  views; the app still needs at least 20 detected corners per accepted frame and
  its existing 24-view/coverage gates. Repositioning frames are skipped, not a
  reason to restart. Moving the board is valid for **lens-only** fitting. The
  separate camera/IMU alignment requires the phone to move in a stationary room.
- Camera/IMU: the iKalibr authors' IEEE T-RO 2025 reference executable, pinned
  Docker base image, rolling-shutter midpoint model and standard COLMAP SfM. No custom
  rotation/translation solver is substituted on failure. Original ZIPs, raw
  hardware timestamps, sensor units, factory metadata, upstream parameters and
  software identities stay available under ignored local storage.
- Magnetometer: all three raw sensors are retained. iKalibr itself uses camera,
  accelerometer and gyroscope; it does not calibrate magnetic heading.
- Equal provisional IMU weights are disclosed in the processor provenance. They
  are not a measured noise model. The separate stationary-noise research tool
  remains available under **Research capture tools**.

Sources: [Zhang, 2000](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/),
[OpenCV partial-view ChArUco calibration](https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html),
[iKalibr authors](https://github.com/Unsigned-Long/iKalibr).

## Local GPU processing

The companion automatically selects the installed CUDA COLMAP worker when Docker
has an NVIDIA runtime. Frankie's RTX 5060 and WSL Docker runtime are now configured.
The official CUDA COLMAP snapshot is pinned by digest; its version and executable
hash are recorded separately from the unchanged iKalibr executable. Feature
extraction and matching request CUDA. Reconstruction and the reference calibration
solver remain on CPU; the authors' installed Ceres library has no CUDA component.
If GPU processing fails, its logs are kept, the fallback is recorded and the CPU
path is tried. GPU acceleration changes processing time, not clinical readiness.

The actual GPU-assisted synthetic control completed with 199 registered images:
24 seconds for extraction, 19 for matching, 43 for reconstruction and about
15.6 minutes overall including fresh image preparation and CPU calibration.
Known geometry/timing checks passed (6.46 mm translation, 0.033-degree rotation,
0.161 ms clock error). This is not a controlled whole-job speed comparison with
the earlier CPU run, which reused preparation and used a different COLMAP version.
It is also not a physical phone accuracy result. All distance readiness remains
false; GPU processing does not itself validate metric walking distance.

For another NVIDIA computer, configure the free
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
before launching the companion. On WSL, keep the Windows NVIDIA driver; do not
install a Linux display driver. The launcher builds the small Python wrapper on
the official CUDA image automatically. The first GPU image download is about
3.37 GB; it stays outside Git and is reused. Non-NVIDIA computers retain CPU
processing. No paid GPU service is involved.
