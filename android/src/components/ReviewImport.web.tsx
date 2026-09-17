import React, { useState } from 'react';
import { Card, Body, ui } from './Screen';
import { Text, t, useLanguage } from '../i18n';
import { importReviewRecording } from '../store.web';

export default function ReviewImport({onOpen}:{onOpen:(id:string)=>void}) {
  useLanguage();const [error,setError]=useState('');
  return <Card><Text style={ui.label}>Review an exported recording</Text><Body muted>Open a JSON export from this app. It stays in this browser tab and is cleared when you refresh. No upload.</Body>
    {React.createElement('input',{type:'file',accept:'.json,application/json','aria-label':t('Review an exported recording'),style:{fontSize:16,maxWidth:'100%',minHeight:48},onChange:async(e:React.ChangeEvent<HTMLInputElement>)=>{
      const file=e.currentTarget.files?.[0];e.currentTarget.value='';setError('');if(!file)return;
      try{if(file.size>20*1024*1024)throw new Error('Choose a valid Gait Steps device JSON export (up to 20 MB).');onOpen(importReviewRecording(await file.text()));}
      catch{setError('Choose a valid Gait Steps device JSON export (up to 20 MB).');}
    }})}
    {!!error&&<Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Card>;
}
