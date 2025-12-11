/**
 * Day 15: UI Foundation Tests
 * Simple validation tests for screen and navigation structure
 */

const fs = require('fs');
const path = require('path');

describe('Day 15: UI Foundation - File Structure', () => {
  const screensDir = path.join(__dirname, '../src/screens');
  const navigationDir = path.join(__dirname, '../src/navigation');

  test('HomeScreen.js exists', () => {
    const filePath = path.join(screensDir, 'HomeScreen.js');
    expect(fs.existsSync(filePath)).toBe(true);
  });

  test('NotificationsScreen.js exists', () => {
    const filePath = path.join(screensDir, 'NotificationsScreen.js');
    expect(fs.existsSync(filePath)).toBe(true);
  });

  test('PrivacyScreen.js exists', () => {
    const filePath = path.join(screensDir, 'PrivacyScreen.js');
    expect(fs.existsSync(filePath)).toBe(true);
  });

  test('SettingsScreen.js exists', () => {
    const filePath = path.join(screensDir, 'SettingsScreen.js');
    expect(fs.existsSync(filePath)).toBe(true);
  });

  test('AnalyticsScreen.js exists', () => {
    const filePath = path.join(screensDir, 'AnalyticsScreen.js');
    expect(fs.existsSync(filePath)).toBe(true);
  });

  test('GoalsScreen.js exists', () => {
    const filePath = path.join(screensDir, 'GoalsScreen.js');
    expect(fs.existsSync(filePath)).toBe(true);
  });

  test('AppNavigator.js exists', () => {
    const filePath = path.join(navigationDir, 'AppNavigator.js');
    expect(fs.existsSync(filePath)).toBe(true);
  });
});

describe('Day 15: UI Foundation - Screen Content', () => {
  test('HomeScreen contains dashboard components', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/screens/HomeScreen.js'),
      'utf8'
    );
    expect(content).toContain('HomeScreen');
    expect(content).toContain('useState');
    expect(content).toContain('useEffect');
    expect(content).toContain('export default');
  });

  test('NotificationsScreen contains notification logic', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/screens/NotificationsScreen.js'),
      'utf8'
    );
    expect(content).toContain('NotificationsScreen');
    expect(content).toContain('export default');
  });

  test('PrivacyScreen contains privacy controls', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/screens/PrivacyScreen.js'),
      'utf8'
    );
    expect(content).toContain('PrivacyScreen');
    expect(content).toContain('export default');
  });

  test('SettingsScreen contains settings options', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/screens/SettingsScreen.js'),
      'utf8'
    );
    expect(content).toContain('SettingsScreen');
    expect(content).toContain('export default');
  });
});

describe('Day 15: Navigation Structure', () => {
  test('AppNavigator uses React Navigation', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/navigation/AppNavigator.js'),
      'utf8'
    );
    expect(content).toContain('@react-navigation');
    expect(content).toContain('NavigationContainer');
    expect(content).toContain('createBottomTabNavigator');
  });

  test('AppNavigator registers all screens', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/navigation/AppNavigator.js'),
      'utf8'
    );
    expect(content).toContain('HomeScreen');
    expect(content).toContain('NotificationsScreen');
    expect(content).toContain('PrivacyScreen');
    expect(content).toContain('SettingsScreen');
    expect(content).toContain('AnalyticsScreen');
    expect(content).toContain('GoalsScreen');
  });

  test('AppNavigator uses bottom tab navigation', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/navigation/AppNavigator.js'),
      'utf8'
    );
    expect(content).toContain('Tab.Navigator');
    expect(content).toContain('Tab.Screen');
  });

  test('AppNavigator exports properly', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../src/navigation/AppNavigator.js'),
      'utf8'
    );
    expect(content).toContain('export default');
  });
});

describe('Day 15: UI Foundation - Screen Exports', () => {
  test('All screens are properly exported', () => {
    const screens = [
      'HomeScreen.js',
      'NotificationsScreen.js',
      'PrivacyScreen.js',
      'SettingsScreen.js',
      'AnalyticsScreen.js',
      'GoalsScreen.js',
    ];

    screens.forEach((screen) => {
      const content = fs.readFileSync(
        path.join(__dirname, '../src/screens', screen),
        'utf8'
      );
      expect(content).toMatch(/export default/);
    });
  });
});

describe('Day 15: App Entry Point', () => {
  test('App.js uses AppNavigator', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../App.js'),
      'utf8'
    );
    expect(content).toContain('AppNavigator');
    expect(content).toContain('export default');
  });

  test('App.js has error boundary', () => {
    const content = fs.readFileSync(
      path.join(__dirname, '../App.js'),
      'utf8'
    );
    expect(content).toContain('ErrorBoundary');
  });
});
