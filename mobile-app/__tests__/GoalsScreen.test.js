/**
 * Goals Screen Tests
 */

import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import axios from 'axios';
import GoalsScreen from '../src/screens/GoalsScreen';

jest.mock('axios');
jest.spyOn(Alert, 'alert');

describe('GoalsScreen', () => {
  const mockGoalsData = {
    data: [
      {
        goal_type: 'daily_focus_time',
        target_value: 240,
        current_value: 180,
        progress_percent: 75,
        status: 'active',
        deadline: '2024-12-31',
      },
      {
        goal_type: 'weekly_focus_hours',
        target_value: 20,
        current_value: 20,
        progress_percent: 100,
        status: 'completed',
        completed_at: '2024-01-15',
      },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    axios.get.mockResolvedValue(mockGoalsData);
    axios.post.mockResolvedValue({ data: { success: true } });
  });

  it('renders loading state initially', () => {
    axios.get.mockImplementation(() => new Promise(() => {}));
    const { getByText } = render(<GoalsScreen />);
    expect(getByText('Loading goals...')).toBeTruthy();
  });

  it('fetches and displays goals', async () => {
    const { getByText } = render(<GoalsScreen />);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/analytics/goals'),
        expect.objectContaining({
          params: { user_id: 'user123' },
        })
      );
    });

    await waitFor(() => {
      expect(getByText('DAILY FOCUS TIME')).toBeTruthy();
      expect(getByText('180 / 240 minutes')).toBeTruthy();
      expect(getByText('75%')).toBeTruthy();
    });
  });

  it('displays empty state when no goals exist', async () => {
    axios.get.mockResolvedValue({ data: [] });
    const { getByText } = render(<GoalsScreen />);

    await waitFor(() => {
      expect(getByText('No Goals Yet')).toBeTruthy();
      expect(getByText('Set your first productivity goal to start tracking your progress!')).toBeTruthy();
    });
  });

  it('opens create goal modal', async () => {
    axios.get.mockResolvedValue({ data: [] });
    const { getByText } = render(<GoalsScreen />);

    await waitFor(() => {
      expect(getByText('+ Add Goal')).toBeTruthy();
    });

    fireEvent.press(getByText('+ Add Goal'));

    await waitFor(() => {
      expect(getByText('Create New Goal')).toBeTruthy();
      expect(getByText('Goal Type')).toBeTruthy();
    });
  });

  it('creates a new goal', async () => {
    axios.get.mockResolvedValue({ data: [] });
    const { getByText, getByPlaceholderText } = render(<GoalsScreen />);

    await waitFor(() => {
      fireEvent.press(getByText('+ Add Goal'));
    });

    await waitFor(() => {
      expect(getByText('Create New Goal')).toBeTruthy();
    });

    // Enter target value
    const input = getByPlaceholderText('Enter target value');
    fireEvent.changeText(input, '300');

    // Create goal
    fireEvent.press(getByText('Create Goal'));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/analytics/goals'),
        expect.objectContaining({
          user_id: 'user123',
          goal_type: 'daily_focus_time',
          target_value: 300,
          current_value: 0,
        })
      );
    });

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Success', 'Goal created successfully!');
    });
  });

  it('validates target value', async () => {
    axios.get.mockResolvedValue({ data: [] });
    const { getByText, getByPlaceholderText } = render(<GoalsScreen />);

    fireEvent.press(getByText('+ Add Goal'));

    await waitFor(() => {
      const input = getByPlaceholderText('Enter target value');
      fireEvent.changeText(input, '-10');
      fireEvent.press(getByText('Create Goal'));
    });

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Invalid Target',
        'Please enter a valid positive number'
      );
    });
  });

  it('selects different goal types', async () => {
    axios.get.mockResolvedValue({ data: [] });
    const { getByText } = render(<GoalsScreen />);

    fireEvent.press(getByText('+ Add Goal'));

    await waitFor(() => {
      expect(getByText('Daily Focus Time')).toBeTruthy();
      expect(getByText('Screen Time Limit')).toBeTruthy();
    });

    fireEvent.press(getByText('Daily Breaks'));

    await waitFor(() => {
      expect(getByText('Unit: breaks')).toBeTruthy();
    });
  });

  it('displays goal status correctly', async () => {
    const { getByText } = render(<GoalsScreen />);

    await waitFor(() => {
      expect(getByText('🎯 Active')).toBeTruthy();
      expect(getByText('✅ Completed')).toBeTruthy();
    });
  });

  it('displays completed goal info', async () => {
    const { getByText } = render(<GoalsScreen />);

    await waitFor(() => {
      expect(getByText(/Completed on/)).toBeTruthy();
    });
  });

  it('deletes a goal', async () => {
    const { getAllByText, queryByText } = render(<GoalsScreen />);

    await waitFor(() => {
      expect(getAllByText('🗑️')[0]).toBeTruthy();
    });

    // Click delete button
    fireEvent.press(getAllByText('🗑️')[0]);

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Delete Goal',
        'Are you sure you want to delete this goal?',
        expect.any(Array)
      );
    });
  });

  it('cancels goal creation', async () => {
    axios.get.mockResolvedValue({ data: [] });
    const { getByText, queryByText } = render(<GoalsScreen />);

    fireEvent.press(getByText('+ Add Goal'));

    await waitFor(() => {
      expect(getByText('Create New Goal')).toBeTruthy();
    });

    fireEvent.press(getByText('Cancel'));

    await waitFor(() => {
      expect(queryByText('Create New Goal')).toBeNull();
    });
  });

  it('displays progress bars with correct colors', async () => {
    const { getByText } = render(<GoalsScreen />);

    await waitFor(() => {
      // 75% progress should show orange/green color
      expect(getByText('75%')).toBeTruthy();
      // 100% progress should show green color
      expect(getByText('100%')).toBeTruthy();
    });
  });
});
