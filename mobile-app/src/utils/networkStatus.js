/**
 * Network Status Utility
 * Detects online/offline state and network quality
 */

import { useEffect, useState } from 'react';
import NetInfo from '@react-native-community/netinfo';

/**
 * Hook to monitor network connectivity
 */
export const useNetworkStatus = () => {
  const [isConnected, setIsConnected] = useState(true);
  const [isInternetReachable, setIsInternetReachable] = useState(true);
  const [connectionType, setConnectionType] = useState('unknown');

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      setIsConnected(state.isConnected ?? false);
      setIsInternetReachable(state.isInternetReachable ?? false);
      setConnectionType(state.type);
    });

    // Get initial state
    NetInfo.fetch().then((state) => {
      setIsConnected(state.isConnected ?? false);
      setIsInternetReachable(state.isInternetReachable ?? false);
      setConnectionType(state.type);
    });

    return () => unsubscribe();
  }, []);

  return {
    isConnected,
    isInternetReachable,
    isOnline: isConnected && isInternetReachable,
    connectionType,
  };
};

/**
 * Get current network status (promise-based)
 */
export const getNetworkStatus = async () => {
  try {
    const state = await NetInfo.fetch();
    return {
      isConnected: state.isConnected ?? false,
      isInternetReachable: state.isInternetReachable ?? false,
      isOnline: (state.isConnected && state.isInternetReachable) ?? false,
      connectionType: state.type,
    };
  } catch (error) {
    console.error('Error getting network status:', error);
    return {
      isConnected: false,
      isInternetReachable: false,
      isOnline: false,
      connectionType: 'unknown',
    };
  }
};

export default {
  useNetworkStatus,
  getNetworkStatus,
};
