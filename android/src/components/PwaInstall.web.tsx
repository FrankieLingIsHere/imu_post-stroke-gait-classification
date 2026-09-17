import React, { useEffect, useState } from 'react';
import { View } from 'react-native';
import BigButton from './BigButton';
import { Text } from '../i18n';
import { ui } from './Screen';

type DeferredInstall = { prompt(): Promise<void>; userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }> };

export default function PwaInstall() {
  const [prompt, setPrompt] = useState<DeferredInstall | null>(null);
  const [installed, setInstalled] = useState(false);
  useEffect(() => {
    const ready = (event: Event) => { event.preventDefault(); setPrompt(event as unknown as DeferredInstall); };
    const complete = () => { setInstalled(true); setPrompt(null); };
    window.addEventListener('beforeinstallprompt', ready);
    window.addEventListener('appinstalled', complete);
    return () => { window.removeEventListener('beforeinstallprompt', ready); window.removeEventListener('appinstalled', complete); };
  }, []);
  if (installed || window.matchMedia('(display-mode: standalone)').matches) return null;
  if (prompt) return <BigButton label="Install on this phone" variant="outline" onPress={() => { void prompt.prompt().then(() => prompt.userChoice).then(choice => { if (choice.outcome === 'accepted') setInstalled(true); setPrompt(null); }).catch(() => {}); }} />;
  return <View style={{ gap: 4 }}><Text style={ui.caption}>To install, open your browser menu and choose Add to Home screen. Browser sensor access can still vary.</Text></View>;
}
