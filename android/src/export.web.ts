import type { SessionRecord } from './store';
import { exportCSV, exportCSVBundle, exportJSON, exportFeatureCSV } from './exportData';
export async function shareRecording(session:SessionRecord,format:'csv'|'json'|'features') {
  const content=format==='json'?exportJSON(session):format==='features'?exportFeatureCSV(session):exportCSV(session);
  const url=URL.createObjectURL(new Blob([content],{type:format==='json'?'application/json':'text/csv;charset=utf-8'}));
  const anchor=document.createElement('a');anchor.href=url;
  anchor.download='gait-'+session.id.replace(/[^a-zA-Z0-9_-]/g,'_')+(format==='features'?'-features.csv':'.'+format);
  document.body.appendChild(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export async function shareRecordingsCSV(sessions: SessionRecord[]) {
  if (!sessions.length) throw new Error('There are no recordings to export.');
  const url=URL.createObjectURL(new Blob([exportCSVBundle(sessions)],{type:'text/csv;charset=utf-8'}));
  const anchor=document.createElement('a');anchor.href=url;anchor.download='gait-recordings-all.csv';document.body.appendChild(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
