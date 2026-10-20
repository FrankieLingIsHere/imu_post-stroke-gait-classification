import { assistedNotice } from '../protocolFlow';
import {prepareGaitDistance} from '../gaitDistance';
import {phoneDistanceProfile} from '../onDeviceSetup';
import React, { useEffect, useRef, useState } from 'react';
import { View, Pressable, Switch, AppState, Platform, Modal, TextInput, ScrollView } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours } from '../theme';
import { checkSensors } from '../sensors';
import * as Location from 'expo-location';
import { checkGoogleRecordingPermission } from '../googleRecordingBridge';
import { checkBrowserSensors, BrowserCheck } from '../browserSensors';
import { SENSOR_NAMES } from '../recording';
import { ensureVoice, speak, stopSpeaking } from '../audio';
import { Text, LanguagePicker, useLanguage, t } from '../i18n';
import { getParticipants, saveParticipant, type ParticipantSex, type AssistiveDevice, type ClinicalSide } from '../store';
import { resolveTestParticipant, participantKey, automaticStudyLabel } from '../testParticipant';
import { clinicalIntakeIssue } from '../clinicalIntake';
import { protocolGuides } from '../protocolGuides';
import ProtocolTutorial from '../components/ProtocolTutorial';
import type { AssessmentProtocol, AssessmentSetup, ParticipantProfile } from '../store';

