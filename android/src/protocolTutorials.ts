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
    {title:'Follow the marked path',text:'A worker marks a 12 metre path: 1 metre to start, 10 metres timed, then 1 metre to slow down.',picture:'zone'},
    {title:'Walk past both marks',text:'Walk at your comfortable pace. Keep walking past the second mark; the worker times the middle 10 metres.',picture:'path'},
    {title:'Slow down at the end',text:'Slow down after the final mark. The worker enters your time. The phone timer is not your 10 metre result.',picture:'finish'},
  ],
  '2mwt': [
    {title:'Walk for two minutes',text:'Follow the measured route. Walk as far as you safely can in two minutes. Use your usual aid.',picture:'loop'},
    {title:'Rest if you need to',text:'You may slow down or stop to rest. The two-minute clock keeps running.',picture:'rest'},
    {title:'Follow the worker’s stop cue',text:'The clock starts at Go and keeps running during rests. Stop at the finish cue. The worker confirms your measured distance.',picture:'finish'},
  ],
  '6mwt': [
    {title:'Walk for six minutes',text:'Follow the worker’s marked route. Walk as far as you can at your own pace for six minutes. Keep your usual aid.',picture:'loop'},
    {title:'Rest if you need to',text:'You may slow down or stand and rest. The six-minute clock keeps running.',picture:'rest'},
    {title:'Listen to the worker',text:'The app gives start and finish cues. During the test, the worker gives standard timed instructions and measures your distance.',picture:'finish'},
  ],
  'tug': [
    {title:'Start seated',text:'Sit with your back against the chair. On the worker’s Go, stand and walk to the mark three metres away.',picture:'chair'},
    {title:'Turn and come back',text:'Turn at the mark. Walk back at a comfortable, safe pace with your usual aid.',picture:'return'},
    {title:'Sit down again',text:'Sit back down. The worker stops the stopwatch when you sit. Practise once before the timed test.',picture:'chair'},
  ],
};
