/**
 * Notification Service
 * React Native interface for Android NotificationListenerService
 */

import { NativeModules, NativeEventEmitter, AppRegistry } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api';

const { NotificationModule } = NativeModules;

const STORAGE_KEY = '@notifications';
const MAX_STORED_NOTIFICATIONS = 100;

class NotificationService {
  constructor() {
    this.notifications = [];
    this.listeners = [];
    this.setupHeadlessTask();
  }

  /**
   * Setup headless task to receive notifications in background
   */
  setupHeadlessTask() {
    AppRegistry.registerHeadlessTask('NotificationReceived', () => async (taskData) => {
      try {
        const notificationData = JSON.parse(taskData.notificationData);
        await this.handleNewNotification(notificationData);
      } catch (error) {
        console.error('Error handling notification in headless task:', error);
      }
    });
  }

  /**
   * Check if notification permission is granted
   */
  async checkPermission() {
    try {
      return await NotificationModule.checkNotificationPermission();
    } catch (error) {
      console.error('Error checking notification permission:', error);
      return false;
    }
  }

  /**
   * Open notification settings to grant permission
   */
  openSettings() {
    try {
      NotificationModule.openNotificationSettings();
    } catch (error) {
      console.error('Error opening notification settings:', error);
    }
  }

  /**
   * Get all active notifications from system
   */
  async getActiveNotifications() {
    try {
      const notifications = await NotificationModule.getActiveNotifications();
      return notifications || [];
    } catch (error) {
      console.error('Error getting active notifications:', error);
      return [];
    }
  }

  /**
   * Load stored notifications from AsyncStorage
   */
  async loadStoredNotifications() {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEY);
      if (stored) {
        this.notifications = JSON.parse(stored);
        this.notifyListeners();
      }
    } catch (error) {
      console.error('Error loading stored notifications:', error);
    }
  }

  /**
   * Save notifications to AsyncStorage
   */
  async saveNotifications() {
    try {
      // Keep only the latest MAX_STORED_NOTIFICATIONS
      const toStore = this.notifications.slice(0, MAX_STORED_NOTIFICATIONS);
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(toStore));
    } catch (error) {
      console.error('Error saving notifications:', error);
    }
  }

  /**
   * Handle new notification received
   */
  async handleNewNotification(notificationData) {
    try {
      // Classify notification using API
      const classification = await this.classifyNotification(notificationData);

      const enrichedNotification = {
        ...notificationData,
        priority: classification.priority,
        score: classification.score,
        category: classification.category,
        read: false,
        received: Date.now(),
      };

      // Add to beginning of array
      this.notifications.unshift(enrichedNotification);

      // Save to storage
      await this.saveNotifications();

      // Notify listeners
      this.notifyListeners();

      return enrichedNotification;
    } catch (error) {
      console.error('Error handling new notification:', error);
      
      // Add without classification if API fails
      const basicNotification = {
        ...notificationData,
        priority: 'NORMAL',
        score: 50,
        category: 'general',
        read: false,
        received: Date.now(),
      };

      this.notifications.unshift(basicNotification);
      await this.saveNotifications();
      this.notifyListeners();

      return basicNotification;
    }
  }

  /**
   * Classify notification using ML API
   */
  async classifyNotification(notificationData) {
    try {
      const result = await api.notifications.classifyNotification({
        text: `${notificationData.title} ${notificationData.text}`,
        sender: notificationData.packageName,
        timestamp: notificationData.timestamp,
      });

      return {
        priority: result.priority,
        score: result.score,
        category: result.category || 'general',
      };
    } catch (error) {
      console.error('Error classifying notification:', error);
      return {
        priority: 'NORMAL',
        score: 50,
        category: 'general',
      };
    }
  }

  /**
   * Get all notifications
   */
  getNotifications() {
    return this.notifications;
  }

  /**
   * Get unread notifications count
   */
  getUnreadCount() {
    return this.notifications.filter(n => !n.read).length;
  }

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId) {
    const notification = this.notifications.find(n => n.id === notificationId);
    if (notification) {
      notification.read = true;
      await this.saveNotifications();
      this.notifyListeners();
    }
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead() {
    this.notifications.forEach(n => n.read = true);
    await this.saveNotifications();
    this.notifyListeners();
  }

  /**
   * Dismiss notification (remove from system and list)
   */
  async dismissNotification(notificationId) {
    try {
      // Remove from system
      await NotificationModule.dismissNotification(notificationId);

      // Remove from local list
      this.notifications = this.notifications.filter(n => n.id !== notificationId);
      await this.saveNotifications();
      this.notifyListeners();

      return true;
    } catch (error) {
      console.error('Error dismissing notification:', error);
      return false;
    }
  }

  /**
   * Dismiss all notifications
   */
  async dismissAll() {
    try {
      await NotificationModule.dismissAllNotifications();
      this.notifications = [];
      await this.saveNotifications();
      this.notifyListeners();
      return true;
    } catch (error) {
      console.error('Error dismissing all notifications:', error);
      return false;
    }
  }

  /**
   * Delete notification (remove from list only)
   */
  async deleteNotification(notificationId) {
    this.notifications = this.notifications.filter(n => n.id !== notificationId);
    await this.saveNotifications();
    this.notifyListeners();
  }

  /**
   * Clear all notifications
   */
  async clearAll() {
    this.notifications = [];
    await this.saveNotifications();
    this.notifyListeners();
  }

  /**
   * Add listener for notification changes
   */
  addListener(callback) {
    this.listeners.push(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  /**
   * Notify all listeners of changes
   */
  notifyListeners() {
    this.listeners.forEach(listener => {
      try {
        listener(this.notifications);
      } catch (error) {
        console.error('Error in notification listener:', error);
      }
    });
  }

  /**
   * Get notifications by filter
   */
  getFilteredNotifications(filter) {
    switch (filter) {
      case 'unread':
        return this.notifications.filter(n => !n.read);
      case 'urgent':
        return this.notifications.filter(n => n.priority === 'URGENT');
      case 'normal':
        return this.notifications.filter(n => n.priority === 'NORMAL');
      default:
        return this.notifications;
    }
  }

  /**
   * Get notifications by app
   */
  getNotificationsByApp(packageName) {
    return this.notifications.filter(n => n.packageName === packageName);
  }

  /**
   * Get notification statistics
   */
  getStatistics() {
    const total = this.notifications.length;
    const unread = this.getUnreadCount();
    const urgent = this.notifications.filter(n => n.priority === 'URGENT').length;
    
    // Get app distribution
    const appCounts = {};
    this.notifications.forEach(n => {
      appCounts[n.packageName] = (appCounts[n.packageName] || 0) + 1;
    });

    return {
      total,
      unread,
      urgent,
      normal: total - urgent,
      byApp: appCounts,
    };
  }
}

// Export singleton instance
const notificationService = new NotificationService();
export default notificationService;
