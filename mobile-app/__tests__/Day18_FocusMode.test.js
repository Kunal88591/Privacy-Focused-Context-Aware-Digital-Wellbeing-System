/**
 * Day 18: Focus Mode System Tests
 * Tests for app blocking, Pomodoro timer, and blocking overlay
 */

const fs = require('fs');
const path = require('path');

// File paths
const androidDir = path.join(__dirname, '../android/app/src/main/java/com/privacywellbeingmobile');
const serviceDir = path.join(__dirname, '../src/services');
const screenDir = path.join(__dirname, '../src/screens');

describe('Day 18: Focus Mode System', () => {
  
  // ===== ANDROID NATIVE FILES =====
  describe('Android Native Implementation', () => {
    
    test('FocusModeService.java exists', () => {
      const filePath = path.join(androidDir, 'FocusModeService.java');
      expect(fs.existsSync(filePath)).toBe(true);
    });
    
    test('BlockingOverlayActivity.java exists', () => {
      const filePath = path.join(androidDir, 'BlockingOverlayActivity.java');
      expect(fs.existsSync(filePath)).toBe(true);
    });
    
    test('FocusModeModule.java exists', () => {
      const filePath = path.join(androidDir, 'FocusModeModule.java');
      expect(fs.existsSync(filePath)).toBe(true);
    });
    
    test('NotificationPackage.java includes FocusModeModule', () => {
      const filePath = path.join(androidDir, 'NotificationPackage.java');
      const content = fs.readFileSync(filePath, 'utf8');
      expect(content).toContain('FocusModeModule');
      expect(content).toContain('modules.add(new FocusModeModule(reactContext))');
    });
    
    test('AndroidManifest.xml declares FocusModeService', () => {
      const manifestPath = path.join(__dirname, '../android/app/src/main/AndroidManifest.xml');
      const content = fs.readFileSync(manifestPath, 'utf8');
      expect(content).toContain('FocusModeService');
      expect(content).toContain('android:name=".FocusModeService"');
    });
    
    test('AndroidManifest.xml declares BlockingOverlayActivity', () => {
      const manifestPath = path.join(__dirname, '../android/app/src/main/AndroidManifest.xml');
      const content = fs.readFileSync(manifestPath, 'utf8');
      expect(content).toContain('BlockingOverlayActivity');
      expect(content).toContain('android:name=".BlockingOverlayActivity"');
    });
    
    test('AndroidManifest.xml has PACKAGE_USAGE_STATS permission', () => {
      const manifestPath = path.join(__dirname, '../android/app/src/main/AndroidManifest.xml');
      const content = fs.readFileSync(manifestPath, 'utf8');
      expect(content).toContain('PACKAGE_USAGE_STATS');
    });
  });
  
  // ===== FOCUS MODE SERVICE (ANDROID) =====
  describe('FocusModeService Validation', () => {
    let serviceContent;
    
    beforeAll(() => {
      const filePath = path.join(androidDir, 'FocusModeService.java');
      serviceContent = fs.readFileSync(filePath, 'utf8');
    });
    
    test('extends Android Service', () => {
      expect(serviceContent).toContain('extends Service');
    });
    
    test('has DEFAULT_BLOCKED_APPS list', () => {
      expect(serviceContent).toContain('DEFAULT_BLOCKED_APPS');
      expect(serviceContent).toContain('com.instagram.android');
      expect(serviceContent).toContain('com.twitter.android');
      expect(serviceContent).toContain('com.facebook.katana');
      expect(serviceContent).toContain('com.zhiliaoapp.musically'); // TikTok
    });
    
    test('implements startFocusMode method', () => {
      expect(serviceContent).toContain('private void startFocusMode(');
      expect(serviceContent).toContain('isFocusModeActive = true');
    });
    
    test('implements stopFocusMode method', () => {
      expect(serviceContent).toContain('private void stopFocusMode()');
      expect(serviceContent).toContain('isFocusModeActive = false');
    });
    
    test('implements checkForBlockedApps method', () => {
      expect(serviceContent).toContain('private void checkForBlockedApps()');
      expect(serviceContent).toContain('getForegroundApp()');
    });
    
    test('uses UsageStatsManager to detect foreground app', () => {
      expect(serviceContent).toContain('UsageStatsManager');
      expect(serviceContent).toContain('getForegroundApp()');
    });
    
    test('shows blocking overlay when blocked app detected', () => {
      expect(serviceContent).toContain('showBlockingOverlay');
      expect(serviceContent).toContain('BlockingOverlayActivity');
    });
    
    test('broadcasts status updates', () => {
      expect(serviceContent).toContain('broadcastStatus');
      expect(serviceContent).toContain('FOCUS_MODE_STATUS');
    });
    
    test('handles START_FOCUS intent action', () => {
      expect(serviceContent).toContain('"START_FOCUS"');
      expect(serviceContent).toContain('onStartCommand');
    });
    
    test('handles STOP_FOCUS intent action', () => {
      expect(serviceContent).toContain('"STOP_FOCUS"');
    });
    
    test('tracks session end time', () => {
      expect(serviceContent).toContain('sessionEndTime');
      expect(serviceContent).toContain('getRemainingTime()');
    });
  });
  
  // ===== BLOCKING OVERLAY ACTIVITY =====
  describe('BlockingOverlayActivity Validation', () => {
    let activityContent;
    
    beforeAll(() => {
      const filePath = path.join(androidDir, 'BlockingOverlayActivity.java');
      activityContent = fs.readFileSync(filePath, 'utf8');
    });
    
    test('extends Android Activity', () => {
      expect(activityContent).toContain('extends Activity');
    });
    
    test('displays blocked app name', () => {
      expect(activityContent).toContain('appNameText');
      expect(activityContent).toContain('blockedApp');
    });
    
    test('displays remaining time', () => {
      expect(activityContent).toContain('timerText');
      expect(activityContent).toContain('remainingTime');
    });
    
    test('has close button to return home', () => {
      expect(activityContent).toContain('closeButton');
      expect(activityContent).toContain('goHome()');
    });
    
    test('creates UI programmatically (no XML)', () => {
      expect(activityContent).toContain('createLayout()');
      expect(activityContent).toContain('LinearLayout');
    });
    
    test('updates timer every second', () => {
      expect(activityContent).toContain('updateTimer()');
      expect(activityContent).toContain('handler.postDelayed');
    });
    
    test('has friendly app names mapping', () => {
      expect(activityContent).toContain('getAppName');
      expect(activityContent).toContain('Instagram');
      expect(activityContent).toContain('Twitter');
      expect(activityContent).toContain('TikTok');
    });
    
    test('prevents back button bypass', () => {
      expect(activityContent).toContain('onBackPressed()');
    });
  });
  
  // ===== FOCUS MODE MODULE (BRIDGE) =====
  describe('FocusModeModule Validation', () => {
    let moduleContent;
    
    beforeAll(() => {
      const filePath = path.join(androidDir, 'FocusModeModule.java');
      moduleContent = fs.readFileSync(filePath, 'utf8');
    });
    
    test('extends ReactContextBaseJavaModule', () => {
      expect(moduleContent).toContain('extends ReactContextBaseJavaModule');
    });
    
    test('has checkUsageStatsPermission method', () => {
      expect(moduleContent).toContain('checkUsageStatsPermission');
      expect(moduleContent).toContain('@ReactMethod');
      expect(moduleContent).toContain('AppOpsManager');
    });
    
    test('has openUsageStatsSettings method', () => {
      expect(moduleContent).toContain('openUsageStatsSettings');
      expect(moduleContent).toContain('ACTION_USAGE_ACCESS_SETTINGS');
    });
    
    test('has startFocusMode method', () => {
      expect(moduleContent).toContain('startFocusMode');
      expect(moduleContent).toContain('durationMinutes');
    });
    
    test('has stopFocusMode method', () => {
      expect(moduleContent).toContain('stopFocusMode');
    });
    
    test('has updateBlockedApps method', () => {
      expect(moduleContent).toContain('updateBlockedApps');
      expect(moduleContent).toContain('ReadableArray');
    });
    
    test('has getFocusModeStatus method', () => {
      expect(moduleContent).toContain('getFocusModeStatus');
    });
    
    test('has getDefaultBlockedApps method', () => {
      expect(moduleContent).toContain('getDefaultBlockedApps');
    });
    
    test('uses BroadcastReceiver for status updates', () => {
      expect(moduleContent).toContain('BroadcastReceiver');
      expect(moduleContent).toContain('registerStatusReceiver');
    });
    
    test('sends events to React Native', () => {
      expect(moduleContent).toContain('sendEvent');
      expect(moduleContent).toContain('FocusModeStatusChanged');
    });
  });
  
  // ===== FOCUS MODE SERVICE (REACT NATIVE) =====
  describe('Focus Mode Service Layer', () => {
    let serviceContent;
    
    beforeAll(() => {
      const filePath = path.join(serviceDir, 'focusMode.js');
      serviceContent = fs.readFileSync(filePath, 'utf8');
    });
    
    test('focusMode.js service file exists', () => {
      const filePath = path.join(serviceDir, 'focusMode.js');
      expect(fs.existsSync(filePath)).toBe(true);
    });
    
    test('imports FocusModeModule from NativeModules', () => {
      expect(serviceContent).toContain('NativeModules');
      expect(serviceContent).toContain('FocusModeModule');
    });
    
    test('imports AsyncStorage for persistence', () => {
      expect(serviceContent).toContain('@react-native-async-storage/async-storage');
    });
    
    test('has DURATIONS constants (25, 50, 90 minutes)', () => {
      expect(serviceContent).toContain('DURATIONS');
      expect(serviceContent).toContain('SHORT: 25');
      expect(serviceContent).toContain('MEDIUM: 50');
      expect(serviceContent).toContain('LONG: 90');
    });
    
    test('has DEFAULT_BLOCKED_APPS list', () => {
      expect(serviceContent).toContain('DEFAULT_BLOCKED_APPS');
      expect(serviceContent).toContain('com.instagram.android');
      expect(serviceContent).toContain('com.twitter.android');
    });
    
    test('has checkPermission method', () => {
      expect(serviceContent).toContain('checkPermission()');
      expect(serviceContent).toContain('checkUsageStatsPermission');
    });
    
    test('has openSettings method', () => {
      expect(serviceContent).toContain('openSettings()');
      expect(serviceContent).toContain('openUsageStatsSettings');
    });
    
    test('has startSession method', () => {
      expect(serviceContent).toContain('startSession(');
      expect(serviceContent).toContain('duration');
    });
    
    test('has stopSession method', () => {
      expect(serviceContent).toContain('stopSession()');
    });
    
    test('has getStatus method', () => {
      expect(serviceContent).toContain('getStatus()');
      expect(serviceContent).toContain('isActive');
      expect(serviceContent).toContain('remainingTime');
    });
    
    test('has getRemainingTime method', () => {
      expect(serviceContent).toContain('getRemainingTime()');
    });
    
    test('has getProgress method', () => {
      expect(serviceContent).toContain('getProgress()');
    });
    
    test('has updateBlockedApps method', () => {
      expect(serviceContent).toContain('updateBlockedApps(');
    });
    
    test('has getBlockedApps method', () => {
      expect(serviceContent).toContain('getBlockedApps()');
    });
    
    test('has getStats method for statistics', () => {
      expect(serviceContent).toContain('getStats()');
      expect(serviceContent).toContain('totalSessions');
      expect(serviceContent).toContain('totalMinutes');
      expect(serviceContent).toContain('longestStreak');
    });
    
    test('tracks session statistics', () => {
      expect(serviceContent).toContain('updateStats(');
      expect(serviceContent).toContain('currentStreak');
    });
    
    test('implements observer pattern with listeners', () => {
      expect(serviceContent).toContain('addListener(');
      expect(serviceContent).toContain('notifyListeners()');
    });
    
    test('saves state to AsyncStorage', () => {
      expect(serviceContent).toContain('saveState()');
      expect(serviceContent).toContain('AsyncStorage.setItem');
    });
    
    test('loads saved state on init', () => {
      expect(serviceContent).toContain('loadSavedData()');
      expect(serviceContent).toContain('AsyncStorage.getItem');
    });
    
    test('exports singleton instance', () => {
      expect(serviceContent).toContain('export default new FocusModeService()');
    });
  });
  
  // ===== FOCUS MODE SCREEN =====
  describe('FocusModeScreen Integration', () => {
    let screenContent;
    
    beforeAll(() => {
      const filePath = path.join(screenDir, 'FocusModeScreen.js');
      screenContent = fs.readFileSync(filePath, 'utf8');
    });
    
    test('FocusModeScreen.js file exists', () => {
      const filePath = path.join(screenDir, 'FocusModeScreen.js');
      expect(fs.existsSync(filePath)).toBe(true);
    });
    
    test('imports focusModeService', () => {
      expect(screenContent).toContain("from '../services/focusMode'");
    });
    
    test('has permission check state', () => {
      expect(screenContent).toContain('hasPermission');
      expect(screenContent).toContain('setHasPermission');
    });
    
    test('has permission request UI', () => {
      expect(screenContent).toContain('permissionCard');
      expect(screenContent).toContain('Permission Required');
      expect(screenContent).toContain('Grant Permission');
    });
    
    test('displays active session with timer', () => {
      expect(screenContent).toContain('activeSessionCard');
      expect(screenContent).toContain('timerText');
      expect(screenContent).toContain('Focus Mode Active');
    });
    
    test('has duration selection buttons (25, 50, 90 min)', () => {
      expect(screenContent).toContain('selectedDuration');
      expect(screenContent).toContain('25');
      expect(screenContent).toContain('50');
      expect(screenContent).toContain('90');
      expect(screenContent).toContain('durationButton');
    });
    
    test('has start session button', () => {
      expect(screenContent).toContain('startButton');
      expect(screenContent).toContain('handleStartSession');
    });
    
    test('has stop session button', () => {
      expect(screenContent).toContain('stopButton');
      expect(screenContent).toContain('handleStopSession');
    });
    
    test('displays progress bar', () => {
      expect(screenContent).toContain('progressBar');
      expect(screenContent).toContain('progressContainer');
    });
    
    test('displays statistics', () => {
      expect(screenContent).toContain('statsCard');
      expect(screenContent).toContain('Total Sessions');
      expect(screenContent).toContain('Minutes Focused');
      expect(screenContent).toContain('Day Streak');
    });
    
    test('subscribes to focusModeService updates', () => {
      expect(screenContent).toContain('focusModeService.addListener');
      expect(screenContent).toContain('handleStatusUpdate');
    });
    
    test('updates timer every second', () => {
      expect(screenContent).toContain('timerIntervalRef');
      expect(screenContent).toContain('setInterval');
    });
    
    test('formats time display', () => {
      expect(screenContent).toContain('formatTime');
    });
    
    test('shows blocked apps list', () => {
      expect(screenContent).toContain('Blocked Apps');
      expect(screenContent).toContain('Instagram');
      expect(screenContent).toContain('Twitter');
    });
    
    test('shows completion alert when session ends', () => {
      expect(screenContent).toContain('Focus Session Complete');
    });
  });
  
  // ===== NAVIGATION INTEGRATION =====
  describe('Navigation Integration', () => {
    let navContent;
    
    beforeAll(() => {
      const filePath = path.join(__dirname, '../src/navigation/AppNavigator.js');
      navContent = fs.readFileSync(filePath, 'utf8');
    });
    
    test('imports FocusModeScreen', () => {
      expect(navContent).toContain("import FocusModeScreen from '../screens/FocusModeScreen'");
    });
    
    test('has FocusMode tab in navigator', () => {
      expect(navContent).toContain('name="FocusMode"');
      expect(navContent).toContain('component={FocusModeScreen}');
    });
    
    test('has Focus tab label', () => {
      expect(navContent).toContain("tabBarLabel: 'Focus'");
    });
  });
  
  // ===== FILE STATISTICS =====
  describe('File Statistics', () => {
    
    test('all Android files created (3 files)', () => {
      const files = [
        'FocusModeService.java',
        'BlockingOverlayActivity.java',
        'FocusModeModule.java',
      ];
      
      files.forEach(file => {
        const filePath = path.join(androidDir, file);
        expect(fs.existsSync(filePath)).toBe(true);
      });
    });
    
    test('React Native service created', () => {
      const filePath = path.join(serviceDir, 'focusMode.js');
      expect(fs.existsSync(filePath)).toBe(true);
    });
    
    test('FocusModeScreen created', () => {
      const filePath = path.join(screenDir, 'FocusModeScreen.js');
      expect(fs.existsSync(filePath)).toBe(true);
    });
    
    test('FocusModeService.java has reasonable size', () => {
      const filePath = path.join(androidDir, 'FocusModeService.java');
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n').length;
      expect(lines).toBeGreaterThan(180); // Expect ~200 lines
    });
    
    test('focusMode.js service has reasonable size', () => {
      const filePath = path.join(serviceDir, 'focusMode.js');
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n').length;
      expect(lines).toBeGreaterThan(340); // Expect ~360 lines
    });
    
    test('FocusModeScreen.js has reasonable size', () => {
      const filePath = path.join(screenDir, 'FocusModeScreen.js');
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n').length;
      expect(lines).toBeGreaterThan(420); // Expect ~450 lines
    });
  });
  
  // ===== INTEGRATION SUMMARY =====
  describe('Integration Summary', () => {
    
    test('Android app blocking service complete', () => {
      const serviceFile = path.join(androidDir, 'FocusModeService.java');
      const serviceExists = fs.existsSync(serviceFile);
      
      const moduleFile = path.join(androidDir, 'FocusModeModule.java');
      const moduleExists = fs.existsSync(moduleFile);
      
      expect(serviceExists && moduleExists).toBe(true);
    });
    
    test('Blocking overlay complete', () => {
      const overlayFile = path.join(androidDir, 'BlockingOverlayActivity.java');
      const overlayExists = fs.existsSync(overlayFile);
      
      const manifestPath = path.join(__dirname, '../android/app/src/main/AndroidManifest.xml');
      const manifestContent = fs.readFileSync(manifestPath, 'utf8');
      const manifestConfigured = manifestContent.includes('BlockingOverlayActivity');
      
      expect(overlayExists && manifestConfigured).toBe(true);
    });
    
    test('React Native service layer complete', () => {
      const serviceFile = path.join(serviceDir, 'focusMode.js');
      const content = fs.readFileSync(serviceFile, 'utf8');
      
      const hasCore = content.includes('startSession') && 
                      content.includes('stopSession') &&
                      content.includes('getStatus');
      
      const hasStats = content.includes('getStats') && 
                       content.includes('updateStats');
      
      expect(hasCore && hasStats).toBe(true);
    });
    
    test('UI integration complete', () => {
      const screenFile = path.join(screenDir, 'FocusModeScreen.js');
      const screenContent = fs.readFileSync(screenFile, 'utf8');
      
      const navFile = path.join(__dirname, '../src/navigation/AppNavigator.js');
      const navContent = fs.readFileSync(navFile, 'utf8');
      
      const screenComplete = screenContent.includes('FocusModeScreen');
      const navComplete = navContent.includes('FocusModeScreen');
      
      expect(screenComplete && navComplete).toBe(true);
    });
    
    test('Pomodoro timer durations available (25, 50, 90 min)', () => {
      const serviceFile = path.join(serviceDir, 'focusMode.js');
      const content = fs.readFileSync(serviceFile, 'utf8');
      
      const has25 = content.includes('SHORT: 25');
      const has50 = content.includes('MEDIUM: 50');
      const has90 = content.includes('LONG: 90');
      
      expect(has25 && has50 && has90).toBe(true);
    });
    
    test('Statistics tracking implemented', () => {
      const serviceFile = path.join(serviceDir, 'focusMode.js');
      const content = fs.readFileSync(serviceFile, 'utf8');
      
      const hasStats = content.includes('totalSessions') &&
                       content.includes('totalMinutes') &&
                       content.includes('longestStreak') &&
                       content.includes('currentStreak');
      
      expect(hasStats).toBe(true);
    });
  });
});
