import React, { useState } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import ReviewImport from '../components/ReviewImport';
import { Text, LanguagePicker } from '../i18n';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours as c } from '../theme';
import PwaInstall from '../components/PwaInstall';
import ReleaseInfo from '../components/ReleaseInfo';
export default function HomeScreen({ navigation }: NativeStackScreenProps<RootStackParamList, 'Home'>) {
  const [more, setMore] = useState(false);
  return <Screen title="Your walking space" actions={<>
    <BigButton label="Start a walk" onPress={() => navigation.navigate('Prepare', { duration: 20, audioEnabled: true, isPractice: false })} />
  </>}>
    <LanguagePicker />
    <Body>Take your time. We will guide you.</Body>
    <View style={{flexDirection:'row',flexWrap:'wrap',gap:10}}>
      <BigButton style={s.tile} label="My recordings" variant="outline" onPress={() => navigation.navigate('History')} />
      <BigButton style={s.tile} label="Participants and profiles" variant="outline" onPress={() => navigation.navigate('Participants')} />
      <BigButton style={s.tile} label="How to use the app" variant="outline" onPress={() => navigation.navigate('Onboarding')} />
      <BigButton style={s.tile} label={more?'Close more options':'More options'} variant="outline" onPress={()=>setMore(!more)} />
    </View>
    {more && <View style={{gap:12}}>
    <BigButton label="Progress dashboard" variant="outline" onPress={() => navigation.navigate('Dashboard')} />
    <ReleaseInfo />
    {Platform.OS === 'web' && <PwaInstall />}
    <Card><Text style={s.label}>Your walk can help research</Text><Body muted>{Platform.OS==='web'?'Check whether this browser can record all three sensors, or preview the steps and review an exported file.':'Record your movement and choose when to share it. Your recordings stay on this phone.'}</Body></Card>
    <ReviewImport onOpen={id=>navigation.navigate('Details',{sessionId:id})}/>
    <Text style={s.note}>For movement research. This app does not diagnose stroke or assess whether it is safe to walk.</Text>
    </View>}
  </Screen>;
}
const s = StyleSheet.create({ tile:{flexBasis:'45%',flexGrow:1,minWidth:120},label: { fontSize: 20, fontWeight: '700', color: c.textPrimary }, note: { fontSize: 16, lineHeight: 22, color: c.textSecondary } });
