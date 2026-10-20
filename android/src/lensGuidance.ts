/** Change the handling instructions, not the native Zhang solver or admission gates. */
const movingBoard:Record<string,string>={
 'Checking lens parameters. You can hold the phone comfortably.':'Checking lens parameters. You can hold the phone comfortably.',
 'Point the front camera at the digital board.':'Rest the bagged phone securely. Face the tablet board toward its front camera.',
 'Keep the whole board in view.':'Bring the board back into view and pause briefly.',
 'Hold the phone steady for a clear view.':'Pause the tablet briefly for a clear view.',
 'Move a little closer to the board.':'Bring the tablet a little closer to the phone.',
 'Move slowly to show a different view.':'Move the tablet slowly to show a different view.',
 'Tilt the phone gently left and right.':'Turn the tablet gently left and right, keeping its screen toward the phone.',
 'Tilt the phone gently up and down.':'Tilt the tablet gently up and down, keeping its screen toward the phone.',
 'Move the board toward the left and right of the view.':'Move the tablet a little left and right.',
 'Move the board toward the top and bottom of the view.':'Move the tablet a little up and down.',
 'Try a clearer view from another angle.':'Pause the tablet at a different angle for a clear view.',
 'Lens parameters saved. Sensor alignment is still needed.':'Lens parameters saved. Sensor alignment is still needed.',
};
export type LensMode='computer'|'tablet';
export const lensPreparation='Keep the computer board still. Hold the phone in its usual bag, facing the board. Watch the framing on your computer. Move slowly and pause between positions.';
export const tabletLensPreparation='Rest the phone securely in its usual bag, with its front camera facing the tablet. Move only the tablet board. Follow the voice and pause between positions.';
const movingPhone:Record<string,string>={
 'Checking lens parameters. You can hold the phone comfortably.':'Checking lens parameters. You can hold the phone comfortably.',
 'Point the front camera at the digital board.':'Face the front camera toward the board on your computer.',
 'Keep the whole board in view.':'Bring the board back into view and pause briefly.',
 'Hold the phone steady for a clear view.':'Pause the phone briefly for a clear view.',
 'Move a little closer to the board.':'Move the phone a little closer to the computer.',
 'Move slowly to show a different view.':'Move the phone slowly to show a different view.',
 'Tilt the phone gently left and right.':'Move the phone to each side, aiming its camera back at the board. Pause at each position.',
 'Tilt the phone gently up and down.':'Hold the phone above the board centre and aim down at it. Then hold it below the centre and aim up. Pause at each angle.',
 'Move the board toward the left and right of the view.':'Move the phone a little sideways, watching the computer framing.',
 'Move the board toward the top and bottom of the view.':'Move the phone a little up and down, watching the computer framing.',
 'Try a clearer view from another angle.':'Pause the phone at a different angle for a clear view.',
 'Lens parameters saved. Sensor alignment is still needed.':'Lens parameters saved. Sensor alignment is still needed.',
};
export function lensGuidance(nativeHint:string,mode:LensMode='computer'){return mode==='tablet'?(movingBoard[nativeHint]??'Move the tablet slowly to show a different view.'):(movingPhone[nativeHint]??'Move the phone slowly to show a different view.');}

export type LensRound='framing'|'side-angles'|'high-low-angles'|'horizontal'|'vertical'|'variety'|'fitting'|'complete';
export const roundLabels:Record<LensRound,string>={framing:'Find the board', 'side-angles':'Round 1: Side angles','high-low-angles':'Round 2: High and low angles',horizontal:'Round 3: Left and right positions',vertical:'Round 4: Top and bottom positions',variety:'Round 5: Final clear views',fitting:'Checking lens parameters. You can hold the phone comfortably.',complete:'Lens parameters saved. Sensor alignment is still needed.'};
export function lensRoundCue(round:LensRound,mode:LensMode){
 const hint:Record<LensRound,string>={framing:'Move slowly to show a different view.','side-angles':'Tilt the phone gently left and right.','high-low-angles':'Tilt the phone gently up and down.',horizontal:'Move the board toward the left and right of the view.',vertical:'Move the board toward the top and bottom of the view.',variety:'Move slowly to show a different view.',fitting:'Checking lens parameters. You can hold the phone comfortably.',complete:'Lens parameters saved. Sensor alignment is still needed.'};
 return lensGuidance(hint[round],mode);
}
const roundDone:Partial<Record<LensRound,string>>={
 'side-angles':'Side angles complete.', 'high-low-angles':'High and low angles complete.',horizontal:'Left and right positions complete.',vertical:'Top and bottom positions complete.',variety:'Clear views collected.',
};
/** One active utterance and one latest update. Stage changes wait for speech to
 * finish; obsolete instructions never accumulate behind it. */
export function createLensVoiceGuide(say:(text:string)=>Promise<void>,onError:(error:unknown)=>void){
 let stopped=false,busy=false,pending:{round:LensRound;cue:string;mode:LensMode}|null=null;
 let spokenRound:LensRound|undefined,lastCue='',lastTime=0,task:Promise<void>|null=null;
 async function drain(){
  busy=true;
  try{while(pending&&!stopped){
   const next=pending;pending=null;
   if(next.round!==spokenRound){
    const done=spokenRound&&roundDone[spokenRound];if(done){await say(done);if(stopped)break;}
    // Sensor coverage can advance during the completion announcement.
    const current=pending??next;pending=null;
    spokenRound=current.round;lastCue=lensRoundCue(current.round,current.mode);lastTime=Date.now();
    await say(lastCue);
   }else if(next.cue!==lastCue&&Date.now()-lastTime>=8000){
    lastCue=next.cue;lastTime=Date.now();await say(next.cue);
   }
  }}catch(error){stopped=true;pending=null;onError(error);}finally{busy=false;}
 }
 return {update(round:LensRound,cue:string,mode:LensMode){if(stopped)return;pending={round,cue,mode};if(!busy)task=drain();},stop(){stopped=true;pending=null;},get completion(){return task;}};
}
