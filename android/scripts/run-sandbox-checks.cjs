// Exercises production UI/components/native contracts without connecting a phone.
// Substituted hardware and clocks are software evidence, never patient measurements.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {spawn} = require('node:child_process');
const app = path.resolve(__dirname, '..');
const output = path.join(app, 'dist', 'sandbox-checks');
const python = process.env.GAIT_PYTHON || path.join(os.homedir(), '.venv', 'Scripts', 'python.exe');
const nativeTools = path.join(app, 'dist', 'native-distance-tools');
const javaHome = process.env.JAVA_HOME || path.join(nativeTools, 'jdk-17.0.20.1+1');
const jsonJar = process.env.GAIT_JSON_JAR || path.join(app, 'dist', 'phone-vio-native', 'json.jar');
const prerequisites = [python, jsonJar, path.join(javaHome, 'bin', process.platform === 'win32' ? 'javac.exe' : 'javac')];
const steps = [
  ['app-components', process.execPath, ['--test', ...fs.readdirSync(path.join(app, 'tests')).filter(n => n.endsWith('.test.cjs')).sort().map(n => path.join(app, 'tests', n))], app],
  ['typescript', process.execPath, [require.resolve('typescript/lib/tsc.js'), '--noEmit'], app],
  ['native-contracts', python, ['-m', 'unittest', 'android/research/test_vio_bootstrap.py', '-v'], path.dirname(app)],
  ['browser-flows', process.execPath, [require.resolve('@playwright/test/cli'), 'test'], app],
];
async function run() {
  fs.mkdirSync(output, {recursive: true});
  const report = {startedAt: new Date().toISOString(), physicalPhoneUsed: false,
    simulatedHardware: true, clinicalValidation: false, distanceAccuracyValidated: false,
    audibleSpeechValidated: false, steps: [], passed: false};
  const save = () => fs.writeFileSync(path.join(output, 'verification.json'), JSON.stringify(report, null, 2) + '\n');
  save();
  const missing = prerequisites.filter(p => !fs.existsSync(p));
  if (missing.length) {
    report.error = `Missing local prerequisites: ${missing.join(', ')}. Set GAIT_PYTHON, JAVA_HOME or GAIT_JSON_JAR; no checks were silently skipped.`;
    save(); throw new Error(report.error);
  }
  for (const [name, executable, args, cwd] of steps) {
    console.log(`Starting ${name} (no physical phone).`);
    const began = Date.now();
    const result = await new Promise((resolve, reject) => {
      let stdout = '', stderr = '';
      const child = spawn(executable, args, {cwd, env: {...process.env, JAVA_HOME: javaHome, GAIT_JSON_JAR: jsonJar, CI: '1', NO_COLOR: '1'}});
      child.stdout.on('data', b => {stdout += b;});
      child.stderr.on('data', b => {stderr += b;});
      child.on('error', reject);
      child.on('close', code => resolve({code, stdout, stderr}));
    });
    fs.writeFileSync(path.join(output, name + '.log'), result.stdout + '\n--- stderr ---\n' + result.stderr);
    const skipped = name === 'native-contracts' && /\bskipped\b/i.test(result.stdout + result.stderr);
    const record = {name, exitCode: result.code, seconds: (Date.now() - began) / 1000, passed: result.code === 0 && !skipped, log: name + '.log'};
    report.steps.push(record); save();
    if (!record.passed) throw new Error(`${name} failed; inspect ${path.join(output, record.log)}.`);
    console.log(`Passed ${name} (${record.seconds.toFixed(1)} s).`);
  }
  report.passed = true; report.completedAt = new Date().toISOString(); save();
  console.log(`Software checks passed. Report: ${path.join(output, 'verification.json')}`);
  console.log('Phone camera scheduling, audible TTS and measured walking distance remain physical checks.');
}
run().catch(error => {console.error(error.message); process.exitCode = 1;});
