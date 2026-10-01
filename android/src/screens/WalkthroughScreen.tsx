import React,{useState} from 'react';
import { View } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../App';
import { Screen,Card,Body,ui } from '../components/Screen';
import { Text } from '../i18n';
import BigButton from '../components/BigButton';
import ClinicalCapture from '../components/ClinicalCapture';
import {protocolFlows} from '../protocolFlow';
import type {AssessmentProtocol} from '../store';

const shared=[
 ['Mount the phone','Take your time to place the phone. Keep it horizontal at your lower back, screen facing out, then stand still. The phone check waits for you.'],
 ['Check live sensors','Checks sensor readings, phone angle and settling. Lower-back location cannot be verified.'],
 ['Short movement check','Move comfortably for a short moment, then stop and stand still until the movement check is complete. Rest if needed. We are checking phone motion, not counting your steps.'],
];
export default function WalkthroughScreen({navigation,route}:NativeStackScreenProps<RootStackParamList,'Walkthrough'>){
 const [protocol,setProtocol]=useState<AssessmentProtocol>(route.params?.protocol??'research-walk');
 const [page,setPage]=useState(0),[complete,setComplete]=useState(false);
 const flow=protocolFlows[protocol];
 if(page===3&&protocol!=='research-walk'&&!complete)return <ClinicalCapture key={protocol} protocol={protocol} audioEnabled={false} preview
   say={async()=>{}} receiving={()=>true} onBegin={()=>{}} onFinish={()=>setComplete(true)} onCancel={()=>setPage(2)}/>;
 const stages=[...shared,[flow.title,flow.intro],['Recording',flow.active],['Review and export',flow.finish]];
 const shown=complete?stages.length-1:page;
 return <Screen title="Supervisor walkthrough" eyebrow="PREVIEW — NO RECORDING SAVED" actions={<>
   <BigButton label={shown===stages.length-1?'Back to home':'Next step'} onPress={()=>shown===stages.length-1?navigation.popToTop():setPage(page+1)}/>
   <BigButton label="Previous" variant="outline" disabled={shown===0} onPress={()=>{setComplete(false);setPage(Math.max(0,shown-1));}}/>
 </>}>
   {page===0&&<View style={{gap:8}}>{(Object.keys(protocolFlows) as AssessmentProtocol[]).map(p=><BigButton key={p} label={protocolFlows[p].title} icon={protocol===p?'●':'○'} variant={protocol===p?'primary':'outline'} onPress={()=>setProtocol(p)}/>)}</View>}
   <Card><Text style={ui.label}>{stages[shown][0]}</Text><Body>{stages[shown][1]}</Body></Card>
   <Body muted>These are explanatory screens. No sensor check has passed and no recording is created.</Body>
 </Screen>;
}
