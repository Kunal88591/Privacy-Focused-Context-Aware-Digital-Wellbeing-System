/**
 * Android Permissions Utility
 * Handles all dangerous/special permissions for Privacy Wellbeing app
 */

import { NativeModules, Linking, Platform, PermissionsAndroid } from 'react-native';

const { 
  NotificationPermissions, 
  UsageStats, 
  PrivacyVpn, 
  FocusModeModule 
} = NativeModules;

/**
 * Request Notification Listener Permission
 * User must manually enable in Settings → Notification Access
 */
export const requestNotificationAccess = async () => {
  if (Platform.OS !== 'android') return false;
  
  try {
    // Check if already granted
    const granted = await NotificationPermissions?.isEnabled();
    
    if (!granted) {
      // Open notification listener settings
      await Linking.sendIntent('android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS');
    }
    
    return granted;
  } catch (error) {
    console.error('Notification permission error:', error);
    
    // Fallback: Open app settings
    Linking.openSettings();
    return false;
  }
};

/**
 * Check if Notification Access is granted
 */
export const checkNotificationAccess = async () => {
  if (Platform.OS !== 'android') return false;
  
  try {
    return await NotificationPermissions?.isEnabled() || false;
  } catch (error) {
    return false;
  }
};

/**
 * Request Usage Stats Permission (App Usage Tracking)
 * Required for wellbeing insights and focus mode
 */
export const requestUsageStatsPermission = async () => {
  if (Platform.OS !== 'android') return false;
  
  try {
    const granted = await UsageStats?.hasPermission();
    
    if (!granted) {
      // Open usage access settings
      await UsageStats?.requestPermission();
    }
    
    return granted;
  } catch (error) {
    console.error('Usage stats permission error:', error);
    return false;
  }
};

/**
 * Get app usage data for a time range
 */
export const getAppUsage = async (startTime, endTime) => {
  if (Platform.OS !== 'android') return [];
  
  try {
    const hasPermission = await UsageStats?.hasPermission();
    if (!hasPermission) {
      throw new Error('Usage stats permission not granted');
    }
    
    return await UsageStats?.getAppUsage(startTime, endTime) || [];
  } catch (error) {
    console.error('Get app usage error:', error);
    return [];
  }
};

/**
 * Request VPN Permission for Privacy Features
 * Shows system dialog for VPN approval
 */
export const requestVPNPermission = async () => {
  if (Platform.OS !== 'android') return false;
  
  try {
    // This will show Android VPN permission dialog
    return await PrivacyVpn?.requestPermission() || false;
  } catch (error) {
    console.error('VPN permission error:', error);
    return false;
  }
};

/**
 * Start Privacy VPN Service
 */
export const startVPN = async (config = {}) => {
  if (Platform.OS !== 'android') return false;
  
  try {
    const {
      blockTrackers = true,
      blockAds = true,
      customDomains = [],
    } = config;
    
    return await PrivacyVpn?.start({
      blockTrackers,
      blockAds,
      customDomains,
    }) || false;
  } catch (error) {
    console.error('Start VPN error:', error);
    return false;
  }
};

/**
 * Stop Privacy VPN Service
 */
export const stopVPN = async () => {
  if (Platform.OS !== 'android') return false;
  
  try {
    return await PrivacyVpn?.stop() || false;
  } catch (error) {
    console.error('Stop VPN error:', error);
    return false;
  }
};

/**
 * Get VPN Status
 */
export const getVPNStatus = async () => {
  if (Platform.OS !== 'android') return { active: false };
  
  try {
    return await PrivacyVpn?.getStatus() || { active: false };
  } catch (error) {
    return { active: false };
  }
};

/**
 * Request Accessibility Service Permission
 * Required for Focus Mode app blocking
 */
export const requestAccessibilityService = async () => {
  if (Platform.OS !== 'android') return false;
  
  try {
    const granted = await FocusModeModule?.isAccessibilityEnabled();
    
    if (!granted) {
      // Open accessibility settings
      await Linking.sendIntent('android.settings.ACCESSIBILITY_SETTINGS');
    }
    
    return granted;
  } catch (error) {
    console.error('Accessibility permission error:', error);
    
    // Fallback
    Linking.openSettings();
    return false;
  }
};

