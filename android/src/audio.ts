/**
 * audio.ts — expo-speech wrapper for Gait Steps
 *
 * Screens never call expo-speech directly.
 * All TTS goes through this module so we can:
 *   • Swap the engine later without touching screens
 *   • Enforce consistent speech options (language, rate, pitch)
 *   • Gracefully handle errors without crashing the UI
 *
 * Usage:
 *   import { speak, stopSpeaking, isSpeaking } from '../audio';
 *   await speak('Please place your phone on your lower back.');
 */

import * as Speech from 'expo-speech';
import { getLanguage, locale, translate } from './language';

let speechRequest = 0;
let queuedSpeech: Promise<void> = Promise.resolve();
let queueGeneration = 0;

export async function ensureVoice() {
  const language = getLanguage();
  const voices = await Speech.getAvailableVoicesAsync();
  const matching = voices.find(v => v.language.toLowerCase() === locale(language).toLowerCase())
    ?? voices.find(v => v.language.toLowerCase().split(/[-_]/)[0] === language);
  if (!matching) throw new Error('Voice unavailable in this language. Install a matching phone voice, or use a helper with voice off.');
  return matching;
}

// ─── Speech options ───────────────────────────────────────────────────────────

const DEFAULT_OPTIONS: Speech.SpeechOptions = {
  language: 'en-AU',   // Australian English — adjust to user locale if needed
  rate: 0.85,          // slightly slower than default for elderly users
  pitch: 1.0,
  volume: 1.0,
};

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Speak a text string aloud.
 * Stops any currently playing speech before starting the new utterance.
 *
 * @param text     The string to speak.
 * @param options  Optional overrides for language, rate, pitch, volume.
 * @returns        Promise that resolves when speech starts (not when it ends).
 */
export async function speak(
  text: string,
  options?: Partial<Speech.SpeechOptions>,
): Promise<void> {
  const request = ++speechRequest;
  try {
    // Stop any in-progress speech first to avoid overlap
    const speaking = await Speech.isSpeakingAsync();
    if (request !== speechRequest) return;
    if (speaking) {
      await Speech.stop();
    }
    if (request !== speechRequest) return;

    const voice = await ensureVoice();
    if (request !== speechRequest) return;
    Speech.speak(translate(text), {
      ...DEFAULT_OPTIONS,
      ...options,
      language: voice.language,
      voice: voice.identifier,
      onDone: () => { if (request === speechRequest) options?.onDone?.(); },
      onError: error => { if (request === speechRequest) options?.onError?.(error); },
    });
  } catch (error) {
    // Audio failure must never crash the app — log and continue silently
    console.warn('[audio] speak() failed:', error);
    if (request === speechRequest) options?.onError?.(error instanceof Error ? error : new Error(String(error)));
  }
}

/**
 * Speak after the current utterance finishes. This is for stage guidance where
 * cutting off an instruction is more confusing than waiting a moment. The
 * regular speak() API remains interruptible for countdown cues.
 */
export function speakQueued(text: string, options?: Partial<Speech.SpeechOptions>): Promise<void> {
  const generation = queueGeneration;
  const task = queuedSpeech.then(() => new Promise<void>(resolve => {
    if (generation !== queueGeneration) { resolve(); return; }
    let settled = false;
    const finish = () => { if (!settled) { settled = true; resolve(); } };
    void speak(text, {
      ...options,
      onDone: () => { options?.onDone?.(); finish(); },
      onError: error => { options?.onError?.(error); finish(); },
    });
    // A broken platform TTS callback must not block every later instruction.
    setTimeout(finish, 15000);
  }));
  queuedSpeech = task.catch(() => {});
  return task;
}

/**
 * Stop any currently playing speech immediately.
 */
export function stopSpeaking(): void {
  speechRequest += 1;
  queueGeneration += 1;
  queuedSpeech = Promise.resolve();
  try {
    void Speech.stop().catch(() => {});
  } catch (error) {
    console.warn('[audio] stopSpeaking() failed:', error);
  }
}

/**
 * Returns true if the TTS engine is currently speaking.
 * Safe to call at any time — returns false on error.
 */
export async function isSpeaking(): Promise<boolean> {
  try {
    return await Speech.isSpeakingAsync();
  } catch (error) {
    console.warn('[audio] isSpeaking() failed:', error);
    return false;
  }
}

// ─── Canned guidance phrases ──────────────────────────────────────────────────
// Centralised here so wording is consistent across screens.

export const PHRASES = {
  // Onboarding steps
  onboarding1:
    'Step 1. Place your phone on your lower back, just above your waistband, screen facing outward.',
  onboarding2:
    'Step 2. Secure the phone with a waistband, belt, or ask someone to hold it flat against your back.',
  onboarding3:
    'Step 3. Stand still for a moment so the phone can settle before you start walking.',
  onboarding4:
    'Step 4. Walk at your normal, comfortable pace. The app will stop recording automatically.',

  // Prepare screen
  prepareReady:
    'When you are ready, press Start. You will have 20 seconds to get into position before recording begins.',

  // Countdown cues (spoken at specific seconds remaining)
  countdown20: 'Get ready. Place the phone on your lower back now.',
  countdown15: '15 seconds.',
  countdown10: '10 seconds. Almost ready.',
  countdown5: '5.',
  countdown4: '4.',
  countdown3: '3.',
  countdown2: '2.',
  countdown1: '1.',
  countdownGo: 'Go! Walk at your normal pace.',

  // Recording
  recordingStart: 'Recording started. Walk at your normal comfortable pace.',
  recordingHalfway: 'Halfway there. Keep walking.',
  recordingDone: 'Recording complete. Please stop and stand still.',

  // Result
  resultGood: 'Great result. Your recording looks good.',
  resultAcceptable: 'Acceptable result. The recording is usable.',
  resultRepeat: 'Please try again. The recording quality was not clear enough.',
} as const;

export type PhraseKey = keyof typeof PHRASES;
