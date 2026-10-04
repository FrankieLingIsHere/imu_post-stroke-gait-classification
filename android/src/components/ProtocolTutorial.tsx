import React, { useEffect, useState } from 'react';
import { Modal, View, useWindowDimensions, Linking } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Svg, { Path, Rect, Circle, Line, Text as SvgText } from 'react-native-svg';
import type { AssessmentProtocol } from '../store';
import { protocolGuides } from '../protocolGuides';
import { protocolTutorials, TutorialPicture } from '../protocolTutorials';
import { speak, stopSpeaking } from '../audio';
import { Text, t, useLanguage } from '../i18n';
import { Screen, Body, ui } from './Screen';
import BigButton from './BigButton';
import { colours } from '../theme';

/** Simple schematic media: marked distances and movement direction, not inferred anatomy. */
function Diagram({ picture, protocol }: {picture:TutorialPicture;protocol:AssessmentProtocol}) {
  const {height}=useWindowDimensions();
  const colour=colours.primary;
  return <View accessible={false} importantForAccessibility="no-hide-descendants" style={{alignItems:'center',backgroundColor:colours.surfaceAlt,borderRadius:20}}>
    <Svg width="100%" height={Math.max(100,Math.min(170,height*0.23))} viewBox="0 0 320 160">
      {picture==='loop' ? <>
        <Rect x="35" y="38" width="250" height="82" rx="40" fill="none" stroke={colour} strokeWidth="7" />
        <Path d="M145 24 L168 38 L145 52 M175 106 L152 120 L175 134" fill="none" stroke={colour} strokeWidth="6" />
        <SvgText x="160" y="89" textAnchor="middle" fontSize="25" fill={colour}>{protocol==='2mwt'?'2 min':'6 min'}</SvgText>
      </> : picture==='rest' ? <>
        <Circle cx="160" cy="80" r="52" fill="none" stroke={colour} strokeWidth="6" />
        <Path d="M146 60 V100 M174 60 V100" stroke={colour} strokeWidth="12" />
      </> : <>
        <Line x1="30" x2="292" y1="120" y2="120" stroke={colour} strokeWidth="4" />
        <Circle cx="70" cy="37" r="11" fill={colour} />
        <Path d={picture==='chair'?'M70 52 V80 H98 L105 117 M70 58 L97 72':'M70 52 L78 82 L59 116 M78 82 L100 112 M73 60 L98 75 M73 60 L52 81'} stroke={colour} strokeWidth="7" fill="none" strokeLinecap="round" />
        {picture==='chair'&&<Path d="M49 62 V90 H84 M53 90 V119 M83 90 V119" stroke={colour} strokeWidth="5" fill="none" />}
        <Path d={picture==='return'?'M126 58 H235 Q270 58 270 79 Q270 100 235 100 H130 M148 87 L130 100 L148 113':'M122 76 H263 M245 61 L263 76 L245 91'} stroke={colour} strokeWidth="5" fill="none" />
        {picture==='zone'&&protocol==='10mwt'?<>
          <Line x1="110" x2="110" y1="30" y2="130" stroke={colour} strokeWidth="3" strokeDasharray="5 5" />
          <Line x1="254" x2="254" y1="30" y2="130" stroke={colour} strokeWidth="3" strokeDasharray="5 5" />
          <SvgText x="77" y="150" fontSize="16" fill={colour}>1 m</SvgText><SvgText x="159" y="150" fontSize="19" fill={colour}>10 m</SvgText><SvgText x="264" y="150" fontSize="16" fill={colour}>1 m</SvgText>
        </>:protocol==='tug'?<SvgText x="193" y="145" fontSize="20" fill={colour}>3 m</SvgText>:null}
        {picture==='finish'&&<Path d="M262 36 V120 M263 38 H295 V60 H263" stroke={colour} strokeWidth="4" fill="none" />}
      </>}
    </Svg>
  </View>;
}
export default function ProtocolTutorial({protocol,onClose}:{protocol:AssessmentProtocol;onClose:()=>void}) {
  const language=useLanguage();
  const [step,setStep]=useState(0),[details,setDetails]=useState(false),[playing,setPlaying]=useState(false),[error,setError]=useState('');
  const steps=protocolTutorials[protocol],current=steps[step],guide=protocolGuides[protocol];
  useEffect(()=>{setPlaying(false);setError('');stopSpeaking();return ()=>stopSpeaking();},[step,details,language,protocol]);
  function listen(){if(playing){stopSpeaking();setPlaying(false);return;}setPlaying(true);void speak(current.text,{onDone:()=>setPlaying(false),onError:()=>{setPlaying(false);setError('Could not play the voice. Check phone speech and volume settings, or use a helper with voice off.');}});}
  return <Modal visible animationType="slide" onRequestClose={onClose}>
    <SafeAreaView edges={['top']} style={{flex:1,backgroundColor:colours.background}}>
      <Screen key={`${step}-${details}`} title={details?'Worker protocol notes':current.title} eyebrow={t('Tutorial step {0} of {1}').replace('{0}',String(step+1)).replace('{1}',String(steps.length))} actions={<>
        <BigButton label={details?'Back to tutorial':step===steps.length-1?'Done':'Next step'} onPress={()=>details?setDetails(false):step===steps.length-1?onClose():setStep(step+1)} />
        <View style={ui.row}><BigButton style={ui.fill} label="Previous" variant="ghost" disabled={step===0||details} onPress={()=>setStep(step-1)}/><BigButton style={ui.fill} label="Close instructions" variant="ghost" onPress={onClose}/></View>
      </>}>
        {details?<><Body>{guide.body}</Body>{guide.extra&&<Body>{guide.extra}</Body>}<Body>Source basis: Shirley Ryan AbilityLab RehabMeasures Database; ATS 6MWT statement. GaitTrace is a sensor-capture aid and does not itself administer or validate these clinical tests.</Body>{guide.sourceUrl&&<BigButton label="Open clinical protocol source" variant="outline" onPress={()=>void Linking.openURL(guide.sourceUrl!).catch(()=>setError('Could not open the protocol source.'))}/>}</>:<>
          <Diagram picture={current.picture} protocol={protocol}/>
          <Body>{current.text}</Body>
          <BigButton label={playing?'Stop sample':'Read aloud'} variant="outline" onPress={listen}/>
          <BigButton label="Worker protocol notes" variant="ghost" onPress={()=>setDetails(true)}/>
        </>}
        {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
      </Screen>
    </SafeAreaView>
  </Modal>;
}
