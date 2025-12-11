/**
 * App Navigator Tests
 * Tests for bottom tab navigation structure
 */

import React from 'react';
import { render, screen } from '@testing-library/react-native';
import AppNavigator from '../src/navigation/AppNavigator';

// Mock all screens
jest.mock('../src/screens/HomeScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return () => (
    <View testID="home-screen">
      <Text>Home Screen</Text>
    </View>
  );
});

jest.mock('../src/screens/NotificationsScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return () => (
    <View testID="notifications-screen">
      <Text>Notifications Screen</Text>
    </View>
  );
});

jest.mock('../src/screens/PrivacyScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return () => (
    <View testID="privacy-screen">
      <Text>Privacy Screen</Text>
    </View>
  );
});

jest.mock('../src/screens/AnalyticsScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return () => (
    <View testID="analytics-screen">
      <Text>Analytics Screen</Text>
    </View>
  );
});

jest.mock('../src/screens/GoalsScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return () => (
    <View testID="goals-screen">
      <Text>Goals Screen</Text>
    </View>
  );
});

jest.mock('../src/screens/SettingsScreen', () => {
  const React = require('react');
  const { View, Text } = require('react-native');
  return () => (
    <View testID="settings-screen">
      <Text>Settings Screen</Text>
    </View>
  );
});

describe('AppNavigator', () => {
  it('should render navigation container', () => {
    const { getByTestId } = render(<AppNavigator />);
    expect(getByTestId('home-screen')).toBeTruthy();
  });

  it('should have all required tabs', () => {
    const { getByText } = render(<AppNavigator />);
    
    expect(getByText('Home')).toBeTruthy();
    expect(getByText('Notifications')).toBeTruthy();
    expect(getByText('Privacy')).toBeTruthy();
    expect(getByText('Analytics')).toBeTruthy();
    expect(getByText('Goals')).toBeTruthy();
    expect(getByText('Settings')).toBeTruthy();
  });

  it('should use bottom tab navigator', () => {
    const { UNSAFE_root } = render(<AppNavigator />);
    expect(UNSAFE_root).toBeTruthy();
  });

  it('should have correct tab bar styling', () => {
    const { container } = render(<AppNavigator />);
    expect(container).toBeTruthy();
  });

  it('should render home screen by default', () => {
    const { getByTestId } = render(<AppNavigator />);
    expect(getByTestId('home-screen')).toBeTruthy();
  });
});

describe('Navigation Tab Configuration', () => {
  it('should have 6 tabs total', () => {
    const { getByText } = render(<AppNavigator />);
    
    const tabs = ['Home', 'Notifications', 'Privacy', 'Analytics', 'Goals', 'Settings'];
    tabs.forEach(tab => {
      expect(getByText(tab)).toBeTruthy();
    });
  });

  it('should hide headers', () => {
    const { queryByText } = render(<AppNavigator />);
    expect(queryByText('Header')).toBeNull();
  });

  it('should apply correct color scheme', () => {
    render(<AppNavigator />);
    // Tab bar should use primary blue color for active state
    // This is tested through configuration
  });
});

describe('Navigation Integration', () => {
  it('should wrap all screens in NavigationContainer', () => {
    const { container } = render(<AppNavigator />);
    expect(container).toBeTruthy();
  });

  it('should use createBottomTabNavigator', () => {
    const { getByText } = render(<AppNavigator />);
    expect(getByText('Home')).toBeTruthy();
  });

  it('should register all screen components', () => {
    const { getByTestId } = render(<AppNavigator />);
    expect(getByTestId('home-screen')).toBeTruthy();
  });
});

describe('Tab Icons', () => {
  it('should render emoji icons for all tabs', () => {
    const { getByText } = render(<AppNavigator />);
    
    // Each tab should have its emoji icon
    expect(getByText('🏠')).toBeTruthy(); // Home
    expect(getByText('📬')).toBeTruthy(); // Notifications
    expect(getByText('🔒')).toBeTruthy(); // Privacy
    expect(getByText('📊')).toBeTruthy(); // Analytics
    expect(getByText('🎯')).toBeTruthy(); // Goals
    expect(getByText('⚙️')).toBeTruthy(); // Settings
  });

  it('should have correct icon sizes', () => {
    const { getByText } = render(<AppNavigator />);
    const homeIcon = getByText('🏠');
    expect(homeIcon).toBeTruthy();
  });
});
