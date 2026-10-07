import { recoverParticipantProfiles, assignRecordingParticipant } from './participantLinks';
import { locale } from './language';
﻿import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import type { RecordingQuality, IMUWindow } from './sensorSim';
import type { Recording } from './recording';
import { parseReviewRecording, parseReviewRecordingCsv } from './reviewRecording';
import type { DistanceCalibration } from './distanceEstimation';
export type ParticipantSex = 'female' | 'male' | 'intersex' | 'prefer-not-to-say';
export interface ParticipantDemographics { ageYears: number | null; sex: ParticipantSex; heightCm?: number | null; }
export type AssistiveDevice = 'none' | 'single-point-cane' | 'quad-cane' | 'other';
export type ClinicalSide = 'left' | 'right' | 'bilateral' | 'unknown';
export interface ParticipantProfile {
  id: string; label: string; favorite: boolean; archived: boolean; createdAt: string; updatedAt: string;
  demographics: ParticipantDemographics & { weightKg?: number | null };
  distanceCalibration?: DistanceCalibration;
  clinical: { strokeType: string; lesionLocation: string; monthsSinceStroke: number | null; chronicityStatus?: 'known' | 'unknown'; affectedHemisphere?: ClinicalSide; affectedBodySide?: ClinicalSide; historySource?: 'patient-or-caregiver-report' | 'clinician-record'; premorbidGaitNotes: string; jointOrOrthopaedicNotes: string; assistiveDevice: AssistiveDevice };
}
export type AssessmentProtocol = 'research-walk' | '10mwt' | '2mwt' | '6mwt' | 'tug';
export interface AssessmentSetup {
  protocol: AssessmentProtocol; courseLengthM: number | null; timedDistanceM: number | null;
  protocolVariant?: '10mwt-12m-central10m-v1';
  trialNumber?: number | null;
  speedCondition: 'comfortable' | 'fast-safe'; turnDirection: 'left' | 'right' | 'self-selected';
}
export interface AssessmentForm {
  gaitAssessment?: import('./gaitAssessment').GaitAssessment;
  completed: boolean; completionStatus: 'completed' | 'modified' | 'not-completed';
  timedZoneSeconds: number | null; distanceWalkedM: number | null; lapCount: number | null;
  restCount: number; perceivedExertion: number | null; symptoms: string; clinicianNotes: string;
  observedGaitScore: number | null; observedGaitScale: string;
}
export interface SessionRecord {
  cameraTrial?:import('./cameraTrial').CameraTrial;
  googleDistanceTrial?:import('./googleDistanceTrial').GoogleDistanceTrial;
  id: string; date: string; duration: number; isPractice: boolean;
  quality: RecordingQuality; windowCount: number; windows: IMUWindow;
  demographics?: ParticipantDemographics;
  participantId?: string; participantLabel?: string;
  participantSnapshot?: ParticipantProfile;
  assessmentSetup?: AssessmentSetup;
  protocolExecution?: import('./protocolFlow').ProtocolExecution;
  assessment?: AssessmentForm & { speedMps: number | null; distanceSource: 'measured-course' | 'experimental-phone-estimate' | 'unavailable' };
  recording?: Recording;
  hasDeviceRecording?: boolean;
}
const LEGACY_KEY = 'gaitsteps:sessions';
const INDEX_KEY = 'gaitsteps:index:v2';
const PARTICIPANTS_KEY = 'gaitsteps:participants:v1';
export function generateSessionId() { return new Date().toISOString().replace(/[:.]/g, '-') + '-' + Math.random().toString(16).slice(2, 10); }
function directory() {
  if (!FileSystem.documentDirectory) throw new Error('Local recording storage is unavailable.');
  return FileSystem.documentDirectory + 'recordings/';
}
async function index(): Promise<SessionRecord[]> {
  const raw = await AsyncStorage.getItem(INDEX_KEY);
  if (!raw) return [];
  const parsed = JSON.parse(raw);
  if (!Array.isArray(parsed)) throw new Error('Recording index could not be read.');
  return parsed;
}
/** Separate raw files avoid AsyncStorage per-row limits. Same ID makes a save retry idempotent. */
export async function saveSession(session: SessionRecord) {
  await FileSystem.makeDirectoryAsync(directory(), { intermediates: true });
  await FileSystem.writeAsStringAsync(directory() + session.id + '.json', JSON.stringify(session));
  const existing = await index();
  const { recording, windows, ...summary } = session;
  await AsyncStorage.setItem(INDEX_KEY, JSON.stringify([...existing.filter(s => s.id !== session.id), { ...summary, windows: [], hasDeviceRecording: recording?.source === 'device' }]));
}
/** Import an app JSON export or raw long-format CSV into this phone's local history. */
export async function importReviewRecording(text: string, format: 'json' | 'csv' = 'json') {
  const session = format === 'csv' ? parseReviewRecordingCsv(text) : parseReviewRecording(text);
  await saveSession(session);
  return session.id;
}
export async function getSessions(): Promise<SessionRecord[]> {
  const [current, raw] = await Promise.all([index(), AsyncStorage.getItem(LEGACY_KEY)]);
  const legacy: SessionRecord[] = raw ? JSON.parse(raw) : [];
  if (!Array.isArray(legacy)) throw new Error('Older recording history could not be read.');
  return [...current, ...legacy.filter(s => !current.some(n => n.id === s.id))].sort((a, b) => b.date.localeCompare(a.date));
}
export async function getParticipants(): Promise<ParticipantProfile[]> {
  const raw = await AsyncStorage.getItem(PARTICIPANTS_KEY);
  const rows = raw ? JSON.parse(raw) : [];
  if (!Array.isArray(rows)) throw new Error('Participant list could not be read.');
  const valid=rows.filter((p): p is ParticipantProfile => !!p && typeof p.id === 'string' && typeof p.label === 'string' && !!p.demographics && !!p.clinical);
  const recovered=recoverParticipantProfiles(valid,await getSessions());
  if(recovered.length!==valid.length)await AsyncStorage.setItem(PARTICIPANTS_KEY,JSON.stringify(recovered));
  return recovered;
}
export async function saveParticipant(profile: ParticipantProfile): Promise<void> {
  const profiles = await getParticipants();
  await AsyncStorage.setItem(PARTICIPANTS_KEY, JSON.stringify([...profiles.filter(p => p.id !== profile.id), profile]));
}
export async function saveParticipantDistanceCalibration(id: string, calibration: DistanceCalibration): Promise<ParticipantProfile | undefined> {
  const profiles=await getParticipants(); const target=profiles.find(p=>p.id===id); if(!target)return undefined;
  const updated={...target,distanceCalibration:calibration,updatedAt:new Date().toISOString()};
  await AsyncStorage.setItem(PARTICIPANTS_KEY,JSON.stringify(profiles.map(p=>p.id===id?updated:p)));
  return updated;
}
export async function toggleParticipantFavorite(id: string): Promise<void> {
  const profiles = await getParticipants();
  const target = profiles.find(p => p.id === id);
  if (!target) return;
  await AsyncStorage.setItem(PARTICIPANTS_KEY, JSON.stringify(profiles.map(p => p.id === id ? { ...p, favorite: !p.favorite, updatedAt: new Date().toISOString() } : p)));
}
export async function archiveParticipant(id: string): Promise<void> {
  const profiles = await getParticipants();
  await AsyncStorage.setItem(PARTICIPANTS_KEY, JSON.stringify(profiles.map(p => p.id === id ? { ...p, archived: true, updatedAt: new Date().toISOString() } : p)));
}
export async function getSession(id: string): Promise<SessionRecord | undefined> {
  if ((await index()).some(s => s.id === id)) return JSON.parse(await FileSystem.readAsStringAsync(directory() + id + '.json'));
  return (await getSessions()).find(s => s.id === id);
}
export function formatSessionDate(date: string) { return new Date(date).toLocaleString(locale(), { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }); }
export function formatDuration(seconds: number) { return seconds + ' seconds'; }

export async function linkSessionParticipant(sessionId:string,participantId:string):Promise<SessionRecord> {
  const session=await getSession(sessionId),profile=(await getParticipants()).find(p=>p.id===participantId);
  if(!session||!profile)throw new Error('Recording or participant not found.');
  const linked=assignRecordingParticipant(session,profile);
  await saveSession(linked);
  return linked;
}
