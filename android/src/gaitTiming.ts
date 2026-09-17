import type { Recording, Sample } from './recording';
import { motionWindow } from './movement';

const SETTINGS = { resampleHz:50, maxGapSeconds:.1, minIntervalSeconds:.3, maxIntervalSeconds:2,
  highPassHz:.3, lowPassHz:3, minProminenceG:.025, prominenceSdMultiplier:.35, minBoutEvents:4, edgeSeconds:.3 };
type Feature = { value:number|null; unit:string; status:string; definition:string; reason:string|null };
const definitions: Record<string, [string,string]> = {
  step_count:['steps','Number of candidate step peaks retained in accepted bouts; not total verified steps.'],
  cadence:['steps/min','60 times total within-bout interval count divided by total within-bout interval duration. Pauses between bouts excluded.'],
  candidate_bout_duration:['s','Sum of first-to-last candidate event spans in accepted bouts; excludes boundary portions, not full walking duration.'],
  step_time_mean:['s','Mean successive candidate-event interval within bouts.'],
  step_time_sd:['s','Sample SD (n−1) of successive candidate-event intervals within bouts.'],
  step_time_cv:['fraction','Sample SD / mean of successive candidate-event intervals within bouts; includes changes of pace.'],
};
const mean = (a:number[]) => a.reduce((s,x)=>s+x,0)/a.length;
const sd = (a:number[]) => { const average=mean(a); return Math.sqrt(a.reduce((s,x)=>s+(x-average)**2,0)/(a.length-1)); };

