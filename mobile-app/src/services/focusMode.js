import { NativeModules, NativeEventEmitter, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { FocusModeModule } = NativeModules;

/**
 * Focus Mode Service - Manages app blocking and Pomodoro timer sessions
 */
class FocusModeService {
  constructor() {
    this.isActive = false;
    this.currentSession = null;
    this.listeners = [];
    this.eventEmitter = null;
    
    // Storage keys
    this.STORAGE_KEY = '@focusMode';
    this.STATS_KEY = '@focusStats';
    
    // Pomodoro durations (in minutes)
    this.DURATIONS = {
      SHORT: 25,
      MEDIUM: 50,
      LONG: 90,
    };
    
    // Default blocked apps
    this.DEFAULT_BLOCKED_APPS = [
      'com.instagram.android',
      'com.twitter.android',
      'com.facebook.katana',
      'com.facebook.orca',
      'com.snapchat.android',
      'com.zhiliaoapp.musically',
      'com.reddit.frontpage',
      'com.pinterest',
      'com.linkedin.android',
      'com.tumblr',
    ];
    
    this.blockedApps = [...this.DEFAULT_BLOCKED_APPS];
    this.stats = {
      totalSessions: 0,
      totalMinutes: 0,
      longestStreak: 0,
      currentStreak: 0,
      lastSessionDate: null,
    };
    
    this.init();
  }
  
  /**
   * Initialize service
   */
  async init() {
    // Setup event emitter for native events
    if (Platform.OS === 'android' && FocusModeModule) {
      this.eventEmitter = new NativeEventEmitter(FocusModeModule);
      this.eventEmitter.addListener('FocusModeStatusChanged', this.handleStatusChange.bind(this));
    }
    
    // Load saved data
    await this.loadSavedData();
  }
  
  /**
   * Check if usage stats permission is granted
   */
  async checkPermission() {
    if (Platform.OS !== 'android' || !FocusModeModule) {
      return false;
    }
    
    try {
      const hasPermission = await FocusModeModule.checkUsageStatsPermission();
      return hasPermission;
    } catch (error) {
      console.error('Error checking usage stats permission:', error);
      return false;
    }
  }
  
  /**
   * Open usage stats settings
   */
  openSettings() {
    if (Platform.OS === 'android' && FocusModeModule) {
      FocusModeModule.openUsageStatsSettings();
    }
  }
  
  /**
   * Start Focus Mode session
   * @param {number} duration - Duration in minutes (25, 50, or 90)
   */
  async startSession(duration = this.DURATIONS.SHORT) {
    if (Platform.OS !== 'android' || !FocusModeModule) {
      throw new Error('Focus Mode is only available on Android');
    }
    
    try {
      // Start native service
      await FocusModeModule.startFocusMode(duration);
      
      // Update local state
      this.isActive = true;
      this.currentSession = {
        startTime: Date.now(),
        duration: duration * 60 * 1000,
        endTime: Date.now() + (duration * 60 * 1000),
        durationMinutes: duration,
      };
      
      // Save state
      await this.saveState();
      
      // Notify listeners
      this.notifyListeners();
      
      return true;
    } catch (error) {
      console.error('Error starting Focus Mode:', error);
      throw error;
    }
  }
  
  /**
   * Stop Focus Mode session
   */
  async stopSession() {
    if (Platform.OS !== 'android' || !FocusModeModule) {
      return false;
    }
    
    try {
      // Stop native service
      await FocusModeModule.stopFocusMode();
      
      // Update stats if session was completed
      if (this.currentSession) {
        const minutesCompleted = Math.floor(
          (Date.now() - this.currentSession.startTime) / 1000 / 60
        );
        await this.updateStats(minutesCompleted);
      }
      
      // Clear local state
      this.isActive = false;
      this.currentSession = null;
      
      // Save state
      await this.saveState();
      
      // Notify listeners
      this.notifyListeners();
      
      return true;
    } catch (error) {
      console.error('Error stopping Focus Mode:', error);
      throw error;
    }
  }
  
  /**
   * Get current Focus Mode status
   */
  getStatus() {
    return {
      isActive: this.isActive,
      session: this.currentSession,
      remainingTime: this.getRemainingTime(),
      remainingMinutes: Math.ceil(this.getRemainingTime() / 1000 / 60),
      progress: this.getProgress(),
    };
  }
  
  /**
   * Get remaining time in milliseconds
   */
  getRemainingTime() {
    if (!this.isActive || !this.currentSession) {
      return 0;
    }
    
    const remaining = this.currentSession.endTime - Date.now();
    return Math.max(0, remaining);
  }
  
  /**
   * Get session progress (0-100)
   */
  getProgress() {
    if (!this.isActive || !this.currentSession) {
      return 0;
    }
    
    const elapsed = Date.now() - this.currentSession.startTime;
    const total = this.currentSession.duration;
    return Math.min(100, (elapsed / total) * 100);
  }
  
  /**
   * Update blocked apps list
   * @param {string[]} apps - Array of package names
   */
  async updateBlockedApps(apps) {
    if (Platform.OS !== 'android' || !FocusModeModule) {
      return false;
    }
    
    try {
      this.blockedApps = [...apps];
      await FocusModeModule.updateBlockedApps(apps);
      await this.saveState();
      this.notifyListeners();
      return true;
    } catch (error) {
      console.error('Error updating blocked apps:', error);
      throw error;
    }
  }
  
  /**
   * Get list of blocked apps
   */
  getBlockedApps() {
    return [...this.blockedApps];
  }
  
  /**
   * Add app to blocked list
   */
  async addBlockedApp(packageName) {
    if (!this.blockedApps.includes(packageName)) {
      this.blockedApps.push(packageName);
      await this.updateBlockedApps(this.blockedApps);
    }
  }
  
  /**
   * Remove app from blocked list
   */
  async removeBlockedApp(packageName) {
    const index = this.blockedApps.indexOf(packageName);
    if (index > -1) {
      this.blockedApps.splice(index, 1);
      await this.updateBlockedApps(this.blockedApps);
    }
  }
  
  /**
   * Reset to default blocked apps
   */
  async resetBlockedApps() {
    await this.updateBlockedApps(this.DEFAULT_BLOCKED_APPS);
  }
  
  /**
   * Get focus statistics
   */
  getStats() {
    return { ...this.stats };
  }
  
  /**
   * Update statistics after session
   */
  async updateStats(minutesCompleted) {
    this.stats.totalSessions += 1;
    this.stats.totalMinutes += minutesCompleted;
    
    // Update streak
    const today = new Date().toDateString();
    const lastDate = this.stats.lastSessionDate 
      ? new Date(this.stats.lastSessionDate).toDateString() 
      : null;
    
    if (lastDate === today) {
      // Same day - no streak change
    } else if (lastDate === new Date(Date.now() - 86400000).toDateString()) {
      // Yesterday - continue streak
      this.stats.currentStreak += 1;
    } else {
      // Streak broken - start new
      this.stats.currentStreak = 1;
    }
    
    this.stats.longestStreak = Math.max(
      this.stats.longestStreak,
      this.stats.currentStreak
    );
    
    this.stats.lastSessionDate = Date.now();
    
    await this.saveStats();
    this.notifyListeners();
  }
  
  /**
   * Handle native status change event
   */
  handleStatusChange(event) {
    console.log('Focus Mode status changed:', event);
    
    if (event.status === 'STOPPED') {
      this.isActive = false;
      this.currentSession = null;
      this.saveState();
    }
    
    this.notifyListeners();
  }
  
  /**
   * Subscribe to Focus Mode changes
   */
  addListener(callback) {
    this.listeners.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }
  
  /**
   * Notify all listeners of changes
   */
  notifyListeners() {
    const status = this.getStatus();
    this.listeners.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error in Focus Mode listener:', error);
      }
    });
  }
  
  /**
   * Load saved state from storage
   */
  async loadSavedData() {
    try {
      // Load state
      const stateJson = await AsyncStorage.getItem(this.STORAGE_KEY);
      if (stateJson) {
        const state = JSON.parse(stateJson);
        this.isActive = state.isActive || false;
        this.currentSession = state.currentSession || null;
        this.blockedApps = state.blockedApps || [...this.DEFAULT_BLOCKED_APPS];
        
        // Check if session expired
        if (this.currentSession && Date.now() >= this.currentSession.endTime) {
          this.isActive = false;
          this.currentSession = null;
          await this.saveState();
        }
      }
      
      // Load stats
      const statsJson = await AsyncStorage.getItem(this.STATS_KEY);
      if (statsJson) {
        this.stats = JSON.parse(statsJson);
      }
      
    } catch (error) {
      console.error('Error loading Focus Mode data:', error);
    }
  }
  
  /**
   * Save current state to storage
   */
  async saveState() {
    try {
      const state = {
        isActive: this.isActive,
        currentSession: this.currentSession,
        blockedApps: this.blockedApps,
      };
      
      await AsyncStorage.setItem(this.STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Error saving Focus Mode state:', error);
    }
  }
  
  /**
   * Save statistics to storage
   */
  async saveStats() {
    try {
      await AsyncStorage.setItem(this.STATS_KEY, JSON.stringify(this.stats));
    } catch (error) {
      console.error('Error saving Focus Mode stats:', error);
    }
  }
  
  /**
   * Clear all data
   */
  async clearAllData() {
    try {
      await AsyncStorage.removeItem(this.STORAGE_KEY);
      await AsyncStorage.removeItem(this.STATS_KEY);
      
      this.isActive = false;
      this.currentSession = null;
      this.blockedApps = [...this.DEFAULT_BLOCKED_APPS];
      this.stats = {
        totalSessions: 0,
        totalMinutes: 0,
        longestStreak: 0,
        currentStreak: 0,
        lastSessionDate: null,
      };
      
      this.notifyListeners();
    } catch (error) {
      console.error('Error clearing Focus Mode data:', error);
    }
  }
}

// Export singleton instance
export default new FocusModeService();
