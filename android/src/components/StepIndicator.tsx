/**
 * StepIndicator.tsx — 4-step progress indicator for Gait Steps
 *
 * Shows the user where they are in the walking test flow:
 *   Step 1: Prepare
 *   Step 2: Get ready
 *   Step 3: Walk
 *   Step 4: Done
 *
 * Visual states:
 *   • completed  — filled circle with ✓, connector line filled
 *   • active     — filled circle with step number, pulsing border
 *   • pending    — empty circle with step number, greyed out
 *
 * Usage:
 *   <StepIndicator currentStep={2} />   // 1-indexed; step 2 = "Get ready"
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from '../i18n';
import { colours, fontSizes, fontWeights, spacing, radii } from '../theme';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface StepIndicatorProps {
  /** Current active step (1–4, inclusive) */
  currentStep: 1 | 2 | 3 | 4;
}

interface StepDef {
  number: 1 | 2 | 3 | 4;
  label: string;
}

// ─── Step definitions ─────────────────────────────────────────────────────────

const STEPS: StepDef[] = [
  { number: 1, label: 'Prepare' },
  { number: 2, label: 'Get ready' },
  { number: 3, label: 'Walk' },
  { number: 4, label: 'Done' },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function StepIndicator({ currentStep }: StepIndicatorProps): React.JSX.Element {
  return (
    <View
      style={styles.container}
      accessibilityRole="progressbar"
      accessibilityLabel={`Step ${currentStep} of 4: ${STEPS[currentStep - 1].label}`}
      accessibilityValue={{ min: 1, max: 4, now: currentStep }}
    >
      {STEPS.map((step, index) => {
        const isCompleted = step.number < currentStep;
        const isActive = step.number === currentStep;
        const isPending = step.number > currentStep;
        const isLast = index === STEPS.length - 1;

        return (
          <React.Fragment key={step.number}>
            {/* Step circle + label */}
            <View style={styles.stepWrapper}>
              <View
                style={[
                  styles.circle,
                  isCompleted && styles.circleCompleted,
                  isActive && styles.circleActive,
                  isPending && styles.circlePending,
                ]}
              >
                {isCompleted ? (
                  <Text style={styles.checkmark}>✓</Text>
                ) : (
                  <Text
                    style={[
                      styles.stepNumber,
                      isActive && styles.stepNumberActive,
                      isPending && styles.stepNumberPending,
                    ]}
                  >
                    {step.number}
                  </Text>
                )}
              </View>
              <Text
                style={[
                  styles.stepLabel,
                  isCompleted && styles.stepLabelCompleted,
                  isActive && styles.stepLabelActive,
                  isPending && styles.stepLabelPending,
                ]}
                numberOfLines={1}
              >
                {step.label}
              </Text>
            </View>

            {/* Connector line between steps */}
            {!isLast && (
              <View
                style={[
                  styles.connector,
                  isCompleted && styles.connectorCompleted,
                ]}
              />
            )}
          </React.Fragment>
        );
      })}
    </View>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const CIRCLE_SIZE = 36;

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },

  // ── Step wrapper (circle + label stacked) ──
  stepWrapper: {
    alignItems: 'center',
    width: 72,
  },

  // ── Circles ──
  circle: {
    width: CIRCLE_SIZE,
    height: CIRCLE_SIZE,
    borderRadius: CIRCLE_SIZE / 2,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  circleCompleted: {
    backgroundColor: colours.primary,
    borderWidth: 0,
  },
  circleActive: {
    backgroundColor: colours.primary,
    borderWidth: 3,
    borderColor: colours.primaryLight,
  },
  circlePending: {
    backgroundColor: colours.surfaceAlt,
    borderWidth: 2,
    borderColor: colours.border,
  },

  // ── Step numbers / checkmark ──
  checkmark: {
    color: colours.textOnPrimary,
    fontSize: fontSizes.body,
    fontWeight: fontWeights.bold,
  },
  stepNumber: {
    fontSize: fontSizes.body,
    fontWeight: fontWeights.bold,
  },
  stepNumberActive: {
    color: colours.textOnPrimary,
  },
  stepNumberPending: {
    color: colours.textSecondary,
  },

  // ── Labels ──
  stepLabel: {
    fontSize: fontSizes.step,
    textAlign: 'center',
  },
  stepLabelCompleted: {
    color: colours.primary,
    fontWeight: fontWeights.medium,
  },
  stepLabelActive: {
    color: colours.primary,
    fontWeight: fontWeights.bold,
  },
  stepLabelPending: {
    color: colours.textSecondary,
    fontWeight: fontWeights.regular,
  },

  // ── Connector lines ──
  connector: {
    flex: 1,
    height: 3,
    backgroundColor: colours.border,
    marginTop: CIRCLE_SIZE / 2 - 1.5, // vertically centre on circle
    marginHorizontal: 2,
  },
  connectorCompleted: {
    backgroundColor: colours.primary,
  },
});
