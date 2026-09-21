import type { Recording } from './recording';
import { estimateGaitTiming } from './gaitTiming';

/** Alternation descriptor only. Candidate peaks have no verified foot identity. */
export function alternatingTiming(r: Recording) {
  const timing = estimateGaitTiming(r);
  const bouts = timing.bouts.filter(b => b.intervalsSeconds.length >= 10).map(b => {
    // Pair locally, never across pauses; equal numbers in both alternating groups.
    const pairs = Math.floor(b.intervalsSeconds.length / 2);
    const even = b.intervalsSeconds.slice(0,pairs*2).filter((_,i)=>i%2===0);
    const odd = b.intervalsSeconds.slice(0,pairs*2).filter((_,i)=>i%2===1);
    const mean = (x:number[]) => x.reduce((a,v)=>a+v,0)/x.length;
    const a=mean(even),c=mean(odd);
    return { startSeconds:b.eventTimesSeconds[0], pairs,
      alternatingIntervalDifferencePercent:200*Math.abs(a-c)/(a+c),
      firstGroupMeanSeconds:a, secondGroupMeanSeconds:c };
  });
  const pairs=bouts.reduce((n,b)=>n+b.pairs,0);
  return {version:'candidate-alternation-v1',status:pairs?'experimental':'unavailable',
    differencePercent:pairs?bouts.reduce((n,b)=>n+b.alternatingIntervalDifferencePercent*b.pairs,0)/pairs:null,
    pairs,bouts,footIdentity:'unknown',clinicalSymmetry:'undetermined',neurologicalCause:'undetermined',
    definition:'Pair-weighted mean of per-bout 200*abs(mean A - mean B)/(mean A + mean B); groups alternate candidate peak intervals, not labelled feet.',
    limitation:'Missed/double peaks, turns, posture and phone movement can mimic alternation. No normal/abnormal threshold or causal inference. No stance, swing or step-length symmetry claim.'};
}
