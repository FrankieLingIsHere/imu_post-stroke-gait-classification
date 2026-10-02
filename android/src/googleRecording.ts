/** Google OS comparison only; never a clinical endpoint or replacement for raw IMU. */
export interface GooglePoint {
  kind: 'distance' | 'steps'; value: number; startUnixMs: number; endUnixMs: number;
}
export interface GoogleRead { receivedAtUnixMs: number; points: GooglePoint[] }
export interface GoogleRecordingBridge {
  availability(): Promise<{ available: boolean; permissionGranted: boolean; playServicesCode: number; minimumPlayServicesVersion: number }>;
  subscribe(): Promise<void>;
  readData(startMs: number, endMs: number): Promise<GoogleRead>;
  unsubscribe(): Promise<void>;
}
export interface GoogleRecordingSummary {
  version: 'google-local-recording-v1'; provider: 'google-recording-api-on-mobile'; sdkVersion: '21.3.0';
  status: 'records-received' | 'no-records' | 'partial' | 'error';
  startUnixMs: number | null; endUnixMs: number | null;
  distanceM: number | null; steps: number | null; meanSpeedMps: number | null;
  distanceCoverageFraction: number;
  boundaryRecordsExcluded: number; invalidRecordsExcluded: number; overlappingRecordsExcluded: number;
  observations: (GooglePoint & { firstReceivedAtUnixMs: number })[];
  polls: { requestedAtUnixMs: number; queryEndUnixMs: number; receivedAtUnixMs: number | null; recordCount: number; error: string | null }[];
  /** Research diagnostics only: a read extending past test end, never included in trial totals. */
  contextObservations?: (GooglePoint & { firstReceivedAtUnixMs: number })[];
  contextPolls?: GoogleRecordingSummary['polls'];
  errors: string[]; clinicallyValidated: false; controlsTestEnd: false;
  subscriptionCleanup: 'pending' | 'complete' | 'failed';
}

export function summarizeGoogleRecords(startUnixMs: number | null, endUnixMs: number | null,
  observations: GoogleRecordingSummary['observations'], polls: GoogleRecordingSummary['polls'], errors: string[],
  subscriptionCleanup: GoogleRecordingSummary['subscriptionCleanup'] = 'pending',
  contextObservations: NonNullable<GoogleRecordingSummary['contextObservations']> = [],
  contextPolls: NonNullable<GoogleRecordingSummary['contextPolls']> = []): GoogleRecordingSummary {
  let boundaryRecordsExcluded = 0, invalidRecordsExcluded = 0, overlappingRecordsExcluded = 0;
  const selected: GoogleRecordingSummary['observations'] = [];
  const seen = new Set<string>();
  for (const point of observations) {
    if (!['distance','steps'].includes(point.kind) || ![point.value,point.startUnixMs,point.endUnixMs,point.firstReceivedAtUnixMs].every(Number.isFinite) || point.value < 0 || point.endUnixMs <= point.startUnixMs || (point.kind === 'steps' && !Number.isInteger(point.value))) { invalidRecordsExcluded++; continue; }
    const key = `${point.kind}:${point.startUnixMs}:${point.endUnixMs}:${point.value}`;
    if (seen.has(key)) continue; seen.add(key);
    if (startUnixMs === null || endUnixMs === null || point.startUnixMs < startUnixMs || point.endUnixMs > endUnixMs) { boundaryRecordsExcluded++; continue; }
    selected.push(point);
  }
  let coveredDistanceMs = 0;
  const total = (kind: GooglePoint['kind']) => {
    const points = selected.filter(p => p.kind === kind).sort((a,b) => a.startUnixMs-b.startUnixMs);
    if (!points.length) return null;
    let end = -Infinity, value = 0;
    for (const p of points) {
      if (p.startUnixMs < end) { overlappingRecordsExcluded++; continue; }
      value += p.value; end = p.endUnixMs;
      if (kind === 'distance') coveredDistanceMs += p.endUnixMs-p.startUnixMs;
    }
    return value;
  };
  const distanceM = total('distance'), steps = total('steps');
  const excluded = boundaryRecordsExcluded + invalidRecordsExcluded + overlappingRecordsExcluded;
  const seconds = startUnixMs !== null && endUnixMs !== null ? (endUnixMs-startUnixMs)/1000 : 0;
  const distanceCoverageFraction = seconds>0 ? Math.min(1,coveredDistanceMs/(seconds*1000)) : 0;
  return { version:'google-local-recording-v1',provider:'google-recording-api-on-mobile',sdkVersion:'21.3.0',
    status:distanceM !== null && steps !== null && distanceCoverageFraction>=0.95 && !excluded && !errors.length ? 'records-received' : distanceM !== null || steps !== null ? 'partial' : errors.length ? 'error' : 'no-records',
    startUnixMs,endUnixMs,distanceM,steps,
    // Partial records cannot establish whole-test speed.
    meanSpeedMps:distanceM !== null && distanceCoverageFraction>=0.95 && !excluded && !errors.length && seconds>0 ? distanceM/seconds : null,
    distanceCoverageFraction,
    boundaryRecordsExcluded,invalidRecordsExcluded,overlappingRecordsExcluded,observations,polls,contextObservations,contextPolls,errors,
    clinicallyValidated:false,controlsTestEnd:false,subscriptionCleanup };
}

