import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import type { SessionRecord } from './store';
import { exportCSV, exportJSON, exportFeatureCSV } from './exportData';
import { translate } from './language';
export async function shareRecording(session: SessionRecord, format: 'csv' | 'json' | 'features') {
  if (!await Sharing.isAvailableAsync() || !FileSystem.cacheDirectory) throw new Error('File sharing is unavailable here. Open this recording in the Android app.');
  const directory = FileSystem.cacheDirectory + 'gait-exports/';
  await FileSystem.makeDirectoryAsync(directory, { intermediates: true });
  const path = directory + 'gait-' + session.id.replace(/[^a-zA-Z0-9_-]/g, '_') + (format === 'features' ? '-features.csv' : '.' + format);
  await FileSystem.writeAsStringAsync(path, format === 'csv' ? exportCSV(session) : format === 'features' ? exportFeatureCSV(session) : exportJSON(session));
  await Sharing.shareAsync(path, { mimeType: format === 'json' ? 'application/json' : 'text/csv', UTI: format === 'json' ? 'public.json' : 'public.comma-separated-values-text', dialogTitle: translate('Share your movement recording') });
}
