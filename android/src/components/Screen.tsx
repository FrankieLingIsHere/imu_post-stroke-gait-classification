import React, {useEffect,useRef} from 'react';
import { Text as NativeText, ScrollView, View, StyleSheet, useWindowDimensions, KeyboardAvoidingView, Platform } from 'react-native';
import { Text } from '../i18n';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colours as c } from '../theme';

/** Primary actions stay outside content scrolling; constrained areas scroll within their bounds. */
export function Screen({ children, actions, title, eyebrow, fullScreen = false, scrollKey, translateTitle=true }: React.PropsWithChildren<{ actions?: React.ReactNode; title: string; eyebrow?: string; fullScreen?: boolean; scrollKey?:string|number;translateTitle?:boolean }>) {
  const { height } = useWindowDimensions();
  const scroll=useRef<ScrollView>(null);
  useEffect(()=>{scroll.current?.scrollTo({y:0,animated:false});},[scrollKey]);
  const TitleText=translateTitle?Text:NativeText;
  return <SafeAreaView edges={fullScreen ? ['top', 'left', 'right', 'bottom'] : ['left', 'right', 'bottom']} style={s.safe}>
    <KeyboardAvoidingView style={s.frame} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView ref={scroll} style={{flex:1,minHeight:0}} keyboardShouldPersistTaps="handled" contentContainerStyle={[s.content, { gap: height < 700 ? 8 : 16, padding: height < 700 ? 16 : 20 }]}>
        {eyebrow && <TitleText style={s.eyebrow}>{eyebrow}</TitleText>}
        <TitleText accessibilityRole="header" style={s.title}>{title}</TitleText>
        {children}
      </ScrollView>
      {actions && <ScrollView style={{flexGrow:0,flexShrink:0,maxHeight:'42%'}} keyboardShouldPersistTaps="handled" contentContainerStyle={s.actions}>{actions}</ScrollView>}
    </KeyboardAvoidingView>
  </SafeAreaView>;
}
export function Card({ children }: React.PropsWithChildren) { return <View style={s.card}>{children}</View>; }
export function Body({ children, muted = false }: React.PropsWithChildren<{ muted?: boolean }>) { return <Text style={[s.body, muted && { color: c.textSecondary }]}>{children}</Text>; }
export const ui = StyleSheet.create({
  row: { flexDirection: 'row', gap: 10, alignItems: 'center' },
  fill: { flex: 1, minWidth: 0 }, label: { fontSize: 18, color: c.textPrimary, fontWeight: '700' },
  caption: { fontSize: 16, color: c.textSecondary, lineHeight: 22 },
  error: { color: c.repeat, fontSize: 18 },
  choice: { minHeight: 56, borderRadius: 14, borderWidth: 1, borderColor: c.border, backgroundColor: c.surface, padding: 12, justifyContent: 'center', alignItems: 'center', flex: 1 },
  selected: { backgroundColor: c.surfaceAlt, borderColor: c.primary, borderWidth: 2 },
});
const s = StyleSheet.create({
  safe: { flex: 1, minHeight:0, backgroundColor: c.background }, frame: { flex: 1, minHeight:0, width: '100%', maxWidth: 600, alignSelf: 'center' },
  content: { padding: 20, flexGrow: 1 }, title: { fontSize: 28, fontWeight: '700', color: c.textPrimary, letterSpacing: -0.6 },
  eyebrow: { fontSize: 16, fontWeight: '700', color: c.primary, letterSpacing: 1.4 },
  body: { fontSize: 18, lineHeight: 26, color: c.textPrimary },
  card: { backgroundColor: c.surface, padding: 16, borderRadius: 20, gap: 8, borderWidth: 1, borderColor: c.border },
  actions: { paddingHorizontal: 20, paddingTop: 10, paddingBottom: 12, gap: 8, borderTopWidth: 1, borderColor: c.border, backgroundColor: c.background },
});
