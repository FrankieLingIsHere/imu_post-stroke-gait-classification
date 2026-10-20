import * as FileSystem from 'expo-file-system';

const documents = () => { if (!FileSystem.documentDirectory) throw new Error('Phone storage is unavailable.'); return FileSystem.documentDirectory; };
function safeName(name:string) { return !!name && name!=='.' && name!=='..' && !/[\\/\x00]/.test(name) && !/%(?:2e|2f|5c)/i.test(name); }
async function remove(uri:string) { await FileSystem.deleteAsync(uri,{idempotent:true}); }
async function entries(uri:string) { return (await FileSystem.getInfoAsync(uri)).exists ? FileSystem.readDirectoryAsync(uri) : []; }
/** Only owned directories/names; never trust a video URI imported from JSON. */
export async function removeRecordingFiles(ids:readonly string[]) {
 const root=documents();
 if(ids.some(id=>!/^[a-zA-Z0-9_-]+$/.test(id)))throw new Error('Invalid recording identifier.');
 for(const id of ids) {
  await remove(root+'recordings/'+id+'.json');
  await remove(root+'camera-trials/camera-'+id+'.mp4');
  await remove(root+'gait-camera-captures/gait-camera-'+id+'.zip');
  await remove(root+'gait-camera-captures/gait-camera-'+id+'/');
 }
 // Bundled CSVs may contain any selected recording: discard all app export copies.
 if(FileSystem.cacheDirectory) { await remove(FileSystem.cacheDirectory+'gait-exports/'); await remove(FileSystem.cacheDirectory+'DocumentPicker/'); }
}
export async function removeAllRecordingFiles() {
 const root=documents();
 await remove(root+'recordings/'); await remove(root+'camera-trials/');await remove(root+'gait-camera-captures/');
 if(FileSystem.cacheDirectory) { await remove(FileSystem.cacheDirectory+'gait-exports/'); await remove(FileSystem.cacheDirectory+'Camera/'); await remove(FileSystem.cacheDirectory+'DocumentPicker/'); }
}
/** Preserve small reusable calibration and pairing, remove captures and recovery indices. */
export async function removeResearchCaptures() {
 const root=documents();
 for(const dir of ['camera-distance-trials/','camera-imu-noise/']) await remove(root+dir);
 const calibration=root+'camera-calibration/';
 const keep=new Set(['lens.json','reference.json','rapid-profile.json','on-device-profile.json','geometry.json','computer.json','noise.json']);
 for(const name of await entries(calibration)) {
  if(!safeName(name)) throw new Error('Invalid storage entry.');
  if(!keep.has(name)) await remove(calibration+name);
 }
}
async function size(uri:string):Promise<number> {
 const info=await FileSystem.getInfoAsync(uri);
 if(!info.exists)return 0;
 if(!info.isDirectory)return info.size;
 let bytes=0;
 for(const name of await FileSystem.readDirectoryAsync(uri)) {
  if(!safeName(name)) throw new Error('Invalid storage entry.');
  bytes+=await size(uri.replace(/\/$/,'')+'/'+name);
 }
 return bytes;
}
export async function recordingStorageBytes() {
 const root=documents(); let bytes=0;
 for(const name of ['recordings/','camera-trials/','gait-camera-captures/','camera-distance-trials/','camera-imu-noise/']) bytes+=await size(root+name);
 const keep=new Set(['lens.json','reference.json','rapid-profile.json','on-device-profile.json','geometry.json','computer.json','noise.json']);
 for(const name of await entries(root+'camera-calibration/')) {
  if(!safeName(name))throw new Error('Invalid storage entry.');
  if(!keep.has(name))bytes+=await size(root+'camera-calibration/'+name);
 }
 if(FileSystem.cacheDirectory) for(const name of ['gait-exports/','Camera/','DocumentPicker/']) bytes+=await size(FileSystem.cacheDirectory+name);
 return bytes;
}
