/**
 * React Native Mocks for Testing
 */

export const View = 'View';
export const Text = 'Text';
export const ScrollView = 'ScrollView';
export const TouchableOpacity = 'TouchableOpacity';
export const ActivityIndicator = 'ActivityIndicator';
export const RefreshControl = 'RefreshControl';
export const StyleSheet = {
  create: (styles) => styles,
};
export const Alert = {
  alert: jest.fn(),
};
export const Platform = {
  OS: 'ios',
  select: (obj) => obj.ios,
};
