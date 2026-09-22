import React from 'react';
import { View, Pressable } from 'react-native';
import { Text, t, useLanguage } from '../i18n';
import Svg, { Polyline, Line } from 'react-native-svg';
import type { Sample } from '../recording';
import { ui } from './Screen';
import { colours } from '../theme';
const axes = ['x', 'y', 'z'] as const;
const colors = [colours.primary, '#9B4528', '#4657A3'];
export default function SignalChart({ samples, start, end, units }: { samples: Sample[]; start: number; end: number; units: string }) {
  useLanguage();
  const [selectedAxis, setSelectedAxis] = React.useState<typeof axes[number] | null>(null);
  const visible = samples.filter(s => s.elapsedMs >= start * 1000 && s.elapsedMs < end * 1000);
  if (!visible.length) return <Text style={ui.caption}>No readings in this time range.</Text>;
  let low = Infinity, high = -Infinity;
  for (const sample of visible) for (const axis of axes) { low = Math.min(low, sample[axis]); high = Math.max(high, sample[axis]); }
  const range = Math.max(high - low, 0.001);
  // Bucket min/max preserves short extrema in a display-only reduction. Export retains every sample.
  function points(axis: typeof axes[number]) {
    const reduced: Sample[] = [];
    const size = Math.max(1, Math.ceil(visible.length / 120));
    for (let i = 0; i < visible.length; i += size) {
      const bucket = visible.slice(i, i + size);
      const min = bucket.reduce((a, b) => a[axis] < b[axis] ? a : b);
      const max = bucket.reduce((a, b) => a[axis] > b[axis] ? a : b);
      reduced.push(...[min, max].sort((a, b) => a.elapsedMs - b.elapsedMs));
    }
    return reduced.map(s => `${10 + (s.elapsedMs / 1000 - start) / (end - start) * 300},${120 - (s[axis] - low) / range * 110}`).join(' ');
  }
  return <View accessible accessibilityLabel={t(`Three-axis signal from ${start} to ${end} seconds, range ${low.toFixed(2)} to ${high.toFixed(2)} ${units}. Exact axis readings are in the export.`)}>
    <Text style={ui.caption}>{high.toFixed(2)} {units}</Text>
    <Svg width="100%" height={125} viewBox="0 0 320 130">
      {[10, 65, 120].map(y => <Line key={y} x1="10" x2="310" y1={y} y2={y} stroke={colours.border} />)}
      {axes.map((axis, i) => <Polyline key={axis} points={points(axis)} stroke={colors[i]} opacity={selectedAxis && selectedAxis !== axis ? 0.2 : 1} strokeWidth={selectedAxis === axis ? 2.8 : 1.7} strokeDasharray={i === 1 ? '6,3' : i === 2 ? '2,3' : undefined} fill="none" />)}
    </Svg>
    <Text style={ui.caption}>{low.toFixed(2)} {units} · {start}–{end} sec</Text>
    <View style={[ui.row, { justifyContent: 'space-between' }]}>{axes.map((a, i) => <Pressable key={a} accessibilityRole="button" accessibilityLabel={t(`${a.toUpperCase()} axis`)} accessibilityState={{ selected: selectedAxis === a }} onPress={() => setSelectedAxis(selectedAxis === a ? null : a)} onHoverIn={() => setSelectedAxis(a)} onHoverOut={() => setSelectedAxis(null)} style={{ padding: 6, borderRadius: 8, borderWidth: selectedAxis === a ? 1 : 0, borderColor: colors[i] }}><Text style={[ui.caption, { color: colors[i], fontWeight: '700' }]}>{a.toUpperCase()} {['solid', 'dash', 'dot'][i]}</Text></Pressable>)}</View>
    <Text style={ui.caption}>{selectedAxis ? t(`${selectedAxis.toUpperCase()} axis selected`) : t('Tap an axis legend to highlight it.')}</Text>
  </View>;
}
