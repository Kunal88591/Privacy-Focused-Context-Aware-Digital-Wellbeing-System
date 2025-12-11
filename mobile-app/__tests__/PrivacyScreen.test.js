/**
 * Privacy Screen Tests
 * Tests for privacy controls and settings
 */

import React from 'react';
import { render, waitFor, fireEvent } from '@testing-library/react-native';
import PrivacyScreen from '../src/screens/PrivacyScreen';
import { privacyAPI } from '../src/services/api';

jest.mock('../src/services/api');

const mockNavigation = {
  navigate: jest.fn(),
};

describe('PrivacyScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    privacyAPI.getStatus.mockResolvedValue({
      data_encrypted: true,
      local_processing: true,
      tracking_blocked: true,
      data_retention_days: 30,
      auto_delete_enabled: true,
    });

    privacyAPI.getDataUsage.mockResolvedValue({
      local_storage_mb: 45.2,
      cloud_storage_mb: 0,
      total_events: 1250,
    });
  });

  it('should render loading state initially', () => {
    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    expect(getByTestId('privacy-loading')).toBeTruthy();
  });

  it('should load privacy status on mount', async () => {
    render(<PrivacyScreen navigation={mockNavigation} />);

    await waitFor(() => {
      expect(privacyAPI.getStatus).toHaveBeenCalled();
      expect(privacyAPI.getDataUsage).toHaveBeenCalled();
    });
  });

  it('should display privacy shield status', async () => {
    const { getByText } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Privacy Shield Active')).toBeTruthy();
    });
  });

  it('should show encryption status', async () => {
    const { getByText } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Data Encrypted')).toBeTruthy();
    });
  });

  it('should show local processing status', async () => {
    const { getByText } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Local Processing')).toBeTruthy();
    });
  });

  it('should display data usage stats', async () => {
    const { getByText } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('45.2 MB')).toBeTruthy();
      expect(getByText('1250 events')).toBeTruthy();
    });
  });

  it('should toggle data encryption', async () => {
    privacyAPI.updateSettings.mockResolvedValue({
      data_encrypted: false,
    });

    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('encryption-toggle')).toBeTruthy();
    });

    fireEvent(getByTestId('encryption-toggle'), 'onValueChange', false);

    await waitFor(() => {
      expect(privacyAPI.updateSettings).toHaveBeenCalledWith({
        data_encrypted: false,
      });
    });
  });

  it('should toggle local processing', async () => {
    privacyAPI.updateSettings.mockResolvedValue({
      local_processing: false,
    });

    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('local-processing-toggle')).toBeTruthy();
    });

    fireEvent(getByTestId('local-processing-toggle'), 'onValueChange', false);

    await waitFor(() => {
      expect(privacyAPI.updateSettings).toHaveBeenCalledWith({
        local_processing: false,
      });
    });
  });

  it('should update data retention period', async () => {
    privacyAPI.updateSettings.mockResolvedValue({
      data_retention_days: 7,
    });

    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('retention-picker')).toBeTruthy();
    });

    fireEvent(getByTestId('retention-picker'), 'onValueChange', '7');

    await waitFor(() => {
      expect(privacyAPI.updateSettings).toHaveBeenCalledWith({
        data_retention_days: 7,
      });
    });
  });

  it('should handle delete all data', async () => {
    privacyAPI.deleteAllData.mockResolvedValue({ success: true });

    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('delete-data-button')).toBeTruthy();
    });

    fireEvent.press(getByTestId('delete-data-button'));

    // Confirm deletion in alert
    await waitFor(() => {
      expect(privacyAPI.deleteAllData).toHaveBeenCalled();
    });
  });

  it('should show tracking blocked status', async () => {
    const { getByText } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('Tracking Blocked')).toBeTruthy();
    });
  });

  it('should handle API errors', async () => {
    privacyAPI.getStatus.mockRejectedValue(new Error('Network error'));

    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('error-message')).toBeTruthy();
    });
  });

  it('should display privacy score', async () => {
    privacyAPI.getPrivacyScore.mockResolvedValue({ score: 95 });

    const { getByText } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('95%')).toBeTruthy();
    });
  });
});

describe('PrivacyScreen Data Management', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    privacyAPI.getStatus.mockResolvedValue({});
    privacyAPI.getDataUsage.mockResolvedValue({});
  });

  it('should export data', async () => {
    privacyAPI.exportData.mockResolvedValue({ file_path: '/data/export.json' });

    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('export-data-button')).toBeTruthy();
    });

    fireEvent.press(getByTestId('export-data-button'));

    await waitFor(() => {
      expect(privacyAPI.exportData).toHaveBeenCalled();
    });
  });

  it('should handle auto-delete toggle', async () => {
    privacyAPI.updateSettings.mockResolvedValue({
      auto_delete_enabled: true,
    });

    const { getByTestId } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByTestId('auto-delete-toggle')).toBeTruthy();
    });

    fireEvent(getByTestId('auto-delete-toggle'), 'onValueChange', true);

    await waitFor(() => {
      expect(privacyAPI.updateSettings).toHaveBeenCalledWith({
        auto_delete_enabled: true,
      });
    });
  });

  it('should display zero cloud storage', async () => {
    const { getByText } = render(
      <PrivacyScreen navigation={mockNavigation} />
    );

    await waitFor(() => {
      expect(getByText('0 MB')).toBeTruthy();
    });
  });
});
