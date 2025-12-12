/**
 * Notifications Screen
 * Display and manage classified notifications with swipe-to-dismiss
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
  Platform,
  Animated,
  PanResponder,
} from 'react-native';
import notificationService from '../services/notifications';

import notificationService from '../services/notifications';

const NotificationsScreen = () => {
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [hasPermission, setHasPermission] = useState(false);

  useEffect(() => {
    checkPermissionAndLoad();
    
    // Subscribe to notification updates
    const unsubscribe = notificationService.addListener((newNotifications) => {
      setNotifications(newNotifications);
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    filterNotifications();
  }, [filter]);

  const checkPermissionAndLoad = async () => {
    try {
      const permission = await notificationService.checkPermission();
      setHasPermission(permission);
      
      if (permission) {
        await loadNotifications();
      }
    } catch (error) {
      console.error('Error checking permission:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadNotifications = async () => {
    try {
      await notificationService.loadStoredNotifications();
      const activeNotifications = await notificationService.getActiveNotifications();
      
      // Merge with stored notifications
      for (const notification of activeNotifications) {
        await notificationService.handleNewNotification(notification);
      }
      
      setNotifications(notificationService.getNotifications());
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const filterNotifications = () => {
    const filtered = notificationService.getFilteredNotifications(filter);
    setNotifications(filtered);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadNotifications();
  };

  const handleDismiss = async (notification) => {
    try {
      await notificationService.dismissNotification(notification.id);
      setNotifications(notificationService.getNotifications());
    } catch (error) {
      console.error('Error dismissing notification:', error);
      Alert.alert('Error', 'Failed to dismiss notification');
    }
  };

  const handleDelete = async (notification) => {
    Alert.alert(
      'Delete Notification',
      'Remove this notification from your list?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            await notificationService.deleteNotification(notification.id);
            setNotifications(notificationService.getNotifications());
          },
        },
      ]
    );
  };

  const handleMarkAsRead = async (notification) => {
    await notificationService.markAsRead(notification.id);
    setNotifications(notificationService.getNotifications());
  };

  const handleRequestPermission = () => {
    notificationService.openSettings();
  };

  // Swipeable Notification Card Component
  const SwipeableNotificationCard = ({ item }) => {
    const translateX = new Animated.Value(0);
    const opacity = new Animated.Value(1);

    const panResponder = PanResponder.create({
      onMoveShouldSetPanResponder: (_, gestureState) => {
        return Math.abs(gestureState.dx) > 10;
      },
      onPanResponderMove: (_, gestureState) => {
        translateX.setValue(gestureState.dx);
      },
      onPanResponderRelease: (_, gestureState) => {
        if (gestureState.dx > 120) {
          // Swipe right - dismiss
          Animated.parallel([
            Animated.timing(translateX, {
              toValue: 400,
              duration: 200,
              useNativeDriver: true,
            }),
            Animated.timing(opacity, {
              toValue: 0,
              duration: 200,
              useNativeDriver: true,
            }),
          ]).start(() => {
            handleDismiss(item);
          });
        } else if (gestureState.dx < -120) {
          // Swipe left - delete
          Animated.parallel([
            Animated.timing(translateX, {
              toValue: -400,
              duration: 200,
              useNativeDriver: true,
            }),
            Animated.timing(opacity, {
              toValue: 0,
              duration: 200,
              useNativeDriver: true,
            }),
          ]).start(() => {
            handleDelete(item);
          });
        } else {
          // Return to original position
          Animated.spring(translateX, {
            toValue: 0,
            useNativeDriver: true,
          }).start();
        }
      },
    });

    const getPriorityColor = () => {
      if (item.priority === 'URGENT') return '#e74c3c';
      return '#2ecc71';
    };

    const getPriorityIcon = () => {
      if (item.priority === 'URGENT') return '🔴';
      return '🟢';
    };

    return (
      <Animated.View
        style={[
          styles.swipeableContainer,
          {
            transform: [{ translateX }],
            opacity,
          },
        ]}
        {...panResponder.panHandlers}>
        <TouchableOpacity
          style={[
            styles.notificationCard,
            item.priority === 'URGENT' && styles.urgentCard,
            !item.read && styles.unreadCard,
          ]}
          onPress={() => handleMarkAsRead(item)}
          activeOpacity={0.7}>
          <View style={styles.notificationHeader}>
            <Text style={styles.appName} numberOfLines={1}>
              {item.packageName.split('.').pop()}
            </Text>
            <View
              style={[
                styles.badge,
                { backgroundColor: getPriorityColor() + '20' },
              ]}>
              <Text style={[styles.badgeText, { color: getPriorityColor() }]}>
                {getPriorityIcon()} {item.priority}
              </Text>
            </View>
          </View>

          {item.title && (
            <Text style={styles.notificationTitle} numberOfLines={2}>
              {item.title}
            </Text>
          )}
          
          <Text style={styles.notificationText} numberOfLines={3}>
            {item.text}
          </Text>

          <View style={styles.notificationFooter}>
            <Text style={styles.timestamp}>
              {formatTimestamp(item.timestamp || item.received)}
            </Text>
            {!item.read && <View style={styles.unreadDot} />}
          </View>

          <View style={styles.swipeHint}>
            <Text style={styles.swipeHintText}>
              ← Delete | Dismiss →
            </Text>
          </View>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const renderNotification = ({ item }) => <SwipeableNotificationCard item={item} />;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>📬 Notifications</Text>
        <Text style={styles.subtitle}>
          {notifications.length} notification{notifications.length !== 1 ? 's' : ''}
          {notificationService.getUnreadCount() > 0 && 
            ` • ${notificationService.getUnreadCount()} unread`}
        </Text>
      </View>

      {/* Permission Request */}
      {!hasPermission && !loading && (
        <View style={styles.permissionContainer}>
          <Text style={styles.permissionTitle}>📲 Permission Required</Text>
          <Text style={styles.permissionText}>
            This app needs notification access to classify and manage your notifications.
          </Text>
          <TouchableOpacity
            style={styles.permissionButton}
            onPress={handleRequestPermission}>
            <Text style={styles.permissionButtonText}>Grant Permission</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Filters */}
      {hasPermission && (
        <View style={styles.filterContainer}>
          <TouchableOpacity
            style={[styles.filterButton, filter === 'all' && styles.activeFilter]}
            onPress={() => setFilter('all')}>
            <Text style={[styles.filterText, filter === 'all' && styles.activeFilterText]}>
              All
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.filterButton, filter === 'urgent' && styles.activeFilter]}
            onPress={() => setFilter('urgent')}>
            <Text style={[styles.filterText, filter === 'urgent' && styles.activeFilterText]}>
              Urgent
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.filterButton, filter === 'unread' && styles.activeFilter]}
            onPress={() => setFilter('unread')}>
            <Text style={[styles.filterText, filter === 'unread' && styles.activeFilterText]}>
              Unread
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Notifications List */}
      {loading && !refreshing ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3498db" />
          <Text style={styles.loadingText}>Loading notifications...</Text>
        </View>
      ) : hasPermission ? (
        <FlatList
          data={notifications}
          renderItem={renderNotification}
          keyExtractor={(item, index) => item.id || `notification-${index}`}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>📭</Text>
              <Text style={styles.emptyTitle}>No Notifications</Text>
              <Text style={styles.emptySubtitle}>
                Your notifications will appear here
              </Text>
            </View>
          }
        />
      ) : null}
              <Text style={styles.emptySubtitle}>
                Your notifications will appear here
              </Text>
            </View>
          }
        />
      ) : null}
    </View>
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
    backgroundColor: 'white',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  permissionContainer: {
    backgroundColor: '#fff3cd',
    padding: 20,
    margin: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#ffc107',
  },
  permissionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  permissionText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    lineHeight: 20,
  },
  permissionButton: {
    backgroundColor: '#ffc107',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  permissionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  filterContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: 'white',
    alignItems: 'center',
  },
  activeFilter: {
    backgroundColor: '#2196F3',
  },
  filterText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  activeFilterText: {
    color: 'white',
  },
  swipeableContainer: {
    marginBottom: 12,
  },
  listContainer: {
    padding: 16,
    paddingTop: 0,
  },
  notificationCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  urgentCard: {
    borderLeftColor: '#F44336',
  },
  unreadCard: {
    borderWidth: 2,
    borderColor: '#3498db',
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  appName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    flex: 1,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 6,
    lineHeight: 22,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '600',
  },
  notificationText: {
    fontSize: 15,
    color: '#34495e',
    marginBottom: 12,
    lineHeight: 22,
  },
  notificationFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  timestamp: {
    fontSize: 12,
    color: '#95a5a6',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3498db',
  },
  swipeHint: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
  },
  swipeHintText: {
    fontSize: 10,
    color: '#95a5a6',
    textAlign: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#999',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
});

export default NotificationsScreen;
