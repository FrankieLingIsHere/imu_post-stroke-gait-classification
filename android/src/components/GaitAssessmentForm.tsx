import React,{useState} from 'react';
import { View,Text,TextInput,Pressable } from 'react-native';
import { Screen,Card,ui } from './Screen';
import BigButton,{type BigButtonProps} from './BigButton';
import { colours } from '../theme';
import { gaitRubric } from '../gaitRubric';
import { gaitAssessmentSummary,gaitQualifiers,type GaitAssessment } from '../gaitAssessment';

// User-agreed language policy: original instrument and worker UI in English.
const Button=(props:BigButtonProps)=><BigButton {...props} style={{minHeight:48,paddingVertical:10,...props.style}} labelStyle={{fontSize:18,...props.labelStyle}} translateLabel={false}/>;
const fieldStyle={minHeight:48,borderWidth:1,borderColor:colours.border,borderRadius:12,padding:12,fontSize:17,color:colours.textPrimary};
export default function GaitAssessmentForm({value:form,onChange,onSave,onBack,saving,error,notice}: {
  value:GaitAssessment;onChange:(v:GaitAssessment)=>void;onSave:()=>Promise<boolean>;onBack:()=>void;saving:boolean;error:string;notice:string;
}){
  const initial=gaitAssessmentSummary(form);
  const [page,setPage]=useState(initial.metadataComplete&&!initial.complete?(initial.missingItems[0]??1)-1:-1),[review,setReview]=useState(initial.complete),[branch,setBranch]=useState('');
  const summary=gaitAssessmentSummary(form),item=gaitRubric[Math.max(0,page)];
  const rating=form.ratings[String(item.id)]??{optionId:null,notes:''};
  const set=(patch:Partial<GaitAssessment>)=>{if(!saving)onChange({...form,...patch});};
  const rate=(patch:Partial<typeof rating>)=>set({ratings:{...form.ratings,[item.id]:{...rating,...patch}}});
  const branches=[...new Set(item.options.map(o=>o.branch).filter(Boolean))];
  const selectedBranch=item.options.find(o=>o.id===rating.optionId)?.branch;
  const activeBranch=branch||selectedBranch||branches[0];
  const go=(next:number)=>{setPage(next);setBranch('');setReview(false);};
  const phase=item.phase==='stance-and-swing'?'Observe during stance and swing':item.phase==='stance'?'Observe during stance: assessed foot on the ground':'Observe during swing: assessed foot off the ground';
  const field=(key:'assessor'|'assessedAt'|'diagnosis'|'deviceOrthosisAssist'|'videoReference',label:string)=><View key={key} style={{gap:4}}><Text style={ui.caption}>{label}</Text><TextInput editable={!saving} accessibilityLabel={label} value={form[key]} onChangeText={v=>set({[key]:v})} style={fieldStyle}/></View>;
  return <Screen title={review?'Review assessment':page<0?'Assessor details':`${item.id}. ${item.title}`} eyebrow="G.A.I.T. • ENGLISH" translateTitle={false} scrollKey={`${page}-${review}-${activeBranch}`} actions={<>
    {!review&&<View style={ui.row}><Button style={ui.fill} label={page<0?'Save & back':'Previous item'} variant="outline" disabled={saving} onPress={()=>page<0?void onSave().then(ok=>{if(ok)onBack();}):go(page-1)}/><Button style={ui.fill} label={page===30?'Review assessment':page<0?'Begin items':'Next item'} disabled={saving} onPress={()=>page===30?setReview(true):go(page+1)}/></View>}
    <View style={ui.row}><Button style={ui.fill} label="Save draft" variant="outline" loading={saving} onPress={()=>void onSave()}/><Button style={ui.fill} label={review?'Return to item':'Overview'} variant="outline" disabled={saving} onPress={()=>setReview(!review)}/></View>
    {review&&<Button label="Finish assessment" disabled={!summary.complete||saving} loading={saving} onPress={()=>void onSave().then(ok=>{if(ok)onBack();})}/>}
  </>}>
    <Text style={ui.caption}>Items rated: {summary.rated} of 31</Text>
    <Text style={ui.label}>{summary.total===null?'Total unavailable until all items and assessor details are complete.':`G.A.I.T. total: ${summary.total} / 62`}</Text>
    {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
    {!!notice&&<Text accessibilityLiveRegion="polite" style={ui.caption}>{notice}</Text>}
    {review?<>
      <Text style={ui.caption}>Review in the same order as the paper form. Tap any item to edit. Missing observations remain unresolved; never guess a score.</Text>
      <Button label="Edit assessor details" variant="outline" onPress={()=>go(-1)}/>
      <Button label="Save & close" variant="outline" disabled={saving} onPress={()=>void onSave().then(ok=>{if(ok)onBack();})}/>
      {!summary.complete&&<Text style={ui.error}>Pending: check all 31 ratings, required directions, assessor, valid date, assessed limb and observation source.</Text>}
      {gaitRubric.map(i=>{const r=form.ratings[String(i.id)],o=i.options.find(o=>o.id===r?.optionId);return <Pressable key={i.id} accessibilityRole="button" accessibilityLabel={`Review item ${i.id}: ${i.title}`} onPress={()=>go(i.id-1)} style={[ui.choice,{flexGrow:0,flexShrink:0,flexBasis:'auto',alignItems:'flex-start'}]}><Text style={ui.label}>{i.id}. {i.title}</Text><Text style={ui.caption}>{o?`Score ${o.score}${o.branch?' • '+o.branch:''}${r?.qualifiers?.length?' • '+r.qualifiers.join(', '):''}${summary.missingItems.includes(i.id)?' • Required directions missing':''}`:'Missing / not assessable'}</Text></Pressable>;})}
    </>:page<0?<>
      <Text style={ui.caption}>Required for each real gait recording. A trained observer completes the supplied 31-item, 62-point Appendix A. The phone does not assign clinical scores.</Text>
      <Text style={ui.caption}>This clinical form uses the original English criteria. Save a draft to pause and resume; raw data is already saved.</Text>
      {field('assessor','Assessor ID or initials')}{field('assessedAt','Assessment date (YYYY-MM-DD)')}
      <Text style={ui.label}>Limb assessed</Text><View style={ui.row}>{(['left','right'] as const).map(v=><Button key={v} style={ui.fill} label={v} variant={form.limb===v?'primary':'outline'} onPress={()=>set({limb:v})}/>)}</View>
      <Text style={ui.label}>Observation source</Text><View style={ui.row}>{([['in-person','In-person observation'],['video','Video observation']] as const).map(([v,label])=><Button key={v} style={ui.fill} label={label} variant={form.observationSource===v?'primary':'outline'} onPress={()=>set({observationSource:v})}/>)}</View>
      {field('diagnosis','Diagnosis for this assessment')}{field('deviceOrthosisAssist','Device, orthosis or assistance used')}{field('videoReference','Video reference or filename')}
    </>:<Card>
      <Text style={ui.label}>{phase}</Text><Text style={ui.caption}>Assess {form.limb??'the selected'} limb. Select the matching original criterion.</Text>
      {branches.length>1&&<><Text style={ui.caption}>Choose the applicable branch before rating. Each branch preserves the original scoring criteria.</Text><View style={[ui.row,{flexWrap:'wrap'}]}>{branches.map(b=><Button key={b} style={{flexBasis:'45%',flexGrow:1}} label={`Branch ${b}`} variant={activeBranch===b?'primary':'outline'} onPress={()=>setBranch(b)}/>)}</View></>}
      {item.options.filter(o=>!o.branch||o.branch===activeBranch).map(o=><Pressable key={o.id} disabled={saving} accessibilityRole="radio" aria-checked={rating.optionId===o.id} accessibilityState={{selected:rating.optionId===o.id}} accessibilityLabel={`${o.branch} ${o.score}: ${o.text}`} onPress={()=>rate({optionId:o.id})} style={[ui.choice,{flexGrow:0,flexShrink:0,flexBasis:'auto',alignItems:'flex-start'},rating.optionId===o.id&&ui.selected]}><Text style={ui.label}>Score {o.score}</Text><Text style={ui.caption}>{o.text}</Text></Pressable>)}
      <Button label="Not observed / not assessable" variant={rating.optionId===null?'primary':'outline'} onPress={()=>rate({optionId:null})}/>
      {!!gaitQualifiers(item.id).length&&<><Text style={ui.caption}>For an abnormal rating, select the observed directions or positions.</Text><View style={[ui.row,{flexWrap:'wrap'}]}>{gaitQualifiers(item.id).map(q=><Pressable key={q} disabled={saving} accessibilityRole="checkbox" aria-checked={rating.qualifiers?.includes(q)??false} accessibilityLabel={q} accessibilityState={{checked:rating.qualifiers?.includes(q)??false}} style={[ui.choice,rating.qualifiers?.includes(q)&&ui.selected]} onPress={()=>{const opposite:Record<string,string>={flexion:'extension',extension:'flexion',right:'left',left:'right'};rate({qualifiers:rating.qualifiers?.includes(q)?rating.qualifiers.filter(v=>v!==q):[...(rating.qualifiers??[]).filter(v=>v!==opposite[q]),q]});}}><Text>{q}</Text></Pressable>)}</View></>}
      <Text style={ui.caption}>Item observation notes / reason it cannot be assessed</Text><TextInput editable={!saving} accessibilityLabel="Item observation notes" value={rating.notes} onChangeText={v=>rate({notes:v})} multiline style={fieldStyle}/>
    </Card>}
  </Screen>;
}
