export const setupBeforeInstruction='One-time camera setup. Hold the bagged phone before wearing it.';
export const setupViewInstruction='Point the screen-side camera into a bright room. Keep furniture visible.';
export const setupStartInstruction='Rest the bagged phone securely, with its camera facing the room. Keep it still until I ask you to move.';
export const setupMovementInstruction='Baseline ready. Pick up the bagged phone. Keep the camera facing the room and wait for the next instruction.';
export const setupWaitingMessage='Take your time. Your progress is kept while this setup stays open.';
export const setupTiltInstruction='Gently turn a side edge of the screen towards you, then back. Keep furniture in view.';
export const setupNodInstruction='Gently tip the top edge of the screen towards you, then away. Keep furniture in view.';
export const setupTurnInstruction='Gently turn the phone a little clockwise and back, like a steering wheel. Keep furniture in view.';
export const setupTiltComplete='Side tilt complete.';
export const setupNodComplete='Top tilt complete.';
export const setupTurnComplete='Rotation movement complete.';
// Guidance uses screen axes. Raw IMU axes are never rotated in saved recordings.
export function setupRequestedAxis(hint:string):number|null{return hint===setupNodInstruction?0:hint===setupTiltInstruction?1:hint===setupTurnInstruction?2:null;}
export function setupMovementConfirmation(axis:number):string{return [setupNodComplete,setupTiltComplete,setupTurnComplete][axis]??'';}
export const setupFitInstruction='I still need matching camera and sensor readings. Move the phone slowly left and right, then towards you and away. Keep furniture in view.';
export const setupSlowFramesInstruction='Camera readings are arriving too slowly. Keep the app open and face a brighter room. You do not need bigger movements.';
export const setupDelayedInstruction='Camera readings are delayed. Keep the app open. You do not need bigger movements.';
export const setupChangingInstruction='The camera and sensor fit is still changing. Keep the same small, slow movements.';
export const setupDurationInstruction='Keep making the same gentle movements. I still need a little more recording time.';
export const setupStableInstruction='The readings are nearly ready. Keep the same gentle movements while I check that they stay consistent.';
export const setupOpticsInstruction='The camera view needs more detail. Face furniture in a brighter area and tilt the phone slowly.';
export const setupAlignmentInstruction='The camera and sensors are not aligned reliably yet. Move the phone about a hand-width left and right, then towards you and away.';
export const setupTimingInstruction='The camera and sensors are still matching their timing. Gently alternate tipping and small side-to-side movements.';
export const setupPositionInstruction='Room tracking is uncertain. Point at nearby furniture, keep the camera uncovered and move more slowly.';
export const setupLongWaitInstruction='This check is taking longer. Your setup is not ready yet. Check the camera is uncovered and face a brighter, furnished part of the room.';
export const setupMovementsComplete='The movement directions are recorded. There is still a final camera and sensor check.';
export const setupLostInstruction='Tracking is interrupted. Keep the camera facing the room. If it does not recover, cancel safely; your saved setup is kept.';
export type SetupFeedback={hint:string;roomReady:boolean;movementReady:boolean;fitReady:boolean;axisReady:boolean[];reason:string};
export function phoneSetupFeedback(raw:string|null|undefined,moving:boolean,settled=false,remainingMovementMs?:number,finalCheck?:string|null):SetupFeedback{
 let s:any=null;try{s=raw?JSON.parse(raw):null;}catch{}
 const roomReady=s?.initialized===true&&s?.integrity===true;
 const angles=s?.axisMotionRadians;
 const swap=s?.displayRotationDegrees===90||s?.displayRotationDegrees===270;
 const enough=(i:number)=>{const axis=swap&&i<2?1-i:i;return Array.isArray(angles)&&Number.isFinite(angles[axis])&&angles[axis]>=.5;};
 const movementReady=[0,1,2].every(enough);
 const durationReady=remainingMovementMs===undefined||remainingMovementMs===0;
 const fitReady=roomReady&&movementReady&&s?.numericalCalibrationReady===true&&settled&&durationReady;
 let hint=s?.integrity===false?setupLostInstruction:!roomReady?setupViewInstruction:!moving?'Keep the phone resting still. Wait for the movement instruction.':!enough(0)?setupNodInstruction:!enough(1)?setupTiltInstruction:!enough(2)?setupTurnInstruction:setupFitInstruction;
 let reason=fitReady?'ready':!roomReady?'room':!moving?'baseline':!movementReady?'axis':'readings';
 if(roomReady&&moving&&movementReady&&!fitReady){
  let diagnostic:any=null;try{diagnostic=finalCheck?JSON.parse(finalCheck):null;}catch{}
  const sd=s?.calibrationStd,k=s?.cameraValues;
  const high=(indices:number[],limit:number)=>Array.isArray(sd)&&indices.some(i=>Number.isFinite(sd[i])&&sd[i]>=limit);
  if(diagnostic?.reason==='stale'||diagnostic?.reason==='tracking-gap'){reason='delayed';hint=setupDelayedInstruction;}
  else if(diagnostic?.reason==='slow-frames'){reason='slow-frames';hint=setupSlowFramesInstruction;}
  else if(Number.isFinite(s?.positionStdMetres)&&s.positionStdMetres>=.15){reason='position';hint=setupPositionInstruction;}
  else if(Array.isArray(k)&&Array.isArray(sd)&&(sd[0]/k[0]>=.04||sd[1]/k[1]>=.04||high([2,3],6))){reason='optics';hint=setupOpticsInstruction;}
  else if(high([8,9,10],.035)||high([11,12,13],.015)||s?.state?.tic_norm>.25){reason='alignment';hint=setupAlignmentInstruction;}
  else if(high([14],.003)){reason='timing';hint=setupTimingInstruction;}
  else if(s?.numericalCalibrationReady===true&&remainingMovementMs!==undefined&&remainingMovementMs>0){reason='duration';hint=setupDurationInstruction;}
  else if(diagnostic?.reason==='fit-changing'){reason='changing';hint=setupChangingInstruction;}
  else if(s?.numericalCalibrationReady===true){reason='stable';hint=setupStableInstruction;}
 }
 return {hint,reason,roomReady,movementReady,fitReady,axisReady:[0,1,2].map(enough)};
}
