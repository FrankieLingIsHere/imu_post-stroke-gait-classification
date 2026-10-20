import * as FileSystem from 'expo-file-system';

// Expo's Android UTF-8 reader buffers the whole file as Java chars. Read bounded
// byte ranges instead, preserving Unicode characters split across chunk edges.
export class Utf8Chunks {
  private pending:number[]=[];
  decode(base64:string,final=false):string {
    const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    const lookup=new Int16Array(128);lookup.fill(-1);for(let i=0;i<alphabet.length;i++)lookup[alphabet.charCodeAt(i)]=i;
    const bytes=new Uint8Array(this.pending.length+Math.ceil(base64.length*3/4));bytes.set(this.pending);let used=this.pending.length,bits=0,value=0;
    for(let i=0;i<base64.length;i++){const char=base64.charCodeAt(i);if(char===61)break;if(char===10||char===13||char===32||char===9)continue;const code=char<128?lookup[char]:-1;if(code<0)throw new Error('Invalid encoded file chunk.');value=(value<<6)|code;bits+=6;if(bits>=8){bits-=8;bytes[used++]=(value>>bits)&255;}}
    this.pending=[];const text:string[]=[];let part='';
    for(let i=0;i<used;){
      if(bytes[i]<128){const start=i;while(i<used&&bytes[i]<128&&i-start<4096)i++;text.push(String.fromCharCode(...bytes.subarray(start,i)));continue;}
      const first=bytes[i],count=first>=194&&first<=223?2:first>=224&&first<=239?3:first>=240&&first<=244?4:0;
      if(!count)throw new Error('File is not valid UTF-8.');
      if(i+count>used){if(final)throw new Error('File ends in an incomplete UTF-8 character.');this.pending=Array.from(bytes.subarray(i,used));break;}
      let point=first&[0,127,31,15,7][count];
      for(let n=1;n<count;n++){const next=bytes[i+n];if((next&192)!==128)throw new Error('File is not valid UTF-8.');point=(point<<6)|(next&63);}
      if((count===2&&point<128)||(count===3&&point<2048)||(count===4&&point<65536)||point>0x10ffff||(point>=0xd800&&point<=0xdfff))throw new Error('File is not valid UTF-8.');
      text.push(String.fromCodePoint(point));i+=count;
    }
    text.push(part);return text.join('');
  }
}

export async function readBoundedUtf8(uri:string,maxBytes:number,onProgress?:(fraction:number)=>void,signal?:AbortSignal):Promise<string> {
  const cancelled=()=>{if(signal?.aborted)throw new Error('Import cancelled.');};cancelled();
  const info=await FileSystem.getInfoAsync(uri);
  if(!info.exists||info.isDirectory||!Number.isFinite(info.size)||info.size>maxBytes)throw new Error('Recording file is missing or exceeds the import size limit.');
  const chunkSize=256*1024,decoder=new Utf8Chunks(),parts:string[]=[];onProgress?.(0);
  for(let offset=0;offset<info.size;offset+=chunkSize){cancelled();const encoded=await FileSystem.readAsStringAsync(uri,{encoding:FileSystem.EncodingType.Base64,position:offset,length:Math.min(chunkSize,info.size-offset)});cancelled();parts.push(decoder.decode(encoded,offset+chunkSize>=info.size));onProgress?.(Math.min(1,(offset+chunkSize)/info.size));}
  cancelled();return parts.join('');
}
