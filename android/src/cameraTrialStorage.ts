import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import {saveSession,type SessionRecord} from './store';
import {translate} from './language';
export function cameraFileName(id:string){if(!/^[a-zA-Z0-9_-]+$/.test(id))throw new Error('Invalid camera session ID.');return `camera-${id}.mp4`;}
function directory(){if(!FileSystem.documentDirectory)throw new Error('Local camera storage is unavailable.');return FileSystem.documentDirectory+'camera-trials/';}
export async function cameraVideoAvailable(session:SessionRecord){
  if(session.cameraTrial?.video.status!=='saved'||session.cameraTrial.video.fileName!==cameraFileName(session.id))return false;
  const info=await FileSystem.getInfoAsync(directory()+cameraFileName(session.id));return info.exists&&!info.isDirectory&&info.size>0;
}
/** Move camera cache output into durable app storage before marking the video saved. */
export async function saveCameraTrial(session:SessionRecord,uri:string|null):Promise<SessionRecord>{
  if(!session.cameraTrial)throw new Error('Camera trial metadata is missing.');
  if(!uri){await saveSession(session);return session;}
  await FileSystem.makeDirectoryAsync(directory(),{intermediates:true});
  const fileName=cameraFileName(session.id),dest=directory()+fileName;
  const info=await FileSystem.getInfoAsync(dest);
  if(!info.exists||info.isDirectory||info.size===0){
    if(!uri.startsWith('file://'))throw new Error('Camera returned an invalid local file.');
    await FileSystem.moveAsync({from:uri,to:dest});
  }
  const savedInfo=await FileSystem.getInfoAsync(dest);
  if(!savedInfo.exists||savedInfo.isDirectory||savedInfo.size===0)throw new Error('The video file is empty. Sensor data remains separate.');
  const updated={...session,cameraTrial:{...session.cameraTrial,video:{status:'saved' as const,fileName,error:null}}};
  await saveSession(updated);return updated;
}
export async function shareCameraVideo(session:SessionRecord){
  if(!await cameraVideoAvailable(session))throw new Error('Video is unavailable on this device. JSON imports do not include the MP4 attachment.');
  if(!await Sharing.isAvailableAsync())throw new Error('File sharing is unavailable here.');
  await Sharing.shareAsync(directory()+cameraFileName(session.id),{mimeType:'video/mp4',UTI:'public.mpeg-4',dialogTitle:translate('Export paired camera video')});
}
