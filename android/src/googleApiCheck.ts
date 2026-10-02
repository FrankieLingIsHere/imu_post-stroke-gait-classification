import type { GoogleRecordingBridge, GoogleRead } from './googleRecording';

export interface GoogleApiCheck {
  version:'google-api-check-v1'; startedAt:string; finishedAt:string;
  availability:'passed'|'failed'; subscription:'passed'|'failed'|'not-run';
  reads:{windowSeconds:number;startUnixMs:number;endUnixMs:number;receivedAtUnixMs:number|null;recordCount:number|null;error:string|null}[];
  cleanup:'passed'|'failed'|'not-run'; apiAccess:'passed'|'failed';
  recordsAvailable:boolean; errors:string[];
}
function bounded<T>(promise:Promise<T>):Promise<T>{
  return new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('Google API request timed out.')),4000);
    promise.then(value=>{clearTimeout(timer);resolve(value);},error=>{clearTimeout(timer);reject(error);});});
}
const message=(e:unknown)=>e instanceof Error?e.message:String(e);
/** Connection check only. Context records are never attributed to a gait trial. */
export async function checkGoogleApi(bridge:GoogleRecordingBridge,now=Date.now):Promise<GoogleApiCheck>{
  const result:GoogleApiCheck={version:'google-api-check-v1',startedAt:new Date(now()).toISOString(),finishedAt:'',availability:'failed',subscription:'not-run',reads:[],cleanup:'not-run',apiAccess:'failed',recordsAvailable:false,errors:[]};
  let attempted=false;
  try{
    const status=await bounded(bridge.availability());
    if(!status.available||!status.permissionGranted)throw new Error('Google API availability or activity permission check failed.');
    result.availability='passed';attempted=true;
    // If subscribe resolves after its timeout, release that late registration too.
    const subscription=bridge.subscribe();
    let expired=false;
    subscription.then(()=>{if(expired)void bridge.unsubscribe().catch(()=>{});},()=>{});
    try{await bounded(subscription);result.subscription='passed';}
    catch(e){expired=true;result.subscription='failed';throw e;}
    for(const windowSeconds of [60,600]){
      const endUnixMs=now(),startUnixMs=endUnixMs-windowSeconds*1000;
      const read={windowSeconds,startUnixMs,endUnixMs,receivedAtUnixMs:null as number|null,recordCount:null as number|null,error:null as string|null};
      result.reads.push(read);
      try{
        const response:GoogleRead=await bounded(bridge.readData(startUnixMs,endUnixMs));
        if(!Number.isFinite(response.receivedAtUnixMs)||!Array.isArray(response.points))throw new Error('Google API returned an invalid response.');
        read.receivedAtUnixMs=response.receivedAtUnixMs;read.recordCount=response.points.length;
      }catch(e){read.error=message(e);result.errors.push(read.error);}
    }
  }catch(e){result.errors.push(message(e));}
  finally{
    if(attempted){try{await bounded(bridge.unsubscribe());result.cleanup='passed';}catch(e){result.cleanup='failed';result.errors.push(message(e));}}
    result.finishedAt=new Date(now()).toISOString();
  }
  result.apiAccess=result.availability==='passed'&&result.subscription==='passed'&&result.reads.length===2&&result.reads.every(r=>r.error===null)&&result.cleanup==='passed'?'passed':'failed';
  result.recordsAvailable=result.reads.some(r=>(r.recordCount??0)>0);
  return result;
}
