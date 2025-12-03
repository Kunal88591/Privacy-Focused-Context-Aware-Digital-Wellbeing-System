/**
 * Home Screen
 * Dashboard with stats and quick actions
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { wellbeingAPI, privacyAPI } from '../services/api';
import mqttService from '../services/mqtt';

const HomeScreen = ({ navigation }) => {
  const [stats, setStats] = useState(null);
  const [privacyStatus, setPrivacyStatus] = useState(null);
  const [focusModeActive, setFocusModeActive] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sensorData, setSensorData] = useState({
    temperature: null,
    humidity: null,
    light: null,
    motion: false,
    noise: null,
  });
  const [mqttConnected, setMqttConnected] = useState(false);

  useEffect(() => {
    loadData();
    connectMQTT();

    return () => {
      // Cleanup MQTT listeners
      mqttService.removeListener('sensors/environment', handleEnvironmentData);
      mqttService.removeListener('sensors/motion', handleMotionData);
      mqttService.removeListener('sensors/light', handleLightData);
      mqttService.removeListener('sensors/noise', handleNoiseData);
    };
  }, []);

  const connectMQTT = async () => {
    const connected = await mqttService.connect();
    setMqttConnected(connected);

    if (connected) {
      // Set up listeners for sensor data
      mqttService.addListener('sensors/environment', handleEnvironmentData);
      mqttService.addListener('sensors/motion', handleMotionData);
      mqttService.addListener('sensors/light', handleLightData);
      mqttService.addListener('sensors/noise', handleNoiseData);
    }
  };

  const handleEnvironmentData = (data) => {
    setSensorData((prev) => ({
      ...prev,
      temperature: data.temperature,
      humidity: data.humidity,
    }));
  };

  const handleMotionData = (data) => {
    setSensorData((prev) => ({
      ...prev,
      motion: data.motion_detected,
    }));
  };

  const handleLightData = (data) => {
    setSensorData((prev) => ({
      ...prev,
      light: data.lux,
    }));
  };

  const handleNoiseData = (data) => {
    setSensorData((prev) => ({
      ...prev,
      noise: data.noise_level,
    }));
  };

  const loadData = async () => {
    try {
      const [statsData, privacyData, focusData] = await Promise.all([
        wellbeingAPI.getStats('today'),
        privacyAPI.getStatus(),
        wellbeingAPI.getFocusStatus(),
      ]);
      
      setStats(statsData);
      setPrivacyStatus(privacyData);
      setFocusModeActive(focusData.active);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const toggleFocusMode = async () => {
    try {
      if (focusModeActive) {
        await wellbeingAPI.deactivateFocusMode();
        setFocusModeActive(false);
      } else {
        await wellbeingAPI.activateFocusMode(90, [
          'instagram',
          'twitter',
          'tiktok',
          'facebook',
        ]);
        setFocusModeActive(true);
      }
    } catch (error) {
      console.error('Error toggling focus mode:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }>
      <View style={styles.header}>
        <Text style={styles.title}>🛡️ Privacy Wellbeing</Text>
        <Text style={styles.subtitle}>Your Digital Bodyguard</Text>
      </View>

      {/* Privacy Status Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Privacy Status</Text>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>VPN:</Text>
          <Text
            style={[
              styles.statusValue,
              privacyStatus?.vpn_enabled ? styles.active : styles.inactive,
            ]}>
            {privacyStatus?.vpn_enabled ? '🟢 Active' : '🔴 Inactive'}
          </Text>
        </View>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Caller ID Masked:</Text>
          <Text
            style={[
              styles.statusValue,
              privacyStatus?.caller_id_masked ? styles.active : styles.inactive,
            ]}>
            {privacyStatus?.caller_id_masked ? '✅ Yes' : '❌ No'}
          </Text>
        </View>
      </View>

      {/* Sensor Data Card */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Environment Sensors</Text>
          <Text style={styles.mqttStatus}>
            {mqttConnected ? '🟢 Live' : '🔴 Offline'}
          </Text>
        </View>
        <View style={styles.sensorGrid}>
          <View style={styles.sensorItem}>
            <Text style={styles.sensorIcon}>🌡️</Text>
            <Text style={styles.sensorValue}>
              {sensorData.temperature ? `${sensorData.temperature.toFixed(1)}°C` : '--'}
            </Text>
            <Text style={styles.sensorLabel}>Temperature</Text>
          </View>
          <View style={styles.sensorItem}>
            <Text style={styles.sensorIcon}>💧</Text>
            <Text style={styles.sensorValue}>
              {sensorData.humidity ? `${sensorData.humidity.toFixed(0)}%` : '--'}
            </Text>
            <Text style={styles.sensorLabel}>Humidity</Text>
          </View>
          <View style={styles.sensorItem}>
            <Text style={styles.sensorIcon}>💡</Text>
            <Text style={styles.sensorValue}>
              {sensorData.light ? `${sensorData.light.toFixed(0)} lux` : '--'}
            </Text>
            <Text style={styles.sensorLabel}>Light</Text>
          </View>
          <View style={styles.sensorItem}>
            <Text style={styles.sensorIcon}>🔊</Text>
            <Text style={styles.sensorValue}>
              {sensorData.noise ? `${sensorData.noise.toFixed(0)} dB` : '--'}
            </Text>
            <Text style={styles.sensorLabel}>Noise</Text>
          </View>
        </View>
        {sensorData.motion && (
          <View style={styles.motionAlert}>
            <Text style={styles.motionAlertText}>👤 Motion Detected</Text>
          </View>
        )}
      </View>

      {/* Stats Cards */}
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {stats?.focus_time_minutes || 0}m
          </Text>
          <Text style={styles.statLabel}>Focus Time</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {stats?.distractions_blocked || 0}
          </Text>
          <Text style={styles.statLabel}>Blocked</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {stats?.productivity_score || 0}
          </Text>
          <Text style={styles.statLabel}>Score</Text>
        </View>
      </View>

      {/* Focus Mode Button */}
      <TouchableOpacity
        style={[
          styles.focusButton,
          focusModeActive && styles.focusButtonActive,
        ]}
        onPress={toggleFocusMode}>
        <Text style={styles.focusButtonText}>
          {focusModeActive ? '⏸️ Pause Focus Mode' : '▶️ Start Focus Mode'}
        </Text>
        {focusModeActive && (
          <Text style={styles.focusButtonSubtext}>90 minutes remaining</Text>
        )}
      </TouchableOpacity>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Notifications')}>
          <Text style={styles.actionButtonText}>📬 Notifications</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Privacy')}>
          <Text style={styles.actionButtonText}>🔒 Privacy</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 20,
    paddingTop: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: '#666',
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  active: {
    color: '#4CAF50',
  },
  inactive: {
    color: '#999',
  },
  statsRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 2,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
  focusButton: {
    backgroundColor: '#2196F3',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 20,
    marginBottom: 20,
    alignItems: 'center',
  },
  focusButtonActive: {
    backgroundColor: '#FF9800',
  },
  focusButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
  },
  focusButtonSubtext: {
    fontSize: 14,
    color: 'white',
    marginTop: 4,
    opacity: 0.9,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  mqttStatus: {
    fontSize: 12,
    fontWeight: '600',
  },
  sensorGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  sensorItem: {
    width: '48%',
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    alignItems: 'center',
  },
  sensorIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  sensorValue: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  sensorLabel: {
    fontSize: 12,
    color: '#999',
  },
  motionAlert: {
    backgroundColor: '#FFF3E0',
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
    alignItems: 'center',
  },
  motionAlertText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF9800',
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 40,
  },
  actionButton: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 2,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
});

export default HomeScreen;
