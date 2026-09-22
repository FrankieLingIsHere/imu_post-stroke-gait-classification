import React from 'react';
import { Text } from 'react-native';
import { releaseInfo } from '../releaseInfo';
import { colours } from '../theme';

/** Small, copyable release marker for support and research provenance. */
export default function ReleaseInfo() {
  const r = releaseInfo();
  const version = r.appVersion ? `v${r.appVersion}` : 'web';
  const build = r.buildNumber ? ` · build ${r.buildNumber}` : '';
  const channel = r.channel ? ` · ${r.channel}` : '';
  const update = r.updateId ? ` · update ${r.updateId.slice(0, 8)}` : ' · bundled';
  return <Text selectable style={{ fontSize: 12, color: colours.textSecondary }}>GaitTrace {version}{build}{channel}{update}</Text>;
}
