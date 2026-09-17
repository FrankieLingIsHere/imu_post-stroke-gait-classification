import { locale } from './language';
﻿import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import type { RecordingQuality, IMUWindow } from './sensorSim';
import type { Recording } from './recording';
export interface SessionRecord {
  id: string; date: string; duration: number; isPractice: boolean;
  quality: RecordingQuality; windowCount: number; windows: IMUWindow;
  recording?: Recording;
}
const LEGACY_KEY = 'gaitsteps:sessions';
const INDEX_KEY = 'gaitsteps:index:v2';
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
  await AsyncStorage.setItem(INDEX_KEY, JSON.stringify([...existing.filter(s => s.id !== session.id), { ...summary, windows: [] }]));
}
export async function getSessions(): Promise<SessionRecord[]> {
  const [current, raw] = await Promise.all([index(), AsyncStorage.getItem(LEGACY_KEY)]);
  const legacy: SessionRecord[] = raw ? JSON.parse(raw) : [];
  if (!Array.isArray(legacy)) throw new Error('Older recording history could not be read.');
  return [...current, ...legacy.filter(s => !current.some(n => n.id === s.id))].sort((a, b) => b.date.localeCompare(a.date));
}
export async function getSession(id: string): Promise<SessionRecord | undefined> {
  if ((await index()).some(s => s.id === id)) return JSON.parse(await FileSystem.readAsStringAsync(directory() + id + '.json'));
  return (await getSessions()).find(s => s.id === id);
}
export function formatSessionDate(date: string) { return new Date(date).toLocaleString(locale(), { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }); }
export function formatDuration(seconds: number) { return seconds + ' seconds'; }
