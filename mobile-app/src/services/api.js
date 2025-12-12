/**
 * API Service
 * Handles all HTTP requests to the backend with retry logic, error handling, and offline caching
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_CONFIG } from '../config/api';
import { setCache, getCache } from '../utils/offlineCache';
import { getNetworkStatus } from '../utils/networkStatus';

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Helper function to delay
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Helper function to retry failed requests
const retryRequest = async (fn, retries = MAX_RETRIES) => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && isRetryableError(error)) {
      console.log(`Retrying request... (${MAX_RETRIES - retries + 1}/${MAX_RETRIES})`);
      await delay(RETRY_DELAY);
      return retryRequest(fn, retries - 1);
    }
    throw error;
  }
};

// Check if error is retryable
const isRetryableError = (error) => {
  return (
    !error.response || // Network error
    error.code === 'ECONNABORTED' || // Timeout
    error.response.status >= 500 // Server error
  );
};

// Create custom error with user-friendly message
const createUserFriendlyError = (error) => {
  if (!error.response) {
    return new Error('Network error. Please check your internet connection.');
  }
  
  switch (error.response.status) {
    case 400:
      return new Error('Invalid request. Please check your input.');
    case 401:
      return new Error('Authentication required. Please log in again.');
    case 403:
      return new Error('Access denied. You don\'t have permission.');
    case 404:
      return new Error('Resource not found.');
    case 500:
      return new Error('Server error. Please try again later.');
    case 503:
      return new Error('Service unavailable. Please try again later.');
    default:
      return new Error(error.response.data?.message || 'An error occurred. Please try again.');
  }
};

// Create axios instance
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      await AsyncStorage.removeItem('access_token');
      // TODO: Redirect to login or dispatch logout action
    }
    
    // Transform error to user-friendly message
    const friendlyError = createUserFriendlyError(error);
    return Promise.reject(friendlyError);
  }
);

// Helper function to make cacheable GET requests
const cacheableGet = async (url, cacheKey, params = {}, expiryMs) => {
  const networkStatus = await getNetworkStatus();
  
  // Try cache first if offline
  if (!networkStatus.isOnline) {
    const cached = await getCache(cacheKey);
    if (cached) {
      console.log(`Using cached data for ${cacheKey} (offline)`);
      return { ...cached, fromCache: true, offline: true };
    }
    throw new Error('No internet connection and no cached data available.');
  }
  
  // Try network request
  try {
    const response = await retryRequest(async () => {
      return await api.get(url, { params });
    });
    
    // Cache successful response
    await setCache(cacheKey, response.data);
    return { ...response.data, fromCache: false, offline: false };
  } catch (error) {
    // Fallback to cache on network error
    const cached = await getCache(cacheKey, expiryMs || 24 * 60 * 60 * 1000); // 24h fallback
    if (cached) {
      console.log(`Using cached data for ${cacheKey} (network error)`);
      return { ...cached, fromCache: true, offline: false };
    }
    throw error;
  }
};

// Authentication API
export const authAPI = {
  register: async (username, email, password) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/auth/register', {
        username,
        email,
        password,
      });
      return response.data;
    });
  },

  login: async (email, password) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/auth/login', {
        email,
        password,
      });
      
      // Save token
      if (response.data.access_token) {
        await AsyncStorage.setItem('access_token', response.data.access_token);
        await AsyncStorage.setItem('refresh_token', response.data.refresh_token);
      }
      
      return response.data;
    });
  },

  logout: async () => {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
  },

  getCurrentUser: async () => {
    return retryRequest(async () => {
      const response = await api.get('/api/v1/auth/me');
      return response.data;
    });
  },
};

// Notifications API
export const notificationAPI = {
  classify: async (text, sender, receivedAt) => {
    const response = await api.post('/api/v1/notifications/classify', {
      text,
      sender,
      received_at: receivedAt,
    });
    return response.data;
  },

  getAll: async (limit = 50, offset = 0, filter = 'all') => {
    const cacheKey = `notifications_${filter}_${limit}_${offset}`;
    return await cacheableGet('/api/v1/notifications', cacheKey, { limit, offset, filter });
  },

  delete: async (id) => {
    const response = await api.delete(`/api/v1/notifications/${id}`);
    return response.data;
  },
};

// Privacy API
export const privacyAPI = {
  enableVPN: async () => {
    const response = await api.post('/api/v1/privacy/vpn/enable');
    return response.data;
  },

  disableVPN: async () => {
    const response = await api.post('/api/v1/privacy/vpn/disable');
    return response.data;
  },

  toggleCallerMask: async (enable) => {
    const response = await api.post('/api/v1/privacy/mask-caller', null, {
      params: { enable },
    });
    return response.data;
  },

  toggleLocationSpoof: async (enable) => {
    const response = await api.post('/api/v1/privacy/location-spoof', null, {
      params: { enable },
    });
    return response.data;
  },

  getStatus: async () => {
    return await cacheableGet('/api/v1/privacy/status', 'privacy_status');
  },
};

// Wellbeing API
export const wellbeingAPI = {
  activateFocusMode: async (duration, blockApps) => {
    const response = await api.post('/api/v1/wellbeing/focus-mode', {
      action: 'activate',
      duration,
      block_apps: blockApps,
    });
    return response.data;
  },

  deactivateFocusMode: async () => {
    const response = await api.post('/api/v1/wellbeing/focus-mode', {
      action: 'deactivate',
    });
    return response.data;
  },

  getFocusStatus: async () => {
    return await cacheableGet('/api/v1/wellbeing/focus-mode/status', 'focus_status');
  },

  getStats: async (period = 'today') => {
    return await cacheableGet('/api/v1/wellbeing/stats', `stats_${period}`, { period });
  },

  getInsights: async () => {
    const response = await api.get('/api/v1/wellbeing/insights');
    return response.data;
  },
};

// Devices API
export const devicesAPI = {
  register: async (deviceName, deviceType, macAddress) => {
    const response = await api.post('/api/v1/devices/register', {
      device_name: deviceName,
      device_type: deviceType,
      mac_address: macAddress,
    });
    return response.data;
  },

  getAll: async () => {
    const response = await api.get('/api/v1/devices');
    return response.data;
  },

  sendCommand: async (deviceId, command, parameters) => {
    const response = await api.post(`/api/v1/devices/${deviceId}/command`, {
      command,
      parameters,
    });
    return response.data;
  },
};

// AI Advanced API
export const aiAPI = {
  scorePriority: async (text, appName, timestamp) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/ai/priority/score', {
        text,
        app_name: appName,
        timestamp: timestamp || new Date().toISOString(),
      });
      return response.data;
    });
  },

  predictFocus: async (params = {}) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/ai/focus/predict', params);
      return response.data;
    });
  },

  getDailyFocusSchedule: async (date) => {
    return await cacheableGet(
      '/api/v1/ai/focus/schedule',
      `focus_schedule_${date}`,
      { date: date || new Date().toISOString().split('T')[0] }
    );
  },

  getSuggestions: async (params = {}) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/ai/suggestions', params);
      return response.data;
    });
  },

  analyzeBehavior: async (userId, days = 7) => {
    return await cacheableGet(
      '/api/v1/ai/behavior/analyze',
      `behavior_${userId}_${days}`,
      { user_id: userId, days }
    );
  },

  detectPatterns: async (userId) => {
    return await cacheableGet(
      '/api/v1/ai/behavior/patterns',
      `patterns_${userId}`,
      { user_id: userId }
    );
  },

  getInsights: async (userId) => {
    return await cacheableGet(
      '/api/v1/ai/behavior/insights',
      `insights_${userId}`,
      { user_id: userId }
    );
  },
};

// Analytics API
export const analyticsAPI = {
  trackSession: async (userId, startTime, endTime, deviceType = 'mobile') => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/analytics/sessions/track', {
        user_id: userId,
        start_time: startTime,
        end_time: endTime,
        device_type: deviceType,
      });
      return response.data;
    });
  },

  trackScreenTime: async (userId, appName, durationMinutes, category = 'other') => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/analytics/screen-time/track', {
        user_id: userId,
        app_name: appName,
        duration_minutes: durationMinutes,
        category,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    });
  },

  trackFocusSession: async (userId, startTime, endTime, qualityScore, taskName) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/analytics/focus/track', {
        user_id: userId,
        start_time: startTime,
        end_time: endTime,
        quality_score: qualityScore,
        task_name: taskName,
      });
      return response.data;
    });
  },

  trackNotification: async (userId, appName, priority, wasInteracted) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/analytics/notifications/track', {
        user_id: userId,
        app_name: appName,
        priority,
        was_interacted: wasInteracted,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    });
  },

  getSessionStats: async (userId, period = 'week') => {
    return await cacheableGet(
      '/api/v1/analytics/sessions/stats',
      `session_stats_${userId}_${period}`,
      { user_id: userId, period }
    );
  },

  getScreenTimeStats: async (userId, period = 'week') => {
    return await cacheableGet(
      '/api/v1/analytics/screen-time/stats',
      `screen_time_${userId}_${period}`,
      { user_id: userId, period }
    );
  },

  getFocusStats: async (userId, period = 'week') => {
    return await cacheableGet(
      '/api/v1/analytics/focus/stats',
      `focus_stats_${userId}_${period}`,
      { user_id: userId, period }
    );
  },

  getProductivityScore: async (userId, period = 'today') => {
    return await cacheableGet(
      '/api/v1/analytics/productivity/score',
      `productivity_${userId}_${period}`,
      { user_id: userId, period }
    );
  },

  getWellbeingScore: async (userId) => {
    return await cacheableGet(
      '/api/v1/analytics/wellbeing/score',
      `wellbeing_${userId}`,
      { user_id: userId }
    );
  },

  getDashboard: async (userId, period = 'week') => {
    return await cacheableGet(
      '/api/v1/analytics/dashboard',
      `dashboard_${userId}_${period}`,
      { user_id: userId, period }
    );
  },

  getTrends: async (userId, metric = 'productivity', days = 30) => {
    return await cacheableGet(
      '/api/v1/analytics/trends',
      `trends_${userId}_${metric}_${days}`,
      { user_id: userId, metric, days }
    );
  },

  getGoals: async (userId) => {
    return await cacheableGet(
      '/api/v1/analytics/goals',
      `goals_${userId}`,
      { user_id: userId }
    );
  },

  setGoal: async (userId, goalType, targetValue, timeframe) => {
    return retryRequest(async () => {
      const response = await api.post('/api/v1/analytics/goals', {
        user_id: userId,
        goal_type: goalType,
        target_value: targetValue,
        timeframe,
      });
      return response.data;
    });
  },
};

export default api;
