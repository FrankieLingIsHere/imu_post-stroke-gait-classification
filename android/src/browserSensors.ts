import { REQUESTED_HZ, SENSOR_NAMES, SensorName } from './recording';

type Reading = { x:number; y:number; z:number; timestamp:number };
type Sensor = { x:number|null; y:number|null; z:number|null; timestamp:number|null; start():void; stop():void; addEventListener(type:string,fn:()=>void):void; removeEventListener(type:string,fn:()=>void):void };
type Constructor = new (options:{ frequency:number; referenceFrame:'device' }) => Sensor;
const constructors = { accelerometer:'Accelerometer', gyroscope:'Gyroscope', magnetometer:'Magnetometer' } as const;
export type BrowserSensorStatus = { status:'ready'|'unavailable'|'blocked'|'missing'|'slow'|'invalid'; count:number; hz:number };
export type BrowserCheck = { ready:boolean; sensors:Record<SensorName,BrowserSensorStatus> };
const environment = () => globalThis as unknown as Record<string, unknown>;

/** Generic Sensor API only: never derive a magnetometer from compass/orientation angles. */
export function subscribeBrowserSensor(name:SensorName, callback:(r:Reading)=>void, failed:()=>void=()=>{}) {
  const env=environment();
  if (!env.isSecureContext || typeof env[constructors[name]]!=='function') throw new Error('Browser sensor access unavailable.');
  const Ctor=env[constructors[name]] as Constructor;
  const sensor=new Ctor({frequency:REQUESTED_HZ[name],referenceFrame:'device'});
  let removed=false; let previousTimestamp=-Infinity;
  const remove=()=>{if(removed)return;removed=true;sensor.removeEventListener('reading',reading);sensor.removeEventListener('error',error);sensor.stop();};
  const error=()=>{remove();failed();};
  const reading=()=>{
    if(removed)return;
    const {x,y,z,timestamp}=sensor;
    // Invalid readings are visible to the check, but never enter captured streams.
    if(![x,y,z,timestamp].every(v=>typeof v==='number'&&Number.isFinite(v))||timestamp!<0||timestamp!<=previousTimestamp){error();return;}
    previousTimestamp=timestamp!;
    const divisor=name==='accelerometer'?9.80665:1;
    callback({x:x!/divisor,y:y!/divisor,z:z!/divisor,timestamp:timestamp!/1000});
  };
  sensor.addEventListener('reading',reading);sensor.addEventListener('error',error);
  try{sensor.start();}catch(e){remove();throw e;}
  return {remove};
}

/** Three-second measured check; elapsed time alone can never produce a pass. */
export function checkBrowserSensors(signal?:AbortSignal):Promise<BrowserCheck> {
  const statuses=Object.fromEntries(SENSOR_NAMES.map(n=>[n,{status:'missing',count:0,hz:0}])) as BrowserCheck['sensors'];
  const samples=Object.fromEntries(SENSOR_NAMES.map(n=>[n,[]])) as unknown as Record<SensorName,{time:number;received:number}[]>;
  return new Promise(resolve=>{
    const subscriptions:{remove():void}[]=[];
    let timer:ReturnType<typeof setTimeout>|undefined;let finished=false;
    const finish=()=>{
      if(finished)return;finished=true;clearTimeout(timer);signal?.removeEventListener('abort',finish);
      subscriptions.forEach(s=>s.remove());const now=performance.now();
      for(const n of SENSOR_NAMES){
        const rows=samples[n],state=statuses[n];state.count=rows.length;
        if(['unavailable','blocked','invalid'].includes(state.status))continue;
        if(signal?.aborted||rows.length<3||now-rows[rows.length-1].received>500){state.status='missing';continue;}
        const span=rows[rows.length-1].time-rows[0].time;
        state.hz=span>0?(rows.length-1)/span:0;
        const gaps=rows.slice(1).map((r,i)=>r.time-rows[i].time);
        state.status=span>=1.5&&state.hz>=25&&gaps.every(g=>g>0&&g<=.25)?'ready':'slow';
      }
      resolve({ready:SENSOR_NAMES.every(n=>statuses[n].status==='ready'),sensors:statuses});
    };
    if(signal?.aborted){finish();return;}
    signal?.addEventListener('abort',finish,{once:true});
    for(const name of SENSOR_NAMES){
      const env=environment();
      if(!env.isSecureContext||typeof env[constructors[name]]!=='function'){statuses[name].status='unavailable';continue;}
      try{subscriptions.push(subscribeBrowserSensor(name,r=>{
        const rows=samples[name];
        if(rows.length && r.timestamp<=rows[rows.length-1].time){statuses[name].status='invalid';return;}
        if(rows.length<2000)rows.push({time:r.timestamp,received:performance.now()});
      },()=>{statuses[name].status='blocked';}));}catch{statuses[name].status='blocked';}
    }
    timer=setTimeout(finish,3000);
  });
}

export const browserHardware=Object.fromEntries(SENSOR_NAMES.map(name=>[name,{
  setUpdateInterval(_ms:number){/* Requested rates are passed to the constructor. */},
  addListener(callback:(r:Reading)=>void){return subscribeBrowserSensor(name,callback);},
}])) as Record<SensorName,{setUpdateInterval(ms:number):void;addListener(callback:(r:Reading)=>void):{remove():void}}>;