// The lightweight test renderer does not provide TextInput; native builds do.
const AgeInput: React.ComponentType<any> = TextInput ?? View;
export default function PrepareScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Prepare'>) {
  const language = useLanguage();
  const trial=route.params.googleDistanceTrial;
  const [page, setPage] = useState(0);
  const [profiles, setProfiles] = useState<ParticipantProfile[]>([]);
  const [profilesReady, setProfilesReady] = useState(false);
  const newId = useRef(`participant-${Date.now()}-${Math.random().toString(16).slice(2,10)}`);
  const [participantLabel, setParticipantLabel] = useState(route.params.participantLabel ?? automaticStudyLabel([],newId.current));
  const [selectedId, setSelectedId] = useState<string | undefined>(route.params.participantId);
  const [aid, setAid] = useState<AssistiveDevice>(route.params.participantSnapshot?.clinical.assistiveDevice ?? 'none');
  const [menu, setMenu] = useState<'options' | 'participant' | 'saved' | 'tests' | 'clinical' | null>(null);
  const [savedSearch, setSavedSearch] = useState('');
  const [editProfile,setEditProfile]=useState(false);
  const [duration, setDuration] = useState(route.params.duration);
  const [audioEnabled, setAudio] = useState(route.params.audioEnabled);
  const [isPractice, setPractice] = useState(route.params.isPractice);
  const [ageText, setAgeText] = useState(route.params.demographics?.ageYears?.toString() ?? '');
  const [sex, setSex] = useState<ParticipantSex | null>(route.params.demographics?.sex ?? null);
  const [heightText, setHeightText] = useState(route.params.demographics?.heightCm?.toString() ?? '');
  const [weightText,setWeightText]=useState(route.params.participantSnapshot?.demographics.weightKg?.toString() ?? '');
  const [strokeType,setStrokeType]=useState(route.params.participantSnapshot?.clinical.strokeType ?? '');
  const [lesion,setLesion]=useState(route.params.participantSnapshot?.clinical.lesionLocation ?? '');
  const [premorbid,setPremorbid]=useState(route.params.participantSnapshot?.clinical.premorbidGaitNotes ?? '');
  const [orthopaedic,setOrthopaedic]=useState(route.params.participantSnapshot?.clinical.jointOrOrthopaedicNotes ?? '');
  const [protocol, setProtocol] = useState<AssessmentProtocol>(route.params.assessmentSetup?.protocol ?? 'research-walk');
  const [testChosen,setTestChosen]=useState(!!route.params.assessmentSetup || !!trial);
  const [courseText, setCourseText] = useState(route.params.assessmentSetup?.courseLengthM?.toString() ?? '');
  const [hemisphere,setHemisphere]=useState<ClinicalSide|undefined>(route.params.participantSnapshot?.clinical.affectedHemisphere);
  const [affectedSide,setAffectedSide]=useState<ClinicalSide|undefined>(route.params.participantSnapshot?.clinical.affectedBodySide);
  const [chronicityStatus,setChronicityStatus]=useState<'known'|'unknown'|undefined>(route.params.participantSnapshot?.clinical.chronicityStatus ?? (route.params.participantSnapshot?.clinical.monthsSinceStroke != null ? 'known' : undefined));
  const [monthsText,setMonthsText]=useState(route.params.participantSnapshot?.clinical.monthsSinceStroke?.toString() ?? '');
  const [historySource,setHistorySource]=useState<'patient-or-caregiver-report'|'clinician-record'|undefined>(route.params.participantSnapshot?.clinical.historySource);
  const [guidanceEnabled, setGuidance] = useState(true);
  const [useGpsDistance, setUseGpsDistance] = useState(route.params.useGpsDistance ?? false);
  const [useGoogleDistance, setUseGoogleDistance] = useState(route.params.useGoogleDistance ?? false);
  const [useCameraDistance,setUseCameraDistance]=useState(route.params.useCameraDistance??(Platform.OS==='android'&&!trial));
  const [phoneState,setPhoneState]=useState<'checking'|'needed'|'ready'|'error'>(Platform.OS==='android'&&!trial&&useCameraDistance?'checking':'ready');
  const [openInfo, setOpenInfo] = useState<string | null>(null);
  const [guideOpen, setGuideOpen] = useState(false);
  const [defaultsApplied, setDefaultsApplied] = useState(false);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [testing, setTesting] = useState(false);
  const [canSkip, setCanSkip] = useState(true);
  const [error, setError] = useState('');
  const [browserCheck, setBrowserCheck] = useState<BrowserCheck | null>(null);
  const [checkingBrowser, setCheckingBrowser] = useState(false);
  const [sensorConsent, setSensorConsent] = useState(false);
  const browserRequest = useRef<AbortController | null>(null);
  const webReady = Platform.OS === 'web' && browserCheck?.ready === true;
  const guide = protocolGuides[protocol];
  const timer = useRef<ReturnType<typeof setTimeout>>();
  const deadline = useRef<ReturnType<typeof setTimeout>>();
  const active = useRef(true);
  const request = useRef(0);
  const requestingPermissions = useRef(false);
  function stopSample() {
    request.current++; stopSpeaking(); clearTimeout(timer.current); clearTimeout(deadline.current);
    setTesting(false); setCanSkip(true);
  }
  function useDefaults() {
    stopSample(); setDuration(20); setAudio(true); setGuidance(true); setPractice(false);
    setUseGoogleDistance(false);
    setUseCameraDistance(Platform.OS==='android'&&!trial);
    setOpenInfo(null); setError(''); setDefaultsApplied(true);
  }
  useEffect(() => {
    active.current = true; stopSample(); setError('');
    const app = AppState.addEventListener('change', state => { if (state !== 'active'&&!requestingPermissions.current) { stopSample(); browserRequest.current?.abort(); setBrowserCheck(null); } });
    return () => { active.current = false; request.current++; browserRequest.current?.abort(); app.remove(); stopSpeaking(); clearTimeout(timer.current); clearTimeout(deadline.current); };
  }, [language]);
  async function loadProfiles() {
    try { const rows=await getParticipants(); if(active.current){setProfiles(rows);if(!selectedId)setParticipantLabel(label=>label===automaticStudyLabel([],newId.current)?automaticStudyLabel(rows,newId.current):label);setProfilesReady(true);setError('');} }
    catch { if(active.current)setError('Could not load participants. Try again.'); }
  }
  useEffect(()=>{void loadProfiles();},[]);
  useEffect(()=>{
    let mounted=true;
    const refresh=()=>{
      if(Platform.OS!=='android'||trial||!useCameraDistance){setPhoneState('ready');return;}
      void phoneDistanceProfile().then(p=>{if(mounted)setPhoneState(p?'ready':'needed');}).catch(()=>{if(mounted)setPhoneState('error');});
    };
    refresh();const unsubscribe=navigation.addListener?.('focus',refresh);
    return()=>{mounted=false;unsubscribe?.();};
  },[useCameraDistance,trial,navigation]);
  function selectPerson(p: ParticipantProfile) {
    setMenu(null);setEditProfile(false);setSelectedId(p.id);setParticipantLabel(p.label);setAgeText(p.demographics.ageYears?.toString()??'');
    setSex(p.demographics.sex);setHeightText(p.demographics.heightCm?.toString()??'');setAid(p.clinical.assistiveDevice);
    setHemisphere(p.clinical.affectedHemisphere);setAffectedSide(p.clinical.affectedBodySide);
    setChronicityStatus(p.clinical.chronicityStatus ?? (p.clinical.monthsSinceStroke != null ? 'known' : undefined));
    setWeightText(p.demographics.weightKg?.toString()??'');setStrokeType(p.clinical.strokeType);setLesion(p.clinical.lesionLocation);setPremorbid(p.clinical.premorbidGaitNotes);setOrthopaedic(p.clinical.jointOrOrthopaedicNotes);
    setMonthsText(p.clinical.monthsSinceStroke?.toString()??'');setHistorySource(p.clinical.historySource);setError('');
  }
  function participantInput() { return {id:selectedId,newId:newId.current,label:participantLabel,ageYears:ageText.trim()?Number(ageText):null,sex,heightCm:heightText.trim()?Number(heightText):null,assistiveDevice:aid,weightKg:weightText.trim()?Number(weightText):null,strokeType,lesionLocation:lesion,premorbidGaitNotes:premorbid,jointOrOrthopaedicNotes:orthopaedic,
    affectedHemisphere:hemisphere,affectedBodySide:affectedSide,chronicityStatus,monthsSinceStroke:monthsText.trim()?Number(monthsText):null,historySource}; }
  function checkedParticipant(rows:ParticipantProfile[]) {
    const person=resolveTestParticipant(rows,participantInput());
    if(protocol!=='research-walk') {
      const issue=clinicalIntakeIssue(person.clinical);
      if(issue) throw new Error(issue);
    }
    return person;
  }
  function validateCourse() {
    const value=courseText.trim()?Number(courseText):null;
    if(['2mwt','6mwt'].includes(protocol)&&!useCameraDistance&&(!value||!Number.isFinite(value)||value<3||value>100)) throw new Error('Enter a measured course length from 3 to 100 metres.');
    return value;
  }
  function nextPage() {
    try { if(page===0)resolveTestParticipant(profiles,participantInput());else {if(!testChosen)throw new Error('Choose a test to continue.');validateCourse();checkedParticipant(profiles);}stopSample();setError('');setPage(trial&&page===0?2:page+1); }
    catch(e){setError(e instanceof Error?e.message:'Could not load participants. Try again.');}
  }
  async function checkBrowser() {
    browserRequest.current?.abort(); stopSample(); setBrowserCheck(null); setCheckingBrowser(true); setError('');
    const controller = new AbortController(); browserRequest.current = controller;
    try {
      const result = await checkBrowserSensors(controller.signal);
      if (active.current && !controller.signal.aborted) setBrowserCheck(result);
    } finally { if (active.current && browserRequest.current === controller) setCheckingBrowser(false); }
  }
  async function sample() {
    stopSample(); const id = ++request.current;
    setTesting(true); setCanSkip(false); setError('');
    timer.current = setTimeout(() => { if (active.current && id === request.current) setCanSkip(true); }, 2000);
    const finish = (failed = false) => {
      if (!active.current || id !== request.current) return;
      stopSample(); if (failed) setError('Could not play the voice. Check phone speech and volume settings, or use a helper with voice off.');
    };
    deadline.current = setTimeout(() => finish(true), 10000);
    void speak('Hello. Walk only when you hear begin.', { onDone: () => finish(), onError: () => finish(true) });
  }
  async function start() {
    if (busy) return;
    if(Platform.OS==='web'&&!webReady){stopSample();navigation.navigate('Walkthrough',{protocol});return;}
    stopSample(); setBusy(true); setError('');
    const id = ++request.current;
    requestingPermissions.current=true;
    try {
      const currentProfiles=await getParticipants().catch(()=>{throw new Error('Could not load participants. Try again.');});
      const participant=checkedParticipant(currentProfiles);
      await checkSensors();
      if(useCameraDistance&&!trial){try{await prepareGaitDistance();}catch(e){if(e&&typeof e==='object'&&'message' in e&&e.message==='Phone setup changed or has not completed. Set up this phone again.'){setPhoneState('needed');return;}throw e;}}
      if ((!useCameraDistance&&useGoogleDistance)||trial) await checkGoogleRecordingPermission();
      if (useGpsDistance&&!useCameraDistance) {
        if (Platform.OS !== 'android') throw new Error(t('Optional GPS distance is available in the Android app only.'));
        const permission = await Location.requestForegroundPermissionsAsync();
        if (permission.status !== 'granted') throw new Error(t('Location permission was not granted. Turn off GPS distance to continue without it.'));
        const provider = await Location.getProviderStatusAsync();
        if (!provider.locationServicesEnabled) throw new Error(t('Turn on phone location services, or turn off GPS distance to continue.'));
      }
      if(AppState.currentState!=='active')await new Promise<void>((resolve,reject)=>{
        const subscription=AppState.addEventListener('change',state=>{if(state==='active'){clearTimeout(timeout);subscription.remove();resolve();}});
        const timeout=setTimeout(()=>{subscription.remove();reject(new Error('Could not access motion sensors. Please try again.'));},5000);
      });
      requestingPermissions.current=false;
      if (audioEnabled) await ensureVoice();
      const courseLengthM=validateCourse();
      const plannedSeconds=protocol==='2mwt'?120:protocol==='6mwt'?360:protocol==='10mwt'?180:protocol==='tug'?180:duration;
      const setup:AssessmentSetup={protocol,courseLengthM:protocol==='10mwt'?12:protocol==='tug'?3:courseLengthM,timedDistanceM:protocol==='10mwt'?10:null,
        protocolVariant:protocol==='10mwt'?'10mwt-12m-central10m-v1':undefined,trialNumber:null,speedCondition:'comfortable',turnDirection:'self-selected'};
      if (!active.current || id !== request.current || AppState.currentState !== 'active') return;
      await saveParticipant(participant).catch(()=>{throw new Error('Could not save participant. Try again.');});
      if (!active.current || id !== request.current || AppState.currentState !== 'active') return;
      setSelectedId(participant.id);setProfiles([...currentProfiles.filter(p=>p.id!==participant.id),participant]);
      navigation.navigate('Record', { duration:trial?(trial.routePattern==='5m-out-and-back'?90:60):plannedSeconds, audioEnabled, isPractice:trial?true:isPractice, guidanceEnabled:trial?false:guidanceEnabled, useGpsDistance:trial||useCameraDistance?false:useGpsDistance, useGoogleDistance:trial?true:useCameraDistance?false:useGoogleDistance, useCameraDistance:!trial&&useCameraDistance, googleDistanceTrial:trial, participantId:participant.id,participantLabel:participant.label,participantSnapshot:participant,demographics:participant.demographics,assessmentSetup:trial?route.params.assessmentSetup:setup });
    } catch (e) { if (active.current) setError(e instanceof Error ? e.message : 'Could not access motion sensors. Please try again.'); }
    finally { requestingPermissions.current=false;if (active.current) setBusy(false); }
  }
  const toggles: [string, boolean, (v: boolean) => void, string, string][] = [
    ['Voice guidance', audioEnabled, value => { stopSample(); setAudio(value); }, 'About voice guidance', 'Hear setup instructions, the countdown, and start and finish cues without looking at the phone. If off, ask a helper to signal start and finish.'],
    ['Direction reminders', guidanceEnabled, setGuidance, 'About direction reminders', 'Gentle cues may remind you when the phone detects turning. They cannot confirm a straight path. Move comfortably and keep using your usual support.'],
    ['Practice walk', isPractice, setPractice, 'About practice walk', 'Try the same recording flow for your chosen duration. Your recording is still saved and exported, but labelled as practice.'],
  ];
  const matchingProfiles=profiles.filter(p=>!p.archived&&participantKey(p.label).includes(participantKey(savedSearch))).sort((a,b)=>Number(b.favorite)-Number(a.favorite)||a.label.localeCompare(b.label));
  const fieldStyle={minHeight:52,borderWidth:1,borderColor:colours.inputBorder,borderRadius:12,paddingHorizontal:14,fontSize:18,color:colours.textPrimary,backgroundColor:colours.surface};
  const testChoices=<>
      <Text style={ui.label}>Main clinical tests</Text>
      {(['10mwt','tug','2mwt'] as AssessmentProtocol[]).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityLabel={t(value==='10mwt'?'10MWT':value==='tug'?'TUG':'2MWT')} accessibilityState={{selected:protocol===value}} style={[ui.choice,{flex:0,alignItems:'flex-start',gap:8},protocol===value&&ui.selected]} onPress={()=>{setProtocol(value);setTestChosen(true);setMenu(null);}}>
        <Text style={ui.label}>{t(value==='10mwt'?'10MWT':value==='tug'?'TUG':'2MWT')}{protocol===value?' - '+t('Selected'):''}</Text>
        <Text style={ui.caption}>{t(value==='10mwt'?'Walking speed over 10 metres':value==='tug'?'Stand, walk, turn and sit':'Walk for 2 minutes; rests are allowed')}</Text>
        <Text style={ui.caption}>{t(value==='10mwt'?'1 m build-up / 10 m measured / 1 m slow-down':value==='tug'?'Chair / 3 m mark / return to chair':'Measured route / 2-minute timer')}</Text>
      </Pressable>)}
      <Text style={ui.label}>Other tests</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{([['research-walk','Research walk'],['6mwt','6MWT']] as [AssessmentProtocol,string][]).map(([value,name])=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:protocol===value}} style={[ui.choice,{flexBasis:100},protocol===value&&ui.selected]} onPress={()=>{setProtocol(value);setTestChosen(true);setMenu(null);}}><Text style={ui.label}>{t(name)}</Text></Pressable>)}</View>
  </>;
  if(phoneState!=='ready')return <Screen title="Before your first walk" actions={<>{phoneState==='checking'?<BigButton label="Checking phone setup..." disabled/>:<BigButton label={phoneState==='error'?'Retry phone check':'Set up this phone'} icon="›" onPress={()=>{if(phoneState==='error'){setPhoneState('checking');void phoneDistanceProfile().then(p=>setPhoneState(p?'ready':'needed')).catch(()=>setPhoneState('error'));}else navigation.navigate('PhoneSetup');}}/>}{phoneState!=='checking'&&<BigButton label="Record motion only" variant="outline" onPress={()=>{setUseCameraDistance(false);setPhoneState('ready');}}/>}</>}>
    <LanguagePicker />
    <Body>{phoneState==='error'?'Could not check saved phone setup. Try again.':'Set up this phone once before your first distance-tracked walk.'}</Body>
    <Body>Keep the phone in its usual bag. Hold it in front of you before wearing it. We will guide you by voice.</Body>
    <Text style={ui.caption}>Automatic distance needs phone setup. Motion-only recording does not measure distance.</Text>
  </Screen>;
  return <Screen key={page} scrollKey={page+'-'+testChosen+'-'+protocol} title={['Who is walking?','Choose your test','Sound and readiness'][page]} eyebrow={trial?t('Google trial setup {0} of 2').replace('{0}',String(page===0?1:2)):t('Setup {0} of 3').replace('{0}',String(page+1))} actions={<>
      {page<2?<BigButton label="Continue" disabled={(page===0&&!profilesReady)||(page===1&&!testChosen)} onPress={nextPage}/>:<BigButton label={Platform.OS==='web'&&!webReady?'Preview hands-free flow':testing?'Start without sound test':'Start test'} disabled={checkingBrowser||(Platform.OS==='web'&&!webReady?false:!ready||!canSkip)} loading={busy} onPress={start}/>}
  </>}>
    {page>0&&<BigButton label="Previous" labelStyle={{fontSize:18}} style={{minHeight:48,paddingVertical:8}} variant="ghost" disabled={busy} onPress={()=>{stopSample();setError('');setPage(trial?0:page-1);}}/>}
    <BigButton labelStyle={{fontSize:18}} style={{minHeight:48,paddingVertical:8}} label="Language and audio settings" icon="›" variant="outline" onPress={()=>{stopSample();setMenu('options');}} disabled={busy}/>
    {!!error&&<Text accessibilityRole="alert" accessibilityLiveRegion="assertive" style={ui.error}>{error}</Text>}
    {page===1&&testChosen&&!trial&&Platform.OS==='android'&&<View style={ui.row}><View style={ui.fill}><Text style={ui.label}>Phone distance</Text><Text style={ui.caption}>Set up this phone once. Walking tests then track distance on this phone.</Text></View><Switch accessibilityLabel={t('Phone distance')} value={useCameraDistance} onValueChange={v=>{setUseCameraDistance(v);if(v){setUseGoogleDistance(false);setUseGpsDistance(false);}}}/></View>}
    {page===1&&testChosen&&!trial&&useCameraDistance&&<Text style={ui.caption}>Keep the phone in its usual bag, with the front camera uncovered.</Text>}
    {Platform.OS==='web'&&page===0&&<Text style={ui.caption}>Browser profiles and recordings last only for this tab. Export before closing.</Text>}
    {page===0&&<View style={{gap:8}}>
      {!selectedId&&<Text style={ui.caption}>Your study ID is created automatically. Choose a saved person for a repeat test.</Text>}
      {profiles.some(p=>!p.archived)&&<BigButton label="Choose a saved person" variant="outline" onPress={()=>{setSavedSearch('');setMenu('saved');}}/>}
      {!!selectedId&&!editProfile?<><Text style={ui.label}>{participantLabel}</Text><Text style={ui.caption}>Your saved details are ready. Confirm your walking aid, then continue.</Text><View style={[ui.row,{flexWrap:'wrap'}]}>{(['none','single-point-cane','quad-cane','other'] as AssistiveDevice[]).map(value=><BigButton key={value} style={{flexBasis:'44%',flexGrow:1,minHeight:52,paddingVertical:10}} labelStyle={{fontSize:18}} label={value==='none'?'No walking aid':value==='single-point-cane'?'Single-point cane':value==='quad-cane'?'Quad cane':'Other'} variant={aid===value?'primary':'outline'} onPress={()=>setAid(value)}/>)}</View><BigButton label="Edit participant details" variant="outline" onPress={()=>setEditProfile(true)}/></>:<>
      <View style={{gap:4}}><Text style={ui.caption}>Automatic study ID</Text><Text style={ui.label}>{participantLabel}</Text></View>

      <Text style={ui.caption}>{selectedId?'Using a saved participant':'New participant'}</Text>
      <View style={{gap:6}}><Text style={ui.caption}>{t('Age in years')}</Text><AgeInput value={ageText} onChangeText={setAgeText} accessibilityLabel={t('Age in years')} placeholder={t('Age in years')} maxLength={3} keyboardType="number-pad" style={fieldStyle}/></View>
      <Text style={ui.label}>Select one sex option</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{(['female','male','prefer-not-to-say'] as const).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:sex===value}} onPress={()=>setSex(value)} style={[ui.choice,{flexBasis:90},sex===value&&ui.selected]}><Text style={ui.caption}>{sex===value?'● ':'○ '}{t(value==='prefer-not-to-say'?'Prefer not to say':value==='female'?'Female':'Male')}</Text></Pressable>)}</View>
      <BigButton label="Walking aid and health details" variant="outline" icon="›" onPress={()=>setMenu('participant')}/>


      </>}
      {!profilesReady&&<BigButton label="Retry" variant="outline" onPress={()=>void loadProfiles()}/>}
      {Platform.OS==='web'&&<BigButton label="Preview hands-free flow" variant="ghost" onPress={()=>navigation.navigate('Walkthrough',{protocol})}/>}
    </View>}
    {page===1&&!testChosen&&<View style={{gap:10}}><Body>Choose a test to continue.</Body>{testChoices}</View>}
    {page===1&&testChosen&&<View style={{gap:10}}>
      <BigButton label={t('Change test: {0}').replace('{0}',t(protocol==='research-walk'?'Research walk':protocol.toUpperCase()))} icon="›" variant="outline" onPress={()=>setMenu('tests')} accessibilityHint={t('Choose your test')}/>

      {protocol!=='research-walk'&&<BigButton label="Review stroke history" variant="outline" onPress={()=>setMenu('clinical')}/>}
      <Text style={ui.caption}>{guide.short}</Text>
      {protocol!=='research-walk'&&<Text style={ui.caption}>{assistedNotice}</Text>}
      <BigButton label="Show me how" icon="›" variant="outline" onPress={()=>{stopSample();setGuideOpen(true);}}/>
      {guideOpen&&<ProtocolTutorial protocol={protocol} onClose={()=>{stopSpeaking();setGuideOpen(false);}}/>}
      {(protocol==='2mwt'||protocol==='6mwt')&&<View style={{gap:6}}><Text style={ui.caption}>{t('Measured loop length (metres)')}</Text><AgeInput accessibilityLabel={t('Measured course length in metres')} value={courseText} onChangeText={setCourseText} placeholder={t('Measured loop length (metres)')} keyboardType="decimal-pad" style={fieldStyle}/></View>}
    {protocol==='research-walk'&&<View>
      <View style={ui.row}><Text style={[ui.label,ui.fill]}>Recording duration</Text>
        <Pressable accessibilityRole="button" accessibilityLabel={t('About recording duration')} accessibilityState={{ expanded: openInfo === 'duration' }} onPress={() => setOpenInfo(openInfo === 'duration' ? null : 'duration')} style={{ minWidth:48, minHeight:48, alignItems:'center', justifyContent:'center' }}>
          <Text style={{ fontSize:22, fontWeight:'700', color:colours.primary }}>ⓘ</Text>
        </Pressable>
      </View>
    </View>}
    {protocol==='research-walk'&&<View style={ui.row}>{([10,20,30] as const).map(n => <Pressable key={n} accessibilityRole="radio" accessibilityLabel={t(`Walk for ${n} seconds`)} accessibilityState={{ selected: n === duration }} style={[ui.choice, n === duration && ui.selected]} onPress={() => setDuration(n)}><Text style={ui.label}>{n===duration?'● ':'○ '}{t(`${n} sec`)}</Text></Pressable>)}</View>}
    </View>}
    {page===2&&<View style={{gap:10}}>
    {trial&&<Body>{t('Short Google trial · measured route {0} m').replace('{0}',String(trial.referenceDistanceM))}</Body>}
    {trial?.routePattern==='5m-out-and-back'&&<Body>Measure 5 m to the turn mark, then return to the start: 10 m total. This is a Google distance experiment, not a 10MWT.</Body>}
    {audioEnabled ? <><BigButton label={testing ? 'Stop sample' : 'Play voice sample'} variant="outline" onPress={testing ? stopSample : sample} disabled={busy} /><Text style={ui.caption}>Listen briefly, or skip. Voice guidance stays on. Check your media volume first.</Text></> : <Body>Voice is off. Ask a helper to signal start and finish while the phone is secured.</Body>}
    {(Platform.OS!=='web'||webReady)&&<Pressable accessibilityRole="checkbox" accessibilityLabel={t('I can walk without hands-on help, using my usual cane or quad stick if needed. The path is clear and I agree to save movement data.')} accessibilityState={{ checked:ready }} onPress={() => setReady(!ready)} style={[ui.row,{ minHeight:64 }]}><Text style={{ fontSize:28,color:colours.primary }}>{ready ? '☑' : '☐'}</Text><Text style={[ui.caption,ui.fill]}>I can walk without hands-on help, using my usual cane or quad stick if needed. The path is clear and I agree to save movement data.</Text></Pressable>}
    {Platform.OS === 'web' && <View style={{gap:8}}>
      <Text style={ui.caption}>Keep this page visible and the phone unlocked. Browser recordings stay in this tab: export before refreshing or closing. Vibration may be unavailable.</Text>
      <BigButton label={checkingBrowser?'Checking live sensors…':'Check this phone’s sensors'} variant="outline" onPress={()=>setSensorConsent(true)} disabled={busy || checkingBrowser} />
      <Modal visible={sensorConsent} transparent animationType="fade" onRequestClose={()=>setSensorConsent(false)}>
        <View style={{flex:1,backgroundColor:'#0008',justifyContent:'center',padding:24}}>
          <View accessibilityViewIsModal style={{backgroundColor:colours.surface,borderRadius:20,padding:24,gap:16,maxWidth:430,maxHeight:'95%',width:'100%',alignSelf:'center'}}>
            <ScrollView style={{flexGrow:0}} contentContainerStyle={{gap:16}} keyboardShouldPersistTaps="handled">
            <Text style={ui.label}>Allow a sensor check?</Text>
            <Body>We will read acceleration, rotation and magnetic field for three seconds. This is app consent. Your browser controls access and may not show another prompt. Consent cannot enable an unavailable magnetometer.</Body>
            <BigButton label="Agree and check sensors" onPress={()=>{setSensorConsent(false);void checkBrowser();}} />
            <BigButton label="Cancel" variant="outline" onPress={()=>setSensorConsent(false)} />
            </ScrollView>
          </View>
        </View>
      </Modal>
      {browserCheck && <View accessibilityLiveRegion="polite">
        {SENSOR_NAMES.map(name=><View key={name}><Text style={ui.label}>{name === 'accelerometer'?'Accelerometer':name === 'gyroscope'?'Gyroscope':'Magnetometer'}</Text><Text style={ui.caption}>{t(browserCheck.sensors[name].status === 'ready'?'Live readings received':browserCheck.sensors[name].status === 'unavailable'?'Not exposed by this browser':browserCheck.sensors[name].status === 'blocked'?'Permission denied or sensor error':browserCheck.sensors[name].status === 'slow'?'Readings too slow or interrupted':browserCheck.sensors[name].status === 'invalid'?'Invalid sensor timestamps':'No fresh readings')}{' · '}{browserCheck.sensors[name].hz.toFixed(1)} Hz</Text></View>)}
        <Text style={ui.caption}>{webReady?'All three sensors are responding. Start will recheck them before setup.':'All three sensors are required. Preview the steps or use the Android app.'}</Text>
      </View>}
      {webReady && <BigButton label="Preview hands-free flow" variant="ghost" onPress={()=>{stopSample();navigation.navigate('Walkthrough',{protocol});}} disabled={busy} />}
    </View>}
    </View>}

    <Modal visible={menu!==null} animationType="slide" onRequestClose={()=>setMenu(null)}>
      <Screen fullScreen title={menu==='participant'?'More participant details':menu==='clinical'?'Stroke history':menu==='saved'?'Choose a saved person':menu==='tests'?'Choose your test':'Language and audio settings'}
        actions={<BigButton label="Done" onPress={()=>setMenu(null)}/>}>
        {menu==='options'&&<>
          <LanguagePicker/>

    <View style={{ backgroundColor: colours.surface, borderRadius: 18, paddingHorizontal: 12 }}>{toggles.filter(([label])=>!trial||label==='Voice guidance').map(([label,value,setter,infoLabel,explanation]) => <View key={label}>
      <View style={[ui.row,{ minHeight:48 }]}><Text style={[ui.caption,ui.fill]}>{label}</Text>
        <Pressable accessibilityRole="button" accessibilityLabel={t(infoLabel)} accessibilityState={{ expanded: openInfo === label }} onPress={() => setOpenInfo(openInfo === label ? null : label)} style={{ minWidth:48, minHeight:48, alignItems:'center', justifyContent:'center' }}>
          <Text style={{ fontSize:22, fontWeight:'700', color:colours.primary }}>ⓘ</Text>
        </Pressable>
        <Switch accessibilityLabel={t(label)} value={value} onValueChange={setter} trackColor={{ true: colours.primary }} />
      </View>
      {openInfo === label && <Text accessibilityLiveRegion="polite" style={[ui.caption,{ paddingBottom:12 }]}>{explanation}</Text>}
    </View>)}</View>

    {!trial&&<BigButton label="Use default settings" variant="outline" onPress={useDefaults} disabled={busy} accessibilityHint={t('Sets 20 seconds, voice and direction reminders on, and practice off.')} />}
    {!trial&&defaultsApplied && duration === 20 && audioEnabled && guidanceEnabled && !isPractice && <Text accessibilityLiveRegion="polite" style={ui.caption}>Defaults selected: 20 seconds, voice and direction reminders on, practice off. You can still change these settings.</Text>}
    {Platform.OS === 'android' && <View style={{ backgroundColor: colours.surface, borderRadius: 16, padding: 12 }}>
      <Pressable disabled={!!trial} accessibilityRole="checkbox" accessibilityLabel={t('Google distance test · experimental')} accessibilityState={{ checked: !!trial||useGoogleDistance,disabled:!!trial }} onPress={() => {setUseGoogleDistance(v=>!v);setUseCameraDistance(false);}} style={[ui.row,{minHeight:56}]}>
        <Text style={{fontSize:26,color:colours.primary}}>{trial||useGoogleDistance?'☑':'☐'}</Text><Text style={[ui.label,ui.fill]}>Google distance test · experimental</Text>
      </Pressable>
      <Text style={ui.caption}>Compare Google’s on-device distance and steps with this recording. Activity permission is requested before setup. No Google account is needed. Readings may be delayed or missing; they do not stop the test or replace clinical measurements.</Text>
    </View>}
    {!trial&&Platform.OS === 'android' && <View style={{ backgroundColor: colours.surface, borderRadius: 16, padding: 12 }}>
      <Pressable accessibilityRole="checkbox" accessibilityLabel={t('Optional outdoor GPS distance cross-check')} accessibilityState={{ checked: useGpsDistance }} onPress={() => {setUseGpsDistance(v=>!v);setUseCameraDistance(false);}} style={[ui.row,{minHeight:56}]}>
        <Text style={{fontSize:26,color:colours.primary}}>{useGpsDistance?'☑':'☐'}</Text><Text style={[ui.label,ui.fill]}>{t('Optional outdoor GPS distance cross-check')}</Text>
      </Pressable>
      <Text style={ui.caption}>{t('Uses foreground location only after walking begins. Coordinates are not saved or uploaded; only the distance and reported accuracy summary are kept. Best outdoors on a longer route. It may be unreliable indoors or on short tests and is not a clinical measurement.')}</Text>
    </View>}

        </>}
        {menu==='participant'&&<View style={{gap:12}}>
          <BigButton label="Review stroke history" icon="›" variant="outline" onPress={()=>setMenu('clinical')}/>
          <Text style={ui.caption}>Study ID is automatic. Only change it to match an existing study record.</Text>
      <View style={{gap:6}}><Text style={ui.caption}>{t('Study ID or participant label')}</Text><AgeInput value={participantLabel} autoCorrect={false} autoCapitalize="none" maxLength={80} accessibilityLabel={t('Study ID or participant label')} placeholder={t('Study ID or participant label')} style={fieldStyle} onChangeText={(v:string)=>{setParticipantLabel(v);if(selectedId){newId.current=`participant-${Date.now()}-${Math.random().toString(16).slice(2,10)}`;setSelectedId(undefined);setAgeText('');setSex(null);setHeightText('');setAid('none');setHemisphere(undefined);setAffectedSide(undefined);setChronicityStatus(undefined);setMonthsText('');setHistorySource(undefined);setWeightText('');setStrokeType('');setLesion('');setPremorbid('');setOrthopaedic('');}}}/></View>
          <Text style={ui.caption}>Enter measured height if known. It supports a rough distance estimate, not a measured distance. Leave blank rather than guess.</Text>
        <View style={{gap:6}}><Text style={ui.caption}>{t('Height cm (for experimental estimate)')}</Text><AgeInput value={heightText} onChangeText={setHeightText} accessibilityLabel={t('Height in centimetres')} placeholder={t('Height cm (for experimental estimate)')} keyboardType="decimal-pad" style={fieldStyle}/></View>
        <View style={{gap:6}}><Text style={ui.caption}>{t('Weight kg')}</Text><AgeInput value={weightText} onChangeText={setWeightText} accessibilityLabel={t('Weight kg')} placeholder={t('Weight kg')} keyboardType="decimal-pad" style={fieldStyle}/></View>
        <Text style={ui.label}>Usual walking aid</Text>
        <View style={[ui.row,{flexWrap:'wrap'}]}>{([['none','None'],['single-point-cane','Single-point cane'],['quad-cane','Quad cane'],['other','Other']] as const).map(([value,label])=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:aid===value}} onPress={()=>setAid(value)} style={[ui.choice,{flexBasis:120},aid===value&&ui.selected]}><Text style={ui.caption}>{aid===value?'● ':'○ '}{t(label)}</Text></Pressable>)}</View>

        </View>}
        {menu==='clinical'&&<View style={{gap:14}}>
          <Text style={ui.caption}>Use the participant's clinical record when available. Choose Unknown if the answer is not known; do not guess.</Text>
          <Text style={ui.label}>Stroke type (optional)</Text>
          <View style={{gap:6}}><Text style={ui.caption}>{t('Stroke type (optional)')}</Text><AgeInput value={strokeType} onChangeText={setStrokeType} accessibilityLabel={t('Stroke type (optional)')} placeholder={t('Stroke type (optional)')} style={fieldStyle}/></View>
          <Text style={ui.label}>Lesion location (optional)</Text>
          <View style={{gap:6}}><Text style={ui.caption}>{t('Lesion location (optional)')}</Text><AgeInput value={lesion} onChangeText={setLesion} accessibilityLabel={t('Lesion location (optional)')} placeholder={t('Lesion location (optional)')} style={fieldStyle}/></View>
          <Text style={ui.label}>Affected brain hemisphere</Text>
          <View style={[ui.row,{flexWrap:'wrap'}]}>{(['left','right','bilateral','unknown'] as const).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:hemisphere===value}} onPress={()=>setHemisphere(value)} style={[ui.choice,{flexBasis:110},hemisphere===value&&ui.selected]}><Text>{t(value)}</Text></Pressable>)}</View>
          <Text style={ui.label}>Affected body side</Text>
          <View style={[ui.row,{flexWrap:'wrap'}]}>{(['left','right','bilateral','unknown'] as const).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:affectedSide===value}} onPress={()=>setAffectedSide(value)} style={[ui.choice,{flexBasis:110},affectedSide===value&&ui.selected]}><Text>{t(value)}</Text></Pressable>)}</View>
          <Text style={ui.label}>Time since stroke</Text>
          <View style={[ui.row,{flexWrap:'wrap'}]}>{(['known','unknown'] as const).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:chronicityStatus===value}} onPress={()=>setChronicityStatus(value)} style={[ui.choice,{flexBasis:110},chronicityStatus===value&&ui.selected]}><Text>{t(value)}</Text></Pressable>)}</View>
          {chronicityStatus==='known'&&<View style={{gap:6}}><Text style={ui.caption}>{t('Whole months since stroke')}</Text><AgeInput value={monthsText} onChangeText={setMonthsText} accessibilityLabel={t('Whole months since stroke')} placeholder={t('Whole months since stroke')} keyboardType="number-pad" style={fieldStyle}/></View>}
          <Text style={ui.label}>History source</Text>
          <View style={[ui.row,{flexWrap:'wrap'}]}>{([['patient-or-caregiver-report','Patient or caregiver'],['clinician-record','Clinical record']] as const).map(([value,label])=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:historySource===value}} onPress={()=>setHistorySource(value)} style={[ui.choice,{flexBasis:130},historySource===value&&ui.selected]}><Text>{t(label)}</Text></Pressable>)}</View>
          <Text style={ui.label}>Pre-existing gait pattern/asymmetry</Text>
          <View style={{gap:6}}><Text style={ui.caption}>{t('Pre-existing gait pattern/asymmetry')}</Text><AgeInput value={premorbid} onChangeText={setPremorbid} accessibilityLabel={t('Pre-existing gait pattern/asymmetry')} placeholder={t('Pre-existing gait pattern/asymmetry')} style={fieldStyle}/></View>
          <Text style={ui.label}>Joint conditions or orthopaedic history</Text>
          <View style={{gap:6}}><Text style={ui.caption}>{t('Joint conditions or orthopaedic history')}</Text><AgeInput value={orthopaedic} onChangeText={setOrthopaedic} accessibilityLabel={t('Joint conditions or orthopaedic history')} placeholder={t('Joint conditions or orthopaedic history')} style={fieldStyle}/></View>
        </View>}
        {menu==='tests'&&<View style={{gap:12}}>
          {testChoices}
        </View>}
        {menu==='saved'&&<>
          <View style={{gap:6}}><Text style={ui.caption}>{t('Search saved participants')}</Text><AgeInput value={savedSearch} onChangeText={setSavedSearch} accessibilityLabel={t('Search saved participants')} placeholder={t('Search saved participants')} style={fieldStyle}/></View>
          {matchingProfiles.map(p=><BigButton key={p.id} label={p.label} variant="outline" onPress={()=>selectPerson(p)}/>)}
          {matchingProfiles.length===0&&<Text style={ui.caption}>No matching participants</Text>}
        </>}
      </Screen>
    </Modal>
    <Modal visible={openInfo==='duration'} animationType="slide" onRequestClose={()=>setOpenInfo(null)}>
      <Screen fullScreen title="About recording duration" actions={<BigButton label="Done" onPress={()=>setOpenInfo(null)}/>}>
        <Body>Choose 10, 20 or 30 seconds of recording after the countdown. Setup time is extra. You may pause or stop early.</Body>
      </Screen>
    </Modal>
  </Screen>;
}
