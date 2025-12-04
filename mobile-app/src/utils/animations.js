/**
 * Animation Utilities
 * Common animations for UI components
 */

import { Animated } from 'react-native';

/**
 * Fade in animation
 */
export const fadeIn = (animatedValue, duration = 300) => {
  return Animated.timing(animatedValue, {
    toValue: 1,
    duration,
    useNativeDriver: true,
  });
};

/**
 * Fade out animation
 */
export const fadeOut = (animatedValue, duration = 300) => {
  return Animated.timing(animatedValue, {
    toValue: 0,
    duration,
    useNativeDriver: true,
  });
};

/**
 * Scale in animation
 */
export const scaleIn = (animatedValue, duration = 200) => {
  return Animated.spring(animatedValue, {
    toValue: 1,
    friction: 3,
    tension: 40,
    useNativeDriver: true,
  });
};

/**
 * Scale out animation
 */
export const scaleOut = (animatedValue, duration = 200) => {
  return Animated.spring(animatedValue, {
    toValue: 0,
    friction: 3,
    tension: 40,
    useNativeDriver: true,
  });
};

/**
 * Slide in from bottom
 */
export const slideInFromBottom = (animatedValue, distance = 50, duration = 300) => {
  return Animated.timing(animatedValue, {
    toValue: 0,
    duration,
    useNativeDriver: true,
  });
};

/**
 * Pulse animation (scale up and down)
 */
export const pulse = (animatedValue, duration = 1000) => {
  return Animated.loop(
    Animated.sequence([
      Animated.timing(animatedValue, {
        toValue: 1.05,
        duration: duration / 2,
        useNativeDriver: true,
      }),
      Animated.timing(animatedValue, {
        toValue: 1,
        duration: duration / 2,
        useNativeDriver: true,
      }),
    ])
  );
};

/**
 * Shake animation (error feedback)
 */
export const shake = (animatedValue) => {
  return Animated.sequence([
    Animated.timing(animatedValue, {
      toValue: 10,
      duration: 50,
      useNativeDriver: true,
    }),
    Animated.timing(animatedValue, {
      toValue: -10,
      duration: 50,
      useNativeDriver: true,
    }),
    Animated.timing(animatedValue, {
      toValue: 10,
      duration: 50,
      useNativeDriver: true,
    }),
    Animated.timing(animatedValue, {
      toValue: 0,
      duration: 50,
      useNativeDriver: true,
    }),
  ]);
};

/**
 * Stagger animation for lists
 */
export const staggerList = (animatedValues, duration = 100, staggerDelay = 50) => {
  return Animated.stagger(
    staggerDelay,
    animatedValues.map((value) =>
      Animated.timing(value, {
        toValue: 1,
        duration,
        useNativeDriver: true,
      })
    )
  );
};

export default {
  fadeIn,
  fadeOut,
  scaleIn,
  scaleOut,
  slideInFromBottom,
  pulse,
  shake,
  staggerList,
};
