import React, { useState,useRef,useEffect } from 'react';
import * as DocumentPicker from 'expo-document-picker';
import { readBoundedUtf8 } from '../boundedFileRead';
import { Card, Body, ui } from './Screen';
import { Text, t, useLanguage } from '../i18n';
import BigButton from './BigButton';
import { importReviewRecording } from '../store';

/** Native file import for supervisor review. Files remain local to this phone. */
export default function ReviewImport({ onOpen }: { onOpen: (id: string) => void }) {
  useLanguage();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [readPercent,setReadPercent]=useState<number|null>(null);
  const operation=useRef<AbortController|null>(null),alive=useRef(true);
  useEffect(()=>{alive.current=true;return()=>{alive.current=false;operation.current?.abort();};},[]);
  const [committing,setCommitting]=useState(false);
  const [processing,setProcessing]=useState(false);
  async function pick() {
    const controller=new AbortController();operation.current=controller;
    setError(''); setLoading(true);setReadPercent(null);setProcessing(false);
    try {
      const result = await DocumentPicker.getDocumentAsync({ type: ['application/json', 'text/csv', 'text/comma-separated-values'], copyToCacheDirectory: true, multiple: false });
      if (result.canceled||controller.signal.aborted) return;
      const asset = result.assets[0];
      const format = (asset.name ?? '').toLowerCase().endsWith('.csv') ? 'csv' : 'json';
      if (asset.size && asset.size > (format==='csv'?128:40) * 1024 * 1024) throw new Error(format==='csv'?'File is too large. Choose a CSV export up to 128 MB.':'File is too large. Choose an export up to 40 MB.');
      const text = await readBoundedUtf8(asset.uri,(format==='csv'?128:40)*1024*1024,value=>{if(alive.current)setReadPercent(Math.floor(value*100));},controller.signal);
      setProcessing(true);
      // Let the processing state paint before the bounded parser uses the JS thread.
      await new Promise(resolve=>setTimeout(resolve,0));
      if(controller.signal.aborted)return;
      setCommitting(format==='json');
      const id = await importReviewRecording(text, format,controller.signal,()=>setCommitting(true));
      if(alive.current&&!controller.signal.aborted)onOpen(id);
    } catch (e) {
      if(alive.current&&!controller.signal.aborted)setError(e instanceof Error ? e.message : 'Could not open that recording export.');
    } finally { operation.current=null;if(alive.current){setCommitting(false);setLoading(false);setReadPercent(null);setProcessing(false); }}
  }
  return <Card>
    <Text style={ui.label}>{t('Review an exported recording')}</Text>
    <Body muted>Choose a JSON export or raw CSV from this app. It is copied into this phone's local recordings; nothing is uploaded.</Body>
    <BigButton label={loading ? 'Opening recording...' : 'Choose JSON or CSV file'} loading={loading} onPress={() => { void pick(); }} />
    {loading&&readPercent!==null&&<Text style={ui.caption}>{processing?t('Checking and saving the recording…'):t('Reading file: {0}%').replace('{0}',String(readPercent))}</Text>}
    {loading&&!committing&&<BigButton label="Cancel import" variant="outline" onPress={()=>operation.current?.abort()}/>}
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Card>;
}
