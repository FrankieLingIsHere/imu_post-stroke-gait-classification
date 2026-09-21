import React from 'react';
import { Text } from 'react-native';
import { releaseInfo } from '../releaseInfo';
import { colours } from '../theme';

export default function ReleaseInfo() {
  const r=releaseInfo();
  return <Text selectable style={{fontSize:12,color:colours.textSecondary}}>
    GaitTrace {r.appVersion ?? 'web'}{r.buildNumber ? ` (${r.buildNumber})` : ''}
    {r.channel ? ` · ${r.channel}` : ''}{r.updateId ? ` · ${r.updateId.slice(0,8)}` : ' · bundled'}
  </Text>;
}
