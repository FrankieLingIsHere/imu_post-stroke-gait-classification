import React, { useEffect, useRef, useState } from 'react';
import { View, Pressable, Switch, AppState, Platform, Modal, TextInput, ScrollView } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours } from '../theme';
import { checkSensors } from '../sensors';
import * as Location from 'expo-location';
import { checkBrowserSensors, BrowserCheck } from '../browserSensors';
import { SENSOR_NAMES } from '../recording';
import { ensureVoice, speak, stopSpeaking } from '../audio';
import { Text, LanguagePicker, useLanguage, t } from '../i18n';
import { getParticipants, saveParticipant, type ParticipantSex, type AssistiveDevice } from '../store';
import { resolveTestParticipant, participantKey } from '../testParticipant';
import { protocolGuides } from '../protocolGuides';
import ProtocolTutorial from '../components/ProtocolTutorial';
import type { AssessmentProtocol, AssessmentSetup, ParticipantProfile } from '../store';

// The lightweight test renderer does not provide TextInput; native builds do.
const AgeInput: React.ComponentType<any> = TextInput ?? View;
export default function PrepareScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Prepare'>) {
  const language = useLanguage();
  const [page, setPage] = useState(0);
  const [profiles, setProfiles] = useState<ParticipantProfile[]>([]);
  const [profilesReady, setProfilesReady] = useState(false);
  const [participantLabel, setParticipantLabel] = useState(route.params.participantLabel ?? '');
  const [selectedId, setSelectedId] = useState<string | undefined>(route.params.participantId);
  const [aid, setAid] = useState<AssistiveDevice>(route.params.participantSnapshot?.clinical.assistiveDevice ?? 'none');
  const [menu, setMenu] = useState<'options' | 'participant' | 'saved' | 'tests' | null>(null);
  const [savedSearch, setSavedSearch] = useState('');
  const newId = useRef(`participant-${Date.now()}-${Math.random().toString(16).slice(2,10)}`);
  const [duration, setDuration] = useState(route.params.duration);
  const [audioEnabled, setAudio] = useState(route.params.audioEnabled);
  const [isPractice, setPractice] = useState(route.params.isPractice);
  const [ageText, setAgeText] = useState(route.params.demographics?.ageYears?.toString() ?? '');
  const [sex, setSex] = useState<ParticipantSex | null>(route.params.demographics?.sex ?? null);
  const [heightText, setHeightText] = useState(route.params.demographics?.heightCm?.toString() ?? '');
  const [protocol, setProtocol] = useState<AssessmentProtocol>(route.params.assessmentSetup?.protocol ?? 'research-walk');
  const [courseText, setCourseText] = useState(route.params.assessmentSetup?.courseLengthM?.toString() ?? '');
  const [guidanceEnabled, setGuidance] = useState(true);
  const [useGpsDistance, setUseGpsDistance] = useState(route.params.useGpsDistance ?? false);
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
  function stopSample() {
    request.current++; stopSpeaking(); clearTimeout(timer.current); clearTimeout(deadline.current);
    setTesting(false); setCanSkip(true);
  }
  function useDefaults() {
    stopSample(); setDuration(20); setAudio(true); setGuidance(true); setPractice(false);
    setOpenInfo(null); setError(''); setDefaultsApplied(true);
  }
  useEffect(() => {
    active.current = true; stopSample(); setError('');
    const app = AppState.addEventListener('change', state => { if (state !== 'active') { stopSample(); browserRequest.current?.abort(); setBrowserCheck(null); } });
    return () => { active.current = false; request.current++; browserRequest.current?.abort(); app.remove(); stopSpeaking(); clearTimeout(timer.current); clearTimeout(deadline.current); };
  }, [language]);
  async function loadProfiles() {
    try { const rows=await getParticipants(); if(active.current){setProfiles(rows);setProfilesReady(true);setError('');} }
    catch { if(active.current)setError('Could not load participants. Try again.'); }
  }
  useEffect(()=>{void loadProfiles();},[]);
  function selectPerson(p: ParticipantProfile) {
    setMenu(null);setSelectedId(p.id);setParticipantLabel(p.label);setAgeText(p.demographics.ageYears?.toString()??'');
    setSex(p.demographics.sex);setHeightText(p.demographics.heightCm?.toString()??'');setAid(p.clinical.assistiveDevice);setError('');
  }
  function participantInput() { return {id:selectedId,newId:newId.current,label:participantLabel,ageYears:ageText.trim()?Number(ageText):null,sex,heightCm:heightText.trim()?Number(heightText):null,assistiveDevice:aid}; }
  function validateCourse() {
    const value=courseText.trim()?Number(courseText):null;
    if(['2mwt','6mwt'].includes(protocol)&&(!value||!Number.isFinite(value)||value<3||value>100)) throw new Error('Enter a measured course length from 3 to 100 metres.');
    return value;
  }
  function nextPage() {
    try { if(page===0)resolveTestParticipant(profiles,participantInput());else validateCourse();stopSample();setError('');setPage(page+1); }
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
    if(Platform.OS==='web'&&!webReady){stopSample();navigation.navigate('Walkthrough');return;}
    stopSample(); setBusy(true); setError('');
    const id = ++request.current;
    try {
      const currentProfiles=await getParticipants().catch(()=>{throw new Error('Could not load participants. Try again.');});
      const participant=resolveTestParticipant(currentProfiles,participantInput());
      await checkSensors();
      if (useGpsDistance) {
        if (Platform.OS !== 'android') throw new Error(t('Optional GPS distance is available in the Android app only.'));
        const permission = await Location.requestForegroundPermissionsAsync();
        if (permission.status !== 'granted') throw new Error(t('Location permission was not granted. Turn off GPS distance to continue without it.'));
        const provider = await Location.getProviderStatusAsync();
        if (!provider.locationServicesEnabled) throw new Error(t('Turn on phone location services, or turn off GPS distance to continue.'));
      }
      if (audioEnabled) await ensureVoice();
      const courseLengthM=validateCourse();
      const plannedSeconds=protocol==='2mwt'?120:protocol==='6mwt'?360:protocol==='10mwt'?180:protocol==='tug'?180:duration;
      const setup:AssessmentSetup={protocol,courseLengthM:protocol==='10mwt'?12:protocol==='tug'?3:courseLengthM,timedDistanceM:protocol==='10mwt'?10:null,speedCondition:'comfortable',turnDirection:'self-selected'};
      if (!active.current || id !== request.current || AppState.currentState !== 'active') return;
      await saveParticipant(participant).catch(()=>{throw new Error('Could not save participant. Try again.');});
      if (!active.current || id !== request.current || AppState.currentState !== 'active') return;
      setSelectedId(participant.id);setProfiles([...currentProfiles.filter(p=>p.id!==participant.id),participant]);
      navigation.navigate('Record', { duration:plannedSeconds, audioEnabled, isPractice, guidanceEnabled, useGpsDistance, participantId:participant.id,participantLabel:participant.label,participantSnapshot:participant,demographics:participant.demographics,assessmentSetup:setup });
    } catch (e) { if (active.current) setError(e instanceof Error ? e.message : 'Could not access motion sensors. Please try again.'); }
    finally { if (active.current) setBusy(false); }
  }
  const toggles: [string, boolean, (v: boolean) => void, string, string][] = [
    ['Voice guidance', audioEnabled, value => { stopSample(); setAudio(value); }, 'About voice guidance', 'Hear setup instructions, the countdown, and start and finish cues without looking at the phone. If off, ask a helper to signal start and finish.'],
    ['Direction reminders', guidanceEnabled, setGuidance, 'About direction reminders', 'Gentle cues may remind you when the phone detects turning. They cannot confirm a straight path. Move comfortably and keep using your usual support.'],
    ['Practice walk', isPractice, setPractice, 'About practice walk', 'Try the same recording flow for your chosen duration. Your recording is still saved and exported, but labelled as practice.'],
  ];
  const matchingProfiles=profiles.filter(p=>!p.archived&&participantKey(p.label).includes(participantKey(savedSearch))).sort((a,b)=>Number(b.favorite)-Number(a.favorite)||a.label.localeCompare(b.label));
  const fieldStyle={minHeight:52,borderWidth:1,borderColor:colours.border,borderRadius:12,paddingHorizontal:14,fontSize:18,color:colours.textPrimary,backgroundColor:colours.surface};
  return <Screen key={page} title={['Who is walking?','Choose your test','Sound and readiness'][page]} eyebrow={t('Setup {0} of 3').replace('{0}',String(page+1))} actions={<>
    <View style={ui.row}>
      {page>0&&<BigButton style={ui.fill} label="Previous" variant="outline" disabled={busy} onPress={()=>{stopSample();setError('');setPage(page-1);}}/>}
      {page<2?<BigButton style={ui.fill} label="Continue" disabled={page===0&&!profilesReady} onPress={nextPage}/>:<BigButton style={{flex:2}} label={Platform.OS==='web'&&!webReady?'Preview hands-free flow':testing?'Start without sound test':'Start test'} disabled={checkingBrowser||(Platform.OS==='web'&&!webReady?false:!ready||!canSkip)} loading={busy} onPress={start}/>}
    </View>
  </>}>
    <BigButton label="More options" variant="ghost" onPress={()=>{stopSample();setMenu('options');}} disabled={busy}/>
    {!!error&&<Text accessibilityRole="alert" accessibilityLiveRegion="assertive" style={ui.error}>{error}</Text>}
    {Platform.OS==='web'&&page===0&&<Text style={ui.caption}>Browser profiles and recordings last only for this tab. Export before closing.</Text>}
    {page===0&&<View style={{gap:8}}>
      <Text style={ui.caption}>Choose a saved person, or enter a new study ID. A new profile is saved when you start the test.</Text>
      <AgeInput value={participantLabel} autoCorrect={false} autoCapitalize="none" maxLength={80} accessibilityLabel={t('Study ID or participant label')} placeholder={t('Study ID or participant label')} style={fieldStyle} onChangeText={(v:string)=>{setParticipantLabel(v);if(selectedId){newId.current=`participant-${Date.now()}-${Math.random().toString(16).slice(2,10)}`;setSelectedId(undefined);setAgeText('');setSex(null);setHeightText('');setAid('none');}}}/>
      {profiles.some(p=>!p.archived)&&<BigButton label="Choose a saved person" variant="ghost" onPress={()=>{setSavedSearch('');setMenu('saved');}}/>}
      <Text style={ui.caption}>{selectedId?'Using a saved participant':'New participant'}</Text>
      <AgeInput value={ageText} onChangeText={setAgeText} accessibilityLabel={t('Age in years')} placeholder={t('Age in years')} maxLength={3} keyboardType="number-pad" style={fieldStyle}/>
      <Text style={ui.label}>Sex (self-reported)</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{(['female','male','prefer-not-to-say'] as const).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:sex===value}} onPress={()=>setSex(value)} style={[ui.choice,{flexBasis:90},sex===value&&ui.selected]}><Text style={ui.caption}>{value==='prefer-not-to-say'?'Prefer not to say':value==='female'?'Female':'Male'}</Text></Pressable>)}</View>
      {!profilesReady&&<BigButton label="Retry" variant="outline" onPress={()=>void loadProfiles()}/>}
      {Platform.OS==='web'&&<BigButton label="Preview hands-free flow" variant="ghost" onPress={()=>navigation.navigate('Walkthrough')}/>}
    </View>}
    {page===1&&<View style={{gap:10}}>
      <BigButton label={protocol==='research-walk'?'Research walk':protocol.toUpperCase()} variant="outline" onPress={()=>setMenu('tests')} accessibilityHint={t('Choose your test')}/>

      <Text style={ui.caption}>{guide.short}</Text>
      <BigButton label="Show me how" variant="outline" onPress={()=>{stopSample();setGuideOpen(true);}}/>
      {guideOpen&&<ProtocolTutorial protocol={protocol} onClose={()=>{stopSpeaking();setGuideOpen(false);}}/>}
      {(protocol==='2mwt'||protocol==='6mwt')&&<AgeInput accessibilityLabel={t('Measured course length in metres')} value={courseText} onChangeText={setCourseText} placeholder={t('Measured loop length (metres)')} keyboardType="decimal-pad" style={fieldStyle}/>}
    {protocol==='research-walk'&&<View>
      <View style={ui.row}><Text style={[ui.label,ui.fill]}>Recording duration</Text>
        <Pressable accessibilityRole="button" accessibilityLabel={t('About recording duration')} accessibilityState={{ expanded: openInfo === 'duration' }} onPress={() => setOpenInfo(openInfo === 'duration' ? null : 'duration')} style={{ minWidth:48, minHeight:48, alignItems:'center', justifyContent:'center' }}>
          <Text style={{ fontSize:22, fontWeight:'700', color:colours.primary }}>ⓘ</Text>
        </Pressable>
      </View>
    </View>}
    {protocol==='research-walk'&&<View style={ui.row}>{([10,20,30] as const).map(n => <Pressable key={n} accessibilityRole="radio" accessibilityLabel={t(`Walk for ${n} seconds`)} accessibilityState={{ selected: n === duration }} style={[ui.choice, n === duration && ui.selected]} onPress={() => setDuration(n)}><Text style={ui.label}>{n} sec</Text></Pressable>)}</View>}
    </View>}
    {page===2&&<View style={{gap:10}}>
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
      {webReady && <BigButton label="Preview hands-free flow" variant="ghost" onPress={()=>{stopSample();navigation.navigate('Walkthrough');}} disabled={busy} />}
    </View>}
    </View>}

    <Modal visible={menu!==null} animationType="slide" onRequestClose={()=>setMenu(null)}>
      <Screen fullScreen title={menu==='participant'?'More participant details':menu==='saved'?'Choose a saved person':menu==='tests'?'Choose your test':'More options'}
        actions={<BigButton label="Done" onPress={()=>setMenu(null)}/>}>
        {menu==='options'&&<>
          <LanguagePicker/>
          <BigButton label="More participant details" variant="outline" onPress={()=>setMenu('participant')}/>
    <View style={{ backgroundColor: colours.surface, borderRadius: 18, paddingHorizontal: 12 }}>{toggles.map(([label,value,setter,infoLabel,explanation]) => <View key={label}>
      <View style={[ui.row,{ minHeight:48 }]}><Text style={[ui.caption,ui.fill]}>{label}</Text>
        <Pressable accessibilityRole="button" accessibilityLabel={t(infoLabel)} accessibilityState={{ expanded: openInfo === label }} onPress={() => setOpenInfo(openInfo === label ? null : label)} style={{ minWidth:48, minHeight:48, alignItems:'center', justifyContent:'center' }}>
          <Text style={{ fontSize:22, fontWeight:'700', color:colours.primary }}>ⓘ</Text>
        </Pressable>
        <Switch accessibilityLabel={t(label)} value={value} onValueChange={setter} trackColor={{ true: colours.primary }} />
      </View>
      {openInfo === label && <Text accessibilityLiveRegion="polite" style={[ui.caption,{ paddingBottom:12 }]}>{explanation}</Text>}
    </View>)}</View>

    <BigButton label="Use default settings" variant="outline" onPress={useDefaults} disabled={busy} accessibilityHint={t('Sets 20 seconds, voice and direction reminders on, and practice off.')} />
    {defaultsApplied && duration === 20 && audioEnabled && guidanceEnabled && !isPractice && <Text accessibilityLiveRegion="polite" style={ui.caption}>Defaults selected: 20 seconds, voice and direction reminders on, practice off. You can still change these settings.</Text>}
    {Platform.OS === 'android' && <View style={{ backgroundColor: colours.surface, borderRadius: 16, padding: 12 }}>
      <Pressable accessibilityRole="checkbox" accessibilityLabel={t('Optional outdoor GPS distance cross-check')} accessibilityState={{ checked: useGpsDistance }} onPress={() => setUseGpsDistance(v => !v)} style={[ui.row,{minHeight:56}]}>
        <Text style={{fontSize:26,color:colours.primary}}>{useGpsDistance?'☑':'☐'}</Text><Text style={[ui.label,ui.fill]}>{t('Optional outdoor GPS distance cross-check')}</Text>
      </Pressable>
      <Text style={ui.caption}>{t('Uses foreground location only after walking begins. Coordinates are not saved or uploaded; only the distance and reported accuracy summary are kept. Best outdoors on a longer route. It may be unreliable indoors or on short tests and is not a clinical measurement.')}</Text>
    </View>}

        </>}
        {menu==='participant'&&<View style={{gap:12}}>
        <AgeInput value={heightText} onChangeText={setHeightText} accessibilityLabel={t('Height in centimetres')} placeholder={t('Height cm (for experimental estimate)')} keyboardType="decimal-pad" style={fieldStyle}/>
        <Text style={ui.label}>Usual walking aid</Text>
        <View style={[ui.row,{flexWrap:'wrap'}]}>{([['none','None'],['single-point-cane','Single-point cane'],['quad-cane','Quad cane'],['other','Other']] as const).map(([value,label])=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:aid===value}} onPress={()=>setAid(value)} style={[ui.choice,{flexBasis:120},aid===value&&ui.selected]}><Text style={ui.caption}>{label}</Text></Pressable>)}</View>

        </View>}
        {menu==='tests'&&<View style={{gap:12}}>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{([['research-walk','Research walk'],['10mwt','10MWT'],['2mwt','2MWT'],['6mwt','6MWT'],['tug','TUG']] as [AssessmentProtocol,string][]).map(([value,name])=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:protocol===value}} style={[ui.choice,{flexBasis:100},protocol===value&&ui.selected]} onPress={()=>{setProtocol(value);setMenu(null);}}><Text style={ui.label}>{name}</Text></Pressable>)}</View>
        </View>}
        {menu==='saved'&&<>
          <AgeInput value={savedSearch} onChangeText={setSavedSearch} accessibilityLabel={t('Search saved participants')} placeholder={t('Search saved participants')} style={fieldStyle}/>
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
