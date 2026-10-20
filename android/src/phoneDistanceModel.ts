import {distanceBindingKeys,distanceGeometry,type GaitCameraDistance} from './gaitDistanceModel';
type State=Record<string,number>;
const norm=(v:number[])=>Math.hypot(...v);
const pos=(s:State)=>[s.px,s.py,s.pz];
const delta=(a:number[],b:number[])=>a.map((v,i)=>v-b[i]);
const dot=(a:number[],b:number[])=>a.reduce((sum,v,i)=>sum+v*b[i],0);
function horizontal(rows:State[],geometry:string):number|null{
 const p=rows.map(s=>[s.px,s.py]),times=rows.map(s=>s.imu_time_s);
 if(geometry==='straight'){
  const d=delta(p[p.length-1],p[0]),distance=norm(d);
  // Near-stationary trajectories cannot establish a direction; retain a strict spread bound.
  if(distance<=.05)return p.every(v=>norm(delta(v,p[0]))<=.25)?distance:null;
  const axis=d.map(v=>v/distance),along=p.map(v=>dot(delta(v,p[0]),axis));
  const lateral=Math.max(...p.map((v,i)=>norm(delta(delta(v,p[0]),axis.map(x=>x*along[i])))));
  return Math.max(...along)-Math.min(...along)-distance>.25||lateral>Math.max(.25,.15*distance)?null:distance;
 }
 let left=0,right=0;const sum=[0,0];
 const smooth=p.map((_,i)=>{while(right<p.length&&times[right]<=times[i]+.175){sum[0]+=p[right][0];sum[1]+=p[right++][1];}while(left<right&&times[left]<times[i]-.175){sum[0]-=p[left][0];sum[1]-=p[left++][1];}return sum.map(v=>v/(right-left));});
 smooth[0]=p[0];smooth[smooth.length-1]=p[p.length-1];const selected=[0];
 for(let i=1;i<p.length-1;i++)if(times[i]-times[selected[selected.length-1]]>=.35)selected.push(i);
 selected.push(p.length-1);return selected.slice(1).reduce((sum,index,i)=>sum+norm(delta(smooth[index],smooth[selected[i]])),0);
}
/** Same full-route gate as the computer pilot; never scales to a supplied distance. */
export function assessPhoneStates(rows:State[],start:number,end:number,captureEnd:number,geometry:string){
 const ready=rows.filter(r=>r.initialized===1),walk=ready.filter(r=>r.imu_time_s>=start&&r.imu_time_s<=end);
 const result:any={experimentalSegmentMetres:null,completeRouteEstimateMetres:null,reason:'not-initialized',fullRouteCovered:false,initializedFrames:ready.length,walkingFrames:walk.length};
 if(walk.length<2)return result;
 const fail=(reason:string)=>({...result,completeRouteEstimateMetres:null,fullRouteCovered:false,reason});
 if(rows.some((r,i)=>!Number.isFinite(r.imu_time_s)||i>0&&r.imu_time_s<=rows[i-1].imu_time_s))return fail('tracking-integrity-failed');
 const relevant=rows.filter(r=>r.imu_time_s>=start-.2&&r.imu_time_s<=end);
 const keys=['imu_time_s','px','py','pz','vx','vy','vz','ba_norm','bg_norm','tic_norm','g_norm','rotation_change_deg'];
 if(relevant.some(r=>r.reboot===1)||rows[rows.length-1].initialized!==1||walk.some((r,i)=>keys.some(k=>!Number.isFinite(r[k]))||('position_std_m' in r&&(!Number.isFinite(r.position_std_m)||r.position_std_m>.15||r.position_std_m<0))||norm([r.vx,r.vy,r.vz])>3||r.ba_norm>1||r.bg_norm>.2||r.tic_norm>.25||r.g_norm<9.3||r.g_norm>10.3||r.rotation_change_deg>20||i>0&&(r.imu_time_s<=walk[i-1].imu_time_s||r.imu_time_s-walk[i-1].imu_time_s>.2)))return fail('tracking-integrity-failed');
 const continuous=ready.filter(r=>r.imu_time_s>=start-.2&&r.imu_time_s<=captureEnd);
 let maxRate=0;
 for(let i=1;i<continuous.length;i++){const dt=continuous[i].imu_time_s-continuous[i-1].imu_time_s,rate=norm(delta(pos(continuous[i]),pos(continuous[i-1])))/dt;if(dt<=0||dt>.2||!Number.isFinite(rate)||rate>3)return fail('tracking-integrity-failed');maxRate=Math.max(maxRate,rate);}
 result.maxPoseDisplacementRateMetresPerSecond=maxRate;
 const segment=horizontal(walk,geometry);if(segment===null)return fail('route-geometry-mismatch');
 Object.assign(result,{experimentalSegmentMetres:segment,reason:'partial-route',firstTrackedWalkSeconds:walk[0].imu_time_s-start,lastTrackedWalkSeconds:walk[walk.length-1].imu_time_s-start});
 const before=ready.filter(r=>r.imu_time_s>=start-.2&&r.imu_time_s<=start),allWalk=rows.filter(r=>r.imu_time_s>=start-.15&&r.imu_time_s<=end);
 if(before.length&&allWalk.every(r=>r.initialized===1)&&end-walk[walk.length-1].imu_time_s<=.2){const full=horizontal([before[before.length-1],...walk],geometry);if(full===null)return fail('route-geometry-mismatch');Object.assign(result,{completeRouteEstimateMetres:full,fullRouteCovered:true,reason:'experimental-complete-route'});}
 const tail=ready.filter(r=>r.imu_time_s>=end&&r.imu_time_s<=captureEnd);
 if(tail.length>=2){const drift=Math.max(...tail.map(r=>norm([r.px-tail[0].px,r.py-tail[0].py])));if(!Number.isFinite(drift))return fail('tracking-integrity-failed');result.standingDriftMetres=drift;if(drift>.15)return fail('standing-drift');}
 return result;
}
/** Interpolate only within an accepted adjacent pair; never bridge a tracking gap. */
function endBoundaryRows(rows:State[],end:number):State[]|null{
 const after=rows.findIndex(r=>r.imu_time_s>end);
 if(rows.some(r=>r.imu_time_s===end))return rows;
 if(after<1)return null;
 const a=rows[after-1],b=rows[after],dt=b.imu_time_s-a.imu_time_s;
 if(dt<=0||dt>.2||a.initialized!==1||b.initialized!==1||a.reboot===1||b.reboot===1)return null;
 const f=(end-a.imu_time_s)/dt,at:State={...a,imu_time_s:end};
 for(const key of ['px','py','pz','vx','vy','vz'])at[key]=a[key]+f*(b[key]-a[key]);
 at.position_std_m=Math.max(a.position_std_m??0,b.position_std_m??0);
 at.reboot=b.reboot;
 return [...rows.slice(0,after),at,...rows.slice(after)];
}
function centralZone(rows:State[],start:number,end:number,integrity:any,boundaries?:any,live=false){
 const z:any={status:'unavailable',accelerationMetres:1,timedDistanceMetres:10,decelerationMetres:1,timedZoneSeconds:null,speedMps:null,startOffsetSeconds:null,endOffsetSeconds:null,clinicalOutcomeVerified:false,boundarySource:'estimated-trajectory-crossings'};
 if(!integrity.fullRouteCovered)return z;
 const ready=rows.filter(r=>r.initialized===1&&r.imu_time_s>=start-.2&&r.imu_time_s<=end),before=ready.filter(r=>r.imu_time_s<=start);if(!before.length)return z;
 if(live){
  // The native monitor owns the origin, axis and all three crossings. Verify against
  // accepted recorded poses; never replace them with a post-hoc endpoint direction.
  const q=boundaries,o=q?.origin,u=q?.axis;
  if(q?.version!=='ten-metre-boundaries-v1'||q.usable!==true||![o,u].every(v=>Array.isArray(v)&&v.length===2&&v.every(Number.isFinite))||Math.abs(norm(u)-1)>1e-6)return z;
  const times=[q.startBootNs,q.timedStartBootNs,q.timedEndBootNs,q.finishBootNs].map(v=>v/1e9);
  if(times.some(v=>!Number.isFinite(v))||Math.abs(times[0]-start)>1e-6||Math.abs(times[3]-end)>1e-6||times.some((v,i)=>i>0&&v<=times[i-1])||norm(delta(o,pos(before[before.length-1]).slice(0,2)))>1e-7)return z;
  const route=[{...before[before.length-1],imu_time_s:start},...ready.filter(r=>r.imu_time_s>start)],along=route.map(r=>dot(delta(pos(r).slice(0,2),o),u));
  const marks=[1,11,12];
  for(let index=0;index<marks.length;index++){
   const mark=marks[index];
   let crossing:number|null=null;
   for(let i=0;i<route.length-1;i++)if(along[i]<mark&&along[i+1]>=mark-1e-7&&along[i+1]>along[i]){crossing=route[i].imu_time_s+(mark-along[i])/(along[i+1]-along[i])*(route[i+1].imu_time_s-route[i].imu_time_s);break;}
   if(crossing===null||Math.abs(crossing-times[index+1])>1e-6)return z;
  }
  return {...z,status:'experimental',timedZoneSeconds:times[2]-times[1],speedMps:10/(times[2]-times[1]),startOffsetSeconds:times[1]-start,endOffsetSeconds:times[2]-start,boundaryVersion:q.version,origin:o,axis:u};
 }
 if(integrity.completeRouteEstimateMetres<12)return z;
 const route=[before[before.length-1],...ready.filter(r=>r.imu_time_s>start)],first=pos(route[0]).slice(0,2),d=delta(pos(route[route.length-1]).slice(0,2),first),axis=d.map(v=>v/norm(d));
 const along=route.map(r=>dot(delta(pos(r).slice(0,2),first),axis));
 const crossing=(mark:number)=>{for(let i=0;i<along.length-1;i++)if(along[i]<mark&&along[i+1]>=mark)return route[i].imu_time_s+(mark-along[i])/(along[i+1]-along[i])*(route[i+1].imu_time_s-route[i].imu_time_s);return null;};
 const a=crossing(1),b=crossing(11);return a===null||b===null||b<=a?z:{...z,status:'experimental',timedZoneSeconds:b-a,speedMps:10/(b-a),startOffsetSeconds:a-start,endOffsetSeconds:b-start};
}
export function phoneDistanceResult(raw:any,pending:GaitCameraDistance){
 const m=raw?.manifest,ref=raw?.reference;
 const live=raw?.processingRevision==='android-openvins-live-v1';
 if(raw?.processingLocation!=='phone'||(!live&&raw.processingRevision!=='android-vins-fixed-rows-quiet-v1')||(live&&ref?.kind!=='phone-on-device-camera-imu-profile-v1')||!Array.isArray(raw.states)||raw.states.length>30000||m?.sessionId!==pending.sessionId||m?.captureId!==pending.captureId||m?.protocol!==pending.protocol||ref?.sourceSha256!==pending.referenceSha256||distanceBindingKeys.some(k=>m[k]!==pending.binding[k]))throw new Error('The camera distance result does not match this recording.');
 const start=m.diagnostics.walkStartedBootNs/1e9,end=m.diagnostics.walkEndedBootNs/1e9,geometry=distanceGeometry(pending.protocol);
 const validBoundary=Number.isFinite(start)&&end>start&&end<=raw.captureEndSeconds;
 const trajectory=live?endBoundaryRows(raw.states,end):raw.states;
 const integrity=validBoundary&&trajectory?assessPhoneStates(trajectory,start,end,raw.captureEndSeconds,geometry):{experimentalSegmentMetres:null,completeRouteEstimateMetres:null,reason:validBoundary?'tracking-integrity-failed':'boundary-unavailable',fullRouteCovered:false};
 return {schemaVersion:1,kind:'gait-camera-distance-result-v1',method:live?'openvins-on-device-live-v1':'vins-mono-on-device-v1',sessionId:pending.sessionId,captureId:pending.captureId,protocol:pending.protocol,sourceSha256:raw.sourceSha256,referenceCalibrationSha256:ref.sourceSha256,binding:pending.binding,
  distanceReady:false,independentDistanceValidation:false,groundTruthUsedToSetScale:false,clinicalOutcomeVerified:false,referenceDistanceMetres:null,errorMetres:null,errorPercent:null,
  routeGeometry:geometry,distanceMethod:geometry==='straight'?'horizontal-endpoint-displacement':'smoothed-horizontal-trajectory-350ms',walkBoundarySource:m.diagnostics.endBoundarySource,boundaryInterpolation:live?'adjacent-tracked-poses-at-saved-end-time':'none',
  ...integrity,intervalSeconds:end>start?end-start:null,meanSpeedMps:integrity.fullRouteCovered?integrity.completeRouteEstimateMetres/(end-start):null,
  calibration:{method:ref.method,computerUsed:ref.computerUsed===true,numericalCalibrationReady:ref.numericalCalibrationReady===true,geometryConversion:ref.geometryConversion??null,fixedLensK3:ref.fit?.fixedLensK3??null,referenceReviewRequired:ref.sourceReference?.reviewRequired??[]},
  testOutcome:pending.protocol==='10mwt'?centralZone(trajectory??[],start,end,integrity,m.diagnostics.tenMetreBoundaries,live):null,speedScope:'whole-protocol-capture-including-rests',
  software:live?{openvinsCommit:'69488123ed9362dd44b6f28e7f4680abbff1442b',frontend:'openvins-native-klt',processing:{revision:raw.processingRevision,fixedTimeRowCorrection:false,rollingShutterCorrection:'measured-midpoint-gyro-rotational-row-compensation-v1',quietInitializationRequired:true,location:'phone',live:true}}:{vinsCommit:'90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d',frontend:'android-cpp-lk-fb-calibrated-f-v1',processing:{revision:raw.processingRevision,fixedTimeRowCorrection:true,quietInitializationRequired:true,location:'phone',solverIterations:8,solverDeadlineSeconds:3600}},
  noise:{source:raw.noiseSource,profileSha256:raw.noiseProfileSha256,randomWalkValidated:false},initialization:{startBootNs:raw.initializationStartNs,baselineAdaptation:raw.baselineAdaptation},compute:{processingSeconds:raw.processingSeconds,gpuUsed:false},
  limitations:live?['Distance accuracy is not independently validated','Rotational row compensation does not model translational rolling shutter distortion','Estimated zone crossings are not verified floor crossings']:['Experimental distance; not independently validated','Post-capture phone processing; no live distance stopping','Estimated zone crossings are not verified floor crossings']};
}
