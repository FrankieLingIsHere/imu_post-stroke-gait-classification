export interface LocationDistanceSummary {
  version: 'foreground-gps-distance-v1';
  source: 'android-fused-location';
  distanceM: number | null;
  acceptedFixes: number;
  medianAccuracyM: number | null;
  status: 'usable-cross-check' | 'low-quality' | 'unavailable';
  rawCoordinatesSaved: false;
  note: string;
}

type Fix = { latitude: number; longitude: number; accuracy: number | null; timestamp: number };

/** Keeps only an aggregate; coordinates exist transiently in memory and are never exported. */
export class ForegroundDistanceTracker {
  private previous: Fix | null = null;
  private distances: number[] = [];
  private accuracies: number[] = [];

  add(fix: Fix) {
    if (![fix.latitude, fix.longitude, fix.timestamp].every(Number.isFinite) ||
        fix.latitude < -90 || fix.latitude > 90 || fix.longitude < -180 || fix.longitude > 180 ||
        fix.accuracy === null || !Number.isFinite(fix.accuracy) || fix.accuracy <= 0 || fix.accuracy > 20) return;
    const previous = this.previous;
    this.previous = fix;
    if (!previous) { this.accuracies.push(fix.accuracy); return; }
    const seconds = (fix.timestamp - previous.timestamp) / 1000;
    if (seconds <= 0 || seconds > 8) { this.accuracies.push(fix.accuracy); return; }
    const distance = haversine(previous.latitude, previous.longitude, fix.latitude, fix.longitude);
    const speed = distance / seconds;
    // Drop implausible jumps, including many multipath/GNSS glitches.
    if (!Number.isFinite(distance) || speed > 3.5) return;
    this.distances.push(distance);
    this.accuracies.push(fix.accuracy);
  }

  finish(): LocationDistanceSummary {
    const distanceM = this.distances.reduce((sum, value) => sum + value, 0);
    const accuracy = median(this.accuracies);
    const acceptedFixes = this.accuracies.length;
    const usable = acceptedFixes >= 4 && accuracy !== null && accuracy <= 5 && distanceM >= 10;
    return {
      version: 'foreground-gps-distance-v1', source: 'android-fused-location',
      distanceM: acceptedFixes >= 2 && this.distances.length > 0 ? distanceM : null,
      acceptedFixes, medianAccuracyM: accuracy,
      status: usable ? 'usable-cross-check' : acceptedFixes ? 'low-quality' : 'unavailable',
      rawCoordinatesSaved: false,
      note: 'Outdoor location-derived cross-check only. Accuracy is reported by the device and does not establish clinical validity; short, indoor or obstructed walks may be unreliable.'
    };
  }
}

function median(values: number[]): number | null {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function haversine(lat1: number, lon1: number, lat2: number, lon2: number) {
  const rad = Math.PI / 180;
  const dLat = (lat2 - lat1) * rad, dLon = (lon2 - lon1) * rad;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * rad) * Math.cos(lat2 * rad) * Math.sin(dLon / 2) ** 2;
  return 6371000 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}
