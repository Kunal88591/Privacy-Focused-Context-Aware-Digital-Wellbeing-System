/**
 * Notifications Screen Tests
 * Tests for notification list and filtering
 */

import React from 'react';
import { render, waitFor, fireEvent } from '@testing-library/react-native';
import NotificationsScreen from '../src/screens/NotificationsScreen';
import { notificationAPI } from '../src/services/api';

jest.mock('../src/services/api');

const mockNavigation = {
  navigate: jest.fn(),
};

describe('NotificationsScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    notificationAPI.getNotifications.mockResolvedValue({
      notifications: [
        {
          id: 1,
          app_name: 'WhatsApp',
          title: 'New Message',
          body: 'Hello there!',
          timestamp: new Date().toISOString(),
          category: 'messaging',
          priority: 'high',
          suppressed: false,
        },
        {
          id: 2,
          app_name: 'Instagram',
          title: 'New Like',
          body: 'Someone liked your photo',
          timestamp: new Date().toISOString(),
          category: 'social',
          priority: 'low',
          suppressed: true,
        },
      ],
      total: 2,
    });
  });

  it('should render loading state initially', () => {
    const { getByTestId } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    expect(getByTestId('notifications-loading')).toBeTruthy();
  });

  it('should load notifications on mount', async () => {
    render(<NotificationsScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(notificationAPI.getNotifications).toHaveBeenCalled();
    });
  });

  it('should display notification list', async () => {
    const { getByText } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('New Message')).toBeTruthy();
      expect(getByText('New Like')).toBeTruthy();
    });
  });

  it('should show notification count', async () => {
    const { getByText } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('2 Notifications')).toBeTruthy();
    });
  });

  it('should filter notifications by category', async () => {
    const { getByTestId } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('filter-messaging')).toBeTruthy();
    });

    fireEvent.press(getByTestId('filter-messaging'));

    await waitFor(() => {
      expect(notificationAPI.getNotifications).toHaveBeenCalledWith({
        category: 'messaging',
      });
    });
  });

  it('should show suppressed notifications separately', async () => {
    const { getByText } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Suppressed')).toBeTruthy();
    });
  });

  it('should handle refresh', async () => {
    const { getByTestId } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(notificationAPI.getNotifications).toHaveBeenCalled();
    });

    jest.clearAllMocks();

    fireEvent(getByTestId('notifications-list'), 'refresh');

    await waitFor(() => {
      expect(notificationAPI.getNotifications).toHaveBeenCalled();
    });
  });

  it('should handle empty notification list', async () => {
    notificationAPI.getNotifications.mockResolvedValue({
      notifications: [],
      total: 0,
    });

    const { getByText } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('No notifications')).toBeTruthy();
    });
  });

  it('should handle API errors', async () => {
    notificationAPI.getNotifications.mockRejectedValue(
      new Error('Network error')
    );

    const { getByTestId } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('error-message')).toBeTruthy();
    });
  });

  it('should display notification timestamps', async () => {
    const { getByText } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText(/ago/)).toBeTruthy();
    });
  });

  it('should group notifications by app', async () => {
    const { getByText } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('WhatsApp')).toBeTruthy();
      expect(getByText('Instagram')).toBeTruthy();
    });
  });
});

describe('NotificationsScreen Filtering', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    notificationAPI.getNotifications.mockResolvedValue({
      notifications: [],
      total: 0,
    });
  });

  it('should filter by priority', async () => {
    const { getByTestId } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('filter-high-priority')).toBeTruthy();
    });

    fireEvent.press(getByTestId('filter-high-priority'));

    await waitFor(() => {
      expect(notificationAPI.getNotifications).toHaveBeenCalledWith({
        priority: 'high',
      });
    });
  });

  it('should filter by date range', async () => {
    const { getByTestId } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('filter-today')).toBeTruthy();
    });

    fireEvent.press(getByTestId('filter-today'));

    await waitFor(() => {
      expect(notificationAPI.getNotifications).toHaveBeenCalledWith({
        date: 'today',
      });
    });
  });

  it('should clear filters', async () => {
    const { getByTestId } = render(
      <NotificationsScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('clear-filters')).toBeTruthy();
    });

    fireEvent.press(getByTestId('clear-filters'));

    await waitFor(() => {
      expect(notificationAPI.getNotifications).toHaveBeenCalledWith({});
    });
  });
});
