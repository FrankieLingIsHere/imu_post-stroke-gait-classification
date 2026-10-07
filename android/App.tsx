import React, { useEffect } from 'react';
import {Text as NativeText} from 'react-native';
import {flowLabEnabled} from './src/flowLab';
import { useLanguage, restoreLanguage, t } from './src/i18n';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import HomeScreen from './src/screens/HomeScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';
import PrepareScreen from './src/screens/PrepareScreen';
import RecordScreen from './src/screens/RecordScreen';
import ResultScreen from './src/screens/ResultScreen';
import AssessmentScreen from './src/screens/AssessmentScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import DetailsScreen from './src/screens/DetailsScreen';
import { colours } from './src/theme';
import PhoneFrame from './src/components/PhoneFrame';
import WalkthroughScreen from './src/screens/WalkthroughScreen';
import ParticipantsScreen from './src/screens/ParticipantsScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import GoogleDistanceTrialScreen from './src/screens/GoogleDistanceTrialScreen';
import GoogleApiCheckScreen from './src/screens/GoogleApiCheckScreen';
import CameraIMUTrialScreen from './src/screens/CameraIMUTrialScreen';
import CameraCalibrationScreen from './src/screens/PhoneCalibrationScreen';
import CameraDistanceTrialScreen from './src/screens/CameraDistanceTrialScreen';
import type { AssessmentProtocol, AssessmentSetup, ParticipantDemographics, ParticipantProfile } from './src/store';
type Setup = { duration: number; audioEnabled: boolean; isPractice: boolean; demographics?: ParticipantDemographics; participantId?: string; participantLabel?: string; participantSnapshot?: ParticipantProfile; assessmentSetup?: AssessmentSetup; useGpsDistance?: boolean; useGoogleDistance?: boolean; googleDistanceTrial?:import('./src/googleDistanceTrial').GoogleDistanceTrial };
export type RootStackParamList = {
  Home: undefined; Onboarding: undefined; Prepare: Setup; Walkthrough: {protocol?:AssessmentProtocol} | undefined; Participants: undefined; Dashboard: undefined;
  Record: Setup & { guidanceEnabled: boolean };
  Result: { sessionId: string; openAssessment?: boolean }; Details: { sessionId: string }; History: undefined;
  Assessment:{sessionId:string};
  GoogleDistanceTrial:undefined;
  GoogleApiCheck:undefined;
  CameraIMUTrial:undefined;
  CameraCalibration:undefined;
  CameraDistanceTrial:undefined;
};
const Stack = createNativeStackNavigator<RootStackParamList>();
export default function App() {
  useLanguage();
  useEffect(() => { void restoreLanguage(); }, []);
  return <PhoneFrame><SafeAreaProvider>{flowLabEnabled&&<NativeText style={{backgroundColor:'#fff0c2',padding:8,textAlign:'center'}}>FLOW LAB — DEMO ONLY — NO SENSORS</NativeText>}<StatusBar style="dark" /><NavigationContainer>
    <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: colours.background }, headerTintColor: colours.primary, headerShadowVisible: false, headerTitleStyle: { fontWeight: '700', fontSize: 20 }, contentStyle: { backgroundColor: colours.background } }}>
      <Stack.Screen name="Home" component={HomeScreen} options={{ title: t('Gait Steps') }} />
      <Stack.Screen name="Onboarding" component={OnboardingScreen} options={{ title: t('Your guide') }} />
      <Stack.Screen name="Prepare" component={PrepareScreen} options={{ title: t('Set up your walk') }} />
      <Stack.Screen name="Record" component={RecordScreen} options={{ title: t('Guided walk'), headerBackVisible: false, gestureEnabled: false }} />
      <Stack.Screen name="Result" component={ResultScreen} options={{ title: t('Recording saved'), headerBackVisible: false, gestureEnabled: false }} />
      <Stack.Screen name="Assessment" component={AssessmentScreen} options={{title:'G.A.I.T. worker assessment',headerBackVisible:false,gestureEnabled:false}}/>
      <Stack.Screen name="History" component={HistoryScreen} options={{ title: t('My recordings') }} />
      <Stack.Screen name="Details" component={DetailsScreen} options={{ title: t('Recording details') }} />
      <Stack.Screen name="Walkthrough" component={WalkthroughScreen} options={{ title: t('Supervisor walkthrough') }} />
      <Stack.Screen name="Participants" component={ParticipantsScreen} options={{ title: t('Participants') }} />
      <Stack.Screen name="Dashboard" component={DashboardScreen} options={{ title: t('Progress dashboard') }} />
      <Stack.Screen name="GoogleDistanceTrial" component={GoogleDistanceTrialScreen} options={{title:t('Google distance trial')}}/>
      <Stack.Screen name="GoogleApiCheck" component={GoogleApiCheckScreen} options={{title:t('Quick Google API check'),headerBackVisible:false,gestureEnabled:false}}/>
      <Stack.Screen name="CameraIMUTrial" component={CameraIMUTrialScreen} options={{title:t('Camera + IMU trial'),headerBackVisible:false,gestureEnabled:false}}/>
      <Stack.Screen name="CameraCalibration" component={CameraCalibrationScreen} options={{title:t('Phone calibration'),headerBackVisible:false,gestureEnabled:false}}/>
      <Stack.Screen name="CameraDistanceTrial" component={CameraDistanceTrialScreen} options={{title:t('Camera distance trial'),headerBackVisible:false,gestureEnabled:false}}/>
    </Stack.Navigator>
  </NavigationContainer></SafeAreaProvider></PhoneFrame>;
}
