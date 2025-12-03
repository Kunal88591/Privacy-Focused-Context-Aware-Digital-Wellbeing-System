/**
 * API Service
 * Handles all HTTP requests to the backend
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_CONFIG } from '../config/api';

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
      // TODO: Redirect to login
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  register: async (username, email, password) => {
    const response = await api.post('/api/v1/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  login: async (email, password) => {
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
  },

  logout: async () => {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
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
    const response = await api.get('/api/v1/notifications', {
      params: { limit, offset, filter },
    });
    return response.data;
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
    const response = await api.get('/api/v1/privacy/status');
    return response.data;
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
    const response = await api.get('/api/v1/wellbeing/focus-mode/status');
    return response.data;
  },

  getStats: async (period = 'today') => {
    const response = await api.get('/api/v1/wellbeing/stats', {
      params: { period },
    });
    return response.data;
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

export default api;
