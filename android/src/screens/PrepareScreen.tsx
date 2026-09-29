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
import type { ParticipantDemographics, ParticipantSex } from '../store';
import type { AssessmentProtocol, AssessmentSetup, ParticipantProfile } from '../store';

const protocolGuides: Record<AssessmentProtocol, { title: string; short: string; body: string; extra?: string }> = {
  'research-walk': {
    title: 'Research walk: what it measures',
    short: 'Short sensor capture for research. It is not a standardized clinical walking test.',
    body: 'This option records phone motion during a short walk for research. Choose 10, 20 or 30 seconds. Walk on a clear, straight path at a comfortable pace and use your usual walking aid. The app starts its sensor timer after it detects the first step, so this is not a fixed-distance speed test. For a measured distance or speed, a worker must separately measure the route and timed interval. Phone-only distance is experimental.',
  },
  '10mwt': {
    title: '10-Meter Walk Test (10MWT)',
    short: 'Measures speed over a marked distance. This project uses 1 m to accelerate, 10 m timed, then 1 m to slow down.',
    body: 'Purpose: measure walking speed over a known distance. This project’s selected layout is 12 m in a straight line: 1 m to accelerate, a central 10 m timed zone, and 1 m to slow down. The worker starts and stops the stopwatch as the participant crosses the two timed-zone marks; speed is 10 metres divided by those seconds. Keep the same usual aid and speed condition when comparing visits. The source describes two comfortable-speed trials and two fast-as-safe trials, averaged separately. GaitTrace records phone sensors but does not detect the marks, run those four trials, or time the central 10 m. The app’s 180-second sensor window is not the test time; the worker must time and enter the 10 m result.',
  },
  '2mwt': {
    title: 'Two-Minute Walk Test (2MWT)',
    short: 'Measures the distance covered in 2 minutes on a measured course. Rest is allowed; the clock continues.',
    body: 'Purpose: measure how far the participant can walk in two minutes. Use a measured, clear course and the same usual walking aid on repeat tests. The standardized instruction asks the person to cover as much distance as safely possible; slowing down or stopping to rest is allowed, and the clock keeps running. No hands-on help is allowed for the standard test. The worker starts the protocol stopwatch at “Go”, counts complete laps and measures the final partial distance, then records rests. GaitTrace’s sensor timer waits for a detected first step and is not a substitute for the stopwatch or measured distance. Enter the course length before starting.',
  },
  '6mwt': {
    title: 'Six-Minute Walk Test (6MWT)',
    short: 'Measures distance covered in 6 minutes on a consistent measured course. Rest is allowed; the clock continues.',
    body: 'Purpose: measure the distance walked in six minutes as a self-paced test of functional walking capacity. Use a measured, level course and keep the same course and aid across visits. The ATS standard uses a 30 m corridor with turn markers; shorter courses add turns and can change the distance, so document the actual course. The participant may slow down or stand and rest, but the timer continues. The worker uses the standardized timed encouragement, counts laps and partial distance, and records rests. GaitTrace’s sensor timer waits for a detected first step and does not count laps or administer the standardized protocol. Its live prompts are not the ATS script; for a standardized 6MWT, have a worker administer the test and do not use extra app walking cues as a replacement.',
    extra: 'For a standardized 6MWT, switch off both Voice Guidance and Direction Reminders during the walk. A worker should give only the standard timed messages.',
  },
  'tug': {
    title: 'Timed Up and Go (TUG)',
    short: 'From a chair, stand, walk 3 m, turn, return and sit. A worker times the complete sequence.',
    body: 'Purpose: observe functional mobility through a chair transfer, short walk, turn and return. Use a standard armchair, mark a line 3 m away, and use the person’s usual footwear and walking aid. On “Go”, the person stands, walks at a comfortable and safe pace to the line, turns, walks back and sits. The worker starts the stopwatch at “Go” and stops when the person is seated again (buttocks on the chair). Record the aid and any assistance; standard instructions include a practice trial. GaitTrace does not detect standing, the 3 m line, turning completion or seat contact. Its 180-second sensor capture is not the TUG time; a worker must time and enter the complete sequence.',
  },
};
// The lightweight test renderer does not provide TextInput; native builds do.
const AgeInput: React.ComponentType<any> = TextInput ?? View;
export default function PrepareScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Prepare'>) {
  const language = useLanguage();
  const [duration, setDuration] = useState(route.params.duration);
  const [audioEnabled, setAudio] = useState(route.params.audioEnabled);
  const [isPractice, setPractice] = useState(route.params.isPractice);
  const [ageText, setAgeText] = useState(route.params.demographics?.ageYears?.toString() ?? '');
  const [sex, setSex] = useState<ParticipantSex>(route.params.demographics?.sex ?? 'prefer-not-to-say');
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
      await checkSensors();
      if (useGpsDistance) {
        if (Platform.OS !== 'android') throw new Error(t('Optional GPS distance is available in the Android app only.'));
        const permission = await Location.requestForegroundPermissionsAsync();
        if (permission.status !== 'granted') throw new Error(t('Location permission was not granted. Turn off GPS distance to continue without it.'));
        const provider = await Location.getProviderStatusAsync();
        if (!provider.locationServicesEnabled) throw new Error(t('Turn on phone location services, or turn off GPS distance to continue.'));
      }
      if (audioEnabled) await ensureVoice();
      const parsedAge = ageText.trim() === '' ? null : Number(ageText);
      if (parsedAge !== null && (!Number.isInteger(parsedAge) || parsedAge < 1 || parsedAge > 120)) throw new Error('Enter an age from 1 to 120, or leave age blank.');
      const heightCm=heightText.trim()===''?null:Number(heightText);
      if(heightCm!==null&&(!Number.isFinite(heightCm)||heightCm<100||heightCm>230))throw new Error('Enter height from 100 to 230 cm.');
      const courseLengthM=courseText.trim()===''?null:Number(courseText);
      if(['2mwt','6mwt'].includes(protocol)&&(!courseLengthM||!Number.isFinite(courseLengthM)||courseLengthM<3||courseLengthM>100))throw new Error('Enter a measured course length from 3 to 100 metres.');
      const plannedSeconds=protocol==='2mwt'?120:protocol==='6mwt'?360:protocol==='10mwt'?180:protocol==='tug'?180:duration;
      const setup:AssessmentSetup={protocol,courseLengthM:protocol==='10mwt'?12:protocol==='tug'?3:courseLengthM,timedDistanceM:protocol==='10mwt'?10:null,speedCondition:'comfortable',turnDirection:'self-selected'};
      if (active.current && id === request.current && AppState.currentState === 'active') navigation.navigate('Record', { duration:plannedSeconds, audioEnabled, isPractice, guidanceEnabled, useGpsDistance, participantId:route.params.participantId,participantLabel:route.params.participantLabel,participantSnapshot:route.params.participantSnapshot as ParticipantProfile|undefined,demographics: { ageYears: parsedAge, sex, heightCm },assessmentSetup:setup });
    } catch (e) { if (active.current) setError(e instanceof Error ? e.message : 'Could not access motion sensors. Please try again.'); }
    finally { if (active.current) setBusy(false); }
  }
  const toggles: [string, boolean, (v: boolean) => void, string, string][] = [
    ['Voice guidance', audioEnabled, value => { stopSample(); setAudio(value); }, 'About voice guidance', 'Hear setup instructions, the countdown, and start and finish cues without looking at the phone. If off, ask a helper to signal start and finish.'],
    ['Direction reminders', guidanceEnabled, setGuidance, 'About direction reminders', 'Gentle cues may remind you when the phone detects turning. They cannot confirm a straight path. Move comfortably and keep using your usual support.'],
    ['Practice walk', isPractice, setPractice, 'About practice walk', 'Try the same recording flow for your chosen duration. Your recording is still saved and exported, but labelled as practice.'],
  ];
  return <Screen title="Set up your walk" actions={<BigButton label={Platform.OS==='web'&&!webReady?'Preview hands-free flow':testing ? 'Start without sound test' : 'Start test'} disabled={checkingBrowser || (Platform.OS==='web'&&!webReady?false:!ready || !canSkip)} loading={busy} onPress={start} />}>
    <LanguagePicker />
    <View style={{ gap: 8 }}>
      <Text style={ui.label}>Assessment protocol</Text>
      <View style={[ui.row,{flexWrap:'wrap'}]}>{([['research-walk','Research walk'],['10mwt','10MWT'],['2mwt','2MWT'],['6mwt','6MWT'],['tug','TUG']] as [AssessmentProtocol,string][]).map(([value,name])=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:protocol===value}} style={[ui.choice,protocol===value&&ui.selected]} onPress={()=>setProtocol(value)}><Text>{name}</Text></Pressable>)}</View>
      <Text style={ui.caption}>{t(guide.short)}</Text>
      <BigButton label="Read full test instructions" variant="outline" onPress={()=>setGuideOpen(true)} />
      <Modal visible={guideOpen} transparent animationType="fade" onRequestClose={()=>setGuideOpen(false)}>
        <View style={{flex:1,backgroundColor:'#0008',justifyContent:'center',padding:16}}>
          <View accessibilityViewIsModal style={{backgroundColor:colours.surface,borderRadius:20,padding:20,gap:14,maxWidth:560,maxHeight:'90%',alignSelf:'center',width:'100%'}}>
            <ScrollView contentContainerStyle={{gap:12}}>
              <Text style={ui.label}>{t(guide.title)}</Text>
              <Body>{t(guide.body)}</Body>
              {guide.extra && <Body>{t(guide.extra)}</Body>}
              <Text style={ui.caption}>Source basis: Shirley Ryan AbilityLab RehabMeasures Database; ATS 6MWT statement. GaitTrace is a sensor-capture aid and does not itself administer or validate these clinical tests.</Text>
            </ScrollView>
            {audioEnabled && <BigButton label="Hear these instructions" variant="outline" onPress={()=>void speak(guide.body,{onError:e=>setError(e.message),onDone:guide.extra?()=>void speak(guide.extra!,{onError:e=>setError(e.message)}):undefined})} />}
            <BigButton label="Close instructions" onPress={()=>setGuideOpen(false)} />
          </View>
        </View>
      </Modal>
      {(protocol==='2mwt'||protocol==='6mwt')&&<AgeInput accessibilityLabel="Measured course length in metres" value={courseText} onChangeText={setCourseText} placeholder="Measured loop length (metres)" keyboardType="decimal-pad" style={{ minHeight:52,borderWidth:1,borderColor:colours.border,borderRadius:12,paddingHorizontal:14,fontSize:18,color:colours.textPrimary,backgroundColor:colours.surface }} />}
      <Text style={ui.label}>Participant information</Text>
      <Text style={ui.caption}>Optional research information. It is saved with this recording and is not used for a diagnosis.</Text>
      <AgeInput accessibilityLabel={t('Age in years')} value={ageText} onChangeText={setAgeText} placeholder={t('Age in years (optional)')} keyboardType="number-pad" maxLength={3} style={{ minHeight: 52, borderWidth: 1, borderColor: colours.border, borderRadius: 12, paddingHorizontal: 14, fontSize: 18, color: colours.textPrimary, backgroundColor: colours.surface }} />
      <AgeInput accessibilityLabel="Height in centimetres" value={heightText} onChangeText={setHeightText} placeholder="Height cm (for experimental estimate)" keyboardType="decimal-pad" style={{ minHeight: 52, borderWidth: 1, borderColor: colours.border, borderRadius: 12, paddingHorizontal: 14, fontSize: 18, color: colours.textPrimary, backgroundColor: colours.surface }} />
      <Text style={ui.caption}>Sex</Text>
      <View style={ui.row}>{(['female','male','prefer-not-to-say'] as const).map(value => <Pressable key={value} accessibilityRole="radio" accessibilityState={{ selected: sex === value }} onPress={() => setSex(value)} style={[ui.choice, sex === value && ui.selected]}><Text style={ui.caption}>{value === 'prefer-not-to-say' ? 'Prefer not to say' : value[0].toUpperCase() + value.slice(1)}</Text></Pressable>)}</View>
    </View>
    {Platform.OS === 'android' && <View style={{ backgroundColor: colours.surface, borderRadius: 16, padding: 12 }}>
      <Pressable accessibilityRole="checkbox" accessibilityLabel={t('Optional outdoor GPS distance cross-check')} accessibilityState={{ checked: useGpsDistance }} onPress={() => setUseGpsDistance(v => !v)} style={[ui.row,{minHeight:56}]}>
        <Text style={{fontSize:26,color:colours.primary}}>{useGpsDistance?'☑':'☐'}</Text><Text style={[ui.label,ui.fill]}>{t('Optional outdoor GPS distance cross-check')}</Text>
      </Pressable>
      <Text style={ui.caption}>{t('Uses foreground location only after walking begins. Coordinates are not saved or uploaded; only the distance and reported accuracy summary are kept. Best outdoors on a longer route. It may be unreliable indoors or on short tests and is not a clinical measurement.')}</Text>
    </View>}
    {Platform.OS === 'web' && <View style={{gap:8}}>
      <Text style={ui.caption}>Keep this page visible and the phone unlocked. Browser recordings stay in this tab: export before refreshing or closing. Vibration may be unavailable.</Text>
      <BigButton label={checkingBrowser?'Checking live sensors…':'Check this phone’s sensors'} variant="outline" onPress={()=>setSensorConsent(true)} disabled={busy || checkingBrowser} />
      <Modal visible={sensorConsent} transparent animationType="fade" onRequestClose={()=>setSensorConsent(false)}>
        <View style={{flex:1,backgroundColor:'#0008',justifyContent:'center',padding:24}}>
          <View accessibilityViewIsModal style={{backgroundColor:colours.surface,borderRadius:20,padding:24,gap:16,maxWidth:430,alignSelf:'center'}}>
            <Text style={ui.label}>Allow a sensor check?</Text>
            <Body>We will read acceleration, rotation and magnetic field for three seconds. This is app consent. Your browser controls access and may not show another prompt. Consent cannot enable an unavailable magnetometer.</Body>
            <BigButton label="Agree and check sensors" onPress={()=>{setSensorConsent(false);void checkBrowser();}} />
            <BigButton label="Cancel" variant="outline" onPress={()=>setSensorConsent(false)} />
          </View>
        </View>
      </Modal>
      {browserCheck && <View accessibilityLiveRegion="polite">
        {SENSOR_NAMES.map(name=><View key={name}><Text style={ui.label}>{name === 'accelerometer'?'Accelerometer':name === 'gyroscope'?'Gyroscope':'Magnetometer'}</Text><Text style={ui.caption}>{t(browserCheck.sensors[name].status === 'ready'?'Live readings received':browserCheck.sensors[name].status === 'unavailable'?'Not exposed by this browser':browserCheck.sensors[name].status === 'blocked'?'Permission denied or sensor error':browserCheck.sensors[name].status === 'slow'?'Readings too slow or interrupted':browserCheck.sensors[name].status === 'invalid'?'Invalid sensor timestamps':'No fresh readings')}{' · '}{browserCheck.sensors[name].hz.toFixed(1)} Hz</Text></View>)}
        <Text style={ui.caption}>{webReady?'All three sensors are responding. Start will recheck them before setup.':'All three sensors are required. Preview the steps or use the Android app.'}</Text>
      </View>}
      {webReady && <BigButton label="Preview hands-free flow" variant="ghost" onPress={()=>{stopSample();navigation.navigate('Walkthrough');}} disabled={busy} />}
    </View>}
    <BigButton label="Use default settings" variant="outline" onPress={useDefaults} disabled={busy} accessibilityHint={t('Sets 20 seconds, voice and direction reminders on, and practice off.')} />
    {defaultsApplied && duration === 20 && audioEnabled && guidanceEnabled && !isPractice && <Text accessibilityLiveRegion="polite" style={ui.caption}>Defaults selected: 20 seconds, voice and direction reminders on, practice off. You can still change these settings.</Text>}
    {protocol==='research-walk'&&<View>
      <View style={ui.row}><Text style={[ui.label,ui.fill]}>Recording duration</Text>
        <Pressable accessibilityRole="button" accessibilityLabel={t('About recording duration')} accessibilityState={{ expanded: openInfo === 'duration' }} onPress={() => setOpenInfo(openInfo === 'duration' ? null : 'duration')} style={{ minWidth:48, minHeight:48, alignItems:'center', justifyContent:'center' }}>
          <Text style={{ fontSize:22, fontWeight:'700', color:colours.primary }}>ⓘ</Text>
        </Pressable>
      </View>
      {openInfo === 'duration' && <Text accessibilityLiveRegion="polite" style={ui.caption}>Choose 10, 20 or 30 seconds of recording after the countdown. Setup time is extra. You may pause or stop early.</Text>}
    </View>}
    {protocol==='research-walk'&&<View style={ui.row}>{([10,20,30] as const).map(n => <Pressable key={n} accessibilityRole="radio" accessibilityLabel={t(`Walk for ${n} seconds`)} accessibilityState={{ selected: n === duration }} style={[ui.choice, n === duration && ui.selected]} onPress={() => setDuration(n)}><Text style={ui.label}>{n} sec</Text></Pressable>)}</View>}
    <View style={{ backgroundColor: colours.surface, borderRadius: 18, paddingHorizontal: 12 }}>{toggles.map(([label,value,setter,infoLabel,explanation]) => <View key={label}>
      <View style={[ui.row,{ minHeight:48 }]}><Text style={[ui.caption,ui.fill]}>{label}</Text>
        <Pressable accessibilityRole="button" accessibilityLabel={t(infoLabel)} accessibilityState={{ expanded: openInfo === label }} onPress={() => setOpenInfo(openInfo === label ? null : label)} style={{ minWidth:48, minHeight:48, alignItems:'center', justifyContent:'center' }}>
          <Text style={{ fontSize:22, fontWeight:'700', color:colours.primary }}>ⓘ</Text>
        </Pressable>
        <Switch accessibilityLabel={t(label)} value={value} onValueChange={setter} trackColor={{ true: colours.primary }} />
      </View>
      {openInfo === label && <Text accessibilityLiveRegion="polite" style={[ui.caption,{ paddingBottom:12 }]}>{explanation}</Text>}
    </View>)}</View>
    {audioEnabled ? <><BigButton label={testing ? 'Stop sample' : 'Play voice sample'} variant="outline" onPress={testing ? stopSample : sample} disabled={busy} /><Text style={ui.caption}>Listen briefly, or skip. Voice guidance stays on. Check your media volume first.</Text></> : <Body>Voice is off. Ask a helper to signal start and finish while the phone is secured.</Body>}
    {(Platform.OS!=='web'||webReady)&&<Pressable accessibilityRole="checkbox" accessibilityLabel={t('I can walk without hands-on help, using my usual cane or quad stick if needed. The path is clear and I agree to save movement data.')} accessibilityState={{ checked:ready }} onPress={() => setReady(!ready)} style={[ui.row,{ minHeight:64 }]}><Text style={{ fontSize:28,color:colours.primary }}>{ready ? '☑' : '☐'}</Text><Text style={[ui.caption,ui.fill]}>I can walk without hands-on help, using my usual cane or quad stick if needed. The path is clear and I agree to save movement data.</Text></Pressable>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Screen>;
}
