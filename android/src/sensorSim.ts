/**
 * sensorSim.ts — Simulated IMU data generator for Gait Steps v0.1.0
 *
 * PROTOTYPE ONLY — replace this entire module with expo-sensors in the next phase.
 *
 * Contract (must be preserved when replacing with real sensors):
 *   • Sample rate: 100 Hz (one sample every 10 ms)
 *   • Window size: 500 samples = 5 seconds of data
 *   • Each sample: { x, y, z, magnitude, timestamp }
 *   • magnitude = sqrt(x² + y² + z²) in g (gravitational units)
 *   • timestamp = Unix ms (Date.now() equivalent)
 *   • Output shape for model: (n_windows, 500, 1) — magnitude channel only
 *
 * The simulator generates realistic-looking lower-back walking acceleration:
 *   • Baseline gravity component ~1 g on the vertical axis
 *   • Step-frequency oscillation at ~1.8 Hz (typical post-stroke cadence)
 *   • Low-amplitude noise on all axes
 *   • Occasional micro-jitter to simulate real sensor noise
 *
 * Usage:
 *   import { startSimulation, stopSimulation, getWindows } from '../sensorSim';
 *
 *   startSimulation();
 *   // ... wait for walk duration ...
 *   stopSimulation();
 *   const windows = getWindows();   // IMUSample[][]
 *   const quality = assessQuality(windows);
 */

// ─── Types ────────────────────────────────────────────────────────────────────

/** A single IMU sample — matches the shape expo-sensors will provide. */
export interface IMUSample {
  /** Acceleration on the mediolateral axis (g) */
  x: number;
  /** Acceleration on the vertical axis (g) — includes gravity */
  y: number;
  /** Acceleration on the anteroposterior axis (g) */
  z: number;
  /** Resultant magnitude sqrt(x²+y²+z²) in g */
  magnitude: number;
  /** Unix timestamp in milliseconds */
  timestamp: number;
}

/** Quality assessment result from simulated data */
export type RecordingQuality = 'good' | 'acceptable' | 'repeat';

/** A window of 500 samples (5 seconds at 100 Hz) */
export type IMUWindow = IMUSample[];

// ─── Constants ────────────────────────────────────────────────────────────────

const SAMPLE_RATE_HZ = 100;
const SAMPLE_INTERVAL_MS = 1000 / SAMPLE_RATE_HZ; // 10 ms
const WINDOW_SIZE = 500; // samples per window

// Simulated gait parameters
const STEP_FREQ_HZ = 1.8;          // typical post-stroke step frequency
const STEP_AMPLITUDE = 0.25;       // g — vertical oscillation amplitude
const LATERAL_AMPLITUDE = 0.12;    // g — mediolateral sway
const AP_AMPLITUDE = 0.15;         // g — anteroposterior oscillation
const NOISE_AMPLITUDE = 0.03;      // g — sensor noise floor
const GRAVITY = 1.0;               // g — baseline gravity on vertical axis

// ─── Module state ─────────────────────────────────────────────────────────────

let _intervalId: ReturnType<typeof setInterval> | null = null;
let _samples: IMUSample[] = [];
let _sampleIndex = 0;
let _isRunning = false;

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Gaussian-like noise using Box-Muller (approximated with sum of uniforms) */
function gaussianNoise(amplitude: number): number {
  // Sum of 6 uniforms approximates normal distribution (central limit theorem)
  let sum = 0;
  for (let i = 0; i < 6; i++) {
    sum += Math.random() - 0.5;
  }
  return (sum / 3) * amplitude;
}

