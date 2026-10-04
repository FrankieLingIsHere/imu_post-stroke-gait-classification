import React,{useState} from 'react';
import { View,TextInput,Pressable } from 'react-native';
import { Text,t,useLanguage } from '../i18n';
import { ui,Body } from './Screen';
import BigButton from './BigButton';
import { colours } from '../theme';
import { gaitRubric } from '../gaitRubric';
import { newGaitAssessment,gaitAssessmentSummary,gaitQualifiers,type GaitAssessment } from '../gaitAssessment';

const Field: React.ComponentType<any> = TextInput ?? View;
const style={minHeight:48,borderWidth:1,borderColor:colours.border,borderRadius:12,padding:12,fontSize:17};
export default function GaitAssessmentForm({value,onChange}:{value?:GaitAssessment;onChange:(v:GaitAssessment)=>void}){
  const language=useLanguage();
  const [page,setPage]=useState(0),[open,setOpen]=useState(!!value);
  const form=value??newGaitAssessment(),summary=gaitAssessmentSummary(form),item=gaitRubric[page];
  const rating=form.ratings[String(item.id)]??{optionId:null,notes:''};
  const set=(patch:Partial<GaitAssessment>)=>onChange({...form,...patch});
  const rate=(patch:Partial<typeof rating>)=>set({ratings:{...form.ratings,[item.id]:{...rating,...patch}}});
  return <View style={{gap:12}}>
    <BigButton label={open?'Close item-by-item G.A.I.T. form':'Open item-by-item G.A.I.T. form'} variant="outline" onPress={()=>{if(!open&&!value)onChange(form);setOpen(!open);}}/>
    {open&&<>
      <Body>Observer-entered G.A.I.T.: 31 items, maximum 62. Use a trained assessor; the phone does not score these items.</Body>
      <Body>Original scoring criteria are shown in English. Interface translations are not validated translations of the clinical instrument.</Body>
      <Text style={ui.caption}>{t('Items rated: {0} of 31').replace('{0}',String(summary.rated))}</Text>
      <Text style={ui.label}>{summary.total===null?t('Total unavailable until all items and assessor details are complete.'):t('G.A.I.T. total: {0} / 62').replace('{0}',String(summary.total))}</Text>
      {(['assessor','assessedAt','diagnosis','deviceOrthosisAssist','videoReference'] as const).map((key,i)=><Field key={key} accessibilityLabel={t(['Assessor ID or initials','Assessment date (YYYY-MM-DD)','Diagnosis for this assessment','Device, orthosis or assistance used','Video reference or filename'][i])} placeholder={t(['Assessor ID or initials','Assessment date (YYYY-MM-DD)','Diagnosis for this assessment','Device, orthosis or assistance used','Video reference or filename'][i])} value={form[key]} onChangeText={(v:string)=>set({[key]:v})} style={style}/>)}
      <Text style={ui.label}>Limb assessed</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{(['left','right'] as const).map(v=><BigButton key={v} label={v} variant={form.limb===v?'primary':'outline'} onPress={()=>set({limb:v})}/>)}</View>
      <Text style={ui.label}>Observation source</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{([['in-person','In-person observation'],['video','Video observation']] as const).map(([v,label])=><BigButton key={v} label={label} variant={form.observationSource===v?'primary':'outline'} onPress={()=>set({observationSource:v})}/>)}</View>
      <Text style={ui.label}>{item.id}. {language==='en'?item.title:t(`G.A.I.T. item ${item.id}`)}</Text>
      <BigButton label="Not observed / not assessable" variant={rating.optionId===null?'primary':'outline'} onPress={()=>rate({optionId:null})}/>
      {item.options.map(o=><Pressable key={o.id} accessibilityRole="radio" accessibilityLabel={`${o.branch} ${o.score}: ${o.text}`} accessibilityState={{selected:rating.optionId===o.id}} onPress={()=>rate({optionId:o.id})} style={[ui.choice,rating.optionId===o.id&&ui.selected,{padding:12}]}><Text>{o.branch?`${o.branch} — `:''}{o.score}: {o.text}</Text></Pressable>)}
      {!!gaitQualifiers(item.id).length&&<><Text style={ui.caption}>Select observed directions or positions for an abnormal rating.</Text><View style={[ui.row,{flexWrap:'wrap'}]}>{gaitQualifiers(item.id).map(q=><Pressable key={q} accessibilityRole="checkbox" accessibilityLabel={t(q)} accessibilityState={{checked:rating.qualifiers?.includes(q)??false}} onPress={()=>{
        const opposite:Record<string,string>={flexion:'extension',extension:'flexion',right:'left',left:'right'};
        rate({qualifiers:rating.qualifiers?.includes(q)?rating.qualifiers.filter(v=>v!==q):[...(rating.qualifiers??[]).filter(v=>v!==opposite[q]),q]});
      }} style={[ui.choice,rating.qualifiers?.includes(q)&&ui.selected]}><Text>{t(q)}</Text></Pressable>)}</View></>}
      <Field accessibilityLabel={t('Item observation notes')} placeholder={t('Item observation notes')} value={rating.notes} onChangeText={(v:string)=>rate({notes:v})} multiline style={style}/>
      <View style={ui.row}><BigButton style={ui.fill} label="Previous item" disabled={page===0} variant="outline" onPress={()=>setPage(page-1)}/><BigButton style={ui.fill} label="Next item" disabled={page===30} onPress={()=>setPage(page+1)}/></View>
      <Body>Save the assessment below to keep these item ratings with this recording.</Body>
    </>}
  </View>;
}
