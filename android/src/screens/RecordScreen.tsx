import React, { useEffect, useRef, useState } from 'react';
import { View, AppState, BackHandler, StyleSheet } from 'react-native';
import { Text } from '../i18n';
import { getLanguage } from '../language';
import { useKeepAwake } from 'expo-keep-awake';
import * as Haptics from 'expo-haptics';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours as c } from '../theme';
import { speak, stopSpeaking } from '../audio';
import { SensorRecorder } from '../sensors';
import { recordingIssues } from '../recording';
import type { Recording } from '../recording';
import { saveSession, generateSessionId, SessionRecord } from '../store';
import { SettlingGate } from '../movement';
import { FitCheck } from '../placement';

export default function RecordScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Record'>) {
  useKeepAwake();
  const { duration, isPractice, audioEnabled, guidanceEnabled } = route.params;
  const [attempt, setAttempt] = useState(0);
  const passedFit = useRef<Recording['fitCheck']>();
  const retryRequested = useRef(false);
  const placementSeconds = attempt > 0 ? 8 : 20;
  const [confirmStop, setConfirmStop] = useState(false);
  const stopArmedUntil = useRef(0);
  const [phase, setPhase] = useState('prep');
  const [remaining, setRemaining] = useState(20);
  const [hint, setHint] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [directionReady, setDirectionReady] = useState(false);
  const [setupMessage, setSetupMessage] = useState('Checking live readings…');
  const phaseRef = useRef('prep');
  const recorder = useRef<SensorRecorder | null>(null);
  const pending = useRef<SessionRecord | null>(null);
  const saveBusy = useRef(false);
  const mounted = useRef(true);
  const hintExpires = useRef(0);
  const say = (text: string) => { if (audioEnabled) void speak(text, { onError: () => {
    if (!mounted.current) return;
    void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error).catch(() => {});
    if (phaseRef.current === 'walk') finish('interrupted');
    else if (['prep','checking','fit','countdown'].includes(phaseRef.current)) { recorder.current?.disconnect(); phaseRef.current = 'error'; setPhase('error'); }
    setError('Could not play the voice. Check phone speech and volume settings, or use a helper with voice off.');
  } }); };
  function retry() {
    if (phaseRef.current !== 'error' || retryRequested.current) return;
    retryRequested.current = true;
    stopSpeaking(); setError(''); setHint(''); setConfirmStop(false); stopArmedUntil.current = 0;
    setAttempt(a => a + 1);
  }
  async function persist() {
    if (!pending.current || saveBusy.current) return;
    saveBusy.current = true; setSaving(true); setError('');
    try {
      await saveSession(pending.current);
      if (mounted.current) navigation.replace('Result', { sessionId: pending.current.id });
    } catch { if (mounted.current) setError('Your recording is still here. Saving failed. Free some phone storage, then tap Retry save.'); }
    finally { saveBusy.current = false; if (mounted.current) setSaving(false); }
  }
  function finish(reason: Recording['stopReason']) {
    if (phaseRef.current !== 'walk') return;
    phaseRef.current = 'done'; setPhase('done'); setHint('');
    const recording = recorder.current!.stop(reason);
    recording.setupCheck = { version: 'guided-fit-v2', anatomicalPlacementVerified: false, steadySeconds: 3, retries: attempt, language: getLanguage() };
    pending.current = { id: generateSessionId(), date: recording.startedAt, duration, isPractice,
      quality: recordingIssues(recording).length ? 'repeat' : 'good', windowCount: 0, windows: [], recording };
    say('Recording has ended. Stop safely, then check your phone.');
    void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success).catch(() => {});
    void persist();
  }
  function cancel() {
    if (phaseRef.current === 'walk') finish('user-stopped');
    else if (['prep', 'checking', 'fit', 'countdown', 'error'].includes(phaseRef.current)) {
      phaseRef.current = 'cancelled'; recorder.current?.disconnect(); stopSpeaking(); navigation.goBack();
    }
  }
  useEffect(() => {
    mounted.current = true; retryRequested.current = false;
    phaseRef.current = 'prep'; setPhase('prep'); setRemaining(placementSeconds);
    const engine = new SensorRecorder({ guidanceEnabled, voiceEnabled: audioEnabled }, () => {
      hintExpires.current = performance.now() + 6000;
      setHint('A turn may have happened. Take your time.');
      say('A turn may have happened. Take your time. Continue only if comfortable.');
    }, () => {
      hintExpires.current = performance.now() + 6000;
      setHint('The phone may be moving in its pouch. Check only when safely at rest.');
      say('The phone may be moving in its pouch. You can rest. Check it only when safely stopped.');
    });
    recorder.current = engine;
    engine.restoreFitCheck(passedFit.current);
    try { engine.connect(); }
    catch { phaseRef.current = 'error'; setPhase('error'); setError('Sensors could not start. Return to setup and try again.'); }
    let deadline = performance.now() + placementSeconds * 1000;
    let lastSecond = placementSeconds;
    let gate = new SettlingGate();
    const fit = new FitCheck();
    let fitComplete = !!passedFit.current;
    let checkStarted = 0;
    let lastSetupCue = 0;
    let directionExplained = false;
    if (phaseRef.current === 'prep') say(attempt > 0 ? 'You have 8 seconds to put the phone back. Stay comfortable.' : `You have ${placementSeconds} seconds to secure the phone in a snug belt pouch against your lower back, screen facing out. Then stand comfortably still, facing your clear path.`);
    const timer = setInterval(() => {
      const now = performance.now();
      if (now > stopArmedUntil.current) setConfirmStop(false);
      if (!['prep', 'checking', 'fit', 'countdown', 'walk'].includes(phaseRef.current)) return;
      const seconds = Math.max(0, Math.ceil((deadline - now) / 1000));
      setRemaining(seconds);
      if (phaseRef.current === 'prep') {
        if (attempt === 0 && seconds !== lastSecond && seconds === 5) say('Stand comfortably still. Five seconds.');
        if (seconds === 0) {
          phaseRef.current = 'checking'; setPhase('checking'); checkStarted = now; lastSetupCue = now;
          say('Recording your baseline. Stay comfortably still. No need to touch the screen.');
        }
      } else if (phaseRef.current === 'checking') {
          const motion = engine.motionStatus;
          const message = !engine.allReceiving || !motion.enough ? 'Waiting for continuous sensor readings…' : !motion.upright ? 'Phone angle is not ready. Check the pouch when comfortable.' : !motion.steady ? 'The phone is moving. Let it settle if comfortable.' : 'Recording your baseline…';
          setSetupMessage(message);
          if (gate.update(now, engine.allReceiving, motion) && engine.baselineReady) {
            if (!fitComplete) {
              engine.startFit(); phaseRef.current = 'fit'; setPhase('fit'); deadline = now + 45000; lastSetupCue = now;
              say('Take three comfortable steps forward, then stop. You can rest. No need to touch the phone.');
            } else {
              phaseRef.current = 'countdown'; setPhase('countdown'); deadline = now + 6000; lastSecond = 6;
              say('Phone check complete. Stay still. The walk starts shortly.');
            }
          } else if (now - checkStarted >= 20000) {
            engine.disconnect(); phaseRef.current = 'error'; setPhase('error');
            setError('The phone could not settle or readings were missing. No walk was started. Rest first, then check the pouch and try again.');
            say('The check could not finish. No walk has started. Please rest, then check the phone when safe.');
          } else if (now - lastSetupCue >= 8000) {
            lastSetupCue = now;
            say(!engine.allReceiving ? 'Still waiting for sensor readings. Please stay where you are.' : 'The phone is not steady or upright yet. Adjust only the pouch if comfortable. You can rest.');
          }
      } else if (phaseRef.current === 'fit') {
        const status = fit.update(now, engine.allReceiving, engine.motionStatus);
        if (status === 'review' || seconds === 0) {
          engine.disconnect(); phaseRef.current = 'error'; setPhase('error');
          const message = status === 'review' ? 'The phone may be moving in its pouch. No test started. Rest, then check the fit when safe.' : 'The movement and settling check did not finish. No test started. Rest and try again only when comfortable.';
          setError(message); say(message);
          void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning).catch(() => {});
        } else if (status === 'settled' && engine.baselineReady) {
          engine.finishFit(); passedFit.current = engine.savedFitCheck; fitComplete = true; gate = new SettlingGate();
          phaseRef.current = 'countdown'; setPhase('countdown'); deadline = now + 6000;
          say('Phone check complete. Stay still. The walk starts shortly.');
        } else if (now - lastSetupCue >= 15000) {
          lastSetupCue = now; say('After your comfortable steps, stop and let the phone settle. Rest if you need.');
        }
      } else if (phaseRef.current === 'countdown') {
        if (!engine.allReceiving || !engine.motionStatus.steady || !engine.motionStatus.upright || !engine.baselineReady) {
          gate = new SettlingGate(); phaseRef.current = 'checking'; setPhase('checking'); checkStarted = now; lastSetupCue = now;
          say('Waiting for the phone to settle again. Stay comfortable.');
        } else if (seconds === 0) {
          engine.begin(); phaseRef.current = 'walk'; setPhase('walk'); deadline = now + duration * 1000; setRemaining(duration);
          say('Begin walking at your comfortable pace.');
        } else if (seconds <= 3 && seconds !== lastSecond) say(String(seconds));
      } else {
        setDirectionReady(engine.guidanceReady);
        if (guidanceEnabled && !directionExplained && seconds <= duration - 3) {
          directionExplained = true;
          if (!engine.guidanceReady && now > hintExpires.current) say('Direction reminders are unavailable. Keep to your clear path only as comfortable.');
        }
        if (seconds !== lastSecond && seconds === Math.floor(duration / 2) && now > hintExpires.current) say('Take your time. You can stop whenever you need.');
        if (seconds === 0) finish('completed');
        if (now > hintExpires.current) setHint('');
      }
      lastSecond = seconds;
    }, 100);
    const app = AppState.addEventListener('change', state => {
      if (state === 'active') return;
      if (phaseRef.current === 'walk') finish('interrupted');
      else if (['prep', 'checking', 'fit', 'countdown'].includes(phaseRef.current)) {
        engine.disconnect(); phaseRef.current = 'error'; setPhase('error'); stopSpeaking();
        setError('Setup paused when the app left the screen. Return to setup when ready.');
      }
    });
    const back = BackHandler.addEventListener('hardwareBackPress', () => { cancel(); return true; });
    return () => {
      mounted.current = false; clearInterval(timer); app.remove(); back.remove(); engine.disconnect();
      // Let the hands-free completion cue finish across the transition to results.
      if (phaseRef.current !== 'done') stopSpeaking();
    };
  }, [attempt]);
  return <Screen eyebrow={['prep', 'checking', 'fit', 'countdown'].includes(phase) ? 'STEP 2 · HANDS-FREE SETUP' : 'STEP 3 · YOUR WALK'} title={phase === 'prep' ? 'Settle in. No rush.' : phase === 'checking' ? 'Checking the phone' : phase === 'fit' ? 'Three comfortable steps' : phase === 'countdown' ? 'Ready to begin' : phase === 'walk' ? 'Walk at your own pace' : 'Take a comfortable rest'} actions={
    phase === 'error' ? <><BigButton label="Retry this check" onPress={retry} /><BigButton label="Back to setup" variant="outline" onPress={cancel} /></> :
    phase === 'done' ? <BigButton label={error ? 'Retry save' : 'Saving recording…'} loading={saving} onPress={persist} /> :
    <BigButton label={confirmStop ? (phase === 'walk' ? 'Confirm stop and save' : 'Confirm back to setup') : (phase === 'walk' ? 'Stop and save' : 'Back to setup')} accessibilityHint="Tap, then confirm within five seconds. This prevents accidental pouch touches." variant={phase === 'walk' ? 'danger' : 'outline'} onPress={() => { if (performance.now() <= stopArmedUntil.current) { stopArmedUntil.current = 0; setConfirmStop(false); cancel(); } else { stopArmedUntil.current = performance.now() + 5000; setConfirmStop(true); } }} />
  }>
    {['prep', 'walk'].includes(phase) && <View style={s.timer}>
      <Text style={s.number}>{remaining}</Text><Text style={ui.label}>seconds {phase === 'prep' ? 'to place the phone' : 'remaining'}</Text>
      <View style={s.track}><View style={[s.progress, { width: `${(1 - remaining / (phase === 'prep' ? placementSeconds : duration)) * 100}%` }]} /></View>
    </View>}
    <Card>
      <Text accessible={false} style={s.arrow}>{phase === 'walk' ? '↑' : '•'}</Text>
      <Body>{phase === 'prep' ? 'Secure the phone at your lower back, screen facing out. Listen for the phone check, three comfortable steps and a stop, then the final countdown.' : phase === 'checking' ? setupMessage : phase === 'fit' ? 'Take three comfortable steps, then stop. Rest if needed. We are checking phone motion, not counting your steps.' : phase === 'countdown' ? `Stay comfortably still. Listen for begin. ${remaining} seconds.` : phase === 'walk' ? hint || 'Follow your clear path. Keep your eyes ahead.' : 'Recording stopped. Check your phone when safely settled.'}</Body>
      {phase === 'checking' && <Text style={ui.caption}>Checks sensor readings, phone angle and settling. Lower-back location cannot be verified.</Text>}
      {phase === 'walk' && <Text style={ui.caption}>{guidanceEnabled ? directionReady ? 'Gentle reminders on · arrow is a path reminder' : 'Direction estimate unavailable · walk only as comfortable' : 'Direction reminders off · arrow is a path reminder'}</Text>}
    </Card>
    <Body muted>{phase === 'walk' ? 'Rest whenever you need. Pauses are accepted and saved. Resume only if comfortable; the timer keeps running.' : 'No screen taps needed to continue. Controls require confirmation to prevent accidental touches. Contact and belt tightness cannot be verified.'}</Body>
    {phase === 'error' && <Body>Your settings are kept. You have 8 seconds to put the phone back before this check resumes.</Body>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Screen>;
}
const s = StyleSheet.create({ timer: { padding: 12, alignItems: 'center', gap: 6, backgroundColor: c.surfaceAlt, borderRadius: 24 }, number: { fontSize: 76, fontWeight: '700', color: c.primary, fontVariant: ['tabular-nums'] }, track: { height: 8, backgroundColor: c.border, width: '100%', borderRadius: 4, overflow: 'hidden', marginTop: 8 }, progress: { height: 8, backgroundColor: c.primary }, arrow: { fontSize: 42, textAlign: 'center', color: c.primary } });
