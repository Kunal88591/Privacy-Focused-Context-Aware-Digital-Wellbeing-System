/**
 * API Service Mocks
 */

export const wellbeingAPI = {
  getStats: jest.fn(),
  getFocusStatus: jest.fn(),
  toggleFocusMode: jest.fn(),
  getGoals: jest.fn(),
  updateGoal: jest.fn(),
  getAnalytics: jest.fn(),
};

export const privacyAPI = {
  getStatus: jest.fn(),
  updateSettings: jest.fn(),
  getDataUsage: jest.fn(),
  deleteAllData: jest.fn(),
  exportData: jest.fn(),
  getPrivacyScore: jest.fn(),
};

export const notificationAPI = {
  getNotifications: jest.fn(),
  markAsRead: jest.fn(),
  deleteNotification: jest.fn(),
  updatePreferences: jest.fn(),
};

export const settingsAPI = {
  getSettings: jest.fn(),
  updateSetting: jest.fn(),
  resetSettings: jest.fn(),
};
