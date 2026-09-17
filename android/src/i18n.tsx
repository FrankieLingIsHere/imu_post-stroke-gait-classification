import React, { useSyncExternalStore } from 'react';
import { Text as NativeText, TextProps, View, Pressable } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getLanguage, setLanguage, subscribeLanguage, translate, locale, Language } from './language';
export { translate as t } from './language';
export function useLanguage() { return useSyncExternalStore(subscribeLanguage, getLanguage, getLanguage); }
let selectionChanged = false;
export async function restoreLanguage() {
  try { const value = await AsyncStorage.getItem('gait-language-v1'); if (!selectionChanged && ['en','ms','zh'].includes(value ?? '')) setLanguage(value as Language); } catch { /* English remains available when storage fails. */ }
}
export function Text({ children, accessibilityLabel, ...props }: TextProps) {
  const language = useLanguage();
  const parts = React.Children.toArray(children);
  const content = parts.every(p => typeof p === 'string' || typeof p === 'number') ? translate(parts.join(''), language) : parts.map((p, i) => typeof p === 'string' ? translate(p, language) : p);
  return <NativeText {...props} accessibilityLanguage={locale(language)} accessibilityLabel={accessibilityLabel ? translate(accessibilityLabel, language) : undefined}>{content}</NativeText>;
}
export function LanguagePicker() {
  const current = useLanguage();
  return <View accessibilityRole="radiogroup" style={{ flexDirection: 'row', gap: 8 }}>
    {(['en','ms','zh'] as const).map((language, i) => <Pressable key={language} accessibilityRole="radio" accessibilityState={{ selected: current === language }} accessibilityLabel={['English','Bahasa Melayu','简体中文'][i]} onPress={() => { selectionChanged = true; setLanguage(language); void AsyncStorage.setItem('gait-language-v1', language).catch(() => {}); }} style={{ flex: 1, minHeight: 48, padding: 8, justifyContent: 'center', alignItems: 'center', borderWidth: current === language ? 2 : 1, borderColor: '#176B62', borderRadius: 12 }}><NativeText style={{ fontSize: 17, color: '#164E48', fontWeight: current === language ? '700' : '400' }}>{['English','Melayu','中文'][i]}</NativeText></Pressable>)}
  </View>;
}
