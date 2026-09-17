/**
 * QualityBadge.tsx — Recording quality result badge for Gait Steps
 *
 * Displays one of three quality outcomes with:
 *   • Colour-coded background (green / amber / red)
 *   • Large emoji icon for quick recognition
 *   • Plain-language label and description
 *   • Full accessibility label for screen readers
 *
 * Quality levels:
 *   'good'        → ✅ Good — green
 *   'acceptable'  → ⚠️ Acceptable — amber
 *   'repeat'      → 🔄 Repeat recommended — red
 *
 * Usage:
 *   <QualityBadge quality="good" />
 *   <QualityBadge quality="repeat" showDescription />
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from '../i18n';
import { colours, fontSizes, fontWeights, spacing, radii, shadows } from '../theme';
import type { RecordingQuality } from '../sensorSim';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface QualityBadgeProps {
  /** The quality level to display */
  quality: RecordingQuality;
  /** If true, shows the plain-language description below the label */
  showDescription?: boolean;
  /** Override container style */
  style?: object;
}

// ─── Quality definitions ──────────────────────────────────────────────────────

interface QualityDef {
  icon: string;
  label: string;
  description: string;
  bgColour: string;
  textColour: string;
  borderColour: string;
  accessibilityLabel: string;
}

const QUALITY_DEFS: Record<RecordingQuality, QualityDef> = {
  good: {
    icon: '✅',
    label: 'Good',
    description:
      'Your recording looks clear and complete. The data has been saved to your progress.',
    bgColour: colours.good,
    textColour: colours.textOnGood,
    borderColour: colours.primaryDark,
    accessibilityLabel:
      'Recording quality: Good. Your recording looks clear and complete.',
  },
  acceptable: {
    icon: '⚠️',
    label: 'Acceptable',
    description:
      'Your recording is usable, but there were some minor issues. You can save it or try again.',
    bgColour: colours.acceptable,
    textColour: colours.textOnAcceptable,
    borderColour: '#A05800',
    accessibilityLabel:
      'Recording quality: Acceptable. Your recording is usable but had some minor issues.',
  },
  repeat: {
    icon: '🔄',
    label: 'Repeat recommended',
    description:
      'The recording was not clear enough to use. Please try again — make sure the phone is secured to your lower back.',
    bgColour: colours.repeat,
    textColour: colours.textOnRepeat,
    borderColour: '#8B1A12',
    accessibilityLabel:
      'Recording quality: Repeat recommended. The recording was not clear enough. Please try again.',
  },
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function QualityBadge({
  quality,
  showDescription = false,
  style,
}: QualityBadgeProps): React.JSX.Element {
  const def = QUALITY_DEFS[quality];

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: def.bgColour, borderColor: def.borderColour },
        style,
      ]}
      accessibilityRole="text"
      accessibilityLabel={def.accessibilityLabel}
    >
      {/* Icon */}
      <Text style={styles.icon} accessibilityElementsHidden importantForAccessibility="no">
        {def.icon}
      </Text>

      {/* Label */}
      <Text style={[styles.label, { color: def.textColour }]}>
        {def.label}
      </Text>

      {/* Optional description */}
      {showDescription && (
        <Text style={[styles.description, { color: def.textColour }]}>
          {def.description}
        </Text>
      )}
    </View>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    borderRadius: radii.xl,
    borderWidth: 2,
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xl,
    alignItems: 'center',
    width: '100%',
    ...shadows.card,
  },

  icon: {
    fontSize: 48,
    marginBottom: spacing.sm,
  },

  label: {
    fontSize: fontSizes.heading,
    fontWeight: fontWeights.bold,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },

  description: {
    fontSize: fontSizes.body,
    fontWeight: fontWeights.regular,
    textAlign: 'center',
    lineHeight: fontSizes.body * 1.5,
    marginTop: spacing.sm,
  },
});
