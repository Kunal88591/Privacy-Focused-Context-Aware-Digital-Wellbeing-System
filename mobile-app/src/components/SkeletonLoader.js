/**
 * Skeleton Loader Component
 * Animated placeholder for loading states
 */

import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';

const SkeletonLoader = ({ width = '100%', height = 20, borderRadius = 4, style }) => {
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(animatedValue, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(animatedValue, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, [animatedValue]);

  const opacity = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 0.7],
  });

  return (
    <Animated.View
      style={[
        styles.skeleton,
        {
          width,
          height,
          borderRadius,
          opacity,
        },
        style,
      ]}
    />
  );
};

// Skeleton for card component
export const CardSkeleton = () => (
  <View style={styles.card}>
    <SkeletonLoader width="60%" height={20} style={styles.title} />
    <SkeletonLoader width="100%" height={16} style={styles.line} />
    <SkeletonLoader width="80%" height={16} style={styles.line} />
    <SkeletonLoader width="40%" height={14} style={styles.subtitle} />
  </View>
);

// Skeleton for stat card
export const StatCardSkeleton = () => (
  <View style={styles.statCard}>
    <SkeletonLoader width={60} height={30} borderRadius={8} />
    <SkeletonLoader width="80%" height={12} style={{ marginTop: 8 }} />
  </View>
);

// Skeleton for sensor card
export const SensorCardSkeleton = () => (
  <View style={styles.sensorCard}>
    <SkeletonLoader width={40} height={40} borderRadius={20} />
    <SkeletonLoader width="80%" height={18} style={{ marginTop: 8 }} />
    <SkeletonLoader width="60%" height={12} style={{ marginTop: 4 }} />
  </View>
);

// Skeleton for notification item
export const NotificationSkeleton = () => (
  <View style={styles.notificationCard}>
    <View style={styles.notificationHeader}>
      <SkeletonLoader width="40%" height={14} />
      <SkeletonLoader width={60} height={20} borderRadius={10} />
    </View>
    <SkeletonLoader width="100%" height={16} style={{ marginTop: 8 }} />
    <SkeletonLoader width="70%" height={16} style={{ marginTop: 4 }} />
    <SkeletonLoader width="30%" height={12} style={{ marginTop: 8 }} />
  </View>
);

// Skeleton for dashboard (HomeScreen)
export const DashboardSkeleton = () => (
  <View style={styles.container}>
    <View style={styles.header}>
      <SkeletonLoader width="60%" height={32} />
      <SkeletonLoader width="40%" height={16} style={{ marginTop: 8 }} />
    </View>
    
    <CardSkeleton />
    <CardSkeleton />
    
    <View style={styles.statsRow}>
      <StatCardSkeleton />
      <StatCardSkeleton />
      <StatCardSkeleton />
    </View>
  </View>
);

const styles = StyleSheet.create({
  skeleton: {
    backgroundColor: '#E0E0E0',
  },
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 20,
    paddingTop: 40,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 20,
    marginBottom: 20,
  },
  title: {
    marginBottom: 12,
  },
  line: {
    marginBottom: 8,
  },
  subtitle: {
    marginTop: 8,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
  },
  sensorCard: {
    width: '48%',
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    alignItems: 'center',
  },
  statsRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  notificationCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 20,
    marginBottom: 12,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
});

export default SkeletonLoader;
