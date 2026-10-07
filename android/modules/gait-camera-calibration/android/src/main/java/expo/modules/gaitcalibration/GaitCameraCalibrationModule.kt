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
  override fun definition() = ModuleDefinition {
    Name("GaitCameraCalibration")
    Events("progress")
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
    AsyncFunction("captureNoise") { promise: Promise ->
      val ctx = requireNotNull(appContext.reactContext)
      if (run != null) promise.reject("E_BUSY", "A research capture is already running", null)
      else { val capture = Capture(ctx,promise,noiseSeconds=300);run=capture;capture.start() }
    }
    AsyncFunction("beginDistance") { run?.beginDistance() }
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
    return m
  }
  private fun startBoardCapture(opticalSetup: String,promise: Promise,guidedLens:Boolean=false){
    val ctx=requireNotNull(appContext.reactContext)
    if(run!=null)promise.reject("E_BUSY","A research capture is already running",null)
    else if(ctx.checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)promise.reject("E_PERMISSION","Camera permission is required",null)
    else{val capture=Capture(ctx,promise,opticalSetup=opticalSetup,guidedLens=guidedLens);run=capture;capture.start()}
  }

  private inner class Capture(val ctx: Context, val promise: Promise, val distanceTrial: Boolean=false, val profileText: String?=null, val releaseText: String?=null, val noiseSeconds: Int=0, val opticalSetup: String="unconfirmed",val guidedLens:Boolean=false,val alignment:Boolean=false) : SensorEventListener {
    private val thread = HandlerThread("GaitCalibration").apply { start() }
    private val handler = Handler(thread.looper)
    private val processingThread = HandlerThread("GaitCaptureStorage").apply { start() }
    private val processing = Handler(processingThread.looper)
    private val budget = CaptureQueueBudget(4,5000)
    @Volatile private var storageError: String? = null
    private val manager = ctx.getSystemService(Context.CAMERA_SERVICE) as CameraManager
    private val sensors = ctx.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val id = "${if(noiseSeconds>0) "imu-noise" else if(distanceTrial) "distance-trial" else "calibration"}-${System.currentTimeMillis()}"
    private val dir = File(ctx.filesDir, "${if(noiseSeconds>0) "camera-imu-noise" else if(distanceTrial) "camera-distance-trials" else "camera-calibration"}/$id")
    private var tracker: ResearchDistanceTracker? = null
    private var lensSolver:GuidedLensCalibration?=null
    private var alignmentLens:JSONObject?=null
    @Volatile private var alignmentStarted=0L
    @Volatile private var lensFinished=false
    private var trialPhase = "placing"
    private var walkStarted = 0L
    private var movementLast = 0L
    private var latestGyro = 1.0
    private var gyroTimestamp = 0L
    private var accelTimestamp = 0L
    private var magnetTimestamp = 0L
    private val accelerationWindow = ArrayDeque<Pair<Long,Double>>()
    private val cameraMetadata = linkedMapOf<Long,JSONObject>()
    private val pendingImages = linkedMapOf<Long,ByteArray>()
    private var diagnosticRows: BufferedWriter? = null
    fun beginDistance() { handler.post { if(distanceTrial&&trialPhase=="cue") {trialPhase="waiting";accelerationWindow.clear()} } }
    fun beginAlignmentMovement(){handler.post{if(alignment&&!closed&&alignmentStarted==0L){alignmentStarted=SystemClock.elapsedRealtimeNanos();handler.postDelayed({finish("completed",null)},50000)}}}
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
            require(profile.getString("kind")=="phone-camera-distance-research-profile-v1"&&profile.getInt("schemaVersion")==1&& !profile.getBoolean("distanceReady") && !profile.getBoolean("fullCalibrationReady")){"Invalid research profile"}
            require(profile.getJSONObject("rotationTiming").getBoolean("passed")){"Research rotation/timing fit did not pass"}
            if(binding.has("capturePipeline"))require(binding.getString("capturePipeline")=="native-camera-imu-v2"&&binding.optString("opticalSetup") in listOf("waist-bag-window","clear-lens")){"Research profile has an incompatible capture or optical setup"}
            require(installation!=null&&binding.getString("installationId")==installation&&binding.getString("cameraId")==cameraId&&binding.getInt("width")==size.width&&binding.getInt("height")==size.height&&binding.getString("imageAxes")=="native-sensor-unrotated-unmirrored"&&binding.getInt("sensorOrientationDegrees")==characteristics!!.get(CameraCharacteristics.SENSOR_ORIENTATION)&&binding.getString("stabilizationRequested")=="off"){"Research profile belongs to another phone or camera setup"}
          }
          tracker=ResearchDistanceTracker(profile)
        }
        dir.mkdirs(); File(dir, "frames").mkdirs()
        if(distanceTrial){diagnosticRows=File(dir,"tracking.ndjson").bufferedWriter();profileText?.let{File(dir,"research-profile.json").writeText(it)}}
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
                  val ranges = characteristics!!.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES).orEmpty()
                  ranges.filter { it.upper >= 30 }.minByOrNull { kotlin.math.abs(it.upper - 30) + kotlin.math.abs(it.lower - 30) }?.let { request.set(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE, it) }
                  started = SystemClock.elapsedRealtimeNanos()
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
                        if(distanceTrial){cameraMetadata[ts]=row;pendingImages.remove(ts)?.let { processTrialImage(ts,it,row) };while(cameraMetadata.size>40)cameraMetadata.remove(cameraMetadata.keys.first())}
                      } }
                    }
                  }, handler)
                  handler.postDelayed({ finish(if(guidedLens||alignment) "quality-time-limit" else if(distanceTrial) "time-limit" else "completed", if(guidedLens)"Not enough clear, varied views. Your previous lens profile is kept." else if(alignment)"Calibration guidance did not finish." else null) }, if(guidedLens)300000 else if(alignment)120000 else if(distanceTrial)180000 else 40000)
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
      // No artificial frame throttle. Bounded queue drops are counted, never hidden.
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
          frames?.write(JSONObject().put("file",name).put("timestampNs",timestamp).put("arrivalBootNs",arrival).put("processingStartedBootNs",workStarted).toString()+"\n")
          budget.saved(timestamp);frameCount++
          if(guidedLens&&!lensFinished){
            lensSolver?.observe(nv21.copyOf(width*height),timestamp)
            if(lensSolver?.ready()==true){lensFinished=true;handler.post{finish("completed",null)}}
            else if((lensSolver?.acceptedViews()?:0)>=48){lensFinished=true;handler.post{finish("quality-failed","Try a clearer view from another angle.")}}
          }
          if(distanceTrial&&phaseAtArrival=="walking"){
            val luma=nv21.copyOf(width*height);val result=cameraMetadata[timestamp]
            if(result!=null)processTrialImage(timestamp,luma,result)
            else{pendingImages[timestamp]=luma;while(pendingImages.size>8)pendingImages.remove(pendingImages.keys.first())}
          }
          val now=SystemClock.elapsedRealtimeNanos()
          if(now-lastProgress>500000000L){
            lastProgress=now;val elapsed=(now-started)/1e9
            val phase=if(alignment)if(alignmentStarted>0)"alignment-move" else if(elapsed>=10)"alignment-cue" else "alignment-still" else if(guidedLens)"lens" else if(distanceTrial)phaseAtArrival else if(elapsed<5)"still" else "move"
            sendEvent("progress",mapOf("elapsedSeconds" to elapsed,"frames" to frameCount,"imageUri" to File(dir,name).toURI().toString(),"phase" to phase,"tracking" to tracker?.snapshot()?.toString(),"lens" to lensSolver?.progress()?.toString()))
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
    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
    fun requestStop(reason: String) { handler.post { finish(reason,null) } }
    private fun finish(reason: String,error: String?) {
      if (closed) return
      closed = true
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
          if(error!=null||reason=="interrupted"||reason=="user-stopped"){diagnostics.put("status","rejected").put("reason",error?:reason);diagnostics.remove("experimentalHorizontalCameraPathMetres");diagnostics.remove("experimentalMeanCameraSpeedMps")}
          metadata.put("kind","front-camera-distance-research-v1").put("diagnostics",diagnostics)
          releaseText?.let { metadata.put("appRelease",JSONObject(it)) }
          File(dir,"distance-diagnostics.json").writeText(diagnostics.toString(2))
        }
        c?.let { val factory=factoryMetadata(it);for(key in factory.keys())metadata.put(key,factory.get(key)) }
        if(guidedLens){
          metadata.put("captureMode","guided-lens-zhang").put("boardUnits","arbitrary-uniform-units-not-metres")
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
        lensSolver?.close()
        File(dir,"manifest.json").writeText(metadata.toString(2))
        val zip=File(dir.parentFile,"$id.zip")
        ZipOutputStream(zip.outputStream().buffered()).use { target -> dir.walkTopDown().filter { it.isFile }.forEach { file ->
          target.putNextEntry(ZipEntry(file.relativeTo(dir).invariantSeparatorsPath));file.inputStream().use { it.copyTo(target) };target.closeEntry()
        } }
        promise.resolve(mapOf("uri" to zip.toURI().toString(),"metadata" to metadata.toString(),"error" to error))
      } catch(e: Exception) { promise.reject("E_CAPTURE",e.message,e) }
      processingThread.quitSafely()
      handler.post {run=null;thread.quitSafely()}
    }
  }
}
