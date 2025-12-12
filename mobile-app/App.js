/**
 * Privacy-Focused Digital Wellbeing Mobile App
 * Main Application Entry Point
 */

import React from 'react';
import { StatusBar, View } from 'react-native';
import AppNavigator from './src/navigation/AppNavigator';
import ErrorBoundary from './src/components/ErrorBoundary';
import OfflineIndicator from './src/components/OfflineIndicator';
import { AppProvider } from './src/context/AppContext';
import { AuthProvider } from './src/contexts/AuthContext';

const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppProvider>
          <View style={{ flex: 1 }}>
            <StatusBar barStyle="dark-content" backgroundColor="white" />
            <OfflineIndicator />
            <AppNavigator />
          </View>
        </AppProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
