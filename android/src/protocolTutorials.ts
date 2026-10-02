import type { AssessmentProtocol } from './store';
export type TutorialPicture = 'path' | 'zone' | 'finish' | 'loop' | 'rest' | 'chair' | 'return';
export interface TutorialStep { title: string; text: string; picture: TutorialPicture; }
export const protocolTutorials: Record<AssessmentProtocol, TutorialStep[]> = {
  'research-walk': [
    {title:'A clear path',text:'Choose a clear, level path. Keep your usual walking aid.',picture:'path'},
    {title:'Listen for the start',text:'Wait for the start cue. Walk at your comfortable pace. Recording waits for your first detected step.',picture:'zone'},
    {title:'Stop safely',text:'Rest whenever needed. When the voice says finished, stop before checking your phone.',picture:'finish'},
  ],
  '10mwt': [
    {title:'Follow the marked path',text:'Prepare a 12 metre path: 1 metre to get moving, 10 metres in the middle, then 1 metre to slow down.',picture:'zone'},
    {title:'Walk past both marks',text:'Wait for Go, then walk comfortably through both marks without touching the phone.',picture:'path'},
    {title:'Slow down at the end',text:'At the final marker, stop and stand still. The phone saves automatically; its speed is only an estimate.',picture:'finish'},
  ],
  '2mwt': [
    {title:'Walk for two minutes',text:'Follow the measured route. Walk as far as you safely can in two minutes. Use your usual aid.',picture:'loop'},
    {title:'Rest if you need to',text:'You may slow down or stop to rest. The two-minute clock keeps running.',picture:'rest'},
    {title:'Follow the finish cue',text:'The clock starts at Go and keeps running during rests. The phone stops and saves at two minutes.',picture:'finish'},
  ],
  '6mwt': [
    {title:'Walk for six minutes',text:'Follow a clear route at your own pace for six minutes. Keep your usual walking aid.',picture:'loop'},
    {title:'Rest if you need to',text:'You may slow down or stand and rest. The six-minute clock keeps running.',picture:'rest'},
    {title:'Listen to the phone',text:'The phone gives start and finish cues, then saves automatically. Its distance is an estimate.',picture:'finish'},
  ],
  'tug': [
    {title:'Start seated',text:'Sit with your back against the chair. Wait for the phone to say Go, then stand and walk to the mark three metres away.',picture:'chair'},
    {title:'Turn and come back',text:'Turn at the mark. Walk back at a comfortable, safe pace with your usual aid.',picture:'return'},
    {title:'Sit down again',text:'Sit back down and stay still until the phone saves. It cannot verify chair contact.',picture:'chair'},
  ],
};
