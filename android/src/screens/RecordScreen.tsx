import ClinicalCapture from '../components/ClinicalCapture';
import { protocolFlows,clinicalInterrupted,clinicalLimit,type ProtocolExecution } from '../protocolFlow';
import React, { useEffect, useRef, useState } from 'react';
import { View, AppState, BackHandler, StyleSheet, Platform, ActivityIndicator } from 'react-native';
import { Text } from '../i18n';
import { getLanguage } from '../language';
import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake';
import * as Haptics from 'expo-haptics';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours as c } from '../theme';
import { speak, speakQueued, stopSpeaking, discardPendingSpeech } from '../audio';
import { SensorRecorder } from '../sensors';
import { recordingIssues } from '../recording';
import type { Recording } from '../recording';
import { getSessions, saveSession, generateSessionId, SessionRecord } from '../store';
import { SettlingGate } from '../movement';
import { describeMovement, walkFeedback } from '../movement';
import { spokenWalkFeedback } from '../patientSummary';
import { FitCheck } from '../placement';
import * as Location from 'expo-location';
import { ForegroundDistanceTracker } from '../locationDistance';
import { GoogleRecordingCapture } from '../googleRecording';
import { googleRecordingBridge } from '../googleRecordingBridge';

const ProgressIndicator: React.ComponentType<any> = ActivityIndicator ?? View;

