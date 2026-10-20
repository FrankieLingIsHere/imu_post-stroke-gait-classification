import type { AssessmentProtocol } from './store';
export const protocolGuides: Record<AssessmentProtocol, { title: string; short: string; body: string; extra?: string; sourceUrl?: string }> = {
  'research-walk': {
    title: 'Research walk: what it measures',
    short: 'Short sensor capture for research. It is not a standardized clinical walking test.',
    body: 'This option records phone motion during a short walk for research. Choose 10, 20 or 30 seconds. Walk on a clear, straight path at a comfortable pace and use your usual walking aid. The app starts its sensor timer after it detects the first step, so this is not a fixed-distance speed test. For a measured distance or speed, a worker must separately measure the route and timed interval. Phone-only distance is experimental.',
  },
  '10mwt': {
    sourceUrl: 'https://www.sralab.org/rehabilitation-measures/10-meter-walk-test',
    title: '10-Meter Walk Test (10MWT)',
    short: 'Measures speed over a marked distance. This project uses 1 m to accelerate, 10 m timed, then 1 m to slow down.',
    body: 'Use a marked 12 m path: 1 m to build pace, 10 m for measurement, then 1 m to slow down. Wait for Go at the first mark. Stop at the final mark and stay still until you hear finished. Camera distance is processed afterwards. Any central 10 m speed is an experimental estimate, not a verified clinical result.',
  },
  '2mwt': {
    sourceUrl: 'https://www.sralab.org/rehabilitation-measures/2-minute-walk-test',
    title: 'Two-Minute Walk Test (2MWT)',
    short: 'Measures the distance covered in 2 minutes on a measured course. Rest is allowed; the clock continues.',
    body: 'Follow a clear measured route for two minutes. Stand still at the start until you hear Go. Rest if needed; the clock keeps running. The phone stops and saves automatically. Phone distance is an estimate. A measured course is needed to validate it.',
  },
  '6mwt': {
    sourceUrl: 'https://www.sralab.org/rehabilitation-measures/6-minute-walk-test',
    title: 'Six-Minute Walk Test (6MWT)',
    short: 'Measures distance covered in 6 minutes on a consistent measured course. Rest is allowed; the clock continues.',
    body: 'Follow a clear, level route for six minutes. Stand still at the start until you hear Go. You may slow down or rest; the clock keeps running. The phone stops and saves automatically. Its distance is an estimate. Record any different course length for later validation.',
    extra: 'App walking commentary and turn reminders are disabled for this test. The worker provides the standard timed messages. Optional app audio gives setup, Go and finish cues only.',
  },
  'tug': {
    sourceUrl: 'https://www.sralab.org/rehabilitation-measures/timed-and-go',
    title: 'Timed Up and Go (TUG)',
    short: 'From a chair, stand, walk 3 m, turn, return and sit. The phone saves after you sit still.',
    body: 'Use a sturdy chair and a mark 3 m away. After the standing phone check, sit back and stay still until you hear Go. Stand, walk to the mark, turn, return and sit. Stay still until the phone saves. It cannot verify chair contact or a clinical TUG endpoint, so the saved time is provisional.',
  },
};
