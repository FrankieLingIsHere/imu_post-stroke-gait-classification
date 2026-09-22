import React, { useState } from 'react';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import { Card, Body, ui } from './Screen';
import { Text, t, useLanguage } from '../i18n';
import BigButton from './BigButton';
import { importReviewRecording } from '../store';

/** Native file import for supervisor review. Files remain local to this phone. */
export default function ReviewImport({ onOpen }: { onOpen: (id: string) => void }) {
  useLanguage();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  async function pick() {
    setError(''); setLoading(true);
    try {
      const result = await DocumentPicker.getDocumentAsync({ type: ['application/json', 'text/csv', 'text/comma-separated-values'], copyToCacheDirectory: true, multiple: false });
      if (result.canceled) return;
      const asset = result.assets[0];
      if (asset.size && asset.size > 40 * 1024 * 1024) throw new Error('File is too large. Choose an export up to 40 MB.');
      const text = await FileSystem.readAsStringAsync(asset.uri);
      const format = (asset.name ?? '').toLowerCase().endsWith('.csv') ? 'csv' : 'json';
      const id = await importReviewRecording(text, format);
      onOpen(id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not open that recording export.');
    } finally { setLoading(false); }
  }
  return <Card>
    <Text style={ui.label}>{t('Review an exported recording')}</Text>
    <Body muted>Choose a JSON export or raw CSV from this app. It is copied into this phone's local recordings; nothing is uploaded.</Body>
    <BigButton label={loading ? 'Opening recording...' : 'Choose JSON or CSV file'} loading={loading} onPress={() => { void pick(); }} />
    {!!error && <Text accessibilityRole="alert" style={ui.error}>{error}</Text>}
  </Card>;
}
