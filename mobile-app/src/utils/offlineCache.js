/**
 * Offline Cache Utility
 * Handles caching and retrieval of API responses for offline mode
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const CACHE_PREFIX = '@cache_';
const CACHE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes

/**
 * Save data to cache with timestamp
 */
export const setCache = async (key, data) => {
  try {
    const cacheItem = {
      data,
      timestamp: Date.now(),
    };
    await AsyncStorage.setItem(
      `${CACHE_PREFIX}${key}`,
      JSON.stringify(cacheItem)
    );
    return true;
  } catch (error) {
    console.error('Error setting cache:', error);
    return false;
  }
};

/**
 * Get data from cache if not expired
 */
export const getCache = async (key, expiryMs = CACHE_EXPIRY_MS) => {
  try {
    const cached = await AsyncStorage.getItem(`${CACHE_PREFIX}${key}`);
    if (!cached) return null;

    const cacheItem = JSON.parse(cached);
    const isExpired = Date.now() - cacheItem.timestamp > expiryMs;

    if (isExpired) {
      await clearCache(key);
      return null;
    }

    return cacheItem.data;
  } catch (error) {
    console.error('Error getting cache:', error);
    return null;
  }
};

/**
 * Clear specific cache entry
 */
export const clearCache = async (key) => {
  try {
    await AsyncStorage.removeItem(`${CACHE_PREFIX}${key}`);
    return true;
  } catch (error) {
    console.error('Error clearing cache:', error);
    return false;
  }
};

/**
 * Clear all cache entries
 */
export const clearAllCache = async () => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    const cacheKeys = keys.filter((key) => key.startsWith(CACHE_PREFIX));
    await AsyncStorage.multiRemove(cacheKeys);
    return true;
  } catch (error) {
    console.error('Error clearing all cache:', error);
    return false;
  }
};

/**
 * Get cache metadata (size, count, etc.)
 */
export const getCacheInfo = async () => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    const cacheKeys = keys.filter((key) => key.startsWith(CACHE_PREFIX));
    
    const cacheItems = await AsyncStorage.multiGet(cacheKeys);
    const items = cacheItems.map(([key, value]) => {
      try {
        return { key: key.replace(CACHE_PREFIX, ''), ...JSON.parse(value) };
      } catch {
        return null;
      }
    }).filter(Boolean);

    return {
      count: items.length,
      items,
      totalSize: JSON.stringify(items).length,
    };
  } catch (error) {
    console.error('Error getting cache info:', error);
    return { count: 0, items: [], totalSize: 0 };
  }
};

export default {
  setCache,
  getCache,
  clearCache,
  clearAllCache,
  getCacheInfo,
};
