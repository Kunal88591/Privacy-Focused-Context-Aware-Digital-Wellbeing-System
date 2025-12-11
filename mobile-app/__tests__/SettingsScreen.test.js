/**
 * Settings Screen Tests
 * Tests for app configuration and preferences
 */

import React from 'react';
import { render, waitFor, fireEvent } from '@testing-library/react-native';
import SettingsScreen from '../src/screens/SettingsScreen';
import { settingsAPI } from '../src/services/api';

jest.mock('../src/services/api');

const mockNavigation = {
  navigate: jest.fn(),
};

describe('SettingsScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    settingsAPI.getSettings.mockResolvedValue({
      notifications_enabled: true,
      focus_mode_enabled: true,
      dark_mode: false,
      language: 'en',
      sync_interval: 15,
      battery_optimization: true,
    });
  });

  it('should render loading state initially', () => {
    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    expect(getByTestId('settings-loading')).toBeTruthy();
  });

  it('should load settings on mount', async () => {
    render(<SettingsScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(settingsAPI.getSettings).toHaveBeenCalled();
    });
  });

  it('should display notification settings', async () => {
    const { getByText } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Notifications')).toBeTruthy();
    });
  });

  it('should toggle notifications', async () => {
    settingsAPI.updateSetting.mockResolvedValue({
      notifications_enabled: false,
    });

    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('notifications-toggle')).toBeTruthy();
    });

    fireEvent(getByTestId('notifications-toggle'), 'onValueChange', false);

    await waitFor(() => {
      expect(settingsAPI.updateSetting).toHaveBeenCalledWith(
        'notifications_enabled',
        false
      );
    });
  });

  it('should toggle dark mode', async () => {
    settingsAPI.updateSetting.mockResolvedValue({ dark_mode: true });

    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('dark-mode-toggle')).toBeTruthy();
    });

    fireEvent(getByTestId('dark-mode-toggle'), 'onValueChange', true);

    await waitFor(() => {
      expect(settingsAPI.updateSetting).toHaveBeenCalledWith('dark_mode', true);
    });
  });

  it('should change sync interval', async () => {
    settingsAPI.updateSetting.mockResolvedValue({ sync_interval: 30 });

    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('sync-interval-picker')).toBeTruthy();
    });

    fireEvent(getByTestId('sync-interval-picker'), 'onValueChange', '30');

    await waitFor(() => {
      expect(settingsAPI.updateSetting).toHaveBeenCalledWith('sync_interval', 30);
    });
  });

  it('should change language', async () => {
    settingsAPI.updateSetting.mockResolvedValue({ language: 'es' });

    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('language-picker')).toBeTruthy();
    });

    fireEvent(getByTestId('language-picker'), 'onValueChange', 'es');

    await waitFor(() => {
      expect(settingsAPI.updateSetting).toHaveBeenCalledWith('language', 'es');
    });
  });

  it('should toggle battery optimization', async () => {
    settingsAPI.updateSetting.mockResolvedValue({
      battery_optimization: false,
    });

    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('battery-optimization-toggle')).toBeTruthy();
    });

    fireEvent(getByTestId('battery-optimization-toggle'), 'onValueChange', false);

    await waitFor(() => {
      expect(settingsAPI.updateSetting).toHaveBeenCalledWith(
        'battery_optimization',
        false
      );
    });
  });

  it('should handle API errors', async () => {
    settingsAPI.getSettings.mockRejectedValue(new Error('Network error'));

    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('error-message')).toBeTruthy();
    });
  });

  it('should display app version', async () => {
    const { getByText } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText(/Version/)).toBeTruthy();
    });
  });

  it('should navigate to about screen', async () => {
    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('about-button')).toBeTruthy();
    });

    fireEvent.press(getByTestId('about-button'));

    expect(mockNavigation.navigate).toHaveBeenCalledWith('About');
  });

  it('should reset settings to defaults', async () => {
    settingsAPI.resetSettings.mockResolvedValue({ success: true });

    const { getByTestId } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('reset-button')).toBeTruthy();
    });

    fireEvent.press(getByTestId('reset-button'));

    await waitFor(() => {
      expect(settingsAPI.resetSettings).toHaveBeenCalled();
    });
  });

  it('should show focus mode settings', async () => {
    const { getByText } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Focus Mode')).toBeTruthy();
    });
  });
});

describe('SettingsScreen Sections', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    settingsAPI.getSettings.mockResolvedValue({});
  });

  it('should display general settings section', async () => {
    const { getByText } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('General')).toBeTruthy();
    });
  });

  it('should display privacy settings section', async () => {
    const { getByText } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Privacy')).toBeTruthy();
    });
  });

  it('should display data settings section', async () => {
    const { getByText } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Data & Sync')).toBeTruthy();
    });
  });

  it('should display about section', async () => {
    const { getByText } = render(
      <SettingsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('About')).toBeTruthy();
    });
  });
});