function timed<T>(operation: Promise<T>, timeoutMs = 4000): Promise<T> {
  return new Promise((resolve,reject) => {
    const timer = setTimeout(() => reject(new Error('Google Recording API request timed out.')),timeoutMs);
    operation.then(v => { clearTimeout(timer); resolve(v); },e => { clearTimeout(timer); reject(e); });
  });
}
export function validGoogleSummary(value: unknown): value is GoogleRecordingSummary {
  const g = value as GoogleRecordingSummary | null;
  const nullable = (v: unknown) => v === null || (typeof v === 'number' && Number.isFinite(v) && v >= 0);
  return !!g && g.version === 'google-local-recording-v1' && g.provider === 'google-recording-api-on-mobile' && g.sdkVersion === '21.3.0' &&
    ['records-received','no-records','partial','error'].includes(g.status) &&
    [g.startUnixMs,g.endUnixMs,g.distanceM,g.steps,g.meanSpeedMps].every(nullable) &&
    typeof g.distanceCoverageFraction === 'number' && Number.isFinite(g.distanceCoverageFraction) && g.distanceCoverageFraction >= 0 && g.distanceCoverageFraction <= 1 &&
    [g.boundaryRecordsExcluded,g.invalidRecordsExcluded,g.overlappingRecordsExcluded].every(v => Number.isInteger(v) && v >= 0) &&
    g.clinicallyValidated === false && g.controlsTestEnd === false && ['pending','complete','failed'].includes(g.subscriptionCleanup) &&
    Array.isArray(g.errors) && g.errors.length <= 2000 && g.errors.every(e => typeof e === 'string') &&
    Array.isArray(g.observations) && g.observations.length <= 50000 && g.observations.every(p => p && ['distance','steps'].includes(p.kind) && [p.value,p.startUnixMs,p.endUnixMs,p.firstReceivedAtUnixMs].every(v => typeof v === 'number' && Number.isFinite(v))) &&
    Array.isArray(g.polls) && g.polls.length <= 2000 && g.polls.every(p => p && [p.requestedAtUnixMs,p.queryEndUnixMs].every(v => typeof v === 'number' && Number.isFinite(v)) && nullable(p.receivedAtUnixMs) && Number.isInteger(p.recordCount) && p.recordCount >= 0 && (p.error === null || typeof p.error === 'string')) &&
    (g.contextObservations === undefined || (Array.isArray(g.contextObservations) && g.contextObservations.length <= 50000 && g.contextObservations.every(p => p && ['distance','steps'].includes(p.kind) && [p.value,p.startUnixMs,p.endUnixMs,p.firstReceivedAtUnixMs].every(v => typeof v === 'number' && Number.isFinite(v))))) &&
    (g.contextPolls === undefined || (Array.isArray(g.contextPolls) && g.contextPolls.length <= 2000 && g.contextPolls.every(p => p && [p.requestedAtUnixMs,p.queryEndUnixMs].every(v => typeof v === 'number' && Number.isFinite(v)) && nullable(p.receivedAtUnixMs) && Number.isInteger(p.recordCount) && p.recordCount >= 0 && (p.error === null || typeof p.error === 'string'))));
}
export class GoogleRecordingCapture {
  private start: number | null = null;
  private stop: number | null = null;
  private observations: GoogleRecordingSummary['observations'] = [];
  private polls: GoogleRecordingSummary['polls'] = [];
  private contextObservations: NonNullable<GoogleRecordingSummary['contextObservations']> = [];
  private contextPolls: NonNullable<GoogleRecordingSummary['contextPolls']> = [];
  private errors: string[] = [];
  private busy: Promise<void> | null = null;
  private timer: ReturnType<typeof setInterval> | null = null;
  private closed = false;
  private ready = false;
  private cleanup: GoogleRecordingSummary['subscriptionCleanup'] = 'pending';
  constructor(private bridge: GoogleRecordingBridge, private now = Date.now) {}
  async prepare() {
    try {
      // A late subscribe must be followed by cleanup if the screen was cancelled.
      const subscribing = this.bridge.subscribe();
      subscribing.then(() => { if (this.closed) void this.cancel(); }, () => {});
      await timed(subscribing);
      if (!this.closed) this.ready = true;
    } catch (e) { this.errors.push(e instanceof Error ? e.message : String(e)); }
  }
  begin(startUnixMs: number) {
    if (this.closed || this.start !== null) return;
    this.start = startUnixMs;
    this.timer = setInterval(() => { void this.poll(this.now()); },2000);
  }
  private async poll(endUnixMs: number) {
    if (!this.ready || this.start === null || endUnixMs <= this.start || this.closed) return;
    if (this.busy) return this.busy;
    const poll = { requestedAtUnixMs:this.now(),queryEndUnixMs:endUnixMs,receivedAtUnixMs:null as number|null,recordCount:0,error:null as string|null };
    this.polls.push(poll);
    this.busy = (async () => {
      try {
        const read = await timed(this.bridge.readData(this.start!,endUnixMs));
        poll.receivedAtUnixMs = read.receivedAtUnixMs; poll.recordCount = read.points.length;
        for (const p of read.points) {
          if (!this.observations.some(old => old.kind===p.kind && old.startUnixMs===p.startUnixMs && old.endUnixMs===p.endUnixMs && old.value===p.value))
            this.observations.push({...p,firstReceivedAtUnixMs:read.receivedAtUnixMs});
        }
      } catch (e) { poll.error = e instanceof Error ? e.message : String(e); this.errors.push(poll.error); }
    })().finally(() => { this.busy = null; });
    return this.busy;
  }
  private async pollContext(endUnixMs: number) {
    if (!this.ready || this.start === null || this.stop === null || endUnixMs <= this.stop || this.closed) return;
    const poll = { requestedAtUnixMs:this.now(),queryEndUnixMs:endUnixMs,receivedAtUnixMs:null as number|null,recordCount:0,error:null as string|null };
    this.contextPolls.push(poll);
    try {
      const read = await timed(this.bridge.readData(this.start,endUnixMs));
      poll.receivedAtUnixMs = read.receivedAtUnixMs; poll.recordCount = read.points.length;
      for (const p of read.points) {
        if (!this.contextObservations.some(old => old.kind===p.kind && old.startUnixMs===p.startUnixMs && old.endUnixMs===p.endUnixMs && old.value===p.value))
          this.contextObservations.push({...p,firstReceivedAtUnixMs:read.receivedAtUnixMs});
      }
    } catch (e) { poll.error = e instanceof Error ? e.message : String(e); }
  }
  async finish(endUnixMs: number, extendedObservation = false): Promise<GoogleRecordingSummary> {
    if (this.timer) clearInterval(this.timer); this.timer = null; this.stop = endUnixMs;
    // Fixed test window: observe delayed records without including later walking.
    if (this.busy) await this.busy;
    await this.poll(endUnixMs);
    if (this.ready && this.start !== null) {
      const waits = extendedObservation?[2000,3000,5000,10000,10000]:[2000];
      for (let index=0; index<waits.length; index++) {
        await new Promise<void>(resolve => setTimeout(resolve,waits[index]));
        if(this.closed)break;
        if(extendedObservation && index===waits.length-1)
          await Promise.all([this.poll(endUnixMs),this.pollContext(this.now())]);
        else await this.poll(endUnixMs);
        const summary=summarizeGoogleRecords(this.start,this.stop,this.observations,this.polls,this.errors);
        if(extendedObservation&&summary.status==='records-received')break;
      }
    }
    await this.cancel();
    return summarizeGoogleRecords(this.start,this.stop,this.observations,this.polls,this.errors,this.cleanup,this.contextObservations,this.contextPolls);
  }
  async cancel() {
    this.closed = true;
    if (this.timer) clearInterval(this.timer); this.timer = null;
    try { await timed(this.bridge.unsubscribe()); this.cleanup = 'complete'; }
    catch (e) { this.cleanup = 'failed'; this.errors.push(e instanceof Error ? e.message : String(e)); }
  }
}
