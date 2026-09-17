import { messages } from './translations';
export type Language = 'en' | 'ms' | 'zh';
let current: Language = 'en';
const listeners = new Set<() => void>();
export const locale = (language = current) => ({ en: 'en-MY', ms: 'ms-MY', zh: 'zh-CN' })[language];
export const getLanguage = () => current;
export function setLanguage(language: Language) { current = language; listeners.forEach(fn => fn()); }
export function subscribeLanguage(fn: () => void) { listeners.add(fn); return () => { listeners.delete(fn); }; }
const templates = Object.entries(messages).filter(([key]) => key.includes('{0}')).map(([key, values]) => {
  const escaped = key.split(/(\{\d+\})/).map(p => /^\{\d+\}$/.test(p) ? '(.+?)' : p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('');
  return { pattern: new RegExp('^' + escaped + '$'), values };
});
/** Explicit catalog templates preserve numbers and raw research identifiers. */
export function translate(text: string, language = current): string {
  if (language === 'en') return text;
  const index = language === 'ms' ? 0 : 1;
  if (Object.prototype.hasOwnProperty.call(messages, text)) return messages[text][index];
  for (const { pattern, values } of templates) {
    const match = text.match(pattern);
    if (match) return values[index].replace(/\{(\d+)\}/g, (_, n) => translate(match[Number(n) + 1], language));
  }
  // Composed captions and multiline capture notes retain their separators.
  if (text.includes('\n')) return text.split('\n').map(s => translate(s, language)).join('\n');
  if (text.includes(' · ')) return text.split(' · ').map(s => translate(s, language)).join(' · ');
  return text;
}
