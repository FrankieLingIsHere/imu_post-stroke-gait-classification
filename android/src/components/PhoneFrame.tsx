import React from 'react';
import { Platform, View, useWindowDimensions } from 'react-native';
import { Text } from '../i18n';
import { colours } from '../theme';

export default function PhoneFrame({children}:React.PropsWithChildren) {
  const {width,height}=useWindowDimensions();
  if(Platform.OS!=='web')return <>{children}</>;
  const framed=width>=600;
  return <View style={{flex:1,alignItems:'center',justifyContent:'center',backgroundColor:framed?'#DEE7E4':colours.background}}>
    <View style={{width:framed?430:'100%',height:framed?Math.min(900,height-32):'100%',maxWidth:'100%',overflow:'hidden',backgroundColor:colours.background,borderWidth:framed?6:0,borderColor:colours.textPrimary,borderRadius:framed?30:0}}>
      <Text style={{fontSize:13,lineHeight:18,textAlign:'center',padding:8,color:colours.noticeText,backgroundColor:colours.noticeBg}}>Browser mode · sensor access varies</Text>
      {children}
    </View>
  </View>;
}
