import { t, useLanguage } from '../i18n';
import React, { useState, useEffect } from 'react';
import { Image, View, useWindowDimensions } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen, Body, ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { speak, stopSpeaking } from '../audio';
const steps = [
  ['Choose a clear path', 'Choose a clear, level space. Use your usual walking aid and support. Stop if you feel unwell or unsteady.'],
  ['Secure your phone', 'Place it horizontally at your lower back, screen facing out, in a firm belt pouch. Ask someone to help if needed. Do not hold it while walking.'],
  ['Listen, then move and stop', 'Listen for the phone check. Move comfortably for a short moment, then stop and stand still until the movement check is complete. Rest whenever needed.'],
  ['Rest, then review', 'The voice tells you when recording ends. Stop safely before checking your phone. Open your recording to see movement signals or share a file.'],
];
const illustrations = [require('../../assets/guides/path.png'), require('../../assets/guides/placement.png'), require('../../assets/guides/walk.png'), require('../../assets/guides/review.png')];
const imageDescriptions = ['An older adult with a walking aid and nearby helper in a clear hallway.', 'A helper secures a horizontal phone in a pouch at the centre of the lower back, screen facing outward.', 'Walking comfortably with the phone secured at the lower back, eyes ahead.', 'Seated safely after walking, reviewing a recording on the phone.'];
export default function OnboardingScreen({ navigation }: NativeStackScreenProps<RootStackParamList, 'Onboarding'>) {
  useLanguage();
  const [step, setStep] = useState(0);
  const { height, fontScale } = useWindowDimensions();
  useEffect(() => () => stopSpeaking(), [step]);
  return <Screen eyebrow={`QUICK GUIDE · ${step + 1} OF 4`} title={steps[step][0]} actions={<>
    <BigButton label={step === 3 ? 'Set up my walk' : 'Next step'} onPress={() => step === 3 ? navigation.replace('Prepare', { duration: 20, audioEnabled: true, isPractice: false }) : setStep(step + 1)} />
    <View style={ui.row}><BigButton style={ui.fill} variant="outline" label="Previous" disabled={step === 0} onPress={() => setStep(step - 1)} /><BigButton style={ui.fill} variant="outline" label="Read aloud" onPress={() => speak(steps[step][1])} /></View>
  </>}>{step !== 1 && <Image source={illustrations[step]} resizeMode="contain" accessibilityLabel={t(imageDescriptions[step])} style={{ width: '100%', height: Math.max(110, Math.min(230, height - 490 - Math.max(0, fontScale - 1) * 130)), borderRadius: 18 }} />}
    <Body>{steps[step][1]}</Body>
  </Screen>;
}
