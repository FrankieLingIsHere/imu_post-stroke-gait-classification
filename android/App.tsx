import React, { useEffect } from 'react';
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
import HistoryScreen from './src/screens/HistoryScreen';
import DetailsScreen from './src/screens/DetailsScreen';
import { colours } from './src/theme';
import PhoneFrame from './src/components/PhoneFrame';
import WalkthroughScreen from './src/screens/WalkthroughScreen';
type Setup = { duration: 10 | 20 | 30; audioEnabled: boolean; isPractice: boolean };
export type RootStackParamList = {
  Home: undefined; Onboarding: undefined; Prepare: Setup; Walkthrough: undefined;
  Record: Setup & { guidanceEnabled: boolean };
  Result: { sessionId: string }; Details: { sessionId: string }; History: undefined;
};
const Stack = createNativeStackNavigator<RootStackParamList>();
export default function App() {
  useLanguage();
  useEffect(() => { void restoreLanguage(); }, []);
  return <PhoneFrame><SafeAreaProvider><StatusBar style="dark" /><NavigationContainer>
    <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: colours.background }, headerTintColor: colours.primary, headerShadowVisible: false, headerTitleStyle: { fontWeight: '700', fontSize: 20 }, contentStyle: { backgroundColor: colours.background } }}>
      <Stack.Screen name="Home" component={HomeScreen} options={{ title: t('Gait Steps') }} />
      <Stack.Screen name="Onboarding" component={OnboardingScreen} options={{ title: t('Your guide') }} />
      <Stack.Screen name="Prepare" component={PrepareScreen} options={{ title: t('Set up your walk') }} />
      <Stack.Screen name="Record" component={RecordScreen} options={{ title: t('Guided walk'), headerBackVisible: false, gestureEnabled: false }} />
      <Stack.Screen name="Result" component={ResultScreen} options={{ title: t('Recording saved'), headerBackVisible: false, gestureEnabled: false }} />
      <Stack.Screen name="History" component={HistoryScreen} options={{ title: t('My recordings') }} />
      <Stack.Screen name="Details" component={DetailsScreen} options={{ title: t('Recording details') }} />
      <Stack.Screen name="Walkthrough" component={WalkthroughScreen} options={{ title: t('Supervisor walkthrough') }} />
    </Stack.Navigator>
  </NavigationContainer></SafeAreaProvider></PhoneFrame>;
}
