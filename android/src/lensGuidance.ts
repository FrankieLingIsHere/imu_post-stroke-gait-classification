/** Change the handling instructions, not the native Zhang solver or admission gates. */
const movingBoard:Record<string,string>={
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
 'Point the front camera at the digital board.':'Face the front camera toward the board on your computer.',
 'Keep the whole board in view.':'Bring the board back into view and pause briefly.',
 'Hold the phone steady for a clear view.':'Pause the phone briefly for a clear view.',
 'Move a little closer to the board.':'Move the phone a little closer to the computer.',
 'Move slowly to show a different view.':'Move the phone slowly to show a different view.',
 'Tilt the phone gently left and right.':'Turn the phone gently left and right. Watch the computer framing.',
 'Tilt the phone gently up and down.':'Tilt the phone gently up and down. Watch the computer framing.',
 'Move the board toward the left and right of the view.':'Move the phone a little sideways, watching the computer framing.',
 'Move the board toward the top and bottom of the view.':'Move the phone a little up and down, watching the computer framing.',
 'Try a clearer view from another angle.':'Pause the phone at a different angle for a clear view.',
 'Lens parameters saved. Sensor alignment is still needed.':'Lens parameters saved. Sensor alignment is still needed.',
};
export function lensGuidance(nativeHint:string,mode:LensMode='computer'){return mode==='tablet'?(movingBoard[nativeHint]??'Move the tablet slowly to show a different view.'):(movingPhone[nativeHint]??'Move the phone slowly to show a different view.');}
