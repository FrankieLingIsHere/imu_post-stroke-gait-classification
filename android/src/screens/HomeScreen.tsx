import React from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import ReviewImport from '../components/ReviewImport';
import { Text, LanguagePicker } from '../i18n';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours as c } from '../theme';
import PwaInstall from '../components/PwaInstall';
export default function HomeScreen({ navigation }: NativeStackScreenProps<RootStackParamList, 'Home'>) {
  return <Screen eyebrow="YOUR DAILY WALK" title={'A little walk.\nAt your pace.'} actions={<>
    <BigButton label="Start a walk" onPress={() => navigation.navigate('Prepare', { duration: 20, audioEnabled: true, isPractice: false })} />
    <BigButton label="My recordings" variant="outline" onPress={() => navigation.navigate('History')} />
    <BigButton label="How to use the app" variant="ghost" onPress={() => navigation.navigate('Onboarding')} />
  </>}>
    <LanguagePicker />
    {Platform.OS === 'web' && <PwaInstall />}
    <View style={s.hero}><Text style={s.arrow} accessible={false}>↑</Text><Text style={s.heroText}>One step at a time</Text><Body>10–30 seconds · Guided by voice</Body></View>
    <Card><Text style={s.label}>Your walk can help research</Text><Body muted>{Platform.OS==='web'?'Check whether this browser can record all three sensors, or preview the steps and review an exported file.':'Record your movement and choose when to share it. Your recordings stay on this phone.'}</Body></Card>
    <ReviewImport onOpen={id=>navigation.navigate('Details',{sessionId:id})}/>
    <Text style={s.note}>For movement research. This app does not diagnose stroke or assess whether it is safe to walk.</Text>
  </Screen>;
}
const s = StyleSheet.create({ hero: { backgroundColor: c.surfaceAlt, borderRadius: 24, padding: 18, alignItems: 'center', gap: 5 }, arrow: { fontSize: 60, color: c.primary }, heroText: { fontSize: 22, color: c.textPrimary, fontWeight: '700' }, label: { fontSize: 20, fontWeight: '700', color: c.textPrimary }, note: { fontSize: 16, lineHeight: 22, color: c.textSecondary } });
