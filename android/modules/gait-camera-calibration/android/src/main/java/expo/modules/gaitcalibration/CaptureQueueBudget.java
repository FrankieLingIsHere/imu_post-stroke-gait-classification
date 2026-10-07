package expo.modules.gaitcalibration;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/** Bounded acquisition backlog and observed clocks; no invented uniform samples. */
public final class CaptureQueueBudget {
  private final int maxFrames,maxSensors;
  private final AtomicInteger frames=new AtomicInteger(),sensors=new AtomicInteger();
  private final AtomicInteger peakFrames=new AtomicInteger(),peakSensors=new AtomicInteger();
  private final AtomicLong droppedFrames=new AtomicLong(),rejectedSensors=new AtomicLong();
  private long firstCamera=-1,lastCamera=-1,cameraCount=0,firstSaved=-1,lastSaved=-1,savedCount=0;
  private long maxCallbackDelay=0,maxQueueDelay=0,maxProcessing=0;
  public CaptureQueueBudget(int maxFrames,int maxSensors){
    if(maxFrames<1||maxSensors<1)throw new IllegalArgumentException("Invalid capture queue limits");
    this.maxFrames=maxFrames;this.maxSensors=maxSensors;
  }
  private static boolean reserve(AtomicInteger count,AtomicInteger peak,int maximum){
    for(;;){int old=count.get();if(old>=maximum)return false;
      if(count.compareAndSet(old,old+1)){peak.accumulateAndGet(old+1,Math::max);return true;}}
  }
  public boolean reserveFrame(){boolean ok=reserve(frames,peakFrames,maxFrames);if(!ok)droppedFrames.incrementAndGet();return ok;}
  public boolean reserveSensor(){boolean ok=reserve(sensors,peakSensors,maxSensors);if(!ok)rejectedSensors.incrementAndGet();return ok;}
  public void releaseFrame(){if(frames.decrementAndGet()<0)throw new IllegalStateException("Unbalanced frame queue");}
  public void releaseSensor(){if(sensors.decrementAndGet()<0)throw new IllegalStateException("Unbalanced sensor queue");}
  public synchronized void camera(long timestamp){if(timestamp>lastCamera){if(firstCamera<0)firstCamera=timestamp;lastCamera=timestamp;cameraCount++;}}
  public synchronized void saved(long timestamp){if(timestamp<=lastSaved)throw new IllegalArgumentException("Nonmonotonic frame clock");if(firstSaved<0)firstSaved=timestamp;lastSaved=timestamp;savedCount++;}
  public synchronized void timing(long callbackDelay,long queueDelay,long processing){
    maxCallbackDelay=Math.max(maxCallbackDelay,Math.max(0,callbackDelay));
    maxQueueDelay=Math.max(maxQueueDelay,Math.max(0,queueDelay));
    maxProcessing=Math.max(maxProcessing,Math.max(0,processing));
  }
  private double rate(long count,long first,long last){return count>1&&last>first?(count-1)*1e9/(last-first):0;}
  public synchronized Map<String,Number> snapshot(){
    Map<String,Number> out=new LinkedHashMap<>();
    out.put("cameraMetadataFrames",cameraCount);out.put("savedFrames",savedCount);
    out.put("cameraMetadataHz",rate(cameraCount,firstCamera,lastCamera));out.put("savedCameraHz",rate(savedCount,firstSaved,lastSaved));
    out.put("droppedImageCallbacks",droppedFrames.get());out.put("rejectedSensorCallbacks",rejectedSensors.get());
    out.put("pendingFrames",frames.get());out.put("pendingSensors",sensors.get());
    out.put("peakPendingFrames",peakFrames.get());out.put("peakPendingSensors",peakSensors.get());
    out.put("maxImageCallbackLatencyMs",maxCallbackDelay/1e6);out.put("maxQueueLatencyMs",maxQueueDelay/1e6);out.put("maxFrameProcessingMs",maxProcessing/1e6);
    return out;
  }
}
