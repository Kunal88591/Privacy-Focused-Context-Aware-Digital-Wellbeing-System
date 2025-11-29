/**
 * Privacy-Focused Digital Wellbeing Mobile App
 * Main Application Entry Point
 */

import React from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';

const App = () => {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.content}>
        <Text style={styles.title}>🛡️ Privacy Wellbeing</Text>
        <Text style={styles.subtitle}>
          Your Digital Bodyguard & Focus Coach
        </Text>
        <View style={styles.statusCard}>
          <Text style={styles.statusLabel}>Status</Text>
          <Text style={styles.statusValue}>🟢 Protected</Text>
        </View>
        <View style={styles.statsContainer}>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>0</Text>
            <Text style={styles.statLabel}>Blocked</Text>
            <Text style={styles.statLabel}>Distractions</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>0h</Text>
            <Text style={styles.statLabel}>Focus</Text>
            <Text style={styles.statLabel}>Time</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>100%</Text>
            <Text style={styles.statLabel}>Privacy</Text>
            <Text style={styles.statLabel}>Score</Text>
          </View>
        </View>
        <Text style={styles.comingSoon}>🚧 Full App Coming Soon</Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  content: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 40,
    textAlign: 'center',
  },
  statusCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    width: '100%',
    marginBottom: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusLabel: {
    fontSize: 14,
    color: '#999',
    marginBottom: 8,
  },
  statusValue: {
    fontSize: 24,
    fontWeight: '600',
    color: '#4CAF50',
  },
  statsContainer: {
    flexDirection: 'row',
    width: '100%',
    justifyContent: 'space-between',
    marginBottom: 40,
  },
  statBox: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    flex: 1,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 2,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
  },
  comingSoon: {
    fontSize: 14,
    color: '#FF9800',
    marginTop: 20,
  },
});

export default App;
