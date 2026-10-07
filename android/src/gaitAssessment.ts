import { gaitRubric, GAIT_FORM_VERSION } from './gaitRubric';

export interface GaitAssessment {
  version: typeof GAIT_FORM_VERSION;
  assessor: string;
  assessedAt: string;
  limb: 'left' | 'right' | null;
  diagnosis: string;
  deviceOrthosisAssist: string;
  observationSource: 'in-person' | 'video' | null;
  videoReference: string;
  ratings: Record<string, { optionId: string | null; notes: string; qualifiers?: string[] }>;
}
export function newGaitAssessment(): GaitAssessment {
  return { version: GAIT_FORM_VERSION, assessor:'', assessedAt:new Date().toISOString().slice(0,10), limb:null,
    diagnosis:'', deviceOrthosisAssist:'', observationSource:null, videoReference:'', ratings:{} };
}
/** Incomplete/unobservable items never become normal zeroes or a prorated total. */
export function gaitAssessmentSummary(form: GaitAssessment) {
  let rated=0, subtotal=0, detailsComplete=true;
  const missingItems:number[]=[];
  for (const item of gaitRubric) {
    const option=item.options.find(o=>o.id===form.ratings[String(item.id)]?.optionId);
    let itemComplete=!!option;
    if(option){rated++;subtotal+=option.score;
      const flags=form.ratings[String(item.id)]?.qualifiers??[];
      if(option.score>0){
        const flex=flags.includes('flexion')||flags.includes('extension'),side=flags.includes('right')||flags.includes('left');
        if(item.id===1&&!flags.length)itemComplete=false;
        if([5,19].includes(item.id)&&!flex)itemComplete=false;
        if([6,20].includes(item.id)&&!side)itemComplete=false;
        if(item.id===4&&((option.score===1&&!flex)||(option.score===2&&!side)||(option.score===3&&(!flex||!side))))itemComplete=false;
      }
    }
    if(!itemComplete){missingItems.push(item.id);detailsComplete=false;}
  }
  const validDate=/^\d{4}-\d{2}-\d{2}$/.test(form.assessedAt)&&Number.isFinite(Date.parse(form.assessedAt))&&new Date(form.assessedAt).toISOString().slice(0,10)===form.assessedAt;
  const complete=rated===31 && detailsComplete && !!form.assessor.trim() && !!form.limb && !!form.observationSource && validDate;
  const metadataComplete=!!form.assessor.trim()&&!!form.limb&&!!form.observationSource&&validDate;
  return {rated,subtotal,total:complete?subtotal:null,maximum:62,complete,missingItems,metadataComplete};
}
export function validGaitAssessment(value: unknown): value is GaitAssessment {
  const f=value as GaitAssessment;
  if(!f||f.version!==GAIT_FORM_VERSION||!f.ratings||typeof f.ratings!=='object'||Array.isArray(f.ratings)||
    ![null,'left','right'].includes(f.limb)||![null,'in-person','video'].includes(f.observationSource))return false;
  for(const key of ['assessor','assessedAt','diagnosis','deviceOrthosisAssist','videoReference'] as const)
    if(typeof f[key]!=='string'||f[key].length>2000)return false;
  return Object.entries(f.ratings).every(([id,r])=>{
    const item=gaitRubric.find(i=>String(i.id)===id);
    const choices=gaitQualifiers(Number(id));
    return !!item&&!!r&&typeof r.notes==='string'&&r.notes.length<=4000&&(r.optionId===null||item.options.some(o=>o.id===r.optionId))&&
      (r.qualifiers===undefined||(Array.isArray(r.qualifiers)&&r.qualifiers.every(v=>choices.includes(v))&&new Set(r.qualifiers).size===r.qualifiers.length&&
        !(r.qualifiers.includes('left')&&r.qualifiers.includes('right'))&&!(r.qualifiers.includes('flexion')&&r.qualifiers.includes('extension'))));
  });
}
export function gaitQualifiers(itemId:number):string[]{
  if(itemId===1)return ['depressed','elevated','retracted','protracted'];
  if(itemId===4)return ['flexion','extension','right','left'];
  if([5,19].includes(itemId))return ['flexion','extension'];
  if([6,20].includes(itemId))return ['right','left'];
  return [];
}

/** Worker-label completeness, not sensor quality or clinical validation. */
export function gaitReviewStatus(session: { isPractice?:boolean; googleDistanceTrial?:unknown; assessment?:{gaitAssessment?:GaitAssessment} }) {
  const form=session.assessment?.gaitAssessment;
  const summary=form?gaitAssessmentSummary(form):null;
  const required=!session.isPractice&&!session.googleDistanceTrial;
  const complete=!!form&&validGaitAssessment(form)&&!!summary?.complete;
  return {required,complete,rated:summary?.rated??0,status:required?(complete?'complete':'pending'):'not-required',labelledAnalysisReady:required&&complete};
}
export function orderGaitReviews<T extends {date:string;isPractice?:boolean;googleDistanceTrial?:unknown;assessment?:{gaitAssessment?:GaitAssessment}}>(sessions:T[]):T[] {
  return [...sessions].sort((a,b)=>Number(gaitReviewStatus(b).status==='pending')-Number(gaitReviewStatus(a).status==='pending')||b.date.localeCompare(a.date));
}
