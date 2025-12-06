/**
 * Mobile App Configuration
 */

// Environment detection
const __DEV__ = typeof __DEV__ !== 'undefined' ? __DEV__ : false;

export const API_CONFIG = {
  BASE_URL: __DEV__ 
    ? 'http://localhost:8000'  // Local development
    : (process.env.EXPO_PUBLIC_API_URL || 'https://your-api-domain.com'), // Production
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
};

export const MQTT_CONFIG = {
  BROKER_URL: __DEV__
    ? 'mqtt://localhost:1883'  // Local development
    : (process.env.EXPO_PUBLIC_MQTT_URL || 'mqtt://your-mqtt-domain.com:1883'), // Production
  CLIENT_ID: 'mobile-app-',
  RECONNECT_PERIOD: 5000,
};

export const PRIVACY_CONFIG = {
  VPN_ENABLED: true,
  CALLER_ID_MASKING: true,
  AUTO_WIPE_THRESHOLD: 3, // Untrusted network detections
  LOCATION_SPOOFING: false,
};

export const NOTIFICATION_CONFIG = {
  BATCH_INTERVAL: 300000, // 5 minutes in ms
  URGENT_KEYWORDS: ['urgent', 'asap', 'emergency', 'important'],
  ALLOWED_CONTACTS: [], // VIP contacts that bypass filters
};

export const FOCUS_MODE_CONFIG = {
  DEEP_WORK_DURATION: 90, // minutes
  BREAK_DURATION: 15, // minutes
  BLOCKED_APPS: [
    'com.facebook.katana',
    'com.instagram.android',
    'com.twitter.android',
  ],
};

export const THEME = {
  colors: {
    primary: '#4CAF50',
    secondary: '#2196F3',
    accent: '#FF9800',
    danger: '#F44336',
    background: '#F5F5F5',
    surface: '#FFFFFF',
    text: '#333333',
    textSecondary: '#666666',
    border: '#E0E0E0',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
  },
};
