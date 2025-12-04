/**
 * App Context
 * Global state management using React Context API
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNetworkStatus } from '../utils/networkStatus';

const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  // Network status
  const networkStatus = useNetworkStatus();
  
  // Authentication state
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // App settings
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost:8000',
    mqttBroker: 'localhost:1883',
    notificationsEnabled: true,
    focusModeEnabled: false,
    darkMode: false,
  });

  // Sensor data (shared across screens)
  const [sensorData, setSensorData] = useState({
    temperature: null,
    humidity: null,
    light: null,
    noise: null,
    motion: false,
    lastUpdated: null,
  });

  // Privacy status (shared across screens)
  const [privacyStatus, setPrivacyStatus] = useState({
    vpn_enabled: false,
    caller_id_masked: false,
    location_spoofed: false,
    auto_wipe_armed: false,
    privacy_score: 0,
  });

  // Wellbeing stats
  const [wellbeingStats, setWellbeingStats] = useState({
    focus_time_minutes: 0,
    distractions_blocked: 0,
    productivity_score: 0,
  });

  // Load persisted data on mount
  useEffect(() => {
    loadPersistedData();
  }, []);

  const loadPersistedData = async () => {
    try {
      const [storedUser, storedToken, storedSettings] = await Promise.all([
        AsyncStorage.getItem('user'),
        AsyncStorage.getItem('token'),
        AsyncStorage.getItem('settings'),
      ]);

      if (storedUser) setUser(JSON.parse(storedUser));
      if (storedToken) {
        setToken(storedToken);
        setIsAuthenticated(true);
      }
      if (storedSettings) setSettings(JSON.parse(storedSettings));
    } catch (error) {
      console.error('Error loading persisted data:', error);
    }
  };

  // Auth functions
  const login = async (userData, authToken) => {
    try {
      setUser(userData);
      setToken(authToken);
      setIsAuthenticated(true);

      await Promise.all([
        AsyncStorage.setItem('user', JSON.stringify(userData)),
        AsyncStorage.setItem('token', authToken),
      ]);
    } catch (error) {
      console.error('Error saving login data:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      setUser(null);
      setToken(null);
      setIsAuthenticated(false);

      await Promise.all([
        AsyncStorage.removeItem('user'),
        AsyncStorage.removeItem('token'),
      ]);
    } catch (error) {
      console.error('Error clearing login data:', error);
    }
  };

  // Settings functions
  const updateSettings = async (newSettings) => {
    try {
      const updated = { ...settings, ...newSettings };
      setSettings(updated);
      await AsyncStorage.setItem('settings', JSON.stringify(updated));
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  };

  // Sensor data functions
  const updateSensorData = (newData) => {
    setSensorData((prev) => ({
      ...prev,
      ...newData,
      lastUpdated: new Date().toISOString(),
    }));
  };

  // Privacy functions
  const updatePrivacyStatus = (newStatus) => {
    setPrivacyStatus((prev) => ({ ...prev, ...newStatus }));
  };

  // Wellbeing functions
  const updateWellbeingStats = (newStats) => {
    setWellbeingStats((prev) => ({ ...prev, ...newStats }));
  };

  const value = {
    // Network status
    networkStatus,
    isOnline: networkStatus.isOnline,
    
    // Auth state
    user,
    token,
    isAuthenticated,
    login,
    logout,

    // Settings
    settings,
    updateSettings,

    // Sensor data
    sensorData,
    updateSensorData,

    // Privacy status
    privacyStatus,
    updatePrivacyStatus,

    // Wellbeing stats
    wellbeingStats,
    updateWellbeingStats,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export default AppContext;
