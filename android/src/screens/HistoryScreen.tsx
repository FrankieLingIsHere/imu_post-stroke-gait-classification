import React, { useCallback, useState } from 'react';
import { Alert, Platform, View, Pressable, Modal, useWindowDimensions } from 'react-native';
import { Text, t, useLanguage } from '../i18n';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { deleteSessions, getSessions, getSession, SessionRecord, formatSessionDate } from '../store';
import { shareRecordingsCSV } from '../export';
import { gaitReviewStatus, orderGaitReviews } from '../gaitAssessment';

export default function HistoryScreen({ navigation }: NativeStackScreenProps<RootStackParamList, 'History'>) {
  useLanguage();
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [page, setPage] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [manageOpen,setManageOpen]=useState(false);
  const { height, fontScale } = useWindowDimensions();
  const pageSize = height < 700 || fontScale > 1.3 ? 2 : 3;
  const load = useCallback(() => { let active = true; setLoading(true); setError('');
    getSessions().then(s => { if (active) { setSessions(orderGaitReviews(s)); setSelectedIds(ids => ids.filter(id => s.some(item => item.id === id))); setPage(0); } }).catch(() => { if (active) setError('Could not read your recordings. Please try again.'); }).finally(() => { if (active) setLoading(false); });
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
  function confirmDelete() {
    const ids=[...selectedIds];if(!ids.length||exporting)return;
    const message=t('Permanently delete {0} selected recordings and their videos? There is no undo.').replace('{0}',String(ids.length));
    async function remove(){setExporting(true);setError('');try{await deleteSessions(ids);setSelectedIds([]);setSessions(orderGaitReviews(await getSessions()));setPage(0);}catch{setError('Deletion did not finish. Please retry; some files may remain.');}finally{setExporting(false);}}
    if(Platform.OS==='web'){if(window.confirm(message))void remove();}
    else Alert.alert(t('Delete recorded data?'),message,[{text:t('Cancel'),style:'cancel'},{text:t('Delete permanently'),style:'destructive',onPress:()=>void remove()}]);
  }
  const pages = Math.max(1, Math.ceil(sessions.length / pageSize));
  const current = Math.min(page, pages - 1);
  return <Screen scrollKey={current} title="Recordings" actions={<>
    <BigButton label="Export or delete" labelStyle={{fontSize:18}} variant="outline" onPress={()=>setManageOpen(true)}/>
  </>}>
    <Modal visible={manageOpen} animationType="slide" onRequestClose={()=>setManageOpen(false)}>
    <Screen fullScreen title="Manage recordings" actions={<BigButton label="Done" onPress={()=>setManageOpen(false)}/>}>
    <Text style={ui.label}>{t('{0} recordings selected').replace('{0}',String(selectedIds.length))}</Text>
    <View style={ui.row}><BigButton style={ui.fill} label="Select all recordings" variant="outline" disabled={!sessions.length || exporting} onPress={() => setSelectedIds(sessions.map(s => s.id))} /><BigButton style={ui.fill} label="Clear selection" variant="outline" disabled={!selectedIds.length || exporting} onPress={() => setSelectedIds([])} /></View>
    <BigButton label={exporting ? 'Preparing CSV...' : 'Export selected CSV'} variant="outline" disabled={!selectedIds.length || exporting} onPress={() => { void exportSelected(); }} />
    <BigButton label="Delete selected recordings" variant="outline" disabled={!selectedIds.length || exporting} onPress={confirmDelete}/>
    <BigButton label="Storage" variant="ghost" disabled={exporting} onPress={()=>{setManageOpen(false);navigation.navigate('Storage');}}/>
    <BigButton label="Back to home" variant="ghost" onPress={() => {setManageOpen(false);navigation.popToTop();}} />
    {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
    </Screen></Modal>
    {!!sessions.some(s=>gaitReviewStatus(s).status==='pending')&&<Text style={ui.caption}>{t('{0} assessments to complete').replace('{0}',String(sessions.filter(s=>gaitReviewStatus(s).status==='pending').length))}</Text>}
    <Text style={ui.caption}>{loading ? t('Loading recordings…') : sessions.length ? t('Page {0} of {1}').replace('{0}',String(current+1)).replace('{1}',String(pages)) : t('Your first recording will appear here.')}</Text>
    {selectedIds.length > 0 && <Text style={ui.caption}>{t('{0} recordings selected').replace('{0}',String(selectedIds.length))}</Text>}
    {error && <><Text accessibilityRole="alert" style={ui.error}>{error}</Text><BigButton label="Try again" onPress={load} /></>}
    {sessions.slice(current * pageSize, (current + 1) * pageSize).map(s => <View key={s.id} style={{gap:8}}><Pressable accessibilityRole="button" accessibilityLabel={t(`Open ${formatSessionDate(s.date)}, ${s.duration} second ${s.isPractice ? 'practice' : 'walk'}`)} onPress={() => navigation.navigate('Details', { sessionId: s.id })}>
      <Card><View style={ui.row}><Pressable accessibilityRole="checkbox" accessibilityState={{ checked: selectedIds.includes(s.id) }} accessibilityLabel={`${selectedIds.includes(s.id) ? 'Deselect' : 'Select'} ${formatSessionDate(s.date)} for export`} style={[ui.choice, { flex: 0, minWidth: 58, paddingHorizontal: 8 }]} onPress={event => { event.stopPropagation(); toggleSelected(s.id); }}><Text style={ui.label}>{selectedIds.includes(s.id) ? '✓' : '○'}</Text></Pressable><Text style={[ui.label, ui.fill]}>{formatSessionDate(s.date)}</Text><Text style={ui.label}>›</Text></View><Body>{s.cameraTrial?t('Camera + IMU trial'):s.googleDistanceTrial?t('Google distance trial'): `${t('{0} sec planned').replace('{0}',String(s.duration))} · ${t(s.isPractice?'Practice':'Walk')}`}</Body>{s.googleDistanceTrial&&<Text style={ui.caption}>{t('Measured reference route: {0} m').replace('{0}',String(s.googleDistanceTrial.referenceDistanceM))}</Text>}<Text style={ui.caption}>{s.participantId?s.participantLabel||s.participantId:t('Needs participant assignment')}</Text></Card>
    </Pressable>
      {gaitReviewStatus(s).required&&<BigButton label={gaitReviewStatus(s).complete?'G.A.I.T. complete — review':'Complete required G.A.I.T. assessment'} variant="outline" onPress={()=>navigation.navigate('Assessment',{sessionId:s.id})}/>}
    </View>)}
    {pages>1&&<View style={ui.row}><BigButton style={ui.fill} label="Previous" variant="outline" disabled={current === 0} onPress={() => setPage(current - 1)} /><BigButton style={ui.fill} label="Next" variant="outline" disabled={current + 1 >= pages} onPress={() => setPage(current + 1)} /></View>}
  </Screen>;
}
