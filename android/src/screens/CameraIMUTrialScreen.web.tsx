import React from 'react';
import {Screen,Body} from '../components/Screen';
import BigButton from '../components/BigButton';
export default function CameraIMUTrialScreen({navigation}:{navigation:{goBack:()=>void}}){return <Screen title="Camera + IMU trial" actions={<BigButton label="Back to home" onPress={()=>navigation.goBack()}/>}><Body>Simultaneous camera and IMU capture requires the new Android APK. Browser previews do not create paired recordings.</Body></Screen>;}
