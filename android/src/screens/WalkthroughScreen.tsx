import React,{useState} from 'react';
import { View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen,Card,Body,ui } from '../components/Screen';
import { Text } from '../i18n';
import BigButton from '../components/BigButton';

const stages=[
  ['Mount the phone','The Android app gives 20 seconds to secure the phone at the lower back. This browser walkthrough does not check placement.'],
  ['Check live sensors','The Android app waits for live readings and a steady baseline. Missing readings or movement can pause the check.'],
  ['Comfortable steps, then stop','Voice guidance asks for three comfortable steps and a stop. The app checks movement and settling, not an exact step count or anatomical placement.'],
  ['Countdown and recording','The countdown starts automatically after checks pass. Walking and rests are saved. A failed check can be retried without repeating completed fit checks.'],
  ['Review and export','The Android app saves the recording locally. Review the signals and export raw data or experimental features. No diagnosis or classification is provided.'],
];
export default function WalkthroughScreen({navigation}:NativeStackScreenProps<RootStackParamList,'Walkthrough'>){
  const [page,setPage]=useState(0);
  return <Screen title="Supervisor walkthrough" eyebrow="BROWSER PREVIEW · NO SENSOR RECORDING" actions={<>
    <BigButton label={page===stages.length-1?'Back to home':'Next step'} onPress={()=>page===stages.length-1?navigation.popToTop():setPage(page+1)}/>
    <BigButton label="Previous" variant="outline" disabled={page===0} onPress={()=>setPage(page-1)}/>
  </>}><View style={ui.row}>{stages.map((_,i)=><Text key={i} style={ui.caption}>{i===page?'●':'○'}</Text>)}</View>
    <Card><Text style={ui.label}>{stages[page][0]}</Text><Body>{stages[page][1]}</Body></Card>
    <Body muted>These are explanatory screens. No sensor check has passed and no recording is created.</Body>
  </Screen>;
}
