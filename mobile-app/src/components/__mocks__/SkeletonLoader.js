/**
 * Skeleton Loader Mocks
 */

import React from 'react';
import { View } from 'react-native';

export const DashboardSkeleton = () => (
  <View testID="dashboard-skeleton">Skeleton Loading...</View>
);

export const NotificationsSkeleton = () => (
  <View testID="notifications-loading">Loading Notifications...</View>
);

export const PrivacySkeleton = () => (
  <View testID="privacy-loading">Loading Privacy...</View>
);

export const SettingsSkeleton = () => (
  <View testID="settings-loading">Loading Settings...</View>
);
