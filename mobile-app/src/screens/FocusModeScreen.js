import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Switch,
  Alert,
  ActivityIndicator,
} from 'react-native';
import focusModeService from '../services/focusMode';

const FocusModeScreen = () => {
  const [hasPermission, setHasPermission] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [remainingMinutes, setRemainingMinutes] = useState(0);
  const [progress, setProgress] = useState(0);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDuration, setSelectedDuration] = useState(25);
  
  const timerIntervalRef = useRef(null);
  
  useEffect(() => {
    init();
    
    // Subscribe to Focus Mode changes
    const unsubscribe = focusModeService.addListener(handleStatusUpdate);
    
    return () => {
      unsubscribe();
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    };
  }, []);
  
  /**
   * Initialize screen
   */
  const init = async () => {
    try {
      // Check permission
      const permission = await focusModeService.checkPermission();
      setHasPermission(permission);
      
      // Load status
      const status = focusModeService.getStatus();
      updateStatus(status);
      
      // Load stats
      const statsData = focusModeService.getStats();
      setStats(statsData);
      
      // Start timer updates if active
      if (status.isActive) {
        startTimerUpdates();
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error initializing Focus Mode screen:', error);
      setLoading(false);
    }
  };
  
  /**
   * Handle Focus Mode status update
   */
  const handleStatusUpdate = (status) => {
    updateStatus(status);
    
    if (status.isActive && !timerIntervalRef.current) {
      startTimerUpdates();
    } else if (!status.isActive && timerIntervalRef.current) {
      stopTimerUpdates();
    }
  };
  
  /**
   * Update UI with status
   */
  const updateStatus = (status) => {
    setIsActive(status.isActive);
    setCurrentSession(status.session);
    setRemainingMinutes(status.remainingMinutes);
    setProgress(status.progress);
  };
  
  /**
   * Start timer interval
   */
  const startTimerUpdates = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }
    
    timerIntervalRef.current = setInterval(() => {
      const status = focusModeService.getStatus();
      updateStatus(status);
      
      if (status.remainingTime <= 0) {
        stopTimerUpdates();
        Alert.alert(
          '🎉 Focus Session Complete!',
          'Great work! You completed your focus session.',
          [{ text: 'OK' }]
        );
      }
    }, 1000);
  };
  
  /**
   * Stop timer interval
   */
  const stopTimerUpdates = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  };
  
  /**
   * Request usage stats permission
   */
  const requestPermission = () => {
    Alert.alert(
      'Permission Required',
      'Focus Mode needs usage access permission to block apps. You\'ll be redirected to settings.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Open Settings',
          onPress: () => {
            focusModeService.openSettings();
          },
        },
      ]
    );
  };
  
  /**
   * Start Focus Mode session
   */
  const handleStartSession = async () => {
    try {
      await focusModeService.startSession(selectedDuration);
      Alert.alert(
        '✅ Focus Mode Started',
        `Stay focused for ${selectedDuration} minutes!`,
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to start Focus Mode: ' + error.message);
    }
  };
  
  /**
   * Stop Focus Mode session
   */
  const handleStopSession = () => {
    Alert.alert(
      'Stop Focus Mode?',
      'Are you sure you want to stop your focus session early?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Stop',
          style: 'destructive',
          onPress: async () => {
            try {
              await focusModeService.stopSession();
              const updatedStats = focusModeService.getStats();
              setStats(updatedStats);
            } catch (error) {
              Alert.alert('Error', 'Failed to stop Focus Mode');
            }
          },
        },
      ]
    );
  };
  
  /**
   * Format time display
   */
  const formatTime = (minutes) => {
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hrs > 0) {
      return `${hrs}h ${mins}m`;
    }
    return `${mins}m`;
  };
  
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }
  
  // Permission request UI
  if (!hasPermission) {
    return (
      <View style={styles.container}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.permissionCard}>
            <Text style={styles.permissionIcon}>📊</Text>
            <Text style={styles.permissionTitle}>Permission Required</Text>
            <Text style={styles.permissionText}>
              Focus Mode needs usage access permission to block distracting apps
              and help you stay focused.
            </Text>
            <TouchableOpacity
              style={styles.permissionButton}
              onPress={requestPermission}>
              <Text style={styles.permissionButtonText}>Grant Permission</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </View>
    );
  }
  
  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Active Session Display */}
        {isActive && (
          <View style={styles.activeSessionCard}>
            <Text style={styles.activeTitle}>🎯 Focus Mode Active</Text>
            <Text style={styles.timerText}>{formatTime(remainingMinutes)}</Text>
            <Text style={styles.timerLabel}>remaining</Text>
            
            {/* Progress Bar */}
            <View style={styles.progressContainer}>
              <View style={[styles.progressBar, { width: `${progress}%` }]} />
            </View>
            
            <TouchableOpacity
              style={styles.stopButton}
              onPress={handleStopSession}>
              <Text style={styles.stopButtonText}>Stop Session</Text>
            </TouchableOpacity>
          </View>
        )}
        
        {/* Start Session UI */}
        {!isActive && (
          <View style={styles.startCard}>
            <Text style={styles.sectionTitle}>Start Focus Session</Text>
            
            {/* Duration Selection */}
            <View style={styles.durationContainer}>
              <TouchableOpacity
                style={[
                  styles.durationButton,
                  selectedDuration === 25 && styles.durationButtonActive,
                ]}
                onPress={() => setSelectedDuration(25)}>
                <Text
                  style={[
                    styles.durationText,
                    selectedDuration === 25 && styles.durationTextActive,
                  ]}>
                  25 min
                </Text>
                <Text style={styles.durationLabel}>Short</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[
                  styles.durationButton,
                  selectedDuration === 50 && styles.durationButtonActive,
                ]}
                onPress={() => setSelectedDuration(50)}>
                <Text
                  style={[
                    styles.durationText,
                    selectedDuration === 50 && styles.durationTextActive,
                  ]}>
                  50 min
                </Text>
                <Text style={styles.durationLabel}>Medium</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[
                  styles.durationButton,
                  selectedDuration === 90 && styles.durationButtonActive,
                ]}
                onPress={() => setSelectedDuration(90)}>
                <Text
                  style={[
                    styles.durationText,
                    selectedDuration === 90 && styles.durationTextActive,
                  ]}>
                  90 min
                </Text>
                <Text style={styles.durationLabel}>Long</Text>
              </TouchableOpacity>
            </View>
            
            <TouchableOpacity
              style={styles.startButton}
              onPress={handleStartSession}>
              <Text style={styles.startButtonText}>
                Start {selectedDuration} Minute Session
              </Text>
            </TouchableOpacity>
          </View>
        )}
        
        {/* Statistics */}
        {stats && (
          <View style={styles.statsCard}>
            <Text style={styles.sectionTitle}>Your Statistics</Text>
            
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{stats.totalSessions}</Text>
                <Text style={styles.statLabel}>Total Sessions</Text>
              </View>
              
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{stats.totalMinutes}</Text>
                <Text style={styles.statLabel}>Minutes Focused</Text>
              </View>
              
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{stats.currentStreak}</Text>
                <Text style={styles.statLabel}>Day Streak</Text>
              </View>
              
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{stats.longestStreak}</Text>
                <Text style={styles.statLabel}>Longest Streak</Text>
              </View>
            </View>
          </View>
        )}
        
        {/* Blocked Apps Info */}
        <View style={styles.infoCard}>
          <Text style={styles.sectionTitle}>Blocked Apps</Text>
          <Text style={styles.infoText}>
            During Focus Mode, the following apps will be blocked:
          </Text>
          <Text style={styles.appList}>
            • Instagram{'\n'}
            • Twitter{'\n'}
            • Facebook{'\n'}
            • TikTok{'\n'}
            • Snapchat{'\n'}
            • Reddit{'\n'}
            • And more...
          </Text>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 16,
  },
  
  // Permission UI
  permissionCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  permissionIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  permissionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  permissionText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  permissionButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Active Session
  activeSessionCard: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  activeTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  timerText: {
    fontSize: 64,
    fontWeight: 'bold',
    color: '#fff',
  },
  timerLabel: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
    marginBottom: 16,
  },
  progressContainer: {
    width: '100%',
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.3)',
    borderRadius: 4,
    marginBottom: 16,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#fff',
    borderRadius: 4,
  },
  stopButton: {
    backgroundColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
    marginTop: 8,
  },
  stopButtonText: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Start Session
  startCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  durationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  durationButton: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  durationButtonActive: {
    backgroundColor: '#E8F5E9',
    borderColor: '#4CAF50',
  },
  durationText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
  },
  durationTextActive: {
    color: '#4CAF50',
  },
  durationLabel: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  startButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Statistics
  statsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  
  // Info
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  appList: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
});

export default FocusModeScreen;
