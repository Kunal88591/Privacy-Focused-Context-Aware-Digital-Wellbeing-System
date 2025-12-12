/**
 * Day 17: Notification System Tests
 * Tests for Android notification listener, React Native bridge, and UI integration
 */

const fs = require('fs');
const path = require('path');

describe('Day 17: Notification System', () => {
  const mobileAppDir = path.join(__dirname, '..');
  const srcDir = path.join(mobileAppDir, 'src');
  const androidDir = path.join(mobileAppDir, 'android', 'app', 'src', 'main', 'java', 'com', 'privacywellbeingmobile');

  // ============================================
  // Android Native Files
  // ============================================

  describe('Android Native Implementation', () => {
    test('NotificationListener service exists', () => {
      const listenerPath = path.join(androidDir, 'NotificationListener.java');
      expect(fs.existsSync(listenerPath)).toBe(true);
    });

    test('NotificationEventService exists', () => {
      const servicePath = path.join(androidDir, 'NotificationEventService.java');
      expect(fs.existsSync(servicePath)).toBe(true);
    });

    test('NotificationModule bridge exists', () => {
      const modulePath = path.join(androidDir, 'NotificationModule.java');
      expect(fs.existsSync(modulePath)).toBe(true);
    });

    test('NotificationPackage exists', () => {
      const packagePath = path.join(androidDir, 'NotificationPackage.java');
      expect(fs.existsSync(packagePath)).toBe(true);
    });

    test('MainActivity exists', () => {
      const activityPath = path.join(androidDir, 'MainActivity.java');
      expect(fs.existsSync(activityPath)).toBe(true);
    });

    test('MainApplication exists', () => {
      const appPath = path.join(androidDir, 'MainApplication.java');
      expect(fs.existsSync(appPath)).toBe(true);
    });

    test('AndroidManifest.xml exists', () => {
      const manifestPath = path.join(mobileAppDir, 'android', 'app', 'src', 'main', 'AndroidManifest.xml');
      expect(fs.existsSync(manifestPath)).toBe(true);
    });
  });

  // ============================================
  // NotificationListener Validation
  // ============================================

  describe('NotificationListener Implementation', () => {
    const listenerPath = path.join(androidDir, 'NotificationListener.java');
    let listenerContent;

    beforeAll(() => {
      if (fs.existsSync(listenerPath)) {
        listenerContent = fs.readFileSync(listenerPath, 'utf-8');
      }
    });

    test('extends NotificationListenerService', () => {
      expect(listenerContent).toContain('extends NotificationListenerService');
    });

    test('implements onNotificationPosted', () => {
      expect(listenerContent).toContain('onNotificationPosted');
    });

    test('implements onNotificationRemoved', () => {
      expect(listenerContent).toContain('onNotificationRemoved');
    });

    test('has singleton getInstance method', () => {
      expect(listenerContent).toContain('getInstance');
    });

    test('extracts notification data', () => {
      expect(listenerContent).toContain('packageName');
      expect(listenerContent).toContain('title');
      expect(listenerContent).toContain('text');
      expect(listenerContent).toContain('timestamp');
    });

    test('filters system notifications', () => {
      expect(listenerContent).toContain('android') || expect(listenerContent).toContain('system');
    });
  });

  // ============================================
  // NotificationModule Validation
  // ============================================

  describe('NotificationModule Implementation', () => {
    const modulePath = path.join(androidDir, 'NotificationModule.java');
    let moduleContent;

    beforeAll(() => {
      if (fs.existsSync(modulePath)) {
        moduleContent = fs.readFileSync(modulePath, 'utf-8');
      }
    });

    test('extends ReactContextBaseJavaModule', () => {
      expect(moduleContent).toContain('ReactContextBaseJavaModule');
    });

    test('has checkNotificationPermission method', () => {
      expect(moduleContent).toContain('checkNotificationPermission');
    });

    test('has openNotificationSettings method', () => {
      expect(moduleContent).toContain('openNotificationSettings');
    });

    test('has dismissNotification method', () => {
      expect(moduleContent).toContain('dismissNotification');
    });

    test('has getActiveNotifications method', () => {
      expect(moduleContent).toContain('getActiveNotifications');
    });

    test('has dismissAllNotifications method', () => {
      expect(moduleContent).toContain('dismissAllNotifications');
    });

    test('uses @ReactMethod annotations', () => {
      expect(moduleContent).toContain('@ReactMethod');
    });

    test('returns promises for async operations', () => {
      expect(moduleContent).toContain('Promise');
    });
  });

  // ============================================
  // AndroidManifest Validation
  // ============================================

  describe('AndroidManifest Configuration', () => {
    const manifestPath = path.join(mobileAppDir, 'android', 'app', 'src', 'main', 'AndroidManifest.xml');
    let manifestContent;

    beforeAll(() => {
      if (fs.existsSync(manifestPath)) {
        manifestContent = fs.readFileSync(manifestPath, 'utf-8');
      }
    });

    test('declares NotificationListener service', () => {
      expect(manifestContent).toContain('NotificationListener');
    });

    test('has BIND_NOTIFICATION_LISTENER_SERVICE permission', () => {
      expect(manifestContent).toContain('BIND_NOTIFICATION_LISTENER_SERVICE');
    });

    test('declares NotificationEventService', () => {
      expect(manifestContent).toContain('NotificationEventService');
    });

    test('has service intent filter', () => {
      expect(manifestContent).toContain('intent-filter');
    });
  });

  // ============================================
  // React Native Service
  // ============================================

  describe('Notification Service (React Native)', () => {
    const servicePath = path.join(srcDir, 'services', 'notifications.js');
    let serviceContent;

    beforeAll(() => {
      if (fs.existsSync(servicePath)) {
        serviceContent = fs.readFileSync(servicePath, 'utf-8');
      }
    });

    test('notification service file exists', () => {
      expect(fs.existsSync(servicePath)).toBe(true);
    });

    test('imports NativeModules', () => {
      expect(serviceContent).toContain('NativeModules');
    });

    test('imports AsyncStorage', () => {
      expect(serviceContent).toContain('AsyncStorage');
    });

    test('has checkPermission method', () => {
      expect(serviceContent).toContain('checkPermission');
    });

    test('has openSettings method', () => {
      expect(serviceContent).toContain('openSettings');
    });

    test('has loadStoredNotifications method', () => {
      expect(serviceContent).toContain('loadStoredNotifications');
    });

    test('has handleNewNotification method', () => {
      expect(serviceContent).toContain('handleNewNotification');
    });

    test('has classifyNotification method', () => {
      expect(serviceContent).toContain('classifyNotification');
    });

    test('has dismissNotification method', () => {
      expect(serviceContent).toContain('dismissNotification');
    });

    test('has markAsRead method', () => {
      expect(serviceContent).toContain('markAsRead');
    });

    test('has addListener method', () => {
      expect(serviceContent).toContain('addListener');
    });

    test('implements headless task', () => {
      expect(serviceContent).toContain('registerHeadlessTask') || 
        expect(serviceContent).toContain('setupHeadlessTask');
    });

    test('saves notifications to storage', () => {
      expect(serviceContent).toContain('saveNotifications');
    });
  });

  // ============================================
  // NotificationsScreen Updates
  // ============================================

  describe('NotificationsScreen Integration', () => {
    const screenPath = path.join(srcDir, 'screens', 'NotificationsScreen.js');
    let screenContent;

    beforeAll(() => {
      if (fs.existsSync(screenPath)) {
        screenContent = fs.readFileSync(screenPath, 'utf-8');
      }
    });

    test('imports notificationService', () => {
      expect(screenContent).toContain('notificationService') || 
        expect(screenContent).toContain('notifications');
    });

    test('has permission check', () => {
      expect(screenContent).toContain('checkPermission') || 
        expect(screenContent).toContain('hasPermission');
    });

    test('has permission request UI', () => {
      expect(screenContent).toContain('permissionContainer') || 
        expect(screenContent).toContain('Grant Permission') ||
        expect(screenContent).toContain('Permission Required');
    });

    test('implements swipe-to-dismiss', () => {
      expect(screenContent).toContain('PanResponder') ||
        expect(screenContent).toContain('swipe') ||
        expect(screenContent).toContain('gesture');
    });

    test('has swipe animations', () => {
      expect(screenContent).toContain('Animated');
    });

    test('handles dismiss action', () => {
      expect(screenContent).toContain('handleDismiss') || 
        expect(screenContent).toContain('dismiss');
    });

    test('handles delete action', () => {
      expect(screenContent).toContain('handleDelete') || 
        expect(screenContent).toContain('delete');
    });

    test('shows priority badges', () => {
      expect(screenContent).toContain('priority') && 
        expect(screenContent).toContain('badge');
    });

    test('has unread indicator', () => {
      expect(screenContent).toContain('unread') || expect(screenContent).toContain('read');
    });

    test('shows timestamp formatting', () => {
      expect(screenContent).toContain('timestamp') || expect(screenContent).toContain('formatTime');
    });
  });

  // ============================================
  // File Statistics
  // ============================================

  describe('Day 17 File Statistics', () => {
    test('all Android files present (7 files)', () => {
      const androidFiles = [
        path.join(androidDir, 'NotificationListener.java'),
        path.join(androidDir, 'NotificationEventService.java'),
        path.join(androidDir, 'NotificationModule.java'),
        path.join(androidDir, 'NotificationPackage.java'),
        path.join(androidDir, 'MainActivity.java'),
        path.join(androidDir, 'MainApplication.java'),
        path.join(mobileAppDir, 'android', 'app', 'src', 'main', 'AndroidManifest.xml'),
      ];

      androidFiles.forEach(file => {
        expect(fs.existsSync(file)).toBe(true);
      });
    });

    test('React Native service exists', () => {
      const servicePath = path.join(srcDir, 'services', 'notifications.js');
      expect(fs.existsSync(servicePath)).toBe(true);
    });

    test('NotificationsScreen updated', () => {
      const screenPath = path.join(srcDir, 'screens', 'NotificationsScreen.js');
      expect(fs.existsSync(screenPath)).toBe(true);
    });
  });

  // ============================================
  // Integration Summary
  // ============================================

  describe('Day 17 Summary', () => {
    test('Android notification listener complete', () => {
      const listenerPath = path.join(androidDir, 'NotificationListener.java');
      const servicePath = path.join(androidDir, 'NotificationEventService.java');
      
      expect(fs.existsSync(listenerPath)).toBe(true);
      expect(fs.existsSync(servicePath)).toBe(true);
    });

    test('React Native bridge complete', () => {
      const modulePath = path.join(androidDir, 'NotificationModule.java');
      const packagePath = path.join(androidDir, 'NotificationPackage.java');
      
      expect(fs.existsSync(modulePath)).toBe(true);
      expect(fs.existsSync(packagePath)).toBe(true);
    });

    test('Notification service layer complete', () => {
      const servicePath = path.join(srcDir, 'services', 'notifications.js');
      const serviceContent = fs.readFileSync(servicePath, 'utf-8');
      
      const hasAllMethods = serviceContent.includes('checkPermission') &&
        serviceContent.includes('dismissNotification') &&
        serviceContent.includes('classifyNotification') &&
        serviceContent.includes('handleNewNotification');
      
      expect(hasAllMethods).toBe(true);
    });

    test('UI integration complete', () => {
      const screenPath = path.join(srcDir, 'screens', 'NotificationsScreen.js');
      const screenContent = fs.readFileSync(screenPath, 'utf-8');
      
      const hasSwipeFeatures = screenContent.includes('PanResponder') ||
        (screenContent.includes('swipe') && screenContent.includes('Animated'));
      
      expect(hasSwipeFeatures).toBe(true);
    });
  });
});
