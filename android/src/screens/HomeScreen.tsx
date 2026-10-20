import React, { useState } from 'react';
import { View, StyleSheet, Platform, Modal } from 'react-native';
import ReviewImport from '../components/ReviewImport';
import { Text, LanguagePicker } from '../i18n';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Card, Body } from '../components/Screen';
import BigButton from '../components/BigButton';
import { colours as c } from '../theme';
import PwaInstall from '../components/PwaInstall';
import ReleaseInfo from '../components/ReleaseInfo';
import {flowLabEnabled,FLOW_LAB_SESSION} from '../flowLab';
export default function HomeScreen({ navigation }: NativeStackScreenProps<RootStackParamList, 'Home'>) {
  const [more, setMore] = useState(false);
  const [research, setResearch] = useState(false);
  return <Screen title="Your walking space" actions={<>
    <BigButton label="Start a walk" onPress={() => navigation.navigate('Prepare', { duration: 20, audioEnabled: true, isPractice: false })} />
  </>}>
    <LanguagePicker />
    {flowLabEnabled&&<Card><Text>FLOW LAB — DEMONSTRATION ONLY. No sensors or patient measurements.</Text><BigButton label="Open demo assessment" variant="outline" onPress={()=>navigation.navigate('Assessment',{sessionId:FLOW_LAB_SESSION})}/></Card>}
    <Body>Take your time. We will guide you.</Body>
    <View style={{flexDirection:'row',flexWrap:'wrap',gap:10}}>
      <BigButton style={s.tile} label="My recordings" variant="outline" onPress={() => navigation.navigate('History')} />
      <BigButton style={s.tile} label="Participants and profiles" variant="outline" onPress={() => navigation.navigate('Participants')} />


      <BigButton style={s.tile} label={'Tools and help'} variant="outline" onPress={()=>setMore(!more)} />
    </View>
    <Modal visible={more} animationType="slide" onRequestClose={()=>setMore(false)}>
    <Screen fullScreen title="Tools and help" actions={<BigButton label="Done" onPress={()=>setMore(false)}/>}><View style={{gap:12}}>
    <ReviewImport onOpen={id=>{setMore(false);navigation.navigate('Details',{sessionId:id});}}/>
      <BigButton style={s.tile} label="Progress dashboard" variant="outline" onPress={()=>{setMore(false);navigation.navigate('Dashboard');}} />
      <BigButton style={s.tile} label="How to use the app" variant="outline" onPress={()=>{setMore(false);navigation.navigate('Onboarding');}} />
    {Platform.OS==='android'&&<BigButton label="Set up this phone" variant="outline" onPress={()=>{setMore(false);navigation.navigate('PhoneSetup');}}/>}
    {Platform.OS==='android'&&<><Body muted>Set up this phone once. Walking tests then track distance on this phone.</Body><BigButton label={research?'Close advanced research tools':'Advanced research tools (computer required)'} variant="outline" onPress={()=>setResearch(!research)}/>{research&&<Card><Text style={s.label}>Computer-based reference tools</Text><Body muted>Optional computer-based reference tools. Ordinary walking tests run on this phone.</Body><BigButton label="Phone calibration" variant="outline" onPress={()=>{setMore(false);navigation.navigate('CameraCalibration');}}/><BigButton label="Distance validation" variant="outline" onPress={()=>{setMore(false);navigation.navigate('CameraDistanceTrial');}}/><Body muted>Record a short marked walk. Your paired computer checks the distance.</Body></Card>}</>}
    <BigButton label="Storage" variant="outline" onPress={()=>{setMore(false);navigation.navigate('Storage');}}/>
    <ReleaseInfo />
    {Platform.OS === 'web' && <PwaInstall />}
    <Card><Text style={s.label}>Your walk can help research</Text><Body muted>{Platform.OS==='web'?'Check whether this browser can record all three sensors, or preview the steps and review an exported file.':'Record your movement and choose when to share it. Your recordings stay on this phone.'}</Body></Card>

    <Text style={s.note}>For movement research. This app does not diagnose stroke or assess whether it is safe to walk.</Text>
    </View></Screen></Modal>
  </Screen>;
}
const s = StyleSheet.create({ tile:{flexBasis:'45%',flexGrow:1,minWidth:120},label: { fontSize: 20, fontWeight: '700', color: c.textPrimary }, note: { fontSize: 16, lineHeight: 22, color: c.textSecondary } });
