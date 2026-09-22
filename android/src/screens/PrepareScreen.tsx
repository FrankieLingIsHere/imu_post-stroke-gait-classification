import React, { useEffect, useRef, useState } from 'react';
import { View, Pressable, Switch, AppState, Platform, Modal, TextInput } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours } from '../theme';
import { checkSensors } from '../sensors';
import { checkBrowserSensors, BrowserCheck } from '../browserSensors';
import { SENSOR_NAMES } from '../recording';
import { ensureVoice, speak, stopSpeaking } from '../audio';
import { Text, LanguagePicker, useLanguage, t } from '../i18n';
import type { ParticipantDemographics, ParticipantSex } from '../store';
// The lightweight test renderer does not provide TextInput; native builds do.
const AgeInput: React.ComponentType<any> = TextInput ?? View;
export default function PrepareScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Prepare'>) {
  const language = useLanguage();
  const [duration, setDuration] = useState(route.params.duration);
  const [audioEnabled, setAudio] = useState(route.params.audioEnabled);
  const [isPractice, setPractice] = useState(route.params.isPractice);
  const [ageText, setAgeText] = useState(route.params.demographics?.ageYears?.toString() ?? '');
  const [sex, setSex] = useState<ParticipantSex>(route.params.demographics?.sex ?? 'prefer-not-to-say');
  const [guidanceEnabled, setGuidance] = useState(true);
  const [openInfo, setOpenInfo] = useState<string | null>(null);
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
      if (audioEnabled) await ensureVoice();
      const parsedAge = ageText.trim() === '' ? null : Number(ageText);
      if (parsedAge !== null && (!Number.isInteger(parsedAge) || parsedAge < 1 || parsedAge > 120)) throw new Error('Enter an age from 1 to 120, or leave age blank.');
      if (active.current && id === request.current && AppState.currentState === 'active') navigation.navigate('Record', { duration, audioEnabled, isPractice, guidanceEnabled, demographics: { ageYears: parsedAge, sex } });
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
      <Text style={ui.label}>Participant information</Text>
      <Text style={ui.caption}>Optional research information. It is saved with this recording and is not used for a diagnosis.</Text>
      <AgeInput accessibilityLabel={t('Age in years')} value={ageText} onChangeText={setAgeText} placeholder={t('Age in years (optional)')} keyboardType="number-pad" maxLength={3} style={{ minHeight: 52, borderWidth: 1, borderColor: colours.border, borderRadius: 12, paddingHorizontal: 14, fontSize: 18, color: colours.textPrimary, backgroundColor: colours.surface }} />
      <Text style={ui.caption}>Sex</Text>
      <View style={ui.row}>{(['female','male','intersex','prefer-not-to-say'] as const).map(value => <Pressable key={value} accessibilityRole="radio" accessibilityState={{ selected: sex === value }} onPress={() => setSex(value)} style={[ui.choice, sex === value && ui.selected]}><Text style={ui.caption}>{value === 'prefer-not-to-say' ? 'Prefer not to say' : value[0].toUpperCase() + value.slice(1)}</Text></Pressable>)}</View>
    </View>
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
    <View>
      <View style={ui.row}><Text style={[ui.label,ui.fill]}>Recording duration</Text>
        <Pressable accessibilityRole="button" accessibilityLabel={t('About recording duration')} accessibilityState={{ expanded: openInfo === 'duration' }} onPress={() => setOpenInfo(openInfo === 'duration' ? null : 'duration')} style={{ minWidth:48, minHeight:48, alignItems:'center', justifyContent:'center' }}>
          <Text style={{ fontSize:22, fontWeight:'700', color:colours.primary }}>ⓘ</Text>
        </Pressable>
      </View>
      {openInfo === 'duration' && <Text accessibilityLiveRegion="polite" style={ui.caption}>Choose 10, 20 or 30 seconds of recording after the countdown. Setup time is extra. You may pause or stop early.</Text>}
    </View>
    <View style={ui.row}>{([10,20,30] as const).map(n => <Pressable key={n} accessibilityRole="radio" accessibilityLabel={t(`Walk for ${n} seconds`)} accessibilityState={{ selected: n === duration }} style={[ui.choice, n === duration && ui.selected]} onPress={() => setDuration(n)}><Text style={ui.label}>{n} sec</Text></Pressable>)}</View>
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
    {(Platform.OS!=='web'||webReady)&&<Pressable accessibilityRole="checkbox" accessibilityLabel={t('Path clear, usual support ready. I agree to save my movement data.')} accessibilityState={{ checked:ready }} onPress={() => setReady(!ready)} style={[ui.row,{ minHeight:64 }]}><Text style={{ fontSize:28,color:colours.primary }}>{ready ? '☑' : '☐'}</Text><Text style={[ui.caption,ui.fill]}>Path clear, usual support ready. I agree to save my movement data.</Text></Pressable>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Screen>;
}