/**
 * Enable Focus Mode with app blocking
 */
export const enableFocusMode = async (blockedApps = [], duration = 25) => {
  if (Platform.OS !== 'android') return false;
  
  try {
    const hasPermission = await FocusModeModule?.isAccessibilityEnabled();
    if (!hasPermission) {
      throw new Error('Accessibility service not enabled');
    }
    
    return await FocusModeModule?.enable({
      blockedApps,
      duration,
    }) || false;
  } catch (error) {
    console.error('Enable focus mode error:', error);
    return false;
  }
};

/**
 * Disable Focus Mode
 */
export const disableFocusMode = async () => {
  if (Platform.OS !== 'android') return false;
  
  try {
    return await FocusModeModule?.disable() || false;
  } catch (error) {
    console.error('Disable focus mode error:', error);
    return false;
  }
};

/**
 * Request all basic permissions
 * (Internet, Network State, etc. - these are auto-granted)
 */
export const requestBasicPermissions = async () => {
  if (Platform.OS !== 'android') return true;
  
  try {
    const permissions = [
      PermissionsAndroid.PERMISSIONS.INTERNET,
      PermissionsAndroid.PERMISSIONS.ACCESS_NETWORK_STATE,
    ];
    
    const results = await PermissionsAndroid.requestMultiple(permissions);
    
    return Object.values(results).every(
      result => result === PermissionsAndroid.RESULTS.GRANTED
    );
  } catch (error) {
    console.error('Basic permissions error:', error);
    return false;
  }
};

/**
 * Check All Permissions Status
 * Returns object with status of each permission
 */
export const checkAllPermissions = async () => {
  if (Platform.OS !== 'android') {
    return {
      notifications: false,
      usageStats: false,
      vpn: false,
      accessibility: false,
    };
  }
  
  try {
    const [notifications, usageStats, accessibility] = await Promise.all([
      checkNotificationAccess(),
      UsageStats?.hasPermission() || Promise.resolve(false),
      FocusModeModule?.isAccessibilityEnabled() || Promise.resolve(false),
    ]);
    
    const vpnStatus = await getVPNStatus();
    
    return {
      notifications,
      usageStats,
      vpn: vpnStatus.active,
      accessibility,
    };
  } catch (error) {
    console.error('Check all permissions error:', error);
    return {
      notifications: false,
      usageStats: false,
      vpn: false,
      accessibility: false,
    };
  }
};

/**
 * Request All Permissions in Sequence
 * Guides user through permission flow
 */
export const requestAllPermissions = async (onStepComplete) => {
  const results = {
    notifications: false,
    usageStats: false,
    vpn: false,
    accessibility: false,
  };
  
  try {
    // Step 1: Notification Access
    results.notifications = await requestNotificationAccess();
    onStepComplete?.('notifications', results.notifications);
    
    // Step 2: Usage Stats
    results.usageStats = await requestUsageStatsPermission();
    onStepComplete?.('usageStats', results.usageStats);
    
    // Step 3: VPN
    results.vpn = await requestVPNPermission();
    onStepComplete?.('vpn', results.vpn);
    
    // Step 4: Accessibility
    results.accessibility = await requestAccessibilityService();
    onStepComplete?.('accessibility', results.accessibility);
    
    return results;
  } catch (error) {
    console.error('Request all permissions error:', error);
    return results;
  }
};

export default {
  // Notification
  requestNotificationAccess,
  checkNotificationAccess,
  
  // Usage Stats
  requestUsageStatsPermission,
  getAppUsage,
  
  // VPN
  requestVPNPermission,
  startVPN,
  stopVPN,
  getVPNStatus,
  
  // Focus Mode
  requestAccessibilityService,
  enableFocusMode,
  disableFocusMode,
  
  // All Permissions
  checkAllPermissions,
  requestAllPermissions,
};
