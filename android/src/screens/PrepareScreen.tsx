import React, { useEffect, useRef, useState } from 'react';
import { View, Pressable, Switch, AppState, Platform } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours } from '../theme';
import { checkSensors } from '../sensors';
import { ensureVoice, speak, stopSpeaking } from '../audio';
import { Text, LanguagePicker, useLanguage, t } from '../i18n';
export default function PrepareScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Prepare'>) {
  const language = useLanguage();
  const [duration, setDuration] = useState(route.params.duration);
  const [audioEnabled, setAudio] = useState(route.params.audioEnabled);
  const [isPractice, setPractice] = useState(route.params.isPractice);
  const [guidanceEnabled, setGuidance] = useState(true);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [testing, setTesting] = useState(false);
  const [canSkip, setCanSkip] = useState(true);
  const [error, setError] = useState('');
  const timer = useRef<ReturnType<typeof setTimeout>>();
  const deadline = useRef<ReturnType<typeof setTimeout>>();
  const active = useRef(true);
  const request = useRef(0);
  function stopSample() {
    request.current++; stopSpeaking(); clearTimeout(timer.current); clearTimeout(deadline.current);
    setTesting(false); setCanSkip(true);
  }
  useEffect(() => {
    active.current = true; stopSample(); setError('');
    const app = AppState.addEventListener('change', state => { if (state !== 'active') stopSample(); });
    return () => { active.current = false; request.current++; app.remove(); stopSpeaking(); clearTimeout(timer.current); clearTimeout(deadline.current); };
  }, [language]);
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
    if(Platform.OS==='web'){stopSample();navigation.navigate('Walkthrough');return;}
    stopSample(); setBusy(true); setError('');
    const id = ++request.current;
    try {
      await checkSensors();
      if (audioEnabled) await ensureVoice();
      if (active.current && id === request.current && AppState.currentState === 'active') navigation.navigate('Record', { duration, audioEnabled, isPractice, guidanceEnabled });
    } catch (e) { if (active.current) setError(e instanceof Error ? e.message : 'Could not access motion sensors. Please try again.'); }
    finally { if (active.current) setBusy(false); }
  }
  const toggles: [string, boolean, (v: boolean) => void][] = [
    ['Voice guidance', audioEnabled, value => { stopSample(); setAudio(value); }], ['Direction reminders', guidanceEnabled, setGuidance], ['Practice walk', isPractice, setPractice],
  ];
  return <Screen title="Set up your walk" actions={<BigButton label={Platform.OS==='web'?'Preview hands-free flow':testing ? 'Start without sound test' : 'Start test'} disabled={Platform.OS==='web'?false:!ready || !canSkip} loading={busy} onPress={start} />}>
    <LanguagePicker />
    <View style={ui.row}>{([10,20,30] as const).map(n => <Pressable key={n} accessibilityRole="radio" accessibilityLabel={t(`Walk for ${n} seconds`)} accessibilityState={{ selected: n === duration }} style={[ui.choice, n === duration && ui.selected]} onPress={() => setDuration(n)}><Text style={ui.label}>{n} sec</Text></Pressable>)}</View>
    <View style={{ backgroundColor: colours.surface, borderRadius: 18, paddingHorizontal: 12 }}>{toggles.map(([label,value,setter]) => <View key={label} style={[ui.row,{ minHeight:48 }]}><Text style={[ui.caption,ui.fill]}>{label}</Text><Switch accessibilityLabel={t(label)} value={value} onValueChange={setter} trackColor={{ true: colours.primary }} /></View>)}</View>
    {audioEnabled ? <><BigButton label={testing ? 'Stop sample' : 'Play voice sample'} variant="outline" onPress={testing ? stopSample : sample} disabled={busy} /><Text style={ui.caption}>Listen briefly, or skip. Voice guidance stays on. Check your media volume first.</Text></> : <Body>Voice is off. Ask a helper to signal start and finish while the phone is secured.</Body>}
    {Platform.OS!=='web'&&<Pressable accessibilityRole="checkbox" accessibilityLabel={t('Path clear, usual support ready. I agree to save my movement data.')} accessibilityState={{ checked:ready }} onPress={() => setReady(!ready)} style={[ui.row,{ minHeight:64 }]}><Text style={{ fontSize:28,color:colours.primary }}>{ready ? '☑' : '☐'}</Text><Text style={[ui.caption,ui.fill]}>Path clear, usual support ready. I agree to save my movement data.</Text></Pressable>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Screen>;
}
