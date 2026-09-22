import React, { useCallback, useState } from 'react';
import { View, Pressable, useWindowDimensions } from 'react-native';
import { Text, t, useLanguage } from '../i18n';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { getSessions, getSession, SessionRecord, formatSessionDate } from '../store';
import { shareRecordingsCSV } from '../export';

export default function HistoryScreen({ navigation }: NativeStackScreenProps<RootStackParamList, 'History'>) {
  useLanguage();
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [page, setPage] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const { height, fontScale } = useWindowDimensions();
  const pageSize = height < 700 || fontScale > 1.3 ? 2 : 3;
  const load = useCallback(() => { let active = true; setLoading(true); setError('');
    getSessions().then(s => { if (active) { setSessions(s); setSelectedIds(ids => ids.filter(id => s.some(item => item.id === id))); setPage(0); } }).catch(() => { if (active) setError('Could not read your recordings. Please try again.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  useFocusEffect(load);
  function toggleSelected(id: string) { setSelectedIds(ids => ids.includes(id) ? ids.filter(item => item !== id) : [...ids, id]); }
  async function exportSelected() {
    if (!selectedIds.length || exporting) return;
    setExporting(true); setError('');
    try {
      const full = (await Promise.all(selectedIds.map(id => getSession(id)))).filter((s): s is SessionRecord => !!s);
      await shareRecordingsCSV(full);
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not export recordings.'); }
    finally { setExporting(false); }
  }
  const pages = Math.max(1, Math.ceil(sessions.length / pageSize));
  const current = Math.min(page, pages - 1);
  return <Screen eyebrow="SAVED ON THIS PHONE" title="Every walk, in one place" actions={<>
    <View style={ui.row}><BigButton style={ui.fill} label="Previous" variant="outline" disabled={current === 0} onPress={() => setPage(current - 1)} /><BigButton style={ui.fill} label="Next" variant="outline" disabled={current + 1 >= pages} onPress={() => setPage(current + 1)} /></View>
    <View style={ui.row}><BigButton style={ui.fill} label="Select all recordings" variant="outline" disabled={!sessions.length || exporting} onPress={() => setSelectedIds(sessions.map(s => s.id))} /><BigButton style={ui.fill} label="Clear selection" variant="outline" disabled={!selectedIds.length || exporting} onPress={() => setSelectedIds([])} /></View>
    <BigButton label={exporting ? 'Preparing CSV...' : 'Export selected CSV'} variant="outline" disabled={!selectedIds.length || exporting} onPress={() => { void exportSelected(); }} />
    <BigButton label="Back to home" variant="ghost" onPress={() => navigation.popToTop()} />
  </>}>
    <Body muted>{loading ? 'Loading recordings…' : sessions.length ? `Page ${current + 1} of ${pages} · Choose recordings to export, or tap a walk to explore` : 'Your first recording will appear here.'}</Body>
    {sessions.length > 0 && <Text style={ui.caption}>{selectedIds.length} recordings selected for export.</Text>}
    {error && <><Text accessibilityRole="alert" style={ui.error}>{error}</Text><BigButton label="Try again" onPress={load} /></>}
    {sessions.slice(current * pageSize, (current + 1) * pageSize).map(s => <Pressable key={s.id} accessibilityRole="button" accessibilityLabel={t(`Open ${formatSessionDate(s.date)}, ${s.duration} second ${s.isPractice ? 'practice' : 'walk'}`)} onPress={() => navigation.navigate('Details', { sessionId: s.id })}>
      <Card><View style={ui.row}><Pressable accessibilityRole="checkbox" accessibilityState={{ checked: selectedIds.includes(s.id) }} accessibilityLabel={`${selectedIds.includes(s.id) ? 'Deselect' : 'Select'} ${formatSessionDate(s.date)} for export`} style={[ui.choice, { flex: 0, minWidth: 58, paddingHorizontal: 8 }]} onPress={event => { event.stopPropagation(); toggleSelected(s.id); }}><Text style={ui.label}>{selectedIds.includes(s.id) ? '✓' : '○'}</Text></Pressable><Text style={[ui.label, ui.fill]}>{formatSessionDate(s.date)}</Text><Text style={ui.label}>›</Text></View><Body>{s.duration} sec planned · {s.isPractice ? 'Practice' : 'Walk'}</Body><Text style={ui.caption}>View signals, sensors and export</Text></Card>
    </Pressable>)}
  </Screen>;
}
