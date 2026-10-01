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
    body: "Use the project’s marked 12 m path: 1 m acceleration, 10 m timed, then 1 m deceleration. Keep the same aid and speed condition across visits. The worker times the middle 10 m with a stopwatch. Capture starts before Go and ends after the worker confirms finish, with a three-minute capture limit. Boundary crossings are not detected. Enter the stopwatch result separately. This is one trial; repeat and average trials according to the selected clinical protocol.",
  },
  '2mwt': {
    title: 'Two-Minute Walk Test (2MWT)',
    short: 'Measures the distance covered in 2 minutes on a measured course. Rest is allowed; the clock continues.',
    body: "Measure distance covered in two minutes on a measured, clear course. Use the same aid and course on repeat tests. Rest is allowed while the clock continues. Capture starts before Go; the two-minute app clock starts with the spoken cue, or the worker tap when voice is off. The worker administers the selected protocol, checks timing, counts laps and measures the final partial distance. The app does not detect laps or verify clinical completion.",
  },
  '6mwt': {
    title: 'Six-Minute Walk Test (6MWT)',
    short: 'Measures distance covered in 6 minutes on a consistent measured course. Rest is allowed; the clock continues.',
    body: "Measure distance in six minutes on a level, measured course. The ATS layout uses a 30 m corridor; document any different course. Standing rests are allowed and the clock continues. Capture starts before Go; the app clock starts with the spoken cue, or the worker tap when voice is off. App walking commentary and turn warnings are suppressed. The worker supplies standardized timed encouragement, counts laps, measures the final partial distance and verifies the clinical outcome.",
    extra: 'App walking commentary and turn reminders are disabled for this test. The worker provides the standard timed messages. Optional app audio gives setup, Go and finish cues only.',
  },
  'tug': {
    title: 'Timed Up and Go (TUG)',
    short: 'From a chair, stand, walk 3 m, turn, return and sit. A worker times the complete sequence.',
    body: "Use a standard armchair and a mark 3 m away. After standing phone checks, sit with your back against the chair. The worker confirms readiness. Capture starts before Go, including the chair rise. Stand, walk to the mark, turn, return and sit. The worker times from Go to seat contact with a separate stopwatch and ends capture when settled. The phone does not detect turns or sitting completion. A three-minute capture limit is not a clinical result. Practise once before the scored trial.",
  },
};
