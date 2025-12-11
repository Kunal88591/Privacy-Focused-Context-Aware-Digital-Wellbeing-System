/**
 * Home Screen Tests
 * Tests for the main dashboard screen
 */

import React from 'react';
import { render, waitFor, fireEvent } from '@testing-library/react-native';
import HomeScreen from '../src/screens/HomeScreen';
import { wellbeingAPI, privacyAPI } from '../src/services/api';
import mqttService from '../src/services/mqtt';

// Mock dependencies
jest.mock('../src/services/api');
jest.mock('../src/services/mqtt');

const mockNavigation = {
  navigate: jest.fn(),
};

describe('HomeScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    wellbeingAPI.getStats.mockResolvedValue({
      total_notifications: 45,
      suppressed_count: 12,
      suppression_rate: 26.7,
      screen_time_hours: 3.5,
      focus_time_hours: 1.2,
    });

    wellbeingAPI.getFocusStatus.mockResolvedValue({
      active: false,
      start_time: null,
    });

    privacyAPI.getStatus.mockResolvedValue({
      data_encrypted: true,
      local_processing: true,
      tracking_blocked: true,
    });

    mqttService.connect.mockResolvedValue(true);
    mqttService.addListener = jest.fn();
    mqttService.removeListener = jest.fn();
  });

  it('should render loading state initially', () => {
    const { getByTestId } = render(
      <HomeScreen navigation={mockNavigation} />
    );
    
    expect(getByTestId('dashboard-skeleton')).toBeTruthy();
  });

  it('should load dashboard data on mount', async () => {
    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(wellbeingAPI.getStats).toHaveBeenCalledWith('today');
      expect(privacyAPI.getStatus).toHaveBeenCalled();
      expect(wellbeingAPI.getFocusStatus).toHaveBeenCalled();
    });
  });

  it('should connect to MQTT on mount', async () => {
    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(mqttService.connect).toHaveBeenCalled();
    });
  });

  it('should set up MQTT listeners after connection', async () => {
    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(mqttService.addListener).toHaveBeenCalledWith(
        'sensors/environment',
        expect.any(Function)
      );
      expect(mqttService.addListener).toHaveBeenCalledWith(
        'sensors/motion',
        expect.any(Function)
      );
      expect(mqttService.addListener).toHaveBeenCalledWith(
        'sensors/light',
        expect.any(Function)
      );
      expect(mqttService.addListener).toHaveBeenCalledWith(
        'sensors/noise',
        expect.any(Function)
      );
    });
  });

  it('should display wellbeing stats after loading', async () => {
    const { getByText } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('45')).toBeTruthy(); // Total notifications
      expect(getByText('12')).toBeTruthy(); // Suppressed
      expect(getByText('26.7%')).toBeTruthy(); // Suppression rate
    });
  });

  it('should display privacy status', async () => {
    const { getByText } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Privacy Shield Active')).toBeTruthy();
    });
  });

  it('should handle refresh', async () => {
    const { getByTestId } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(wellbeingAPI.getStats).toHaveBeenCalled();
    });

    jest.clearAllMocks();
    
    const scrollView = getByTestId('home-scroll-view');
    fireEvent(scrollView, 'refresh');

    await waitFor(() => {
      expect(wellbeingAPI.getStats).toHaveBeenCalledWith('today');
    });
  });

  it('should handle API errors gracefully', async () => {
    wellbeingAPI.getStats.mockRejectedValue(new Error('Network error'));

    const { getByTestId } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('error-message')).toBeTruthy();
    });
  });

  it('should cleanup MQTT listeners on unmount', () => {
    const { unmount } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    unmount();

    expect(mqttService.removeListener).toHaveBeenCalledWith(
      'sensors/environment',
      expect.any(Function)
    );
  });

  it('should toggle focus mode', async () => {
    wellbeingAPI.toggleFocusMode = jest.fn().mockResolvedValue({
      active: true,
      start_time: new Date().toISOString(),
    });

    const { getByTestId } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('focus-toggle-button')).toBeTruthy();
    });

    fireEvent.press(getByTestId('focus-toggle-button'));

    await waitFor(() => {
      expect(wellbeingAPI.toggleFocusMode).toHaveBeenCalled();
    });
  });

  it('should show MQTT connection status', async () => {
    const { getByTestId } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('mqtt-status-indicator')).toBeTruthy();
    });
  });

  it('should update sensor data from MQTT', async () => {
    const { getByText } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(mqttService.addListener).toHaveBeenCalled();
    });

    // Simulate sensor data updates
    const environmentHandler = mqttService.addListener.mock.calls.find(
      call => call[0] === 'sensors/environment'
    )[1];

    environmentHandler({ temperature: 22.5, humidity: 45 });

    await waitFor(() => {
      expect(getByText('22.5°C')).toBeTruthy();
      expect(getByText('45%')).toBeTruthy();
    });
  });

  it('should navigate to notifications screen', async () => {
    const { getByTestId } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('view-notifications-button')).toBeTruthy();
    });

    fireEvent.press(getByTestId('view-notifications-button'));

    expect(mockNavigation.navigate).toHaveBeenCalledWith('Notifications');
  });

  it('should display screen time summary', async () => {
    const { getByText } = render(
      <HomeScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('3.5h')).toBeTruthy(); // Screen time
      expect(getByText('1.2h')).toBeTruthy(); // Focus time
    });
  });
});

describe('HomeScreen Sensor Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    wellbeingAPI.getStats.mockResolvedValue({});
    wellbeingAPI.getFocusStatus.mockResolvedValue({ active: false });
    privacyAPI.getStatus.mockResolvedValue({});
    mqttService.connect.mockResolvedValue(true);
    mqttService.addListener = jest.fn();
  });

  it('should handle environment data updates', async () => {
    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(mqttService.addListener).toHaveBeenCalled();
    });

    const handler = mqttService.addListener.mock.calls[0][1];
    handler({ temperature: 25, humidity: 50 });
  });

  it('should handle motion detection', async () => {
    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(mqttService.addListener).toHaveBeenCalled();
    });

    const motionHandler = mqttService.addListener.mock.calls.find(
      call => call[0] === 'sensors/motion'
    )[1];

    motionHandler({ motion_detected: true });
  });

  it('should handle light level updates', async () => {
    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(mqttService.addListener).toHaveBeenCalled();
    });

    const lightHandler = mqttService.addListener.mock.calls.find(
      call => call[0] === 'sensors/light'
    )[1];

    lightHandler({ lux: 450 });
  });

  it('should handle noise level updates', async () => {
    render(<HomeScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(mqttService.addListener).toHaveBeenCalled();
    });

    const noiseHandler = mqttService.addListener.mock.calls.find(
      call => call[0] === 'sensors/noise'
    )[1];

    noiseHandler({ noise_level: 55 });
  });
});