/** Generate one simulated IMU sample at a given time index */
function generateSample(index: number): IMUSample {
  const t = index / SAMPLE_RATE_HZ; // time in seconds
  const stepPhase = 2 * Math.PI * STEP_FREQ_HZ * t;

  // Vertical axis: gravity + step oscillation (dominant component)
  const y = GRAVITY
    + STEP_AMPLITUDE * Math.sin(stepPhase)
    + STEP_AMPLITUDE * 0.3 * Math.sin(2 * stepPhase) // harmonic
    + gaussianNoise(NOISE_AMPLITUDE);

  // Mediolateral: alternating sway at half step frequency (one sway per step)
  const x = LATERAL_AMPLITUDE * Math.sin(stepPhase / 2 + Math.PI / 4)
    + gaussianNoise(NOISE_AMPLITUDE);

  // Anteroposterior: slight forward-backward oscillation
  const z = AP_AMPLITUDE * Math.cos(stepPhase + Math.PI / 6)
    + gaussianNoise(NOISE_AMPLITUDE);

  const magnitude = Math.sqrt(x * x + y * y + z * z);

  return {
    x: parseFloat(x.toFixed(4)),
    y: parseFloat(y.toFixed(4)),
    z: parseFloat(z.toFixed(4)),
    magnitude: parseFloat(magnitude.toFixed(4)),
    timestamp: Date.now(),
  };
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Start the simulated IMU data stream.
 * Clears any previous samples.
 * Fires at 100 Hz using setInterval.
 */
export function startSimulation(): void {
  if (_isRunning) {
    console.warn('[sensorSim] Already running — call stopSimulation() first.');
    return;
  }

  _samples = [];
  _sampleIndex = 0;
  _isRunning = true;

  _intervalId = setInterval(() => {
    const sample = generateSample(_sampleIndex);
    _samples.push(sample);
    _sampleIndex++;
  }, SAMPLE_INTERVAL_MS);

  console.log('[sensorSim] Simulation started at 100 Hz.');
}

/**
 * Stop the simulated IMU data stream.
 * Samples collected so far are preserved and accessible via getWindows().
 */
export function stopSimulation(): void {
  if (!_isRunning) {
    return;
  }

  if (_intervalId !== null) {
    clearInterval(_intervalId);
    _intervalId = null;
  }

  _isRunning = false;
  console.log(`[sensorSim] Simulation stopped. ${_samples.length} samples collected.`);
}

/**
 * Returns all collected samples as non-overlapping windows of 500 samples.
 * Partial final window is discarded.
 *
 * @returns Array of IMUWindow (each window = 500 IMUSamples)
 */
export function getWindows(): IMUWindow[] {
  const windows: IMUWindow[] = [];
  const totalWindows = Math.floor(_samples.length / WINDOW_SIZE);

  for (let w = 0; w < totalWindows; w++) {
    const start = w * WINDOW_SIZE;
    windows.push(_samples.slice(start, start + WINDOW_SIZE));
  }

  return windows;
}

/**
 * Returns all raw samples collected since the last startSimulation() call.
 */
export function getRawSamples(): IMUSample[] {
  return [..._samples];
}

/**
 * Returns true if the simulation is currently running.
 */
export function isSimulationRunning(): boolean {
  return _isRunning;
}

/**
 * Assess recording quality from collected windows.
 *
 * PROTOTYPE LOGIC — placeholder for real quality checks in next phase.
 * Real checks will include: gap detection, jitter analysis, saturation flags.
 *
 * Current heuristic (based on simulated magnitude variance):
 *   • variance > 0.04 g²  → 'good'
 *   • variance > 0.01 g²  → 'acceptable'
 *   • otherwise           → 'repeat'
 *
 * @param windows  Output of getWindows()
 * @returns        RecordingQuality
 */
export function assessQuality(windows: IMUWindow[]): RecordingQuality {
  if (windows.length === 0) {
    return 'repeat';
  }

  // Flatten all magnitudes
  const magnitudes = windows.flat().map((s) => s.magnitude);

  if (magnitudes.length === 0) {
    return 'repeat';
  }

  // Compute variance of magnitude signal
  const mean = magnitudes.reduce((a, b) => a + b, 0) / magnitudes.length;
  const variance =
    magnitudes.reduce((acc, m) => acc + (m - mean) ** 2, 0) / magnitudes.length;

  // Check for flat signal (phone not moving — likely not worn)
  const range = Math.max(...magnitudes) - Math.min(...magnitudes);
  if (range < 0.05) {
    return 'repeat'; // signal too flat — phone probably stationary
  }

  if (variance >= 0.04) {
    return 'good';
  } else if (variance >= 0.01) {
    return 'acceptable';
  } else {
    return 'repeat';
  }
}

// ─── Export constants for use in screens ─────────────────────────────────────

export { SAMPLE_RATE_HZ, WINDOW_SIZE, SAMPLE_INTERVAL_MS };
