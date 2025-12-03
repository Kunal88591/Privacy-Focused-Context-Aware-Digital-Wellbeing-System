/**
 * Privacy-Focused Digital Wellbeing Mobile App
 * Main Application Entry Point
 */

import React from 'react';
import { StatusBar } from 'react-native';
import AppNavigator from './src/navigation/AppNavigator';

const App = () => {
  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor="white" />
      <AppNavigator />
    </>
  );
};

export default App;
