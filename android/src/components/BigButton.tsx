/**
 * BigButton.tsx — Accessible large-touch-target button for Gait Steps
 *
 * Elderly-first constraints enforced:
 *   • Minimum height: 64dp (exceeds 56dp minimum)
 *   • Minimum font size: 22sp
 *   • Icon + text always shown together (never icon-only)
 *   • Disabled state clearly communicated visually and to screen readers
 *   • Full-width by default for easy targeting
 *
 * Usage:
 *   <BigButton
 *     label="Start walking test"
 *     icon="▶"
 *     onPress={() => navigation.navigate('Prepare')}
 *   />
 *   <BigButton label="Cancel" icon="✕" variant="outline" onPress={handleCancel} />
 *   <BigButton label="Loading..." icon="⏳" disabled />
 */

import React from 'react';
import { TouchableOpacity, View, StyleSheet, ActivityIndicator, type ViewStyle, type TextStyle,  } from 'react-native';
import { Text, t, useLanguage } from '../i18n';
import { colours, fontSizes, fontWeights, spacing, touchTargets, radii, shadows } from '../theme';

// ─── Types ────────────────────────────────────────────────────────────────────

export type BigButtonVariant = 'primary' | 'outline' | 'ghost' | 'danger';

export interface BigButtonProps {
  /** Button label — always visible alongside the icon */
  label: string;
  /** Emoji or text icon shown to the left of the label */
  icon?: string;
  /** Called when the button is pressed */
  onPress?: () => void;
  /** Visual style variant */
  variant?: BigButtonVariant;
  /** Disables interaction and dims the button */
  disabled?: boolean;
  /** Shows a loading spinner instead of the icon */
  loading?: boolean;
  /** Accessibility hint read by screen readers */
  accessibilityHint?: string;
  /** Override container style */
  style?: ViewStyle;
  /** Override label text style */
  labelStyle?: TextStyle;
  /** Test ID for automated testing */
  testID?: string;
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function BigButton({
  label,
  icon,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  accessibilityHint,
  style,
  labelStyle,
  testID,
}: BigButtonProps): React.JSX.Element {
  useLanguage();
  const isDisabled = disabled || loading;

  // Resolve colours based on variant and disabled state
  const containerStyle = [
    styles.base,
    styles[variant],
    isDisabled && styles.disabled,
    style,
  ];

  const textStyle = [
    styles.label,
    styles[`${variant}Label` as keyof typeof styles],
    isDisabled && styles.disabledLabel,
    labelStyle,
  ];

  return (
    <TouchableOpacity
      style={containerStyle}
      onPress={isDisabled ? undefined : onPress}
      disabled={isDisabled}
      activeOpacity={0.75}
      accessibilityRole="button"
      accessibilityLabel={t(label)}
      accessibilityHint={accessibilityHint ? t(accessibilityHint) : undefined}
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      testID={testID}
    >
      <View style={styles.content}>
        {/* Icon or spinner — always present if icon prop given */}
        {loading ? (
          <ActivityIndicator
            size="small"
            color={variant === 'primary' ? colours.textOnPrimary : colours.primary}
            style={styles.icon}
          />
        ) : icon ? (
          <Text
            style={[styles.iconText, isDisabled && styles.disabledLabel]}
            accessibilityElementsHidden
            importantForAccessibility="no"
          >
            {icon}
          </Text>
        ) : null}

        {/* Label — always visible */}
        <Text style={textStyle}>
          {label}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  base: {
    minHeight: touchTargets.buttonHeight,
    borderRadius: radii.lg,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
    ...shadows.button,
  },

  // ── Variants ──
  primary: {
    backgroundColor: colours.primary,
    borderWidth: 0,
  },
  outline: {
    backgroundColor: colours.surface,
    borderWidth: 2,
    borderColor: colours.primary,
  },
  ghost: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    elevation: 0,
    shadowOpacity: 0,
  },
  danger: {
    backgroundColor: colours.repeat,
    borderWidth: 0,
  },

  // ── Disabled ──
  disabled: {
    backgroundColor: colours.disabled,
    borderColor: colours.disabled,
    elevation: 0,
    shadowOpacity: 0,
  },

  // ── Content layout ──
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },

  // ── Icon ──
  icon: {
    marginRight: spacing.xs,
  },
  iconText: {
    fontSize: fontSizes.body,
    lineHeight: fontSizes.body * 1.2,
  },

  // ── Labels per variant ──
  label: {
    fontSize: fontSizes.button,
    fontWeight: fontWeights.semibold,
    textAlign: 'center',
    flexShrink: 1,
  },
  primaryLabel: {
    color: colours.textOnPrimary,
  },
  outlineLabel: {
    color: colours.primary,
  },
  ghostLabel: {
    color: colours.primary,
  },
  dangerLabel: {
    color: colours.textOnRepeat,
  },
  disabledLabel: {
    color: colours.disabledText,
  },
});
