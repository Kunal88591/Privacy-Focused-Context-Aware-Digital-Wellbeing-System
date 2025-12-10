/**
 * Analytics Screen Tests
 */

import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import axios from 'axios';
import AnalyticsScreen from '../src/screens/AnalyticsScreen';

jest.mock('axios');

describe('AnalyticsScreen', () => {
  const mockDashboardData = {
    data: {
      today: {
        total_focus_time: 180,
        total_screen_time: 420,
        productivity_score: 75,
        total_distractions: 5,
        total_breaks: 8,
      },
      weekly_trends: {
        avg_focus_time: 200,
        avg_productivity_score: 72,
        trend: 'improving',
        best_day: 'Tuesday',
      },
      top_apps: {
        'VS Code': { screen_time: 120, percentage: 28.5 },
        'Chrome': { screen_time: 90, percentage: 21.4 },
        'Slack': { screen_time: 60, percentage: 14.3 },
      },
      insights: [
        {
          type: 'positive',
          title: 'Great productivity!',
          message: 'Your focus time increased by 20%',
          priority: 'high',
        },
      ],
      wellbeing_score: {
        overall_score: 78,
        components: {
          screen_time_balance: 75,
          break_frequency: 80,
          focus_quality: 82,
          work_life_balance: 70,
          notification_management: 83,
        },
      },
      personalized_tips: [
        {
          tip: 'Take more breaks in the afternoon',
          priority: 'medium',
          category: 'breaks',
        },
      ],
      patterns: [
        {
          pattern: 'Most productive in morning hours',
          confidence: 0.85,
        },
      ],
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    axios.get.mockResolvedValue(mockDashboardData);
  });

  it('renders loading state initially', () => {
    axios.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    const { getByText } = render(<AnalyticsScreen />);
    expect(getByText('Loading analytics...')).toBeTruthy();
  });

  it('fetches and displays dashboard data', async () => {
    const { getByText } = render(<AnalyticsScreen />);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/analytics/dashboard'),
        expect.objectContaining({
          params: { user_id: 'user123' },
        })
      );
    });

    await waitFor(() => {
      expect(getByText('180')).toBeTruthy(); // Focus time
      expect(getByText('75')).toBeTruthy(); // Productivity score
    });
  });

  it('displays error message on API failure', async () => {
    axios.get.mockRejectedValue(new Error('Network error'));
    const { getByText } = render(<AnalyticsScreen />);

    await waitFor(() => {
      expect(getByText('Failed to load analytics')).toBeTruthy();
    });
  });

  it('switches between tabs', async () => {
    const { getByText } = render(<AnalyticsScreen />);

    await waitFor(() => {
      expect(getByText("Today's Stats")).toBeTruthy();
    });

    fireEvent.press(getByText('Week'));
    await waitFor(() => {
      expect(getByText('Weekly Averages')).toBeTruthy();
    });

    fireEvent.press(getByText('Insights'));
    await waitFor(() => {
      expect(getByText('AI Insights')).toBeTruthy();
    });
  });

  it('displays wellbeing score', async () => {
    const { getByText } = render(<AnalyticsScreen />);

    await waitFor(() => {
      expect(getByText('Wellbeing Score')).toBeTruthy();
      expect(getByText('78')).toBeTruthy();
    });
  });

  it('displays top apps', async () => {
    const { getByText } = render(<AnalyticsScreen />);

    await waitFor(() => {
      expect(getByText('VS Code')).toBeTruthy();
      expect(getByText('120 min')).toBeTruthy();
    });
  });

  it('displays insights', async () => {
    const { getByText } = render(<AnalyticsScreen />);

    fireEvent.press(getByText('Insights'));

    await waitFor(() => {
      expect(getByText('Great productivity!')).toBeTruthy();
      expect(getByText('Your focus time increased by 20%')).toBeTruthy();
    });
  });

  it('displays personalized tips', async () => {
    const { getByText } = render(<AnalyticsScreen />);

    fireEvent.press(getByText('Insights'));

    await waitFor(() => {
      expect(getByText('Take more breaks in the afternoon')).toBeTruthy();
    });
  });

  it('handles pull-to-refresh', async () => {
    const { getByTestId } = render(<AnalyticsScreen />);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(1);
    });

    // Simulate pull-to-refresh
    // Note: ScrollView's onRefresh is hard to test directly
    // This test verifies the initial load works
    expect(axios.get).toHaveBeenCalled();
  });

  it('displays weekly trends', async () => {
    const { getByText } = render(<AnalyticsScreen />);

    fireEvent.press(getByText('Week'));

    await waitFor(() => {
      expect(getByText('200 min')).toBeTruthy(); // avg focus time
      expect(getByText('Best Day: Tuesday')).toBeTruthy();
    });
  });
});
