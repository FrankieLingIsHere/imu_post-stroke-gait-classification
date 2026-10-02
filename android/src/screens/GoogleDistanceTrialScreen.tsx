import React,{useState} from 'react';
import { View,Pressable } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Text,t } from '../i18n';
import { Screen,Card,Body,ui } from '../components/Screen';
import BigButton from '../components/BigButton';
import { GOOGLE_TRIAL_LIMIT_SECONDS,type GoogleDistanceTrial } from '../googleDistanceTrial';

export default function GoogleDistanceTrialScreen({navigation}:NativeStackScreenProps<RootStackParamList,'GoogleDistanceTrial'>){
  const [distance,setDistance]=useState<GoogleDistanceTrial['referenceDistanceM']>(3);
  const [marked,setMarked]=useState(false);
  return <Screen title="Google distance trial" eyebrow="RESEARCH TOOL · NOT A CLINICAL TEST" actions={<>
    <BigButton label="Set up this short trial" disabled={!marked} onPress={()=>navigation.navigate('Prepare',{
      duration:GOOGLE_TRIAL_LIMIT_SECONDS,audioEnabled:true,isPractice:true,useGoogleDistance:true,useGpsDistance:false,
      googleDistanceTrial:{version:'google-distance-trial-v1',referenceDistanceM:distance,completedMarkedRoute:null},
      assessmentSetup:{protocol:'research-walk',courseLengthM:distance,timedDistanceM:null,trialNumber:null,speedCondition:'comfortable',turnDirection:'self-selected'}
    })}/>
    <BigButton label="Back to home" variant="outline" onPress={()=>navigation.goBack()}/>
  </>}>
    <Body>Check Google distance on a short, measured route. This is separate from rehabilitation assessments and does not score your gait.</Body>
    <Card>
      <Text style={ui.label}>Choose your measured route</Text>
      <View style={ui.row}>{([2,3,5] as const).map(value=><Pressable key={value} accessibilityRole="radio" accessibilityState={{selected:distance===value}} accessibilityLabel={t('Route length: {0} m').replace('{0}',String(value))} style={[ui.choice,ui.fill,distance===value&&ui.selected]} onPress={()=>{setDistance(value);setMarked(false);}}><Text>{distance===value?'● ':'○ '}{value} m</Text></Pressable>)}</View>
      <Body>Measure with a tape and mark the start and finish. Keep the phone horizontal at your lower back, screen facing out. No 12-metre course is needed.</Body>
      <Pressable accessibilityRole="checkbox" accessibilityState={{checked:marked}} accessibilityLabel={t('I measured this route and the path is clear.')} onPress={()=>setMarked(v=>!v)} style={[ui.row,{minHeight:56}]}><Text style={{fontSize:26}}>{marked?'☑':'☐'}</Text><Text style={ui.fill}>I measured this route and the path is clear.</Text></Pressable>
    </Card>
    <Body>After the phone checks, return to the start mark. Wait for the spoken begin cue, walk to the finish, then stand still. Four seconds of stillness ends the trial; a 60-second limit is only a fallback.</Body>
    <Body>Google readings do not decide when you stop. After walking ends, the app checks for delayed records for up to 30 seconds plus request time. You can rest while it saves.</Body>
    <Body>Export the full JSON from the trial result. Tell us whether you reached the finish and whether you paused. Trial recordings stay linked to your participant and are excluded from rehabilitation progress trends.</Body>
  </Screen>;
}
