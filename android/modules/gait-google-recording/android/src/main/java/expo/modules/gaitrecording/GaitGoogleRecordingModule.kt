package expo.modules.gaitrecording

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import com.google.android.gms.common.ConnectionResult
import com.google.android.gms.common.GoogleApiAvailability
import com.google.android.gms.fitness.FitnessLocal
import com.google.android.gms.fitness.LocalRecordingClient
import com.google.android.gms.fitness.data.LocalDataType
import com.google.android.gms.fitness.data.LocalField
import com.google.android.gms.fitness.request.LocalDataReadRequest
import com.google.android.gms.tasks.Tasks
import expo.modules.kotlin.Promise
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import java.util.concurrent.TimeUnit

/** Accountless local API. No legacy Fit OAuth, cloud upload or gait inference. */
class GaitGoogleRecordingModule : Module() {
  private fun context() = requireNotNull(appContext.reactContext) { "React context unavailable" }
  private fun client() = FitnessLocal.getLocalRecordingClient(context())
  private fun release() = Tasks.whenAll(
    client().unsubscribe(LocalDataType.TYPE_DISTANCE_DELTA),
    client().unsubscribe(LocalDataType.TYPE_STEP_COUNT_DELTA)
  )

  override fun definition() = ModuleDefinition {
    Name("GaitGoogleRecording")

    AsyncFunction("availability") {
      val ctx = context()
      val code = GoogleApiAvailability.getInstance().isGooglePlayServicesAvailable(
        ctx, LocalRecordingClient.LOCAL_RECORDING_CLIENT_MIN_VERSION_CODE
      )
      val permitted = Build.VERSION.SDK_INT < 29 ||
        ctx.checkSelfPermission(Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED
      mapOf("available" to (code == ConnectionResult.SUCCESS),
        "permissionGranted" to permitted, "playServicesCode" to code,
        "minimumPlayServicesVersion" to LocalRecordingClient.LOCAL_RECORDING_CLIENT_MIN_VERSION_CODE)
    }

    AsyncFunction("subscribe") { promise: Promise ->
      try {
        Tasks.whenAll(client().subscribe(LocalDataType.TYPE_DISTANCE_DELTA),
          client().subscribe(LocalDataType.TYPE_STEP_COUNT_DELTA))
          .addOnSuccessListener { promise.resolve(null) }
          .addOnFailureListener { error ->
            try {
              release().addOnCompleteListener { promise.reject("E_GOOGLE_SUBSCRIBE", error.message, error) }
            } catch (_: Exception) {
              promise.reject("E_GOOGLE_SUBSCRIBE", error.message, error)
            }
          }
      } catch (error: Exception) {
        promise.reject("E_GOOGLE_SUBSCRIBE", error.message, error)
      }
    }

    AsyncFunction("readData") { startMs: Double, endMs: Double, promise: Promise ->
      try {
        require(startMs.isFinite() && endMs.isFinite() && startMs > 0 && endMs > startMs)
        val request = LocalDataReadRequest.Builder()
          .read(LocalDataType.TYPE_DISTANCE_DELTA)
          .read(LocalDataType.TYPE_STEP_COUNT_DELTA)
          .setTimeRange(startMs.toLong(), endMs.toLong(), TimeUnit.MILLISECONDS).build()
        client().readData(request).addOnSuccessListener { response ->
          val received = System.currentTimeMillis()
          val points = mutableListOf<Map<String, Any>>()
          for ((type, field, kind) in listOf(
            Triple(LocalDataType.TYPE_DISTANCE_DELTA, LocalField.FIELD_DISTANCE, "distance"),
            Triple(LocalDataType.TYPE_STEP_COUNT_DELTA, LocalField.FIELD_STEPS, "steps"))) {
            for (point in response.getDataSet(type).dataPoints) {
              val value = if (kind == "steps") point.getValue(field).asInt().toDouble()
                else point.getValue(field).asFloat().toDouble()
              points.add(mapOf("kind" to kind, "value" to value,
                "startUnixMs" to point.getStartTime(TimeUnit.MILLISECONDS),
                "endUnixMs" to point.getEndTime(TimeUnit.MILLISECONDS)))
            }
          }
          promise.resolve(mapOf("receivedAtUnixMs" to received, "points" to points))
        }.addOnFailureListener { error -> promise.reject("E_GOOGLE_READ", error.message, error) }
      } catch (error: Exception) {
        promise.reject("E_GOOGLE_READ", error.message, error)
      }
    }

    AsyncFunction("unsubscribe") { promise: Promise ->
      try {
        release().addOnSuccessListener { promise.resolve(null) }
          .addOnFailureListener { error -> promise.reject("E_GOOGLE_UNSUBSCRIBE", error.message, error) }
      } catch (error: Exception) {
        promise.reject("E_GOOGLE_UNSUBSCRIBE", error.message, error)
      }
    }

    OnDestroy { try { release() } catch (_: Exception) { /* No active React context. */ } }
  }
}
