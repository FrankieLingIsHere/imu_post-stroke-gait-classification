/** Shared high-contrast design tokens. Text respects the system font scale. */
export const colours = {
  primary: '#176B63', primaryLight: '#238479', primaryDark: '#104D47', accent: '#E9B96A',
  good: '#176B63', acceptable: '#E9B96A', repeat: '#A33E37',
  background: '#F6F5F0', surface: '#FFFFFF', surfaceAlt: '#E7F0EB', border: '#CBD8D1',
  textPrimary: '#173B35', textSecondary: '#52665F', textOnPrimary: '#FFFFFF',
  textOnRepeat: '#FFFFFF', textOnGood: '#FFFFFF', textOnAcceptable: '#3E3018',
  countdownBg: '#F7EEDC', recordingBg: '#E7F0EB', disabled: '#DEE4DF', disabledText: '#52665F',
  noticeBg: '#F7EEDC', noticeBorder: '#E9B96A', noticeText: '#65451D',
} as const;
export const fontSizes = { hero: 32, heading: 26, subheading: 22, body: 18, button: 19, caption: 16, badge: 18, step: 16 } as const;
export const fontWeights = { regular: '400', medium: '500', semibold: '600', bold: '700' } as const;
export const lineHeights = { tight: 1.2, normal: 1.45, relaxed: 1.7 };
export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48, xxxl: 64 };
export const touchTargets = { buttonHeight: 56, minHeight: 56, iconButton: 56 };
export const radii = { sm: 8, md: 12, lg: 18, xl: 24, pill: 999 };
export const shadows = { card: { elevation: 0 }, button: { elevation: 0 } };
export const layout = { screenPadding: 20, maxContentWidth: 600 };
export default { colours, fontSizes, fontWeights, lineHeights, spacing, touchTargets, radii, shadows, layout };
