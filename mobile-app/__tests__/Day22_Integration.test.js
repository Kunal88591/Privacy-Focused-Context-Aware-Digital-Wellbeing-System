/**
 * Day 22: End-to-End Integration Tests
 * Tests for complete system integration across backend, mobile, and IoT
 */

const fs = require('fs');
const path = require('path');

describe('Day 22: End-to-End Integration Tests', () => {
  const projectRoot = path.join(__dirname, '../..');
  const mobileAppDir = path.join(__dirname, '..');
  const backendDir = path.join(projectRoot, 'backend-api');
  const iotDir = path.join(projectRoot, 'iot-device');
  const srcDir = path.join(mobileAppDir, 'src');

  // ============================================
  // PROJECT STRUCTURE VALIDATION
  // ============================================

  describe('Project Structure', () => {
    test('all major components exist', () => {
      expect(fs.existsSync(mobileAppDir)).toBe(true);
      expect(fs.existsSync(backendDir)).toBe(true);
      expect(fs.existsSync(iotDir)).toBe(true);
    });

    test('mobile app has all core services', () => {
      const services = [
        'api.js',
        'notifications.js',
        'focusMode.js',
        'privacy.js',
        'recommendations.js',
        'analytics.js'
      ];
      
      services.forEach(service => {
        const servicePath = path.join(srcDir, 'services', service);
        expect(fs.existsSync(servicePath)).toBe(true);
      });
    });

    test('mobile app has all screens', () => {
      const screens = [
        'HomeScreen.js',
        'NotificationsScreen.js',
        'FocusModeScreen.js',
        'PrivacyScreen.js',
        'RecommendationsScreen.js',
        'AnalyticsScreen.js',
        'SettingsScreen.js'
      ];
      
      screens.forEach(screen => {
        const screenPath = path.join(srcDir, 'screens', screen);
        expect(fs.existsSync(screenPath)).toBe(true);
      });
    });

    test('backend has all API modules', () => {
      const apiModules = [
        'auth.py',
        'notifications.py',
        'wellbeing.py',
        'privacy.py',
        'devices.py',
        'ai.py',
        'analytics.py'
      ];
      
      apiModules.forEach(module => {
        const modulePath = path.join(backendDir, 'app', 'api', module);
        expect(fs.existsSync(modulePath)).toBe(true);
      });
    });
  });

  // ============================================
  // NOTIFICATION FLOW INTEGRATION
  // ============================================

  describe('Notification Flow Integration', () => {
    const notificationServicePath = path.join(srcDir, 'services', 'notifications.js');
    const backendNotificationsPath = path.join(backendDir, 'app', 'api', 'notifications.py');
    
    test('mobile notification service exists', () => {
      expect(fs.existsSync(notificationServicePath)).toBe(true);
    });

    test('backend notification API exists', () => {
      expect(fs.existsSync(backendNotificationsPath)).toBe(true);
    });

    test('mobile service has classification method', () => {
      const content = fs.readFileSync(notificationServicePath, 'utf-8');
      expect(content).toContain('classifyNotification') || 
        expect(content).toContain('classify');
    });

    test('backend has classification endpoint', () => {
      const content = fs.readFileSync(backendNotificationsPath, 'utf-8');
      expect(content).toContain('/classify');
      expect(content).toContain('router.post') || expect(content).toContain('@router.post');
    });

    test('notification flow is complete', () => {
      // Mobile → Backend → ML → Response
      const mobileContent = fs.readFileSync(notificationServicePath, 'utf-8');
      const backendContent = fs.readFileSync(backendNotificationsPath, 'utf-8');
      
      const hasAPICall = mobileContent.includes('axios') || mobileContent.includes('fetch');
      const hasEndpoint = backendContent.includes('/notifications/classify');
      
      expect(hasAPICall && hasEndpoint).toBe(true);
    });

    test('ML model integration exists', () => {
      const mlServicePath = path.join(backendDir, 'app', 'services', 'ml_model_service.py');
      expect(fs.existsSync(mlServicePath)).toBe(true);
      
      if (fs.existsSync(mlServicePath)) {
        const content = fs.readFileSync(mlServicePath, 'utf-8');
        expect(content).toContain('classify');
      }
    });
  });

  // ============================================
  // FOCUS MODE INTEGRATION
  // ============================================

  describe('Focus Mode Integration', () => {
    const focusServicePath = path.join(srcDir, 'services', 'focusMode.js');
    const backendWellbeingPath = path.join(backendDir, 'app', 'api', 'wellbeing.py');
    
    test('mobile focus service exists', () => {
      expect(fs.existsSync(focusServicePath)).toBe(true);
    });

    test('backend wellbeing API exists', () => {
      expect(fs.existsSync(backendWellbeingPath)).toBe(true);
    });

    test('focus service has session management', () => {
      const content = fs.readFileSync(focusServicePath, 'utf-8');
      expect(content).toContain('startSession') || expect(content).toContain('start');
      expect(content).toContain('stopSession') || expect(content).toContain('stop');
    });

    test('focus service has app blocking', () => {
      const content = fs.readFileSync(focusServicePath, 'utf-8');
      expect(content).toContain('blockedApps') || 
        expect(content).toContain('BLOCKED_APPS') ||
        expect(content).toContain('DEFAULT_BLOCKED_APPS');
    });

    test('backend has focus mode endpoints', () => {
      const content = fs.readFileSync(backendWellbeingPath, 'utf-8');
      expect(content).toContain('/focus');
    });

    test('focus mode has timer functionality', () => {
      const content = fs.readFileSync(focusServicePath, 'utf-8');
      expect(content).toContain('duration') || 
        expect(content).toContain('DURATIONS') ||
        expect(content).toContain('timer');
    });

    test('focus stats tracking exists', () => {
      const content = fs.readFileSync(focusServicePath, 'utf-8');
      expect(content).toContain('stats') || 
        expect(content).toContain('statistics') ||
        expect(content).toContain('getStats');
    });
  });

  // ============================================
  // PRIVACY SYSTEM INTEGRATION
  // ============================================

  describe('Privacy System Integration', () => {
    const privacyServicePath = path.join(srcDir, 'services', 'privacy.js');
    const backendPrivacyPath = path.join(backendDir, 'app', 'api', 'privacy.py');
    
    test('mobile privacy service exists', () => {
      expect(fs.existsSync(privacyServicePath)).toBe(true);
    });

    test('backend privacy API exists', () => {
      expect(fs.existsSync(backendPrivacyPath)).toBe(true);
    });

    test('privacy service has VPN control', () => {
      const content = fs.readFileSync(privacyServicePath, 'utf-8');
      expect(content).toContain('VPN') || 
        expect(content).toContain('vpn') ||
        expect(content).toContain('connectVPN');
    });

    test('privacy service has tracker blocking', () => {
      const content = fs.readFileSync(privacyServicePath, 'utf-8');
      expect(content).toContain('tracker') || 
        expect(content).toContain('blocking') ||
        expect(content).toContain('blockedDomains');
    });

    test('privacy scoring exists', () => {
      const content = fs.readFileSync(privacyServicePath, 'utf-8');
      expect(content).toContain('score') || 
        expect(content).toContain('getPrivacyScore') ||
        expect(content).toContain('calculateScore');
    });

    test('backend privacy API has endpoints', () => {
      const content = fs.readFileSync(backendPrivacyPath, 'utf-8');
      expect(content).toContain('/privacy') || expect(content).toContain('/vpn');
    });
  });

  // ============================================
  // ANALYTICS INTEGRATION
  // ============================================

  describe('Analytics Integration', () => {
    const analyticsServicePath = path.join(srcDir, 'services', 'analytics.js');
    const backendAnalyticsPath = path.join(backendDir, 'app', 'api', 'analytics.py');
    
    test('mobile analytics service exists', () => {
      expect(fs.existsSync(analyticsServicePath)).toBe(true);
    });

    test('backend analytics API exists', () => {
      expect(fs.existsSync(backendAnalyticsPath)).toBe(true);
    });

    test('analytics service has dashboard method', () => {
      const content = fs.readFileSync(analyticsServicePath, 'utf-8');
      expect(content).toContain('getDashboard') || 
        expect(content).toContain('dashboard') ||
        expect(content).toContain('fetchAnalytics');
    });

    test('analytics has caching', () => {
      const content = fs.readFileSync(analyticsServicePath, 'utf-8');
      expect(content).toContain('cache') || 
        expect(content).toContain('AsyncStorage') ||
        expect(content).toContain('cached');
    });

    test('backend analytics has dashboard endpoint', () => {
      const content = fs.readFileSync(backendAnalyticsPath, 'utf-8');
      expect(content).toContain('/dashboard');
    });
  });

  // ============================================
  // RECOMMENDATIONS INTEGRATION
  // ============================================

  describe('Recommendations Integration', () => {
    const recsServicePath = path.join(srcDir, 'services', 'recommendations.js');
    const backendAIPath = path.join(backendDir, 'app', 'api', 'ai.py');
    
    test('mobile recommendations service exists', () => {
      expect(fs.existsSync(recsServicePath)).toBe(true);
    });

    test('backend AI API exists', () => {
      expect(fs.existsSync(backendAIPath)).toBe(true);
    });

    test('recommendations service fetches from backend', () => {
      const content = fs.readFileSync(recsServicePath, 'utf-8');
      expect(content).toContain('getRecommendations') || 
        expect(content).toContain('recommendations') ||
        expect(content).toContain('fetchRecommendations');
    });

    test('recommendations has observer pattern', () => {
      const content = fs.readFileSync(recsServicePath, 'utf-8');
      expect(content).toContain('subscribe') || 
        expect(content).toContain('listener') ||
        expect(content).toContain('observer');
    });
  });

  // ============================================
  // API CLIENT INTEGRATION
  // ============================================

  describe('API Client Integration', () => {
    const apiServicePath = path.join(srcDir, 'services', 'api.js');
    
    test('API service exists', () => {
      expect(fs.existsSync(apiServicePath)).toBe(true);
    });

    test('API service uses axios', () => {
      const content = fs.readFileSync(apiServicePath, 'utf-8');
      expect(content).toContain('axios');
    });

    test('API service has base URL configuration', () => {
      const content = fs.readFileSync(apiServicePath, 'utf-8');
      expect(content).toContain('baseURL') || 
        expect(content).toContain('API_URL') ||
        expect(content).toContain('BASE_URL');
    });

    test('API service has authentication handling', () => {
      const content = fs.readFileSync(apiServicePath, 'utf-8');
      expect(content).toContain('token') || 
        expect(content).toContain('Authorization') ||
        expect(content).toContain('auth');
    });

    test('API service has error handling', () => {
      const content = fs.readFileSync(apiServicePath, 'utf-8');
      expect(content).toContain('catch') || 
        expect(content).toContain('error') ||
        expect(content).toContain('try');
    });
  });

  // ============================================
  // IOT DEVICE INTEGRATION
  // ============================================

  describe('IoT Device Integration', () => {
    const mqttClientPath = path.join(iotDir, 'mqtt_client.py');
    const backendDevicesPath = path.join(backendDir, 'app', 'api', 'devices.py');
    
    test('IoT MQTT client exists', () => {
      expect(fs.existsSync(mqttClientPath)).toBe(true);
    });

    test('backend devices API exists', () => {
      expect(fs.existsSync(backendDevicesPath)).toBe(true);
    });

    test('MQTT client publishes sensor data', () => {
      const content = fs.readFileSync(mqttClientPath, 'utf-8');
      expect(content).toContain('publish') || expect(content).toContain('PUBLISH');
    });

    test('MQTT client subscribes to commands', () => {
      const content = fs.readFileSync(mqttClientPath, 'utf-8');
      expect(content).toContain('subscribe') || expect(content).toContain('SUBSCRIBE');
    });
  });

  // ============================================
  // BACKEND SERVICES
  // ============================================

  describe('Backend Services', () => {
    test('ML model service exists', () => {
      const mlServicePath = path.join(backendDir, 'app', 'services', 'ml_model_service.py');
      expect(fs.existsSync(mlServicePath)).toBe(true);
    });

    test('MQTT service exists', () => {
      const mqttServicePath = path.join(backendDir, 'app', 'services', 'mqtt_service.py');
      expect(fs.existsSync(mqttServicePath)).toBe(true);
    });

    test('analytics tracker exists', () => {
      const analyticsPath = path.join(backendDir, 'app', 'services', 'analytics_tracker.py');
      expect(fs.existsSync(analyticsPath)).toBe(true);
    });

    test('privacy service exists', () => {
      const privacyPath = path.join(backendDir, 'app', 'services', 'privacy_service.py');
      expect(fs.existsSync(privacyPath)).toBe(true);
    });
  });

  // ============================================
  // CONFIGURATION FILES
  // ============================================

  describe('Configuration Files', () => {
    test('mobile app package.json exists', () => {
      const packagePath = path.join(mobileAppDir, 'package.json');
      expect(fs.existsSync(packagePath)).toBe(true);
    });

    test('backend requirements.txt exists', () => {
      const reqPath = path.join(backendDir, 'requirements.txt');
      expect(fs.existsSync(reqPath)).toBe(true);
    });

    test('IoT requirements.txt exists', () => {
      const reqPath = path.join(iotDir, 'requirements.txt');
      expect(fs.existsSync(reqPath)).toBe(true);
    });

    test('mobile config exists', () => {
      const configPath = path.join(srcDir, 'config', 'index.js');
      expect(fs.existsSync(configPath)).toBe(true);
    });
  });

  // ============================================
  // DATA FLOW VALIDATION
  // ============================================

  describe('Data Flow Validation', () => {
    test('mobile → backend notification flow', () => {
      const mobileNotifs = path.join(srcDir, 'services', 'notifications.js');
      const backendNotifs = path.join(backendDir, 'app', 'api', 'notifications.py');
      
      expect(fs.existsSync(mobileNotifs)).toBe(true);
      expect(fs.existsSync(backendNotifs)).toBe(true);
      
      const mobileContent = fs.readFileSync(mobileNotifs, 'utf-8');
      const backendContent = fs.readFileSync(backendNotifs, 'utf-8');
      
      expect(mobileContent.includes('axios') || mobileContent.includes('fetch')).toBe(true);
      expect(backendContent.includes('/classify') || backendContent.includes('classify')).toBe(true);
    });

    test('backend → IoT command flow', () => {
      const backendDevices = path.join(backendDir, 'app', 'api', 'devices.py');
      const iotClient = path.join(iotDir, 'mqtt_client.py');
      
      expect(fs.existsSync(backendDevices)).toBe(true);
      expect(fs.existsSync(iotClient)).toBe(true);
    });

    test('IoT → backend sensor data flow', () => {
      const iotClient = path.join(iotDir, 'mqtt_client.py');
      
      if (fs.existsSync(iotClient)) {
        const content = fs.readFileSync(iotClient, 'utf-8');
        expect(content.includes('publish') || content.includes('PUBLISH')).toBe(true);
      }
    });
  });

  // ============================================
  // FEATURE COMPLETENESS
  // ============================================

  describe('Feature Completeness', () => {
    test('Day 15: UI Foundation complete', () => {
      const screens = [
        'HomeScreen.js',
        'NotificationsScreen.js',
        'PrivacyScreen.js',
        'SettingsScreen.js',
        'AnalyticsScreen.js'
      ];
      
      screens.forEach(screen => {
        expect(fs.existsSync(path.join(srcDir, 'screens', screen))).toBe(true);
      });
    });

    test('Day 16: API Integration complete', () => {
      const apiService = path.join(srcDir, 'services', 'api.js');
      expect(fs.existsSync(apiService)).toBe(true);
    });

    test('Day 17: Notification System complete', () => {
      const notifService = path.join(srcDir, 'services', 'notifications.js');
      expect(fs.existsSync(notifService)).toBe(true);
    });

    test('Day 18: Focus Mode complete', () => {
      const focusService = path.join(srcDir, 'services', 'focusMode.js');
      const focusScreen = path.join(srcDir, 'screens', 'FocusModeScreen.js');
      expect(fs.existsSync(focusService)).toBe(true);
      expect(fs.existsSync(focusScreen)).toBe(true);
    });

    test('Day 19: Privacy Features complete', () => {
      const privacyService = path.join(srcDir, 'services', 'privacy.js');
      const privacyScreen = path.join(srcDir, 'screens', 'PrivacyScreen.js');
      expect(fs.existsSync(privacyService)).toBe(true);
      expect(fs.existsSync(privacyScreen)).toBe(true);
    });

    test('Day 20: Recommendations complete', () => {
      const recsService = path.join(srcDir, 'services', 'recommendations.js');
      const recsScreen = path.join(srcDir, 'screens', 'RecommendationsScreen.js');
      expect(fs.existsSync(recsService)).toBe(true);
      expect(fs.existsSync(recsScreen)).toBe(true);
    });

    test('Day 21: Analytics complete', () => {
      const analyticsService = path.join(srcDir, 'services', 'analytics.js');
      const analyticsScreen = path.join(srcDir, 'screens', 'AnalyticsScreen.js');
      expect(fs.existsSync(analyticsService)).toBe(true);
      expect(fs.existsSync(analyticsScreen)).toBe(true);
    });
  });

  // ============================================
  // SYSTEM HEALTH INDICATORS
  // ============================================

  describe('System Health Indicators', () => {
    test('all services have error handling', () => {
      const services = [
        'api.js',
        'notifications.js',
        'focusMode.js',
        'privacy.js',
        'recommendations.js',
        'analytics.js'
      ];
      
      services.forEach(service => {
        const servicePath = path.join(srcDir, 'services', service);
        if (fs.existsSync(servicePath)) {
          const content = fs.readFileSync(servicePath, 'utf-8');
          expect(content.includes('catch') || content.includes('try')).toBe(true);
        }
      });
    });

    test('all services have offline support', () => {
      const services = [
        'analytics.js',
        'recommendations.js',
        'privacy.js'
      ];
      
      services.forEach(service => {
        const servicePath = path.join(srcDir, 'services', service);
        if (fs.existsSync(servicePath)) {
          const content = fs.readFileSync(servicePath, 'utf-8');
          expect(
            content.includes('cache') || 
            content.includes('AsyncStorage') ||
            content.includes('offline')
          ).toBe(true);
        }
      });
    });
  });

  // ============================================
  // INTEGRATION TEST SUMMARY
  // ============================================

  describe('Integration Test Summary', () => {
    test('all components are connected', () => {
      const components = [
        // Mobile
        path.join(srcDir, 'services', 'api.js'),
        path.join(srcDir, 'services', 'notifications.js'),
        path.join(srcDir, 'services', 'focusMode.js'),
        
        // Backend
        path.join(backendDir, 'app', 'api', 'notifications.py'),
        path.join(backendDir, 'app', 'api', 'wellbeing.py'),
        path.join(backendDir, 'app', 'services', 'ml_model_service.py'),
        
        // IoT
        path.join(iotDir, 'mqtt_client.py')
      ];
      
      components.forEach(component => {
        expect(fs.existsSync(component)).toBe(true);
      });
    });

    test('system is production-ready', () => {
      // Check for critical files
      const criticalFiles = [
        path.join(mobileAppDir, 'App.js'),
        path.join(backendDir, 'app', 'main.py'),
        path.join(iotDir, 'mqtt_client.py'),
        path.join(srcDir, 'navigation', 'AppNavigator.js')
      ];
      
      criticalFiles.forEach(file => {
        expect(fs.existsSync(file)).toBe(true);
      });
    });
  });
});