/** Offline experimental peak estimator, not a published/validated gait-event implementation. */
export function estimateGaitTiming(r:Recording) {
  const features:Record<string,Feature> = Object.fromEntries(Object.entries(definitions).map(([name,[unit,definition]]) => [name,{value:null,unit,definition,status:'unavailable',reason:'No supported candidate bout.'}]));
  const bouts:{eventTimesSeconds:number[]; intervalsSeconds:number[]; cadence:number}[]=[];
  const excluded:{startSeconds:number;endSeconds:number;reason:string}[]=[];
  const result = {version:'phone-step-peaks-v1', status:'unavailable', clinicalValidation:false,
    eventMeaning:'Candidate acceleration peaks, not verified heel strikes. Side and toe-off are unknown.',
    timingBasis:r.platform==='web'?'Browser Sensor.timestamp converted to seconds and mapped to recording elapsed seconds using the first accelerometer sample. Browser timing is not validated against native capture.':'Native sensor seconds mapped to recording elapsed seconds using the first accelerometer sample.',
    processing:'Linear interpolation to 50 Hz within gaps <=100 ms; keep full one-second combined-movement windows; acceleration magnitude minus bidirectionally smoothed 0.3 Hz baseline, then bidirectional 3 Hz exponential smoothing. Local prominence peaks with 300 ms separation; split intervals above 2 s. Nominal filter settings, not Butterworth cutoffs.',
    boundaryPolicy:'Exclude 300 ms at each supported-run boundary and incomplete final one-second windows. Count is partial, not a full-session step count.',
    settings:SETTINGS, features,bouts,excluded,
    limitations:['Periodic phone handling can mimic steps. Slow/shuffling or low-amplitude steps may be missed.',
      'Peak timing is not validated contact timing. No left/right, stance, swing, asymmetry, speed or diagnostic estimate.',
      'Partial bout counts and timing are not directly comparable with annotation-assisted healthy-reference features.']};
  const fail=(reason:string)=>{for(const f of Object.values(features))f.reason=reason;return result;};
  if(r.guidanceEvents.some(e=>e.type==='possible-placement-shift'))return fail('Placement-shift flag; timing withheld.');
  const a=r.streams.accelerometer,g=r.streams.gyroscope;
  const valid=(rows:Sample[])=>rows.length>=2 && rows.every((s,i)=>s.sensorTimestampSeconds!==null && Number.isFinite(s.sensorTimestampSeconds) && [s.x,s.y,s.z,s.elapsedMs].every(Number.isFinite) && (!i || s.sensorTimestampSeconds!>rows[i-1].sensorTimestampSeconds!));
  if(!valid(a)||!valid(g))return fail('Finite acceleration/gyro values and strictly increasing native timestamps required.');
  if([a,g].some(rows=>(rows.length-1)/(rows[rows.length-1].sensorTimestampSeconds!-rows[0].sensorTimestampSeconds!)<25))return fail('At least 25 Hz observed native sampling required for acceleration and gyro.');
  const origin=a[0].sensorTimestampSeconds!-a[0].elapsedMs/1000;
  const time=(s:Sample)=>s.sensorTimestampSeconds!-origin;
  const end=Math.min(r.elapsedSeconds,time(a[a.length-1]),time(g[g.length-1]));
  const start=Math.max(0,time(a[0]),time(g[0]));
  if(!Number.isFinite(end)||end-start<4)return fail('At least four seconds of overlapping native-timed streams required.');
  const interpolate=(rows:Sample[],t:number,index:{v:number}):Sample|null=>{
    while(index.v+1<rows.length && time(rows[index.v+1])<t)index.v++;
    const x=rows[index.v],y=rows[index.v+1];
    if(!y || t<time(x)-1e-8 || t>time(y)+1e-8 || time(y)-time(x)>SETTINGS.maxGapSeconds)return null;
    const w=(t-time(x))/(time(y)-time(x));
    return {x:x.x+w*(y.x-x.x),y:x.y+w*(y.y-x.y),z:x.z+w*(y.z-x.z),elapsedMs:t*1000,receivedAtUnixMs:0,sensorTimestampSeconds:t+origin};
  };
  const ai={v:0},gi={v:0};
  let run:{t:number;v:number}[]=[];
  const process=()=>{
    if(run.length<SETTINGS.resampleHz*2){if(run.length)excluded.push({startSeconds:run[0].t,endSeconds:run[run.length-1].t,reason:'Too short for peak detection.'});run=[];return;}
    const smooth=(values:number[],hz:number)=>{
      const alpha=1-Math.exp(-2*Math.PI*hz/SETTINGS.resampleHz);
      const pass=(v:number[])=>{let last=v[0];return v.map(x=>last=last+alpha*(x-last));};
      return pass(pass(values).reverse()).reverse();
    };
    const raw=run.map(x=>x.v),base=smooth(raw,SETTINGS.highPassHz);
    const filtered=smooth(raw.map((x,i)=>x-base[i]),SETTINGS.lowPassHz);
    const threshold=Math.max(SETTINGS.minProminenceG,SETTINGS.prominenceSdMultiplier*sd(filtered));
    const candidates:number[]=[];
    for(let i=1;i<filtered.length-1;i++){
      if(run[i].t-run[0].t<SETTINGS.edgeSeconds || run[run.length-1].t-run[i].t<SETTINGS.edgeSeconds)continue;
      if(filtered[i]<=filtered[i-1] || filtered[i]<filtered[i+1])continue;
      const radius=Math.round(.25*SETTINGS.resampleHz);
      const left=Math.min(...filtered.slice(Math.max(0,i-radius),i)),right=Math.min(...filtered.slice(i+1,Math.min(filtered.length,i+radius+1)));
      if(filtered[i]-Math.max(left,right)<threshold)continue;
      const last=candidates[candidates.length-1];
      if(last!==undefined && run[i].t-run[last].t<SETTINGS.minIntervalSeconds){if(filtered[i]>filtered[last])candidates[candidates.length-1]=i;}
      else candidates.push(i);
    }
    let events:number[]=[];
    const flush=()=>{
      if(events.length>=SETTINGS.minBoutEvents){const intervals=events.slice(1).map((t,i)=>t-events[i]);bouts.push({eventTimesSeconds:events,intervalsSeconds:intervals,cadence:60/mean(intervals)});}
      else if(events.length)excluded.push({startSeconds:events[0],endSeconds:events[events.length-1],reason:'Fewer than four candidate events.'});
      events=[];
    };
    for(const i of candidates){const t=run[i].t;if(events.length && t-events[events.length-1]>SETTINGS.maxIntervalSeconds)flush();events.push(t);}
    flush();if(!candidates.length)excluded.push({startSeconds:run[0].t,endSeconds:run[run.length-1].t,reason:'No peaks above prominence threshold.'});run=[];
  };
  for(let t=start;t+1<=end+1e-8;t+=1){
    const aa:Sample[]=[],gg:Sample[]=[];
    for(let i=0;i<SETTINGS.resampleHz;i++){const tt=t+i/SETTINGS.resampleHz,x=interpolate(a,tt,ai),y=interpolate(g,tt,gi);if(x)aa.push(x);if(y)gg.push(y);}
    const motion=motionWindow(aa,gg);
    if(aa.length!==50||gg.length!==50||motion.context!=='movement'){
      process();excluded.push({startSeconds:t,endSeconds:t+1,reason:aa.length!==50||gg.length!==50?'Missing samples or native gap above 100 ms.':motion.context});continue;
    }
    run.push(...aa.map(s=>({t:s.elapsedMs/1000,v:Math.hypot(s.x,s.y,s.z)})));
  }
  process();
  const tail=start+Math.floor(end-start+1e-8);
  if(tail<end)excluded.push({startSeconds:tail,endSeconds:end,reason:'Partial final one-second window excluded.'});
  if(start>0)excluded.push({startSeconds:0,endSeconds:start,reason:'No overlapping native streams at start.'});
  if(end<r.elapsedSeconds)excluded.push({startSeconds:end,endSeconds:r.elapsedSeconds,reason:'No overlapping native streams at end.'});
  const intervals=bouts.flatMap(b=>b.intervalsSeconds);
  if(!intervals.length)return fail('No accepted candidate step bout; no verified zero-step claim.');
  const duration=intervals.reduce((sum,x)=>sum+x,0),avg=mean(intervals),deviation=sd(intervals);
  const values:Record<string,number>={step_count:bouts.reduce((n,b)=>n+b.eventTimesSeconds.length,0),cadence:60*intervals.length/duration,candidate_bout_duration:duration,step_time_mean:avg,step_time_sd:deviation,step_time_cv:deviation/avg};
  for(const [name,value] of Object.entries(values))features[name]={...features[name],value,status:'experimental-estimate',reason:null};
  result.status='experimental-estimate';return result;
}
