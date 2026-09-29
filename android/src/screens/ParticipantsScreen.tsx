import React, { useCallback, useState } from 'react';
import { Pressable, TextInput, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { Text, t } from '../i18n';
import { colours } from '../theme';
import { archiveParticipant, getParticipants, ParticipantProfile, saveParticipant, toggleParticipantFavorite } from '../store';

const Field: React.ComponentType<any> = TextInput ?? View;
const inputStyle = { minHeight: 48, borderWidth: 1, borderColor: colours.border, borderRadius: 12, paddingHorizontal: 12, fontSize: 17, color: colours.textPrimary, backgroundColor: colours.surface };
const aidText = { none: 'None', 'single-point-cane': 'Single-point cane', 'quad-cane': 'Quad cane', other: 'Other' } as const;
export default function ParticipantsScreen({ navigation }: NativeStackScreenProps<RootStackParamList, 'Participants'>) {
  const [profiles, setProfiles] = useState<ParticipantProfile[]>([]);
  const [adding, setAdding] = useState(false);
  const [editingProfile, setEditingProfile] = useState<ParticipantProfile | null>(null);
  const [search, setSearch] = useState('');
  const [label, setLabel] = useState(''); const [age, setAge] = useState(''); const [sex, setSex] = useState<'female'|'male'|'prefer-not-to-say'>('prefer-not-to-say');
  const [height, setHeight] = useState(''); const [weight, setWeight] = useState(''); const [strokeType, setStrokeType] = useState('');
  const [lesion, setLesion] = useState(''); const [months, setMonths] = useState(''); const [aid, setAid] = useState<'none'|'single-point-cane'|'quad-cane'|'other'>('none');
  const [premorbid, setPremorbid] = useState(''); const [orthopaedic, setOrthopaedic] = useState(''); const [error, setError] = useState('');
  const refresh = useCallback(() => { let active = true; void getParticipants().then(v => { if (active) setProfiles(v.filter(p => !p.archived).sort((a,b) => Number(b.favorite)-Number(a.favorite) || a.label.localeCompare(b.label))); }).catch(e => { if (active) setError(e.message); }); return () => { active = false; }; }, []);
  useFocusEffect(refresh);
  const reset = () => { setAdding(false); setEditingProfile(null); setLabel(''); setAge(''); setSex('prefer-not-to-say'); setHeight(''); setWeight(''); setStrokeType(''); setLesion(''); setMonths(''); setAid('none'); setPremorbid(''); setOrthopaedic(''); setError(''); };
  function edit(p: ParticipantProfile) {
    setEditingProfile(p); setAdding(true); setLabel(p.label); setAge(p.demographics.ageYears?.toString() ?? ''); setSex(p.demographics.sex === 'female' || p.demographics.sex === 'male' ? p.demographics.sex : 'prefer-not-to-say'); setHeight(p.demographics.heightCm?.toString() ?? ''); setWeight(p.demographics.weightKg?.toString() ?? ''); setStrokeType(p.clinical.strokeType); setLesion(p.clinical.lesionLocation); setMonths(p.clinical.monthsSinceStroke?.toString() ?? ''); setAid(p.clinical.assistiveDevice); setPremorbid(p.clinical.premorbidGaitNotes); setOrthopaedic(p.clinical.jointOrOrthopaedicNotes); setError('');
  }
  async function create() {
    const number = (value: string) => value.trim() ? Number(value) : null;
    const ageValue=number(age),heightValue=number(height),weightValue=number(weight),monthValue=number(months);
    if (ageValue!==null && (!Number.isInteger(ageValue)||ageValue<1||ageValue>120)) { setError('Enter an age from 1 to 120.'); return; }
    if (heightValue!==null && (!Number.isFinite(heightValue)||heightValue<100||heightValue>230)) { setError('Enter height from 100 to 230 cm.'); return; }
    if (weightValue!==null && (!Number.isFinite(weightValue)||weightValue<20||weightValue>300)) { setError('Enter weight from 20 to 300 kg.'); return; }
    if (monthValue!==null && (!Number.isInteger(monthValue)||monthValue<0||monthValue>1200)) { setError('Enter months since stroke from 0 to 1200.'); return; }
    const all = await getParticipants();
    const now = new Date().toISOString();
    const profile: ParticipantProfile = { id: editingProfile?.id ?? `participant-${Date.now()}-${Math.random().toString(16).slice(2,6)}`, label: label.trim() || editingProfile?.label || `Participant ${String(all.length+1).padStart(3,'0')}`, favorite: editingProfile?.favorite ?? false, archived: false, createdAt: editingProfile?.createdAt ?? now, updatedAt: now,
      demographics: { ageYears: ageValue, sex, heightCm: heightValue, weightKg: weightValue },
      distanceCalibration: editingProfile?.distanceCalibration,
      clinical: { strokeType, lesionLocation: lesion, monthsSinceStroke: monthValue, premorbidGaitNotes: premorbid, jointOrOrthopaedicNotes: orthopaedic, assistiveDevice: aid } };
    await saveParticipant(profile); setProfiles([...all.filter(p=>!p.archived&&p.id!==profile.id),profile].sort((a,b)=>Number(b.favorite)-Number(a.favorite)||a.label.localeCompare(b.label))); reset();
  }
  async function favorite(id: string) { await toggleParticipantFavorite(id); await refresh(); }
  async function archive(id: string) { await archiveParticipant(id); await refresh(); }
  return <Screen title="Participants" eyebrow="STORED ON THIS DEVICE" actions={<>
    <BigButton label={adding ? (editingProfile ? 'Save profile changes' : 'Save participant') : 'Add participant'} onPress={() => adding ? void create() : setAdding(true)} />
    {adding && <BigButton label="Cancel" variant="outline" onPress={reset} />}
    <BigButton label="Progress dashboard" variant="outline" onPress={() => navigation.navigate('Dashboard')} />
    <BigButton label="Back to home" variant="ghost" onPress={() => navigation.popToTop()} />
  </>}>
    <Body>Choose a person to prefill their details, or add a profile. Records stay on this phone.</Body>
    {!adding && profiles.length > 0 && <Field value={search} onChangeText={setSearch} placeholder={t('Search participants by study ID')} accessibilityLabel={t('Search participants by study ID')} style={inputStyle}/>}
    {adding && <Card><Text style={ui.label}>New participant profile</Text>
      <Field value={label} onChangeText={setLabel} placeholder={t('Study ID or display label (optional)')} style={inputStyle}/>
      <View style={ui.row}><Field value={age} onChangeText={setAge} placeholder={t('Age')} keyboardType="number-pad" style={[inputStyle,ui.fill]}/><Field value={height} onChangeText={setHeight} placeholder={t('Height cm')} keyboardType="decimal-pad" style={[inputStyle,ui.fill]}/><Field value={weight} onChangeText={setWeight} placeholder={t('Weight kg')} keyboardType="decimal-pad" style={[inputStyle,ui.fill]}/></View>
      <Text style={ui.caption}>Sex (self-reported)</Text><View style={ui.row}>{(['female','male','prefer-not-to-say'] as const).map(v=><Pressable key={v} style={[ui.choice,sex===v&&ui.selected]} onPress={()=>setSex(v)}><Text>{v==='prefer-not-to-say'?'Prefer not to say':v}</Text></Pressable>)}</View>
      <Field value={strokeType} onChangeText={setStrokeType} placeholder={t('Stroke type (optional)')} style={inputStyle}/><Field value={lesion} onChangeText={setLesion} placeholder={t('Lesion location (optional)')} style={inputStyle}/>
      <Field value={months} onChangeText={setMonths} placeholder={t('Months since stroke')} keyboardType="number-pad" style={inputStyle}/>
      <Text style={ui.caption}>Usual walking aid</Text><View style={[ui.row,{flexWrap:'wrap'}]}>{([['none','None'],['single-point-cane','Single-point cane'],['quad-cane','Quad cane'],['other','Other']] as const).map(([v,name])=><Pressable key={v} style={[ui.choice,aid===v&&ui.selected]} onPress={()=>setAid(v)}><Text>{name}</Text></Pressable>)}</View>
      <Field value={premorbid} onChangeText={setPremorbid} placeholder={t('Pre-existing gait pattern/asymmetry')} style={inputStyle}/><Field value={orthopaedic} onChangeText={setOrthopaedic} placeholder={t('Joint conditions or orthopaedic history')} style={inputStyle}/>
      {!!error&&<Text style={ui.error}>{error}</Text>}
    </Card>}
    {profiles.filter(p=>p.label.toLocaleLowerCase().includes(search.trim().toLocaleLowerCase())).map(p=><Card key={p.id}><View style={ui.row}><Text style={[ui.label,ui.fill]}>{p.label} {p.favorite?'★':''}</Text><Pressable accessibilityRole="button" onPress={()=>void favorite(p.id)}><Text style={ui.label}>{p.favorite?'★':'☆'}</Text></Pressable></View>
      <Body>{p.demographics.ageYears ?? '—'} y · {t(p.demographics.sex==='prefer-not-to-say'?'Prefer not to say':p.demographics.sex[0].toUpperCase()+p.demographics.sex.slice(1))} · {p.demographics.heightCm ?? '—'} cm · {t(aidText[p.clinical.assistiveDevice])}</Body>
      <View style={ui.row}><BigButton style={ui.fill} label="Select for assessment" onPress={()=>navigation.navigate('Prepare',{duration:20,audioEnabled:true,isPractice:false,participantId:p.id,participantLabel:p.label,participantSnapshot:p,demographics:p.demographics})}/><BigButton style={ui.fill} label="Edit" variant="outline" onPress={()=>edit(p)}/><BigButton style={ui.fill} label="Archive" variant="outline" onPress={()=>void archive(p.id)}/></View>
    </Card>)}
    {!profiles.length&&!adding&&<Body>No participant profiles yet. Add a coded study ID to begin.</Body>}
    {!!search&&!profiles.some(p=>p.label.toLocaleLowerCase().includes(search.trim().toLocaleLowerCase()))&&<Body>No participant matches that study ID.</Body>}
  </Screen>;
}