export default function RecordScreen({ navigation, route }: NativeStackScreenProps<RootStackParamList, 'Record'>) {
  useEffect(() => {
    const tag = 'gait-recording-' + Date.now(); let disposed = false;
    void activateKeepAwakeAsync(tag).then(() => { if (disposed) void deactivateKeepAwake(tag).catch(() => {}); }).catch(() => {});
    return () => { disposed = true; void deactivateKeepAwake(tag).catch(() => {}); };
  }, []);
  const { duration, isPractice, audioEnabled, guidanceEnabled, useGpsDistance, useGoogleDistance, demographics, participantId, participantLabel, participantSnapshot, assessmentSetup } = route.params;
  const protocol=assessmentSetup?.protocol??'research-walk';
  const clinical=protocol!=='research-walk';
  const execution=useRef<ProtocolExecution>();
  const startLocationRef=useRef<()=>void>(()=>{});
  const [attempt, setAttempt] = useState(0);
  const passedFit = useRef<Recording['fitCheck']>();
  const retryRequested = useRef(false);
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
  const locationTrackerRef = useRef<ForegroundDistanceTracker | null>(null);
  const locationSubscriptionRef = useRef<Location.LocationSubscription | null>(null);
  const googleCaptureRef = useRef<GoogleRecordingCapture | null>(null);
  const googleReadPending = useRef(false);
  const pending = useRef<SessionRecord | null>(null);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const saveBusy = useRef(false);
  const mounted = useRef(true);
  const hintExpires = useRef(0);
  const say = (text: string, options?: Parameters<typeof speak>[1], interrupt = false): Promise<void> => { if (!audioEnabled) return Promise.resolve(); if (interrupt) stopSpeaking(); const talk = interrupt ? speak : speakQueued; return talk(text, { ...options, onError: () => {
    if (!mounted.current) return;
    void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error).catch(() => {});
    if (['walk','clinical'].includes(phaseRef.current)) finish('interrupted');
    else if (['prep','checking','fit','countdown','waiting','clinical-ready'].includes(phaseRef.current)) { recorder.current?.disconnect(); phaseRef.current = 'error'; setPhase('error'); }
    setError('Could not play the voice. Check phone speech and volume settings, or use a helper with voice off.');
  } }); };
  useEffect(() => {
    if (phase === 'error' || phase === 'cancelled') void googleCaptureRef.current?.cancel();
  }, [phase]);
  function retry() {
    if (phaseRef.current !== 'error' || retryRequested.current) return;
    retryRequested.current = true;
    stopSpeaking(); setError(''); setHint(''); setConfirmStop(false); stopArmedUntil.current = 0;
    setAttempt(a => a + 1);
  }
  async function persist() {
    if (!pending.current || saveBusy.current || googleReadPending.current) return;
    saveBusy.current = true; setSaving(true); setError('');
    try {
      await saveSession(pending.current);
      if (mounted.current) navigation.replace('Result', { sessionId: pending.current.id });
    } catch { if (mounted.current) setError('Your recording is still here. Saving failed. Free some phone storage, then tap Retry save.'); }
    finally { saveBusy.current = false; if (mounted.current) setSaving(false); }
  }
  function finish(reason: Recording['stopReason']) {
    if (!['walk','clinical'].includes(phaseRef.current)) return;
    phaseRef.current = 'done'; setPhase('done'); setHint('');
    locationSubscriptionRef.current?.remove(); locationSubscriptionRef.current = null;
    const recording = recorder.current!.stop(reason);
    if(clinical&&!execution.current)execution.current={version:'protocol-flow-v1',protocol,goOffsetMs:null,goSource:audioEnabled?'speech-start-callback':'automatic-silent-cue',elapsedFromGoSeconds:null,end:'interrupted',clinicalOutcomeVerified:false};
    if(clinical&&execution.current&&reason!=='completed')execution.current={...execution.current,end:execution.current.end==='capture-limit'?'capture-limit':'interrupted',elapsedFromGoSeconds:execution.current.goOffsetMs===null?null:Math.max(0,recording.elapsedSeconds-execution.current.goOffsetMs/1000)};
    if (locationTrackerRef.current) recording.locationDistance = locationTrackerRef.current.finish();
    recording.setupCheck = { version: 'guided-fit-v2', anatomicalPlacementVerified: false, steadySeconds: 5, retries: attempt, language: getLanguage() };
    pending.current = { id: generateSessionId(), date: recording.startedAt, duration, isPractice, demographics,
      quality: recordingIssues(recording).length ? 'repeat' : 'good', windowCount: 0, windows: [], recording,
      participantId, participantLabel, participantSnapshot, assessmentSetup, protocolExecution:execution.current,
      assessment: { completed: false, completionStatus: 'not-completed', timedZoneSeconds: null, distanceWalkedM: null, lapCount: null, restCount: 0, perceivedExertion: null, symptoms: '', clinicianNotes: '', observedGaitScore: null, observedGaitScale: '', speedMps: null, distanceSource: 'unavailable' } };
    const previousWalk = async () => {
      if (!participantId || isPractice) return null;
      const sessions = await getSessions();
      const aid = participantSnapshot?.clinical.assistiveDevice;
      const currentProtocol = assessmentSetup?.protocol ?? 'research-walk';
      return sessions.filter(s => s.participantId === participantId && !s.isPractice && !!s.recording && s.duration === duration && (s.assessmentSetup?.protocol ?? 'research-walk') === currentProtocol && s.participantSnapshot?.clinical.assistiveDevice === aid)
        .sort((a,b) => b.date.localeCompare(a.date))[0]?.recording ?? null;
    };
    if(clinical) {
      discardPendingSpeech();
      void say(execution.current?.end==='capture-limit'?clinicalLimit:execution.current?.end==='interrupted'?clinicalInterrupted:protocolFlows[protocol].finish);
    } else void previousWalk().then(previous => {
      const message = spokenWalkFeedback(describeMovement(recording), previous ? describeMovement(previous) : null);
      say(message);
    }).catch(() => say(spokenWalkFeedback(describeMovement(recording), null)));
    void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success).catch(() => {});
    const scheduleSave = () => { if (mounted.current) saveTimer.current = setTimeout(() => { saveTimer.current = null; void persist(); }, 1800); };
    if (googleCaptureRef.current) {
      googleReadPending.current = true; setSaving(true);
      const finishedAt = Date.now();
      void googleCaptureRef.current.finish(finishedAt).then(summary => { recording.googleRecording = summary; })
        .finally(() => { googleReadPending.current = false; scheduleSave(); });
    } else scheduleSave();
  }
  function cancel() {
    if (['walk','clinical'].includes(phaseRef.current)) finish('user-stopped');
    else if (['prep', 'checking', 'fit', 'countdown', 'waiting', 'clinical-ready', 'error'].includes(phaseRef.current)) {
      phaseRef.current = 'cancelled'; recorder.current?.disconnect(); stopSpeaking(); navigation.goBack();
    }
  }
  useEffect(() => {
    mounted.current = true; retryRequested.current = false; execution.current=undefined;
    phaseRef.current = 'prep'; setPhase('prep'); setRemaining(0);
    const engine = new SensorRecorder({ guidanceEnabled:guidanceEnabled&&!clinical, voiceEnabled: audioEnabled }, () => {
      if(clinical)return;
      hintExpires.current = performance.now() + 6000;
      setHint('A turn may have happened. Take your time.');
      say('A turn may have happened. Take your time. Continue only if comfortable.');
    }, () => {
      if(clinical)return;
      hintExpires.current = performance.now() + 6000;
      setHint('The phone may be moving in its pouch. Check only when safely at rest.');
      say('The phone may be moving in its pouch. You can rest. Check it only when safely stopped.');
    });
    recorder.current = engine;
    engine.restoreFitCheck(passedFit.current);
    try { engine.connect(); }
    catch { phaseRef.current = 'error'; setPhase('error'); setError('Sensors could not start. Return to setup and try again.'); }
    let deadline = performance.now();
    let lastSecond = 0;
    let gate = new SettlingGate(5000);
    const fit = new FitCheck();
    let fitComplete = !!passedFit.current;
    let checkStarted = 0;
    let lastSetupCue = 0;
    let directionExplained = false;
    let walkArmedAt = 0;
    let countdownIntroPending = false;
    let fitIntroPending = false;
    let fitStopSpoken = false;
    let prepIntroPending = true;
    let disposed = false;
    if (useGoogleDistance) {
      const bridge = googleRecordingBridge();
      googleCaptureRef.current = bridge ? new GoogleRecordingCapture(bridge) : null;
      if (googleCaptureRef.current) void googleCaptureRef.current.prepare();
    }
    locationTrackerRef.current = useGpsDistance ? new ForegroundDistanceTracker() : null;
    let locationStartRequested = false;
    const startLocation = () => {
      if (!locationTrackerRef.current || locationStartRequested) return;
      locationStartRequested = true;
      void Location.watchPositionAsync({ accuracy: Location.Accuracy.High, timeInterval: 1000, distanceInterval: 1 }, position => {
        locationTrackerRef.current?.add({ latitude: position.coords.latitude, longitude: position.coords.longitude, accuracy: position.coords.accuracy, timestamp: position.timestamp });
      }).then(subscription => {
        if (!['walk','clinical'].includes(phaseRef.current) || disposed) subscription.remove();
        else locationSubscriptionRef.current = subscription;
      }).catch(() => { /* IMU recording continues; the saved location summary will show unavailable. */ });
    };
    startLocationRef.current=startLocation;
    const enterCountdown = (now: number, introduction: string) => {
      if(clinical){engine.preserveSetupBaseline();discardPendingSpeech();phaseRef.current='clinical-ready';setPhase('clinical-ready');return;}
      phaseRef.current = 'countdown'; setPhase('countdown'); deadline = now + 9000; lastSecond = 9; countdownIntroPending = true;
      discardPendingSpeech();
      void say(introduction).finally(() => {
        if (disposed || phaseRef.current !== 'countdown' || !countdownIntroPending) return;
        countdownIntroPending = false; deadline = performance.now() + 9000; lastSecond = 9; setRemaining(9);
      });
    };
    if (phaseRef.current === 'prep') {
      void say(attempt > 0 ? 'Take your time to put the phone back. When it is secure, stand still. I will wait for the phone check.' : 'Take your time. Put the phone horizontally in the middle of your lower back, screen facing out. Keep it snug, then stand still. The check will begin when the instruction finishes.').finally(() => {
        if (disposed || phaseRef.current !== 'prep') return;
        prepIntroPending = false; phaseRef.current = 'checking'; setPhase('checking'); checkStarted = performance.now(); lastSetupCue = performance.now();
        say('Phone check. Keep the phone horizontal at the centre of your lower back, screen facing out. Stand still and do not touch the phone.');
      });
    }
    const timer = setInterval(() => {
      const now = performance.now();
      if (now > stopArmedUntil.current) setConfirmStop(false);
      if (!['prep', 'checking', 'fit', 'countdown', 'waiting', 'walk'].includes(phaseRef.current)) return;
      const seconds = Math.max(0, Math.ceil((deadline - now) / 1000));
      setRemaining(phaseRef.current === 'waiting' ? duration : seconds);
      if (phaseRef.current === 'prep') {
        // TTS engines can take 1–2 seconds to start. Cue slightly early so the
        // spoken five-second warning lands near the visible five-second mark.
        if (prepIntroPending) return;
        if (seconds === 0) {
          phaseRef.current = 'checking'; setPhase('checking'); checkStarted = now; lastSetupCue = now;
          say('Phone check. Keep it horizontal at the centre of your lower back, screen facing out. Stand still and do not touch the phone.');
        }
      } else if (phaseRef.current === 'checking') {
          const motion = engine.motionStatus;
          const message = !engine.allReceiving || !motion.enough ? 'Waiting for continuous sensor readings…' : !motion.upright ? 'Phone angle is not ready. Check the pouch when comfortable.' : !motion.steady ? 'The phone is moving. Let it settle if comfortable.' : 'Recording your baseline…';
          setSetupMessage(message);
          if (gate.update(now, engine.allReceiving, motion) && engine.baselineReady) {
            if (!fitComplete) {
              engine.preserveSetupBaseline();
              phaseRef.current = 'fit'; setPhase('fit'); deadline = Number.POSITIVE_INFINITY; lastSetupCue = now;
              fitIntroPending = true; discardPendingSpeech();
              void say('Baseline check complete. Move comfortably for a short moment. When you hear stop, stop and stand still until I say the movement check is complete. You can rest; do not touch the phone.').finally(() => {
                if (disposed || phaseRef.current !== 'fit') return;
                engine.startFit(); fitIntroPending = false; deadline = Number.POSITIVE_INFINITY; lastSetupCue = performance.now();
              });
            } else {
              enterCountdown(now, 'Phone check complete. Stay still. The walk starts shortly.');
            }
          } else if (now - lastSetupCue >= 8000) {
            lastSetupCue = now;
            say(!engine.allReceiving ? 'Still waiting for sensor readings. Please stay where you are.' : 'The phone is not steady or horizontal yet. Adjust only the pouch if comfortable. You can rest.');
          }
      } else if (phaseRef.current === 'fit') {
        if (fitIntroPending) return;
        const status = fit.update(now, engine.allReceiving, engine.motionStatus);
        if(fit.readyToSettle&&!fitStopSpoken){fitStopSpoken=true;void say('Stop comfortably now. Stand still while the movement check finishes.');}
        if (status === 'review') {
          engine.disconnect(); phaseRef.current = 'error'; setPhase('error');
          const message = 'The phone may be moving in its pouch. No test started. Rest, then check the fit when safe.';
          setError(message); say(message);
          void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning).catch(() => {});
        } else if (status === 'settled' && engine.baselineReady) {
          engine.finishFit(); passedFit.current = engine.savedFitCheck; fitComplete = true; gate = new SettlingGate(5000);
          enterCountdown(now, 'Movement check complete. Stop and stand still. The recording will start shortly.');
        }
      } else if (phaseRef.current === 'countdown') {
        if (countdownIntroPending) {
          setRemaining(9);
          return;
        }
        if (!engine.allReceiving || !engine.motionStatus.steady || !engine.motionStatus.upright || !engine.baselineReady) {
          gate = new SettlingGate(5000); phaseRef.current = 'checking'; setPhase('checking'); checkStarted = now; lastSetupCue = now;
          say('Waiting for the phone to settle again. Stay comfortable.');
        } else if (seconds === 0) {
          phaseRef.current = 'waiting'; setPhase('waiting'); walkArmedAt = now; setRemaining(duration);
          say('Begin walking now. The recording starts when you take your first step.');
        } else if (seconds <= 5 && seconds !== lastSecond) {
          // The displayed value and this cue use the same ceil() boundary. Keep
          // each cue to one short number so TTS cannot run into the next tick.
          say(String(seconds), { rate: 1.1 }, true);
        }
      } else if (phaseRef.current === 'waiting') {
        // Keep subscriptions alive but do not start the saved recording clock
        // until motion begins. This removes the confusing idle lead-in.
        if (engine.allReceiving && engine.motionStatus.enough && !engine.motionStatus.steady && engine.motionStatus.context === 'movement' && engine.candidateStepsAfter(walkArmedAt) >= 1) {
          engine.begin(); googleCaptureRef.current?.begin(Date.now()); phaseRef.current = 'walk'; setPhase('walk'); deadline = now + duration * 1000; setRemaining(duration); startLocation();
          // The preceding “Begin walking now” cue is the start announcement.
          // Do not replace it immediately when the first step is detected.
        } else if (now - walkArmedAt >= 15000) {
          engine.disconnect(); phaseRef.current = 'error'; setPhase('error');
          setError('No walking movement was detected. Rest, then try again when you are ready.');
          say('No walking movement was detected. No recording was saved. Rest, then try again when ready.');
        }
      } else {
        if (Platform.OS === 'web' && !engine.allReceiving) { finish('interrupted'); return; }
        setDirectionReady(engine.guidanceReady);
        if (guidanceEnabled && !directionExplained && seconds <= duration - 3) {
          directionExplained = true;
          if (!engine.guidanceReady && now > hintExpires.current) say('Direction reminders are unavailable. Keep to your clear path only as comfortable.');
        }
        if (seconds !== lastSecond && seconds === Math.floor(duration / 2) && now > hintExpires.current) {
          const feedback = walkFeedback(engine.motionStatus);
          if (feedback === 'encourage') say('You are doing well. Keep a comfortable pace, and stop whenever you need.');
          else if (feedback === 'pause') say('It is okay to rest. Start again only when you feel ready.');
          else if (feedback === 'handling') say('Please stop safely before checking the phone. Keep walking only when the phone is secure.');
        }
        if (seconds === 0) finish('completed');
        if (now > hintExpires.current) setHint('');
      }
      lastSecond = seconds;
    }, 100);
    const app = AppState.addEventListener('change', state => {
      if (state === 'active') return;
      if (['walk','clinical'].includes(phaseRef.current)) finish('interrupted');
      else if (['prep', 'checking', 'fit', 'countdown', 'waiting','clinical-ready'].includes(phaseRef.current)) {
        engine.disconnect(); phaseRef.current = 'error'; setPhase('error'); stopSpeaking();
        setError('Setup paused when the app left the screen. Return to setup when ready.');
      }
    });
    const hidden = () => {
      if (document.visibilityState === 'visible') return;
      if (['walk','clinical'].includes(phaseRef.current)) finish('interrupted');
      else if (['prep','checking','fit','countdown','waiting','clinical-ready'].includes(phaseRef.current)) {
        engine.disconnect(); phaseRef.current = 'error'; setPhase('error'); stopSpeaking();
        setError('Setup paused when the app left the screen. Return to setup when ready.');
      }
    };
    if (Platform.OS === 'web') document.addEventListener('visibilitychange', hidden);
    const back = BackHandler.addEventListener('hardwareBackPress', () => { cancel(); return true; });
    return () => {
      disposed = true; locationSubscriptionRef.current?.remove(); locationSubscriptionRef.current = null; locationTrackerRef.current = null;
      if (googleCaptureRef.current) void googleCaptureRef.current.cancel(); googleCaptureRef.current = null;
      mounted.current = false; if (saveTimer.current) { clearTimeout(saveTimer.current); saveTimer.current = null; } if (Platform.OS === 'web') document.removeEventListener('visibilitychange', hidden); clearInterval(timer); app.remove(); back.remove(); engine.disconnect();
      // Let the hands-free completion cue finish across the transition to results.
      if (phaseRef.current !== 'done') stopSpeaking();
    };
  }, [attempt]);
  if(clinical&&['clinical-ready','clinical'].includes(phase))return <ClinicalCapture protocol={protocol} audioEnabled={audioEnabled} say={say}
    receiving={()=>recorder.current?.allReceiving===true}
    motion={()=>recorder.current!.motionStatus}
    onBegin={()=>{recorder.current!.begin();phaseRef.current='clinical';setPhase('clinical');startLocationRef.current();}}
    onGo={offset=>{googleCaptureRef.current?.begin(Date.now());execution.current={version:'protocol-flow-v1',protocol,goOffsetMs:offset,goSource:audioEnabled?'speech-start-callback':'automatic-silent-cue',elapsedFromGoSeconds:0,end:'interrupted',clinicalOutcomeVerified:false};}}
    onFinish={value=>{execution.current=value;finish(value.end==='interrupted'||value.end==='capture-limit'?'interrupted':'completed');}}
    onCancel={cancel}/>;
  return <Screen eyebrow={['prep', 'checking', 'fit', 'countdown', 'waiting'].includes(phase) ? 'STEP 2 · HANDS-FREE SETUP' : 'STEP 3 · YOUR WALK'} title={phase === 'prep' ? 'Settle in. No rush.' : phase === 'checking' ? 'Checking the phone' : phase === 'fit' ? 'Short movement check' : ['countdown','waiting'].includes(phase) ? 'Ready to begin' : phase === 'walk' ? 'Walk at your own pace' : 'Take a comfortable rest'} actions={
    phase === 'error' ? <><BigButton label="Retry this check" onPress={retry} /><BigButton label="Back to setup" variant="outline" onPress={cancel} /></> :
    phase === 'done' ? <BigButton label={error ? 'Retry save' : 'Saving recording…'} loading={saving} onPress={persist} /> :
    <BigButton label={confirmStop ? (phase === 'walk' ? 'Confirm stop and save' : 'Confirm back to setup') : (phase === 'walk' ? 'Stop and save' : 'Back to setup')} accessibilityHint="Tap, then confirm within five seconds. This prevents accidental pouch touches." variant={phase === 'walk' ? 'danger' : 'outline'} onPress={() => { if (performance.now() <= stopArmedUntil.current) { stopArmedUntil.current = 0; setConfirmStop(false); cancel(); } else { stopArmedUntil.current = performance.now() + 5000; setConfirmStop(true); } }} />
  }>
    {['prep', 'walk'].includes(phase) && <View style={s.timer}>
      {phase === 'prep' ? <Text style={ui.label}>Take your time to place the phone</Text> : phase === 'checking' ? <Text style={ui.label}>Checking live sensors</Text> : <><Text style={s.number}>{remaining}</Text><Text style={ui.label}>seconds remaining</Text></>}
      <View style={s.track}><View style={[s.progress, { width: phase === 'prep' ? '0%' : `${(1 - remaining / duration) * 100}%` }]} /></View>
    </View>}
    <Card>
      <Text accessible={false} style={s.arrow}>{phase === 'walk' ? '↑' : '•'}</Text>
      {['checking', 'fit', 'countdown', 'waiting'].includes(phase) && <ProgressIndicator size="large" color={c.primary} style={s.progressIndicator} />}
      <Body>{phase === 'prep' ? 'Take your time to place the phone. Keep it horizontal at your lower back, screen facing out, then stand still. The phone check waits for you.' : phase === 'checking' ? setupMessage : phase === 'fit' ? 'Move comfortably for a short moment, then stop and stand still until the movement check is complete. Rest if needed. We are checking phone motion, not counting your steps.' : phase === 'countdown' ? `Stay comfortably still. Do not walk until you hear begin. ${remaining} seconds.` : phase === 'waiting' ? 'Begin walking now. The recording starts when your first step is detected.' : phase === 'walk' ? hint || protocolFlows[protocol].active : 'Recording stopped. Check your phone when safely settled.'}</Body>
      {phase === 'checking' && <Text style={ui.caption}>Checks sensor readings, phone angle and settling. Lower-back location cannot be verified.</Text>}
      {phase === 'walk' && <Text style={ui.caption}>{guidanceEnabled ? directionReady ? 'Gentle reminders on · arrow is a path reminder' : 'Direction estimate unavailable · walk only as comfortable' : 'Direction reminders off · arrow is a path reminder'}</Text>}
    </Card>
    <Body muted>{phase === 'walk' ? 'Rest whenever you need. Pauses are accepted and saved. Resume only if comfortable; the timer keeps running.' : 'No screen taps needed to continue. Controls require confirmation to prevent accidental touches. Contact and belt tightness cannot be verified.'}</Body>
    {phase === 'error' && <Body>Your settings are kept. Put the phone back when you are ready, then retry the check.</Body>}
    {phase === 'done' && googleReadPending.current && <Body>Walking has finished. Checking for delayed Google records before saving. You can rest.</Body>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Screen>;
}
const s = StyleSheet.create({ timer: { padding: 12, alignItems: 'center', gap: 6, backgroundColor: c.surfaceAlt, borderRadius: 24 }, number: { fontSize: 76, fontWeight: '700', color: c.primary, fontVariant: ['tabular-nums'] }, track: { height: 8, backgroundColor: c.border, width: '100%', borderRadius: 4, overflow: 'hidden', marginTop: 8 }, progress: { height: 8, backgroundColor: c.primary }, arrow: { fontSize: 42, textAlign: 'center', color: c.primary }, progressIndicator: { marginVertical: 10 } });
