package expo.modules.gaitcalibration

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.YuvImage
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.hardware.camera2.*
import android.media.Image
import android.media.ImageReader
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.SystemClock
import android.util.Range
import android.util.Size
import expo.modules.kotlin.Promise
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.BufferedWriter
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream
import java.util.UUID
import org.opencv.android.OpenCVLoader

/** Research calibration acquisition only. Images, capture results and native IMU retain their clocks. */
class GaitCameraCalibrationModule : Module() {
  @Volatile private var run: Capture? = null
  private val phoneProcessing=java.util.concurrent.atomic.AtomicBoolean(false)
  override fun definition() = ModuleDefinition {
    Name("GaitCameraCalibration")
    Events("progress","distanceProgress")
    AsyncFunction("capture") { promise: Promise -> startBoardCapture("unconfirmed",promise) }
    AsyncFunction("captureWithOptics") { opticalSetup: String, promise: Promise ->
      if(opticalSetup !in listOf("waist-bag-window","clear-lens"))promise.reject("E_OPTICS","Invalid optical setup",null)
      else startBoardCapture(opticalSetup,promise)
    }
    AsyncFunction("captureGuidedLens") { opticalSetup: String, promise: Promise ->
      if(opticalSetup !in listOf("waist-bag-window","clear-lens"))promise.reject("E_OPTICS","Invalid optical setup",null)
      else startBoardCapture(opticalSetup,promise,true)
    }
    AsyncFunction("captureAlignment") { opticalSetup:String,promise:Promise ->
      val ctx=requireNotNull(appContext.reactContext)
      if(opticalSetup !in listOf("waist-bag-window","clear-lens"))promise.reject("E_OPTICS","Invalid optical setup",null)
      else if(run!=null)promise.reject("E_BUSY","A research capture is already running",null)
      else if(ctx.checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)promise.reject("E_PERMISSION","Camera permission is required",null)
      else{val capture=Capture(ctx,promise,opticalSetup=opticalSetup,alignment=true);run=capture;capture.start()}
    }
    AsyncFunction("beginAlignmentMovement") { run?.beginAlignmentMovement() }
    AsyncFunction("captureRapidCalibration") { opticalSetup:String,promise:Promise ->
      val ctx=requireNotNull(appContext.reactContext)
      if(opticalSetup !in listOf("waist-bag-window","clear-lens"))promise.reject("E_OPTICS","Invalid optical setup",null)
      else if(run!=null||phoneProcessing.get())promise.reject("E_BUSY","A capture or calculation is already running",null)
      else if(ctx.checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)promise.reject("E_PERMISSION","Camera permission is required",null)
      else{val capture=Capture(ctx,promise,opticalSetup=opticalSetup,rapidEnrollment=true);run=capture;capture.start()}
    }
    AsyncFunction("captureOnDeviceSetup") { promise:Promise ->
      val ctx=requireNotNull(appContext.reactContext)
      if(run!=null||phoneProcessing.get())promise.reject("E_BUSY","A capture or calculation is already running",null)
      else if(ctx.checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)promise.reject("E_PERMISSION","Camera permission is required",null)
      else{val capture=Capture(ctx,promise,opticalSetup="waist-bag-window",rapidEnrollment=true,onDeviceSetup=true);run=capture;capture.start()}
    }
    AsyncFunction("completeOnDeviceSetup") { captureId:String ->
      val ctx=requireNotNull(appContext.reactContext)
      require(run==null&&!phoneProcessing.get()){"Finish recording first"}
      OnDeviceProfile.finish(ctx.filesDir,captureId).toString()
    }
    AsyncFunction("onDeviceProfile") {
      val ctx=requireNotNull(appContext.reactContext)
      val file=File(ctx.filesDir,"camera-calibration/on-device-profile.json")
      if(file.isFile)file.readText() else null
    }
    AsyncFunction("referenceTrackingProfile") {
      val ctx=requireNotNull(appContext.reactContext)
      val file=File(ctx.filesDir,"camera-calibration/reference.json")
      if(!file.isFile)null else {
        val manager=ctx.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        val id=manager.cameraIdList.firstOrNull { manager.getCameraCharacteristics(it).get(CameraCharacteristics.LENS_FACING)==CameraCharacteristics.LENS_FACING_FRONT }
          ?: error("No front camera available")
        val c=manager.getCameraCharacteristics(id)
        val sizes=c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)!!.getOutputSizes(ImageFormat.YUV_420_888)
        val size=sizes.filter{it.width<=1280&&it.height<=960}.minByOrNull{kotlin.math.abs(it.width*it.height-640*480)}?:sizes.minBy{it.width*it.height}
        val binding=JSONObject().put("installationId",ctx.getSharedPreferences("gait-calibration",Context.MODE_PRIVATE).getString("installationId",null))
          .put("cameraId",id).put("width",size.width).put("height",size.height).put("imageAxes","native-sensor-unrotated-unmirrored")
          .put("sensorOrientationDegrees",c.get(CameraCharacteristics.SENSOR_ORIENTATION)).put("stabilizationRequested","off")
          .put("capturePipeline","native-camera-imu-v3").put("opticalSetup","waist-bag-window")
        ReferenceTrackingProfile.create(JSONObject(file.readText()),binding).toString()
      }
    }
    AsyncFunction("exportRapidEnrollment") { captureId:String, reportText:String ->
      val ctx=requireNotNull(appContext.reactContext)
      require(captureId.matches(Regex("calibration-[0-9]+"))){"Invalid capture identifier"}
      val report=JSONObject(reportText)
      val binding=report.getJSONObject("binding")
      require(binding.getString("captureId")==captureId&&binding.getString("installationId")==ctx.getSharedPreferences("gait-calibration",Context.MODE_PRIVATE).getString("installationId",null)){"Enrollment does not match this capture"}
      val source=File(ctx.filesDir,"camera-calibration/$captureId.zip")
      require(source.isFile&&source.length()>0){"Enrollment capture was cleared"}
      val manifest=JSONObject(File(ctx.filesDir,"camera-calibration/$captureId/manifest.json").readText())
      require(manifest.getString("kind")=="phone-rapid-camera-imu-capture-v1"){"Not an enrollment capture"}
      val destination=File(ctx.filesDir,"camera-calibration/$captureId-enrollment.zip")
      val temp=File(destination.path+".tmp")
      try{ZipOutputStream(temp.outputStream()).use { zip ->
        zip.putNextEntry(ZipEntry("input.zip"));source.inputStream().use{it.copyTo(zip)};zip.closeEntry()
        zip.putNextEntry(ZipEntry("result.json"));zip.write(reportText.toByteArray(Charsets.UTF_8));zip.closeEntry()
        zip.putNextEntry(ZipEntry("training-example.json"));zip.write(report.getJSONObject("trainingExample").toString().toByteArray(Charsets.UTF_8));zip.closeEntry()
      };require(temp.renameTo(destination)){"Could not save enrollment bundle"}}finally{temp.delete()}
      destination.toURI().toString()
    }
    AsyncFunction("phoneCalibrationInfo") {
      val ctx=requireNotNull(appContext.reactContext)
      val manager=ctx.getSystemService(Context.CAMERA_SERVICE) as CameraManager
      val id=manager.cameraIdList.firstOrNull { manager.getCameraCharacteristics(it).get(CameraCharacteristics.LENS_FACING)==CameraCharacteristics.LENS_FACING_FRONT }
        ?: error("No front camera available")
      val c=manager.getCameraCharacteristics(id)
      val preferences=ctx.getSharedPreferences("gait-calibration",Context.MODE_PRIVATE)
      val installation=preferences.getString("installationId",null)?:UUID.randomUUID().toString().also { preferences.edit().putString("installationId",it).commit() }
      val sizes=c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)!!.getOutputSizes(ImageFormat.YUV_420_888)
      val size=sizes.filter{it.width<=1280&&it.height<=960}.minByOrNull{kotlin.math.abs(it.width*it.height-640*480)}?:sizes.minBy{it.width*it.height}
      factoryMetadata(c).put("installationId",installation).put("cameraId",id).put("width",size.width).put("height",size.height)
        .put("imageAxes","native-sensor-unrotated-unmirrored").put("sensorOrientationDegrees",c.get(CameraCharacteristics.SENSOR_ORIENTATION))
        .put("stabilizationRequested","off").put("focusRequestedDioptres",0).put("capturePipeline","native-camera-imu-v2").toString()
    }
    AsyncFunction("digitalCalibrationBoard") {
      val ctx=requireNotNull(appContext.reactContext)
      require(OpenCVLoader.initLocal()){"OpenCV could not start"}
      val image=org.opencv.core.Mat()
      GuidedLensCalibration.newBoard().generateImage(Size(900,700).let{org.opencv.core.Size(it.width.toDouble(),it.height.toDouble())},image)
      val encoded=org.opencv.core.MatOfByte()
      val html=File(ctx.cacheDir,"GaitTrace-digital-board.html")
      try{
        require(org.opencv.imgcodecs.Imgcodecs.imencode(".png",image,encoded)){"Could not generate digital board"}
        val data=android.util.Base64.encodeToString(encoded.toArray(),android.util.Base64.NO_WRAP)
        html.writeText("""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>GaitTrace lens board</title><style>html,body{margin:0;height:100%;background:white}body{display:flex;align-items:center;justify-content:center}img{width:90vw;height:90vh;object-fit:contain;image-rendering:pixelated}</style></head><body><img src="data:image/png;base64,$data" alt="GaitTrace 9 by 7 ChArUco lens calibration board"></body></html>""")
      }finally{image.release();encoded.release()}
      html.toURI().toString()
    }
    AsyncFunction("captureDistance") { profile: String?, release: String, promise: Promise ->
      val ctx = requireNotNull(appContext.reactContext)
      if (profile.isNullOrBlank()) promise.reject("E_PROFILE", "Import the phone research profile before starting.", null)
      else if (run != null) promise.reject("E_BUSY", "A camera capture is already running", null)
      else if (ctx.checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) promise.reject("E_PERMISSION", "Camera permission is required", null)
      else { val capture = Capture(ctx,promise,true,profile,release);run=capture;capture.start() }
    }
    AsyncFunction("captureReferenceDistance") { reference: String, release: String, promise: Promise ->
      val ctx = requireNotNull(appContext.reactContext)
      if (run != null) promise.reject("E_BUSY", "A camera capture is already running", null)
      else if (ctx.checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) promise.reject("E_PERMISSION", "Camera permission is required", null)
      else { val capture = Capture(ctx,promise,true,reference,release,referenceTrial=true);run=capture;capture.start() }
    }
    AsyncFunction("captureNoise") { promise: Promise ->
      val ctx = requireNotNull(appContext.reactContext)
      if (run != null) promise.reject("E_BUSY", "A research capture is already running", null)
      else { val capture = Capture(ctx,promise,noiseSeconds=300);run=capture;capture.start() }
    }
    AsyncFunction("captureGaitDistance") { reference: String, release: String, sessionId: String, protocol: String, promise: Promise ->
      val ctx = requireNotNull(appContext.reactContext)
      require(sessionId.matches(Regex("[a-zA-Z0-9_-]{1,160}"))) { "Invalid recording identifier" }
      require(protocol in listOf("research-walk","10mwt","tug","2mwt","6mwt")) { "Invalid gait protocol" }
      if (run != null) promise.reject("E_BUSY","A camera capture is already running",null)
      else if (ctx.checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) promise.reject("E_PERMISSION","Camera permission is required",null)
      else { val capture=Capture(ctx,promise,true,reference,release,referenceTrial=true,gaitSessionId=sessionId,gaitProtocol=protocol);run=capture;capture.start() }
    }
    AsyncFunction("gaitDistanceReady") { run?.gaitReady() == true }
    AsyncFunction("processGaitDistanceOnPhone") { sessionId: String, promise: Promise ->
      val ctx=requireNotNull(appContext.reactContext)
      if(run!=null||!phoneProcessing.compareAndSet(false,true))promise.reject("E_BUSY","Finish the current capture or distance calculation first",null)
      else Thread({try{android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND);promise.resolve(PhoneVio.process(ctx.filesDir,sessionId))}catch(error:Throwable){promise.reject("E_PHONE_VIO",error.message?:"Phone distance processing failed",error)}finally{phoneProcessing.set(false)}},"GaitPhoneVio").start()
    }
    AsyncFunction("beginGaitDistance") { promise: Promise -> run?.beginGaitDistance(promise) ?: promise.reject("E_CAPTURE","Camera capture is unavailable",null) }
    AsyncFunction("finishGaitDistance") { reason: String -> run?.finishGaitDistance(reason) }
    AsyncFunction("beginDistance") { run?.beginDistance() }
    AsyncFunction("beginDistanceWarmup") { run?.beginDistanceWarmup() }
    AsyncFunction("stop") { run?.requestStop("user-stopped") }
    OnDestroy { run?.requestStop("interrupted") }
  }

  private fun factoryMetadata(c:CameraCharacteristics):JSONObject{

    val m=JSONObject().put("factoryValuesAreVerifiedProfile",false)
    c.get(CameraCharacteristics.LENS_INTRINSIC_CALIBRATION)?.let{m.put("factoryIntrinsics",JSONArray(it.toList()))}
    if(Build.VERSION.SDK_INT>=28)c.get(CameraCharacteristics.LENS_DISTORTION)?.let{m.put("factoryDistortion",JSONArray(it.toList()))}
    c.get(CameraCharacteristics.LENS_POSE_ROTATION)?.let{m.put("factoryPoseRotation",JSONArray(it.toList()))}
    c.get(CameraCharacteristics.LENS_POSE_TRANSLATION)?.let{m.put("factoryPoseTranslation",JSONArray(it.toList()))}
    if(Build.VERSION.SDK_INT>=28)c.get(CameraCharacteristics.LENS_POSE_REFERENCE)?.let{m.put("factoryPoseReference",it)}
    c.get(CameraCharacteristics.SENSOR_INFO_PRE_CORRECTION_ACTIVE_ARRAY_SIZE)?.let{m.put("preCorrectionActiveArray",JSONArray(listOf(it.left,it.top,it.right,it.bottom)))}
    c.get(CameraCharacteristics.LENS_INFO_AVAILABLE_FOCAL_LENGTHS)?.let{m.put("focalLengthsMm",JSONArray(it.toList()))}
    c.get(CameraCharacteristics.SENSOR_INFO_PHYSICAL_SIZE)?.let{m.put("sensorPhysicalSizeMm",JSONArray(listOf(it.width,it.height)))}
    c.get(CameraCharacteristics.SENSOR_INFO_ACTIVE_ARRAY_SIZE)?.let{m.put("activeArray",JSONArray(listOf(it.left,it.top,it.right,it.bottom)))}
    return m
  }
  private fun opticalPrior(c:CameraCharacteristics,crop:Rect):JSONObject{
    val active=requireNotNull(c.get(CameraCharacteristics.SENSOR_INFO_PRE_CORRECTION_ACTIVE_ARRAY_SIZE))
    val raw=c.get(CameraCharacteristics.LENS_INTRINSIC_CALIBRATION)
    // Complete factory intrinsics do not require optional focal/physical-size metadata.
    val fallback=if(raw==null){
      val physical=requireNotNull(c.get(CameraCharacteristics.SENSOR_INFO_PHYSICAL_SIZE)){"This phone does not report its camera optics"}
      val focal=c.get(CameraCharacteristics.LENS_INFO_AVAILABLE_FOCAL_LENGTHS)?.firstOrNull()?:error("Camera focal length is unavailable")
      doubleArrayOf(focal.toDouble()/physical.width*active.width(),focal.toDouble()/physical.height*active.height(),active.width()/2.0,active.height()/2.0)
    }else DoubleArray(4){raw[it].toDouble()}
    val stream=CameraOpticalPrior.stream(fallback[0],fallback[1],fallback[2],fallback[3],crop.left.toDouble(),crop.top.toDouble(),crop.right.toDouble(),crop.bottom.toDouble(),640,480)
    val angle=Math.toRadians(requireNotNull(c.get(CameraCharacteristics.SENSOR_ORIENTATION)).toDouble())/2
    return JSONObject().put("origin",if(raw!=null)"factory-intrinsics-prior" else "factory-focal-size-prior").put("verified",false)
      .put("pixelConvention","camera2-edge-to-opencv-centre-v1").put("cameraValues",JSONArray(stream.toList()))
      .put("imuToCamera",JSONArray(listOf(0,0,-kotlin.math.sin(angle),kotlin.math.cos(angle),0,0,0)))
  }
  private fun startBoardCapture(opticalSetup: String,promise: Promise,guidedLens:Boolean=false){
    val ctx=requireNotNull(appContext.reactContext)
    if(run!=null)promise.reject("E_BUSY","A research capture is already running",null)
    else if(ctx.checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)promise.reject("E_PERMISSION","Camera permission is required",null)
    else{val capture=Capture(ctx,promise,opticalSetup=opticalSetup,guidedLens=guidedLens);run=capture;capture.start()}
  }

  private inner class Capture(val ctx: Context, val promise: Promise, val distanceTrial: Boolean=false, val profileText: String?=null, val releaseText: String?=null, val noiseSeconds: Int=0, val opticalSetup: String="unconfirmed",val guidedLens:Boolean=false,val alignment:Boolean=false,val referenceTrial:Boolean=false,val gaitSessionId:String?=null,val gaitProtocol:String?=null,val rapidEnrollment:Boolean=false,val onDeviceSetup:Boolean=false) : SensorEventListener {
    private val thread = HandlerThread("GaitCalibration").apply { start() }
    private val handler = Handler(thread.looper)
    private val processingThread = HandlerThread("GaitCaptureStorage").apply { start() }
    private val processing = Handler(processingThread.looper)
    private val budget = CaptureQueueBudget(4,5000)
    @Volatile private var storageError: String? = null
    private val manager = ctx.getSystemService(Context.CAMERA_SERVICE) as CameraManager
    private val sensors = ctx.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val id = if(gaitSessionId!=null) "gait-camera-$gaitSessionId" else "${if(noiseSeconds>0) "imu-noise" else if(distanceTrial) "distance-trial" else "calibration"}-${System.currentTimeMillis()}"
    private val dir = File(ctx.filesDir, "${if(gaitSessionId!=null) "gait-camera-captures" else if(noiseSeconds>0) "camera-imu-noise" else if(distanceTrial) "camera-distance-trials" else "camera-calibration"}/$id")
    private val gaitFlow=GaitDistanceFlow()
    private var imageBytes=0L
    fun gaitReady()=gaitSessionId!=null&&!closed&&frameCount>=5&&started>0L&&(onDeviceProfile==null||onDeviceVio?.trackingReady(SystemClock.elapsedRealtimeNanos())==true)
    fun beginGaitDistance(command:Promise){processing.post{try{require(gaitReady()){ "Camera is not ready" };val now=SystemClock.elapsedRealtimeNanos();onDeviceVio?.begin(now,gaitProtocol=="10mwt");gaitFlow.begin(now);walkStarted=gaitFlow.startNs;trialPhase="walking";command.resolve(null)}catch(e:Exception){command.reject("E_CAPTURE",e.message,e)}}}
    fun finishGaitDistance(reason:String){processing.post{if(gaitSessionId!=null&&!closed){try{gaitFlow.end(SystemClock.elapsedRealtimeNanos(),reason);onDeviceVio?.endMotion();trialPhase="finishing";handler.postDelayed({finish(if(gaitFlow.completed())"completed" else reason,null)},if(gaitFlow.completed())4000 else 0)}catch(e:Exception){handler.post{finish("error",e.message)}}}}}
    @Volatile private var onDeviceVio:OnDeviceVio?=null
    private val startupImu=VioBootstrap.PendingImu()
    private var onDeviceCamera:JSONObject?=null
    private var onDeviceProfile:JSONObject?=null
    private var onDeviceStatus:JSONObject?=null
    private val liveTiming=linkedMapOf<Long,JSONObject>()
    private val liveImages=linkedMapOf<Long,File>()
    private var liveProgressAt=0L
    private var tracker: ResearchDistanceTracker? = null
    private var lensSolver:GuidedLensCalibration?=null
    private var alignmentLens:JSONObject?=null
    @Volatile private var alignmentStarted=0L
    @Volatile private var guidedClock:GuidedCaptureClock?=null
    @Volatile private var lensFinished=false
    @Volatile private var lastLensFailure="Not enough different clear views were collected."
    @Volatile private var lensFitting=false
    @Volatile private var lastLensProgress:String?=null
    private var trialPhase = "placing"
    private var walkStarted = 0L
    private val distanceFlow = DistanceTrialFlow()
    private var movementLast = 0L
    private var latestGyro = 1.0
    private var gyroTimestamp = 0L
    private var accelTimestamp = 0L
    private var magnetTimestamp = 0L
    private val accelerationWindow = ArrayDeque<Pair<Long,Double>>()
    private val setupBaseline = SetupBaselineGate()
    private val cameraMetadata = linkedMapOf<Long,JSONObject>()
    private val pendingImages = linkedMapOf<Long,ByteArray>()
    private var diagnosticRows: BufferedWriter? = null
    fun beginDistance() { handler.post { if(distanceTrial&&trialPhase=="cue") {
      if(referenceTrial){distanceFlow.beginMeasured(SystemClock.elapsedRealtimeNanos());trialPhase=distanceFlow.phase}
      else{trialPhase="waiting";accelerationWindow.clear()}
    } } }
    fun beginDistanceWarmup(){handler.post{if(referenceTrial&&!closed){distanceFlow.beginWarmup(SystemClock.elapsedRealtimeNanos());trialPhase=distanceFlow.phase}}}
    fun beginAlignmentMovement(){handler.post{
      val clock=guidedClock
      if(!closed&&clock!=null&&clock.canBegin(SystemClock.elapsedRealtimeNanos())&&(!onDeviceSetup||setupBaseline.accepted())){
        processing.post{guardedStorage{if(!closed){
          clock.begin(SystemClock.elapsedRealtimeNanos()){
            if(onDeviceSetup)requireNotNull(onDeviceVio){"Phone estimator did not start"}.beginMotion()
            else onDeviceVio?.beginMotion()
          }
          alignmentStarted=clock.movementStartedNs()
          handler.postDelayed({finishGuidedMovement()},clock.remainingMovementMs(SystemClock.elapsedRealtimeNanos()))
        }}}
      }
    }}
    private fun finishGuidedMovement(){
      if(closed)return
      val clock=requireNotNull(guidedClock)
      val remaining=clock.remainingMovementMs(SystemClock.elapsedRealtimeNanos())
      if(remaining>0)handler.postDelayed({finishGuidedMovement()},remaining)
      else if(onDeviceSetup)processing.post{if(!closed){if(onDeviceVio?.setupSettled(SystemClock.elapsedRealtimeNanos())==true)handler.post{finish("completed",null)} else handler.postDelayed({finishGuidedMovement()},500)}}
      else finish("completed",null)
    }
    private var device: CameraDevice? = null
    private var session: CameraCaptureSession? = null
    private var reader: ImageReader? = null
    private var imu: BufferedWriter? = null
    private var frames: BufferedWriter? = null
    private var results: BufferedWriter? = null
    private var characteristics: CameraCharacteristics? = null
    private var cameraId = ""
    private var size = Size(640, 480)
    @Volatile private var started = 0L
    private var lastProgress = 0L
    private var lastImageArrival = 0L
    private fun watchLensCamera(){
      if(!guidedLens||closed)return
      val now=SystemClock.elapsedRealtimeNanos()
      if(started>0L&&now-maxOf(started,lastImageArrival)>15000000000L){
        finish("camera-stalled","Camera preview stopped updating. Your previous lens profile is kept.");return
      }
      handler.postDelayed({watchLensCamera()},1000)
    }
    @Volatile private var frameCount = 0
    private val counts = mutableMapOf("accelerometer" to 0, "gyroscope" to 0, "magnetometer" to 0)
    @Volatile private var closed = false
    private val types = mapOf(Sensor.TYPE_ACCELEROMETER to "accelerometer", Sensor.TYPE_GYROSCOPE to "gyroscope", Sensor.TYPE_MAGNETIC_FIELD to "magnetometer")

    fun start() { handler.post {
      try {
        require(ctx.filesDir.usableSpace >= (if(distanceTrial) 750L else 250L) * 1024 * 1024) { if(distanceTrial) "Free at least 750 MB for the camera distance trial" else "Free at least 250 MB for calibration" }
        if(noiseSeconds>0){
          dir.mkdirs();imu=File(dir,"imu.ndjson").bufferedWriter()
          started=SystemClock.elapsedRealtimeNanos()
          subscribeSensors()
          fun progress(){
            if(closed)return
            val elapsed=(SystemClock.elapsedRealtimeNanos()-started)/1e9
            sendEvent("progress",mapOf("elapsedSeconds" to elapsed,"frames" to 0,"imageUri" to "","phase" to "noise"))
            handler.postDelayed({progress()},500)
          }
          progress()
          handler.postDelayed({finish("completed",null)},noiseSeconds*1000L)
          return@post
        }
        cameraId = manager.cameraIdList.firstOrNull { manager.getCameraCharacteristics(it).get(CameraCharacteristics.LENS_FACING) == CameraCharacteristics.LENS_FACING_FRONT }
          ?: error("No front camera available")
        characteristics = manager.getCameraCharacteristics(cameraId)
        val sizes = characteristics!!.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)!!.getOutputSizes(ImageFormat.YUV_420_888)
        size = sizes.filter { it.width <= 1280 && it.height <= 960 }.minByOrNull { kotlin.math.abs(it.width * it.height - 640 * 480) } ?: sizes.minBy { it.width * it.height }
        if(guidedLens){require(OpenCVLoader.initLocal()){ "OpenCV could not start" };lensSolver=GuidedLensCalibration(size.width,size.height)}
        if(rapidEnrollment){
          require(size.width==640&&size.height==480){"Quick enrollment needs a supported 640 by 480 camera stream"}
          require(characteristics!!.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME){"Native camera and IMU must share the real-time hardware clock"}
          require(listOf(Sensor.TYPE_ACCELEROMETER,Sensor.TYPE_GYROSCOPE,Sensor.TYPE_MAGNETIC_FIELD).all{sensors.getDefaultSensor(it)!=null}){"Quick enrollment needs accelerometer, gyroscope and magnetometer hardware"}
        }
        if(alignment){
          val profile=JSONObject(File(ctx.filesDir,"camera-calibration/lens.json").readText())
          val b=profile.getJSONObject("binding")
          require(profile.optBoolean("lensReady")&& !profile.optBoolean("distanceReady")&&profile.optString("method")=="opencv-zhang-2000"){"Lens parameters do not match this camera setup."}
          require(b.optString("installationId")==ctx.getSharedPreferences("gait-calibration",Context.MODE_PRIVATE).getString("installationId",null)
            &&b.optString("cameraId")==cameraId&&b.optInt("width")==size.width&&b.optInt("height")==size.height
            &&b.optString("opticalSetup")==opticalSetup&&b.optString("capturePipeline")=="native-camera-imu-v2"){"Lens parameters do not match this camera setup."}
          require(characteristics!!.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME){"Native camera and IMU must share the real-time hardware clock"}
          alignmentLens=profile
        }
        if(distanceTrial){
          require(characteristics!!.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME){"Native camera and IMU must share the real-time hardware clock"}
          val profile=profileText?.let { JSONObject(it) }
          if(profile!=null){
            val binding=profile.getJSONObject("binding")
            val installation=ctx.getSharedPreferences("gait-calibration",Context.MODE_PRIVATE).getString("installationId",null)
            if(profile.optString("kind")=="phone-on-device-camera-imu-profile-v1"){
              val current=JSONObject(binding.toString()).put("installationId",installation).put("cameraId",cameraId).put("width",size.width).put("height",size.height)
                .put("sensorOrientationDegrees",characteristics!!.get(CameraCharacteristics.SENSOR_ORIENTATION)).put("capturePipeline","native-camera-imu-v3")
              OnDeviceProfile.validate(profile,current);onDeviceProfile=profile
            }else{
            require(profile.getInt("schemaVersion")==1&& !profile.getBoolean("distanceReady") && !profile.getBoolean("fullCalibrationReady")){"Invalid research profile"}
            if(referenceTrial){
              require(profile.getString("kind")=="phone-reference-camera-imu-calibration-v1"&&profile.optString("method")=="ikalibr-tro-2025"&&profile.optString("status")=="reference-solved-review-required"&& !profile.getBoolean("independentDistanceValidation")){"Invalid reference calibration"}
              require(profile.getJSONObject("upstreamParameters").has("CalibParam")){"Missing reference parameters"}
            }else{
              require(profile.getString("kind")=="phone-camera-distance-research-profile-v1"){"Invalid research profile"}
              require(profile.getJSONObject("rotationTiming").getBoolean("passed")){"Research rotation/timing fit did not pass"}
            }
            }
            if(onDeviceProfile==null&&binding.has("capturePipeline"))require(binding.getString("capturePipeline")=="native-camera-imu-v2"&&binding.optString("opticalSetup") in listOf("waist-bag-window","clear-lens")){"Research profile has an incompatible capture or optical setup"}
            require(installation!=null&&binding.getString("installationId")==installation&&binding.getString("cameraId")==cameraId&&binding.getInt("width")==size.width&&binding.getInt("height")==size.height&&binding.getString("imageAxes")=="native-sensor-unrotated-unmirrored"&&binding.getInt("sensorOrientationDegrees")==characteristics!!.get(CameraCharacteristics.SENSOR_ORIENTATION)&&binding.getString("stabilizationRequested")=="off"){"Research profile belongs to another phone or camera setup"}
          }
          // Published reference is used by the paired computer, never the legacy tracker.
          if(!referenceTrial)tracker=ResearchDistanceTracker(profile)
        }
        dir.mkdirs(); File(dir, "frames").mkdirs()
        if(distanceTrial){diagnosticRows=File(dir,"tracking.ndjson").bufferedWriter();profileText?.let{File(dir,if(referenceTrial)"reference-calibration.json" else "research-profile.json").writeText(it)}}
        imu = File(dir, "imu.ndjson").bufferedWriter(); frames = File(dir, "frames.ndjson").bufferedWriter(); results = File(dir, "capture-results.ndjson").bufferedWriter()
        subscribeSensors()
        reader = ImageReader.newInstance(size.width, size.height, ImageFormat.YUV_420_888, 3)
        reader!!.setOnImageAvailableListener({ source ->
          val image = source.acquireLatestImage() ?: return@setOnImageAvailableListener
          try { saveImage(image) } catch (e: Exception) { finish("error", e.message) } finally { image.close() }
        }, handler)
        manager.openCamera(cameraId, object : CameraDevice.StateCallback() {
          override fun onOpened(camera: CameraDevice) {
            if (closed) { camera.close(); return }
            device = camera
            camera.createCaptureSession(listOf(reader!!.surface), object : CameraCaptureSession.StateCallback() {
              override fun onConfigured(s: CameraCaptureSession) {
                if (closed) { s.close(); return }
                session = s
                try {
                  val request = camera.createCaptureRequest(CameraDevice.TEMPLATE_RECORD)
                  request.addTarget(reader!!.surface)
                  request.set(CaptureRequest.CONTROL_VIDEO_STABILIZATION_MODE, CaptureRequest.CONTROL_VIDEO_STABILIZATION_MODE_OFF)
                  request.set(CaptureRequest.LENS_OPTICAL_STABILIZATION_MODE, CaptureRequest.LENS_OPTICAL_STABILIZATION_MODE_OFF)
                  // Keep calibration optics fixed instead of silently changing focal length.
                  request.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF)
                  request.set(CaptureRequest.LENS_FOCUS_DISTANCE, 0f)
                  if(onDeviceSetup||onDeviceProfile!=null){
                    if(Build.VERSION.SDK_INT>=28&&characteristics!!.get(CameraCharacteristics.DISTORTION_CORRECTION_AVAILABLE_MODES)?.contains(CaptureRequest.DISTORTION_CORRECTION_MODE_OFF)==true)
                      request.set(CaptureRequest.DISTORTION_CORRECTION_MODE,CaptureRequest.DISTORTION_CORRECTION_MODE_OFF)
                  }
                  val ranges = characteristics!!.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES).orEmpty()
                  ranges.filter { it.upper >= 30 }.minByOrNull { kotlin.math.abs(it.upper - 30) + kotlin.math.abs(it.lower - 30) }?.let { request.set(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE, it) }
                  started = SystemClock.elapsedRealtimeNanos()
                  guidedClock=if(alignment||rapidEnrollment||onDeviceSetup)GuidedCaptureClock(started,onDeviceSetup) else null
                  if(guidedLens)watchLensCamera()
                  s.setRepeatingRequest(request.build(), object : CameraCaptureSession.CaptureCallback() {
                    override fun onCaptureCompleted(s: CameraCaptureSession, r: CaptureRequest, result: TotalCaptureResult) {
                      if (closed) return
                      val ts = result.get(CaptureResult.SENSOR_TIMESTAMP) ?: return
                      val row = JSONObject().put("timestampNs", ts).put("frameNumber", result.frameNumber)
                        .put("exposureNs", result.get(CaptureResult.SENSOR_EXPOSURE_TIME) ?: JSONObject.NULL)
                        .put("rollingShutterSkewNs", result.get(CaptureResult.SENSOR_ROLLING_SHUTTER_SKEW) ?: JSONObject.NULL)
                        .put("focusDioptres", result.get(CaptureResult.LENS_FOCUS_DISTANCE) ?: JSONObject.NULL)
                        .put("cropRegion",result.get(CaptureResult.SCALER_CROP_REGION)?.let{JSONArray(listOf(it.left,it.top,it.right,it.bottom))}?:JSONObject.NULL)
                        .put("videoStabilizationMode", result.get(CaptureResult.CONTROL_VIDEO_STABILIZATION_MODE) ?: JSONObject.NULL)
                        .put("opticalStabilizationMode", result.get(CaptureResult.LENS_OPTICAL_STABILIZATION_MODE) ?: JSONObject.NULL)
                      budget.camera(ts)
                      processing.post { guardedStorage {
                        results?.write(row.toString()+"\n")
                        if(onDeviceSetup||onDeviceProfile!=null){
                          if(onDeviceVio==null){
                            val crop=result.get(CaptureResult.SCALER_CROP_REGION)?:error("Camera crop metadata is unavailable")
                            onDeviceCamera=JSONObject().put("opticalPrior",opticalPrior(characteristics!!,crop))
                              .put("displayRotationDegrees",(ctx.getSystemService(Context.WINDOW_SERVICE) as android.view.WindowManager).defaultDisplay.rotation*90)
                            onDeviceVio=OnDeviceVio(dir,onDeviceCamera!!,onDeviceProfile)
                            // Camera crop metadata arrives after sensors start. Preserve and
                            // replay actual early IMU before giving the estimator any image.
                            startupImu.replay { name,ns,x,y,z -> onDeviceVio!!.sensor(name,ns,x,y,z) }
                          }
                          liveTiming[ts]=row;liveImages.remove(ts)?.let{onDeviceVio?.frame(ts,it,row)}
                          while(liveTiming.size>40)liveTiming.remove(liveTiming.keys.first())
                        }
                        if(distanceTrial){cameraMetadata[ts]=row;pendingImages.remove(ts)?.let { processTrialImage(ts,it,row) };while(cameraMetadata.size>40)cameraMetadata.remove(cameraMetadata.keys.first())}
                      } }
                    }
                  }, handler)
                  val captureTimeout=object:Runnable {
                    override fun run(){
                      if(closed)return
                      val remaining=guidedClock?.remainingSafetyMs(SystemClock.elapsedRealtimeNanos())?:0L
                      if(remaining>0){handler.postDelayed(this,remaining);return}
                      finish(if(gaitSessionId!=null)"capture-limit" else if(guidedLens||guidedClock!=null) "quality-time-limit" else if(distanceTrial) "time-limit" else "completed", if(gaitSessionId!=null)"Camera capture exceeded its safety limit" else if(guidedLens)(if(lensFitting)"Lens parameter checking did not finish before the time limit." else lastLensFailure) else if(onDeviceSetup&&!setupBaseline.accepted())"A quiet baseline was not established. Your saved setup is kept." else if(guidedClock!=null)"Calibration guidance did not finish." else null)
                    }
                  }
                  // Ordinary phone setup waits for observed quality, not an elapsed-time failure.
                  // User cancellation and actual camera/sensor/storage errors still stop capture.
                  if(!onDeviceSetup)handler.postDelayed(captureTimeout,if(gaitSessionId!=null)900000 else if(guidedLens)300000 else if(guidedClock!=null)GuidedCaptureClock.SAFETY_MS else if(distanceTrial)180000 else 40000)
                } catch (e: Exception) { finish("error", e.message) }
              }
              override fun onConfigureFailed(s: CameraCaptureSession) { finish("error", "Front-camera session could not start") }
            }, handler)
          }
          override fun onDisconnected(camera: CameraDevice) { camera.close(); finish("interrupted", "Camera disconnected") }
          override fun onError(camera: CameraDevice, error: Int) { camera.close(); finish("error", "Camera error $error") }
        }, handler)
        handler.postDelayed({ if (started == 0L) finish("error", "Camera did not start") }, 10000)
      } catch (e: Exception) { finish("error", e.message) }
    } }

    private fun subscribeSensors(){
      for ((type, _) in types) require(sensors.getDefaultSensor(type)!=null){"All three motion sensors are required"}
      for ((type, _) in types) require(sensors.registerListener(this,sensors.getDefaultSensor(type)!!,if(type==Sensor.TYPE_MAGNETIC_FIELD)20000 else 5000,handler)){"Could not subscribe to motion sensor"}
    }
    private fun guardedStorage(block:()->Unit){
      try{block()}catch(e:Exception){
        if(storageError==null)storageError=e.message?:"Capture storage failed"
        handler.post{finish("error",storageError)}
      }
    }
    private fun saveImage(image: Image) {
      if (closed || started == 0L) return
      lastImageArrival=SystemClock.elapsedRealtimeNanos()
      // Lens fitting only observes four views/second. Select before costly copying/JPEG/storage.
      // Camera/IMU alignment and walking retain their original acquisition path.
      if(!budget.selectFrame(image.timestamp,if(guidedLens)GuidedLensCalibration.SAMPLE_INTERVAL_NS else if(onDeviceSetup||onDeviceProfile!=null)50000000L else 0L))return
      if(!budget.reserveFrame())return
      val arrival=SystemClock.elapsedRealtimeNanos()
      val timestamp=image.timestamp;val width=image.width;val height=image.height
      val phaseAtArrival=trialPhase
      val nv21=ByteArray(width*height*3/2)
      try{
        for(plane in 0..2){
          val p=image.planes[plane];val buffer=p.buffer.duplicate();val base=buffer.position()
          val w=if(plane==0)width else width/2;val h=if(plane==0)height else height/2
          for(y in 0 until h)for(x in 0 until w){
            val destination=if(plane==0)y*width+x else width*height+(y*w+x)*2+(if(plane==1)1 else 0)
            nv21[destination]=buffer.get(base+y*p.rowStride+x*p.pixelStride)
          }
        }
      }catch(e:Exception){budget.releaseFrame();throw e}
      processing.post {
        val workStarted=SystemClock.elapsedRealtimeNanos()
        try{guardedStorage{
          val name="frames/${frameCount.toString().padStart(5,'0')}.jpg"
          File(dir,name).outputStream().use{stream->require(YuvImage(nv21,ImageFormat.NV21,width,height,null).compressToJpeg(Rect(0,0,width,height),90,stream))}
          if(gaitSessionId!=null){imageBytes+=File(dir,name).length();require(imageBytes<200L*1024*1024&&ctx.filesDir.usableSpace>100L*1024*1024){ "Camera storage limit reached; motion recording remains separate" }}
          frames?.write(JSONObject().put("file",name).put("timestampNs",timestamp).put("arrivalBootNs",arrival).put("processingStartedBootNs",workStarted).toString()+"\n")
          budget.saved(timestamp);frameCount++
          if(onDeviceSetup||onDeviceProfile!=null){
            val row=liveTiming.remove(timestamp)
            if(row!=null)onDeviceVio?.frame(timestamp,File(dir,name),row)
            else{liveImages[timestamp]=File(dir,name);require(liveImages.size<=8){"Camera timing did not keep up"}}
          }
          if(guidedLens&&!lensFinished&&!closed){
            lensSolver?.setFitListener { lensFitting=true;lastLensProgress=lensSolver?.progress()?.toString();sendEvent("progress",mapOf("phase" to "lens-fitting","imageUri" to File(dir,name).toURI().toString(),"lens" to lastLensProgress)) }
            lensSolver?.observe(nv21.copyOf(width*height),timestamp)
            lensFitting=false
            lastLensFailure=lensSolver?.failureMessage()?:lastLensFailure
            lastLensProgress=lensSolver?.progress()?.toString()
            if(lensSolver?.ready()==true){lensFinished=true;handler.post{finish("completed",null)}}
          }
          if(distanceTrial&&!referenceTrial&&phaseAtArrival=="walking"){
            val luma=nv21.copyOf(width*height);val result=cameraMetadata[timestamp]
            if(result!=null)processTrialImage(timestamp,luma,result)
            else{pendingImages[timestamp]=luma;while(pendingImages.size>8)pendingImages.remove(pendingImages.keys.first())}
          }
          val now=SystemClock.elapsedRealtimeNanos()
          if(!closed&&now-lastProgress>500000000L){
            lastProgress=now;val elapsed=(now-started)/1e9
            val baselineReady=!onDeviceSetup||setupBaseline.ready(now,onDeviceVio?.status())
            val phase=if(alignment||rapidEnrollment)if(alignmentStarted>0)"alignment-move" else if(elapsed>=10&&baselineReady){if(onDeviceSetup&&!setupBaseline.accepted())setupBaseline.accept(now,onDeviceVio?.status());"alignment-cue"} else "alignment-still" else if(guidedLens)"lens" else if(distanceTrial)phaseAtArrival else if(elapsed<5)"still" else "move"
            sendEvent("progress",mapOf("elapsedSeconds" to elapsed,"frames" to frameCount,"imageUri" to File(dir,name).toURI().toString(),"phase" to phase,"tracking" to tracker?.snapshot()?.toString(),"lens" to lensSolver?.progress()?.toString(),"setupTracking" to (if(onDeviceSetup)onDeviceVio?.status()?.toString() else null),"setupFinalCheck" to (if(onDeviceSetup)onDeviceVio?.setupCheck(now)?.toString() else null),"setupMovementRemainingMs" to (if(onDeviceSetup&&alignmentStarted>0)guidedClock?.remainingMovementMs(now) else null),"setupSettled" to (onDeviceSetup&&onDeviceVio?.setupSettled(now)==true)))
          }
        }}finally{budget.timing(if(characteristics?.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME)arrival-timestamp else 0,workStarted-arrival,SystemClock.elapsedRealtimeNanos()-workStarted);budget.releaseFrame()}
      }
    }
    private fun processTrialImage(timestamp: Long,luma: ByteArray,result: JSONObject){
      val diagnostic=tracker?.process(luma,size.width,size.height,timestamp,result)
      diagnosticRows?.write(JSONObject().put("timestampNs",timestamp).put("tracking",diagnostic?:JSONObject.NULL).toString()+"\n")
    }
    override fun onSensorChanged(event: SensorEvent) {
      if (closed || started == 0L) return
      val name = types[event.sensor.type] ?: return
      if(!budget.reserveSensor()){finish("error","Sensor storage could not keep up; capture stopped to preserve integrity");return}
      // Android reuses SensorEvent: copy values before handing off to storage.
      val timestamp=event.timestamp;val arrival=SystemClock.elapsedRealtimeNanos()
      val x=event.values[0].toDouble();val y=event.values[1].toDouble();val z=event.values[2].toDouble();val accuracy=event.accuracy
      processing.post{
        try{guardedStorage{
          imu?.write(JSONObject().put("sensor",name).put("timestampNs",timestamp).put("arrivalBootNs",arrival)
            .put("x",x).put("y",y).put("z",z).put("accuracy",accuracy).toString()+"\n")
          counts[name]=counts.getValue(name)+1
          if(distanceTrial)tracker?.sensor(name,timestamp,x,y,z)
          if(onDeviceSetup||onDeviceProfile!=null){
            if(onDeviceSetup)setupBaseline.sensor(name,timestamp,x,y,z)
            val vio=onDeviceVio
            if(vio==null)startupImu.add(name,timestamp,x,y,z) else vio.sensor(name,timestamp,x,y,z)
          }
          onDeviceVio?.status()?.let{state->onDeviceStatus=state
            val stateNs=(state.getJSONObject("state").getDouble("imu_time_s")*1e9).toLong()
            if(stateNs>liveProgressAt&&timestamp-stateNs in 0L..750000000L){liveProgressAt=stateNs
              sendEvent("distanceProgress",mapOf("sessionId" to gaitSessionId,"status" to state.toString()))
            }
          }
        }}finally{budget.releaseSensor()}
      }
      if(distanceTrial){
        val now=event.timestamp
        if(name=="gyroscope"){gyroTimestamp=now;latestGyro=kotlin.math.sqrt(event.values.sumOf{it.toDouble()*it})}
        if(name=="magnetometer")magnetTimestamp=now
        if(name=="accelerometer"){
          accelTimestamp=now;val magnitude=kotlin.math.sqrt(event.values.sumOf{it.toDouble()*it})
          accelerationWindow.addLast(now to magnitude)
          while(accelerationWindow.isNotEmpty()&&now-accelerationWindow.first().first>2000000000L)accelerationWindow.removeFirst()
          val mean=accelerationWindow.map{it.second}.average()
          val sd=kotlin.math.sqrt(accelerationWindow.map{(it.second-mean)*(it.second-mean)}.average())
          val fresh=now-gyroTimestamp in 0..500000000L&&now-magnetTimestamp in 0..500000000L
          if(gaitSessionId!=null){
            // The main protocol owns start/end. Rests must never end endurance capture.
          }else if(referenceTrial){
            val short=accelerationWindow.filter{now-it.first<=350000000L}.map{it.second}
            val shortMean=short.average()
            val shortSd=kotlin.math.sqrt(short.map{(it-shortMean)*(it-shortMean)}.average())
            val stop=distanceFlow.observe(now,sd<.05*9.80665&&latestGyro<.08,
              shortSd>.025*9.80665||latestGyro>.1,kotlin.math.abs(now-gyroTimestamp)<500000000L&&kotlin.math.abs(now-magnetTimestamp)<500000000L&&frameCount>=5&&accelerationWindow.size>100)
            trialPhase=distanceFlow.phase;walkStarted=distanceFlow.walkStartedNs
            if(stop!=null)finish(stop,null)
          }else{
          if(trialPhase=="placing"&&frameCount>=5&&fresh&&accelerationWindow.size>100&&now-accelerationWindow.first().first>1900000000L&&sd<.05*9.80665&&latestGyro<.08){trialPhase="cue"}
          if(trialPhase=="waiting"&&fresh&&(sd>.025*9.80665||latestGyro>.1)){trialPhase="walking";walkStarted=now;movementLast=now}
          if(trialPhase=="walking"){
            if(sd>.025*9.80665||latestGyro>.1)movementLast=now
            if(now-walkStarted>6000000000L&&now-movementLast>4000000000L)finish("quiet-stop",null)
            else if(now-walkStarted>60000000000L)finish("walk-time-limit",null)
          }
          }
        }
      }
    }
    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
    fun requestStop(reason: String) { handler.post { finish(reason,null) } }
    private fun finish(reason: String,error: String?) {
      if (closed) return
      closed = true
      if(guidedLens)sendEvent("progress",mapOf("phase" to "lens-saving","imageUri" to "","tracking" to reason,"lens" to lastLensProgress,"error" to error))
      sensors.unregisterListener(this)
      try { session?.stopRepeating() } catch (_: Exception) {}
      session?.close(); device?.close(); reader?.close()
      // FIFO barrier: accepted frame/sensor jobs are persisted before closing files.
      processing.post { finalizeCapture(if(storageError!=null)"error" else reason,error?:storageError) }
    }
    private fun finalizeCapture(reason: String,error: String?) {
      try {
        imu?.close(); frames?.close(); results?.close(); diagnosticRows?.close()
        val c=characteristics
        val nativeClock=c?.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)
        val preferences=ctx.getSharedPreferences("gait-calibration",Context.MODE_PRIVATE)
        val installationId=preferences.getString("installationId",null)?:UUID.randomUUID().toString().also { preferences.edit().putString("installationId",it).apply() }
        val metadata=JSONObject().put("schemaVersion",1).put("captureId",id).put("installationId",installationId).put("status",reason).put("error",error?:JSONObject.NULL)
          .put("device",JSONObject().put("manufacturer",Build.MANUFACTURER).put("model",Build.MODEL).put("os",Build.VERSION.RELEASE))
          .put("cameraId",cameraId).put("facing","front").put("width",size.width).put("height",size.height)
          .put("imageAxes","native-sensor-unrotated-unmirrored").put("sensorOrientationDegrees",c?.get(CameraCharacteristics.SENSOR_ORIENTATION)?:JSONObject.NULL)
          .put("timestampSource",if(nativeClock==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME) "realtime" else "unknown")
          .put("startedBootNs",started).put("endedBootNs",SystemClock.elapsedRealtimeNanos()).put("frames",frameCount)
          .put("sensorCounts",JSONObject(counts as Map<*,*>)).put("units",JSONObject().put("accelerometer","m/s2").put("gyroscope","rad/s").put("magnetometer","uT"))
          .put("stabilizationRequested","off").put("focusRequestedDioptres",0).put("calibrationStatus","unprocessed").put("distanceReady",false)
          .put("imageCallbackLatencyComparable",nativeClock==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME).put("capturePipeline","native-camera-imu-v2").put("opticalSetup",if(distanceTrial)profileText?.let{JSONObject(it).getJSONObject("binding").optString("opticalSetup","unconfirmed")}?:"unconfirmed" else opticalSetup).put("capturePerformance",JSONObject(budget.snapshot() as Map<*,*>))
          .put("frameRateTargetHz",if(noiseSeconds>0)0 else 30).put("sensorRateTargetsHz",JSONObject().put("accelerometer",200).put("gyroscope",200).put("magnetometer",50))
        if(noiseSeconds>0){
          metadata.put("kind","phone-imu-noise-capture-v1").put("requestedDurationSeconds",noiseSeconds).put("fullCalibrationReady",false)
          for(key in listOf("cameraId","facing","width","height","imageAxes","sensorOrientationDegrees","timestampSource","stabilizationRequested","focusRequestedDioptres","opticalSetup"))metadata.remove(key)
          metadata.put("timestampSource","sensor-hardware-boot-clock")
        }
        if(distanceTrial){
          val diagnostics=tracker?.finish()?:JSONObject().put("status","unavailable").put("distanceReady",false)
          diagnostics.put("metricReadiness",JSONObject().put("status","blocked").put("reasons",JSONArray(listOf("full-calibration-required","continuous-estimator-not-integrated"))).put("clinicalReady",false))
          diagnostics.put("stopReason",reason).put("walkStartedBootNs",walkStarted).put("placementCompleted",walkStarted>0)
          if(referenceTrial)diagnostics.put("distanceCaptureProtocolVersion",2)
            .put("warmupCompleted",distanceFlow.warmupCompleted).put("warmupIsVioReadiness",false)
            .put("walkEndedBootNs",distanceFlow.walkEndedNs).put("endBoundarySource","last-detected-motion-before-quiet-stop")
          if(error!=null||reason=="interrupted"||reason=="user-stopped"){diagnostics.put("status","rejected").put("reason",error?:reason);diagnostics.remove("experimentalHorizontalCameraPathMetres");diagnostics.remove("experimentalMeanCameraSpeedMps")}
          metadata.put("kind","front-camera-distance-research-v1").put("diagnostics",diagnostics)
          if(gaitSessionId!=null){
            diagnostics.put("walkStartedBootNs",gaitFlow.startNs).put("walkEndedBootNs",gaitFlow.endNs)
              .put("placementCompleted",gaitFlow.startNs>0).put("endBoundarySource","main-protocol-native-command")
            metadata.put("kind","gait-camera-imu-distance-capture-v1").put("sessionId",gaitSessionId).put("protocol",gaitProtocol)
          }
          releaseText?.let { metadata.put("appRelease",JSONObject(it)) }
          File(dir,"distance-diagnostics.json").writeText(diagnostics.toString(2))
        }
        c?.let { val factory=factoryMetadata(it);for(key in factory.keys())metadata.put(key,factory.get(key)) }
        if(guidedLens){
          metadata.put("captureMode","guided-lens-zhang").put("boardUnits","arbitrary-uniform-units-not-metres")
          metadata.put("lensCaptureSamplingHz",4).put("lensDiagnostics",lensSolver?.progress()?:JSONObject.NULL)
          val report=lensSolver?.report()
          // Partial, cancelled and failed recordings can never replace a saved profile.
          if(reason=="completed"&&error==null&&report?.optBoolean("lensReady")==true){
            val binding=JSONObject()
            for(key in listOf("installationId","captureId","cameraId","width","height","imageAxes","sensorOrientationDegrees","stabilizationRequested","focusRequestedDioptres","capturePipeline","opticalSetup"))binding.put(key,metadata.get(key))
            report.put("binding",binding)
            File(dir,"lens-calibration.json").writeText(report.toString(2))
            val temp=File(dir.parentFile,"lens.pending.json");temp.writeText(report.toString(2))
            require(temp.renameTo(File(dir.parentFile,"lens.json"))){"Could not save lens parameters"}
            metadata.put("lensCalibration",report).put("calibrationStatus","lens-only-candidate")
          }
          metadata.put("fullCalibrationReady",false)
        }
        if(alignment){metadata.put("captureMode","targetless-alignment").put("kind","phone-camera-imu-alignment-capture-v1")
          .put("alignmentMovementStartedBootNs",alignmentStarted).put("lensProfile",alignmentLens?:JSONObject.NULL).put("fullCalibrationReady",false)}
        if(onDeviceSetup){
          metadata.put("vioBootstrap",(onDeviceVio?.bootstrapDiagnostics()?:JSONObject()).put("realImuSamplesReplayed",startupImu.replayed()))
          onDeviceVio?.close();onDeviceVio=null
          metadata.put("capturePipeline","native-camera-imu-v3").put("captureMode","on-device-scene-setup").put("kind","phone-on-device-setup-capture-v1")
            .put("alignmentMovementStartedBootNs",alignmentStarted).put("opticalPrior",onDeviceCamera?.optJSONObject("opticalPrior")?:JSONObject.NULL)
        }else if(rapidEnrollment){metadata.put("captureMode","learned-scene-enrollment").put("kind","phone-rapid-camera-imu-capture-v1")
          .put("alignmentMovementStartedBootNs",alignmentStarted).put("fullCalibrationReady",false)}
        if(onDeviceProfile!=null){
          metadata.put("vioBootstrap",(onDeviceVio?.bootstrapDiagnostics()?:JSONObject()).put("realImuSamplesReplayed",startupImu.replayed()))

          val crossing=onDeviceVio?.finishNs()?:0
          if(gaitProtocol=="10mwt")metadata.getJSONObject("diagnostics").put("tenMetreBoundaries",onDeviceVio?.tenMetreBoundaries()?:JSONObject.NULL)

          if(crossing>gaitFlow.startNs&&gaitProtocol=="10mwt"&&reason=="completed")metadata.getJSONObject("diagnostics").put("walkEndedBootNs",crossing).put("endBoundarySource","on-device-estimated-12m-crossing")

          onDeviceVio?.close();onDeviceVio=null;metadata.put("capturePipeline","native-camera-imu-v3").put("opticalSetup","waist-bag-window").put("liveTracking",onDeviceStatus?:JSONObject.NULL)

          metadata.getJSONObject("diagnostics").put("metricReadiness",JSONObject().put("status","accuracy-unvalidated").put("clinicalReady",false).put("liveEstimatorIntegrated",true))

        }

        lensSolver?.close()
        File(dir,"manifest.json").writeText(metadata.toString(2))
        val zip=File(dir.parentFile,"$id.zip")
        ZipOutputStream(zip.outputStream().buffered()).use { target -> dir.walkTopDown().filter { it.isFile }.forEach { file ->
          target.putNextEntry(ZipEntry(file.relativeTo(dir).invariantSeparatorsPath));file.inputStream().use { it.copyTo(target) };target.closeEntry()
        } }
        // JS can start local processing immediately on resolve. Release capture ownership
        // first, and never let this old handler clear a newly started capture.
        if(run===this)run=null
        promise.resolve(mapOf("uri" to zip.toURI().toString(),"metadata" to metadata.toString(),"error" to error))
      } catch(e: Exception) { if(run===this)run=null;promise.reject("E_CAPTURE",e.message,e) }
      processingThread.quitSafely()
      handler.post {thread.quitSafely()}
    }
  }
}
