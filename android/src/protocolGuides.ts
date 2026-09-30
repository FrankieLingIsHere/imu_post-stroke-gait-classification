import type { AssessmentProtocol } from './store';
export const protocolGuides: Record<AssessmentProtocol, { title: string; short: string; body: string; extra?: string }> = {
  'research-walk': {
    title: 'Research walk: what it measures',
    short: 'Short sensor capture for research. It is not a standardized clinical walking test.',
    body: 'This option records phone motion during a short walk for research. Choose 10, 20 or 30 seconds. Walk on a clear, straight path at a comfortable pace and use your usual walking aid. The app starts its sensor timer after it detects the first step, so this is not a fixed-distance speed test. For a measured distance or speed, a worker must separately measure the route and timed interval. Phone-only distance is experimental.',
  },
  '10mwt': {
    title: '10-Meter Walk Test (10MWT)',
    short: 'Measures speed over a marked distance. This project uses 1 m to accelerate, 10 m timed, then 1 m to slow down.',
    body: 'Purpose: measure walking speed over a known distance. This project’s selected layout is 12 m in a straight line: 1 m to accelerate, a central 10 m timed zone, and 1 m to slow down. The worker starts and stops the stopwatch as the participant crosses the two timed-zone marks; speed is 10 metres divided by those seconds. Keep the same usual aid and speed condition when comparing visits. The source describes two comfortable-speed trials and two fast-as-safe trials, averaged separately. GaitTrace records phone sensors but does not detect the marks, run those four trials, or time the central 10 m. The app’s 180-second sensor window is not the test time; the worker must time and enter the 10 m result.',
  },
  '2mwt': {
    title: 'Two-Minute Walk Test (2MWT)',
    short: 'Measures the distance covered in 2 minutes on a measured course. Rest is allowed; the clock continues.',
    body: 'Purpose: measure how far the participant can walk in two minutes. Use a measured, clear course and the same usual walking aid on repeat tests. The standardized instruction asks the person to cover as much distance as safely possible; slowing down or stopping to rest is allowed, and the clock keeps running. No hands-on help is allowed for the standard test. The worker starts the protocol stopwatch at Go, counts complete laps and measures the final partial distance, then records rests. GaitTrace’s sensor timer waits for a detected first step and is not a substitute for the stopwatch or measured distance. Enter the course length before starting.',
  },
  '6mwt': {
    title: 'Six-Minute Walk Test (6MWT)',
    short: 'Measures distance covered in 6 minutes on a consistent measured course. Rest is allowed; the clock continues.',
    body: 'Purpose: measure the distance walked in six minutes as a self-paced test of functional walking capacity. Use a measured, level course and keep the same course and aid across visits. The ATS standard uses a 30 m corridor with turn markers; shorter courses add turns and can change the distance, so document the actual course. The participant may slow down or stand and rest, but the timer continues. The worker uses the standardized timed encouragement, counts laps and partial distance, and records rests. GaitTrace’s sensor timer waits for a detected first step and does not count laps or administer the standardized protocol. Its live prompts are not the ATS script; for a standardized 6MWT, have a worker administer the test and do not use extra app walking cues as a replacement.',
    extra: 'For a standardized 6MWT, switch off both Voice Guidance and Direction Reminders during the walk. A worker should give only the standard timed messages.',
  },
  'tug': {
    title: 'Timed Up and Go (TUG)',
    short: 'From a chair, stand, walk 3 m, turn, return and sit. A worker times the complete sequence.',
    body: 'Purpose: observe functional mobility through a chair transfer, short walk, turn and return. Use a standard armchair, mark a line 3 m away, and use the person’s usual footwear and walking aid. On Go, the person stands, walks at a comfortable and safe pace to the line, turns, walks back and sits. The worker starts the stopwatch at Go and stops when the person is seated again (buttocks on the chair). Record the aid and any assistance; standard instructions include a practice trial. GaitTrace does not detect standing, the 3 m line, turning completion or seat contact. Its 180-second sensor capture is not the TUG time; a worker must time and enter the complete sequence.',
  },
};
