import React from 'react';
import { ScrollView, View, StyleSheet, useWindowDimensions } from 'react-native';
import { Text } from '../i18n';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colours as c } from '../theme';

/** Primary actions stay outside content scrolling; enlarged text may overflow safely. */
export function Screen({ children, actions, title, eyebrow }: React.PropsWithChildren<{ actions?: React.ReactNode; title: string; eyebrow?: string }>) {
  const { height } = useWindowDimensions();
  return <SafeAreaView edges={['left', 'right', 'bottom']} style={s.safe}>
    <View style={s.frame}>
      <ScrollView contentContainerStyle={[s.content, { gap: height < 700 ? 8 : 16, padding: height < 700 ? 16 : 20 }]}>
        {eyebrow && <Text style={s.eyebrow}>{eyebrow}</Text>}
        <Text accessibilityRole="header" style={s.title}>{title}</Text>
        {children}
      </ScrollView>
      {actions && <View style={s.actions}>{actions}</View>}
    </View>
  </SafeAreaView>;
}
export function Card({ children }: React.PropsWithChildren) { return <View style={s.card}>{children}</View>; }
export function Body({ children, muted = false }: React.PropsWithChildren<{ muted?: boolean }>) { return <Text style={[s.body, muted && { color: c.textSecondary }]}>{children}</Text>; }
export const ui = StyleSheet.create({
  row: { flexDirection: 'row', gap: 10, alignItems: 'center' },
  fill: { flex: 1 }, label: { fontSize: 18, color: c.textPrimary, fontWeight: '700' },
  caption: { fontSize: 16, color: c.textSecondary, lineHeight: 22 },
  error: { color: c.repeat, fontSize: 18 },
  choice: { minHeight: 56, borderRadius: 14, borderWidth: 1, borderColor: c.border, backgroundColor: c.surface, padding: 12, justifyContent: 'center', alignItems: 'center', flex: 1 },
  selected: { backgroundColor: c.surfaceAlt, borderColor: c.primary, borderWidth: 2 },
});
const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: c.background }, frame: { flex: 1, width: '100%', maxWidth: 600, alignSelf: 'center' },
  content: { padding: 20, flexGrow: 1 }, title: { fontSize: 28, fontWeight: '700', color: c.textPrimary, letterSpacing: -0.6 },
  eyebrow: { fontSize: 16, fontWeight: '700', color: c.primary, letterSpacing: 1.4 },
  body: { fontSize: 18, lineHeight: 26, color: c.textPrimary },
  card: { backgroundColor: c.surface, padding: 16, borderRadius: 20, gap: 8, borderWidth: 1, borderColor: c.border },
  actions: { paddingHorizontal: 20, paddingTop: 10, paddingBottom: 12, gap: 8, borderTopWidth: 1, borderColor: c.border, backgroundColor: c.background },
});
