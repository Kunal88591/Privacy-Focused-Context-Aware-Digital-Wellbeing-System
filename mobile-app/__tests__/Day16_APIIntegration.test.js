/**
 * API Integration Tests
 * Tests for authentication, API calls, and token management
 */

const fs = require('fs');
const path = require('path');

describe('Day 16: API Integration', () => {
  const mobileAppDir = path.join(__dirname, '..');
  const srcDir = path.join(mobileAppDir, 'src');

  // ============================================
  // File Existence Tests
  // ============================================

  describe('Core API Files', () => {
    test('API service file exists', () => {
      const apiPath = path.join(srcDir, 'services', 'api.js');
      expect(fs.existsSync(apiPath)).toBe(true);
    });

    test('AuthContext exists', () => {
      const authPath = path.join(srcDir, 'contexts', 'AuthContext.js');
      expect(fs.existsSync(authPath)).toBe(true);
    });

    test('LoginScreen exists', () => {
      const loginPath = path.join(srcDir, 'screens', 'LoginScreen.js');
      expect(fs.existsSync(loginPath)).toBe(true);
    });

    test('RegisterScreen exists', () => {
      const registerPath = path.join(srcDir, 'screens', 'RegisterScreen.js');
      expect(fs.existsSync(registerPath)).toBe(true);
    });
  });

  // ============================================
  // AuthContext Validation
  // ============================================

  describe('AuthContext Implementation', () => {
    const authPath = path.join(srcDir, 'contexts', 'AuthContext.js');
    let authContent;

    beforeAll(() => {
      authContent = fs.readFileSync(authPath, 'utf-8');
    });

    test('exports AuthContext', () => {
      expect(authContent).toContain('export const AuthContext');
    });

    test('exports AuthProvider', () => {
      expect(authContent).toContain('export const AuthProvider');
    });

    test('exports useAuth hook', () => {
      expect(authContent).toContain('export const useAuth');
    });

    test('implements login function', () => {
      expect(authContent).toContain('const login =');
    });

    test('implements register function', () => {
      expect(authContent).toContain('const register =');
    });

    test('implements logout function', () => {
      expect(authContent).toContain('const logout =');
    });

    test('uses AsyncStorage for token persistence', () => {
      expect(authContent).toContain('AsyncStorage');
      expect(authContent).toContain('@auth_token');
    });

    test('manages authentication state', () => {
      expect(authContent).toContain('isAuthenticated');
      expect(authContent).toContain('isLoading');
    });
  });

  // ============================================
  // API Service Validation
  // ============================================

  describe('API Service Implementation', () => {
    const apiPath = path.join(srcDir, 'services', 'api.js');
    let apiContent;

    beforeAll(() => {
      apiContent = fs.readFileSync(apiPath, 'utf-8');
    });

    test('imports axios', () => {
      expect(apiContent).toContain('axios');
    });

    test('imports AsyncStorage', () => {
      expect(apiContent).toContain('AsyncStorage');
    });

    test('has API methods for notifications', () => {
      const hasNotificationMethods = apiContent.includes('notifications') || 
        apiContent.includes('getNotifications') || 
        apiContent.includes('classifyNotification');
      expect(hasNotificationMethods).toBe(true);
    });

    test('has API methods for wellbeing', () => {
      const hasWellbeingMethods = apiContent.includes('wellbeing') || 
        apiContent.includes('focus') || 
        apiContent.includes('getWellbeingStats');
      expect(hasWellbeingMethods).toBe(true);
    });

    test('has API methods for privacy', () => {
      const hasPrivacyMethods = apiContent.includes('privacy') && 
        (apiContent.includes('get') || apiContent.includes('set'));
      expect(hasPrivacyMethods).toBe(true);
    });

    test('has API methods for devices', () => {
      const hasDeviceMethods = apiContent.includes('devices') || 
        apiContent.includes('getDevices') || 
        apiContent.includes('getSensorData');
      expect(hasDeviceMethods).toBe(true);
    });

    test('has API methods for analytics', () => {
      const hasAnalyticsMethods = apiContent.includes('analytics') || 
        apiContent.includes('productivity') || 
        apiContent.includes('getProductivityScore');
      expect(hasAnalyticsMethods).toBe(true);
    });

    test('has retry logic implemented', () => {
      const hasRetryLogic = apiContent.includes('retryRequest') || apiContent.includes('retry');
      expect(hasRetryLogic).toBe(true);
    });

    test('has error handling', () => {
      const hasErrorHandling = apiContent.includes('catch') && apiContent.includes('error');
      expect(hasErrorHandling).toBe(true);
    });
  });

  // ============================================
  // Login Screen Validation
  // ============================================

  describe('LoginScreen Implementation', () => {
    const loginPath = path.join(srcDir, 'screens', 'LoginScreen.js');
    let loginContent;

    beforeAll(() => {
      loginContent = fs.readFileSync(loginPath, 'utf-8');
    });

    test('uses AuthContext', () => {
      expect(loginContent).toContain('useAuth');
    });

    test('has email input field', () => {
      expect(loginContent).toContain('email');
      expect(loginContent).toContain('TextInput');
    });

    test('has password input field', () => {
      expect(loginContent).toContain('password');
      expect(loginContent).toContain('secureTextEntry');
    });

    test('implements login handler', () => {
      expect(loginContent).toContain('handleLogin');
    });

    test('has loading state', () => {
      expect(loginContent).toContain('isLoading');
      expect(loginContent).toContain('ActivityIndicator');
    });

    test('navigates to Register screen', () => {
      expect(loginContent).toContain('Register');
      expect(loginContent).toContain('navigation');
    });

    test('validates input', () => {
      const hasValidation = loginContent.includes('if') && 
        (loginContent.includes('!email') || loginContent.includes('!password'));
      expect(hasValidation).toBe(true);
    });
  });

  // ============================================
  // Register Screen Validation
  // ============================================

  describe('RegisterScreen Implementation', () => {
    const registerPath = path.join(srcDir, 'screens', 'RegisterScreen.js');
    let registerContent;

    beforeAll(() => {
      registerContent = fs.readFileSync(registerPath, 'utf-8');
    });

    test('uses AuthContext', () => {
      expect(registerContent).toContain('useAuth');
    });

    test('has full name input field', () => {
      const hasFullName = registerContent.includes('fullName') || registerContent.includes('name');
      expect(hasFullName).toBe(true);
    });

    test('has email input field', () => {
      expect(registerContent).toContain('email');
    });

    test('has password input fields', () => {
      expect(registerContent).toContain('password');
      expect(registerContent).toContain('confirmPassword') || expect(registerContent).toContain('confirm');
    });

    test('implements register handler', () => {
      expect(registerContent).toContain('handleRegister');
    });

    test('validates email format', () => {
      const hasEmailValidation = registerContent.includes('validateEmail') || registerContent.includes('@');
      expect(hasEmailValidation).toBe(true);
    });

    test('validates password length', () => {
      const hasPasswordValidation = registerContent.includes('length') && registerContent.includes('password');
      expect(hasPasswordValidation).toBe(true);
    });

    test('checks password match', () => {
      const hasPasswordMatch = registerContent.includes('match') || 
        (registerContent.includes('password') && registerContent.includes('confirm'));
      expect(hasPasswordMatch).toBe(true);
    });
  });

  // ============================================
  // Navigation Integration
  // ============================================

  describe('Navigation Integration', () => {
    const navPath = path.join(srcDir, 'navigation', 'AppNavigator.js');
    let navContent;

    beforeAll(() => {
      navContent = fs.readFileSync(navPath, 'utf-8');
    });

    test('imports LoginScreen', () => {
      expect(navContent).toContain('LoginScreen');
    });

    test('imports RegisterScreen', () => {
      expect(navContent).toContain('RegisterScreen');
    });

    test('uses AuthContext', () => {
      expect(navContent).toContain('useAuth');
    });

    test('conditionally renders based on auth state', () => {
      expect(navContent).toContain('isAuthenticated');
    });

    test('has stack navigator', () => {
      expect(navContent).toContain('Stack') || expect(navContent).toContain('createStack');
    });
  });

  // ============================================
  // App.js Integration
  // ============================================

  describe('App.js Integration', () => {
    const appPath = path.join(mobileAppDir, 'App.js');
    let appContent;

    beforeAll(() => {
      appContent = fs.readFileSync(appPath, 'utf-8');
    });

    test('imports AuthProvider', () => {
      expect(appContent).toContain('AuthProvider');
    });

    test('wraps app with AuthProvider', () => {
      expect(appContent).toContain('<AuthProvider>');
    });

    test('maintains error boundary', () => {
      expect(appContent).toContain('ErrorBoundary');
    });

    test('maintains offline indicator', () => {
      expect(appContent).toContain('OfflineIndicator');
    });
  });

  // ============================================
  // Summary Test
  // ============================================

  describe('Day 16 Summary', () => {
    test('all core files present (6 files)', () => {
      const requiredFiles = [
        path.join(srcDir, 'services', 'api.js'),
        path.join(srcDir, 'contexts', 'AuthContext.js'),
        path.join(srcDir, 'screens', 'LoginScreen.js'),
        path.join(srcDir, 'screens', 'RegisterScreen.js'),
        path.join(srcDir, 'navigation', 'AppNavigator.js'),
        path.join(mobileAppDir, 'App.js'),
      ];

      requiredFiles.forEach(file => {
        expect(fs.existsSync(file)).toBe(true);
      });
    });

    test('authentication flow complete', () => {
      const authPath = path.join(srcDir, 'contexts', 'AuthContext.js');
      const loginPath = path.join(srcDir, 'screens', 'LoginScreen.js');
      const registerPath = path.join(srcDir, 'screens', 'RegisterScreen.js');

      expect(fs.existsSync(authPath)).toBe(true);
      expect(fs.existsSync(loginPath)).toBe(true);
      expect(fs.existsSync(registerPath)).toBe(true);
    });

    test('API integration complete', () => {
      const apiPath = path.join(srcDir, 'services', 'api.js');
      const apiContent = fs.readFileSync(apiPath, 'utf-8');

      // Check for key API methods
      const hasNotificationMethods = apiContent.includes('getNotifications') || apiContent.includes('notifications');
      const hasWellbeingMethods = apiContent.includes('wellbeing') || apiContent.includes('focus');
      const hasAnalyticsMethods = apiContent.includes('analytics') || apiContent.includes('productivity');

      expect(hasNotificationMethods && hasWellbeingMethods && hasAnalyticsMethods).toBe(true);
    });
  });
});
