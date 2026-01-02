"""
API Client with Request Batching and Caching
Optimized API communication for mobile app performance
"""

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000';
const CACHE_PREFIX = '@api_cache:';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

class APIClient {
  constructor() {
    this.pendingRequests = new Map();
    this.requestQueue = [];
    this.batchTimeout = null;
    this.cacheEnabled = true;
  }

  /**
   * Create axios instance with optimized settings
   */
  createClient() {
    return axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
      // Enable compression
      decompress: true,
    });
  }

  /**
   * Get from cache
   */
  async getFromCache(key) {
    if (!this.cacheEnabled) return null;

    try {
      const cacheKey = `${CACHE_PREFIX}${key}`;
      const cached = await AsyncStorage.getItem(cacheKey);
      
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        const age = Date.now() - timestamp;
        
        // Check if cache is still valid
        if (age < CACHE_DURATION) {
          console.log(`[APIClient] Cache HIT: ${key} (age: ${age}ms)`);
          return data;
        } else {
          // Remove expired cache
          await AsyncStorage.removeItem(cacheKey);
        }
      }
      
      console.log(`[APIClient] Cache MISS: ${key}`);
      return null;
    } catch (error) {
      console.error('[APIClient] Cache read error:', error);
      return null;
    }
  }

  /**
   * Save to cache
   */
  async saveToCache(key, data) {
    if (!this.cacheEnabled) return;

    try {
      const cacheKey = `${CACHE_PREFIX}${key}`;
      const cacheData = {
        data,
        timestamp: Date.now(),
      };
      await AsyncStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.log(`[APIClient] Cached: ${key}`);
    } catch (error) {
      console.error('[APIClient] Cache write error:', error);
    }
  }

  /**
   * Clear cache
   */
  async clearCache(pattern = null) {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(CACHE_PREFIX));
      
      if (pattern) {
        const matchingKeys = cacheKeys.filter(key =>
          key.includes(pattern)
        );
        await AsyncStorage.multiRemove(matchingKeys);
        console.log(`[APIClient] Cleared cache pattern: ${pattern}`);
      } else {
        await AsyncStorage.multiRemove(cacheKeys);
        console.log('[APIClient] Cleared all cache');
      }
    } catch (error) {
      console.error('[APIClient] Cache clear error:', error);
    }
  }

  /**
   * GET request with caching
   */
  async get(endpoint, options = {}) {
    const { cache = true, ...axiosOptions } = options;
    const cacheKey = `GET:${endpoint}`;

    // Try cache first
    if (cache) {
      const cached = await this.getFromCache(cacheKey);
      if (cached) return cached;
    }

    // Deduplicate concurrent requests
    if (this.pendingRequests.has(cacheKey)) {
      console.log(`[APIClient] Deduplicating request: ${endpoint}`);
      return this.pendingRequests.get(cacheKey);
    }

    // Make request
    const requestPromise = this.createClient()
      .get(endpoint, axiosOptions)
      .then(response => {
        // Save to cache
        if (cache) {
          this.saveToCache(cacheKey, response.data);
        }
        return response.data;
      })
      .finally(() => {
        this.pendingRequests.delete(cacheKey);
      });

    this.pendingRequests.set(cacheKey, requestPromise);
    return requestPromise;
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    // Invalidate related cache
    await this.clearCache(endpoint.split('/')[0]);

    return this.createClient()
      .post(endpoint, data, options)
      .then(response => response.data);
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    // Invalidate related cache
    await this.clearCache(endpoint.split('/')[0]);

    return this.createClient()
      .put(endpoint, data, options)
      .then(response => response.data);
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    // Invalidate related cache
    await this.clearCache(endpoint.split('/')[0]);

    return this.createClient()
      .delete(endpoint, options)
      .then(response => response.data);
  }

  /**
   * Batch multiple requests together
   */
  async batchRequests(requests) {
    console.log(`[APIClient] Batching ${requests.length} requests`);

    // Execute all requests in parallel
    const results = await Promise.allSettled(
      requests.map(({ method, endpoint, data, options }) => {
        switch (method.toUpperCase()) {
          case 'GET':
            return this.get(endpoint, options);
          case 'POST':
            return this.post(endpoint, data, options);
          case 'PUT':
            return this.put(endpoint, data, options);
          case 'DELETE':
            return this.delete(endpoint, options);
          default:
            throw new Error(`Unsupported method: ${method}`);
        }
      })
    );

    // Return results with status
    return results.map((result, index) => ({
      request: requests[index],
      success: result.status === 'fulfilled',
      data: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason : null,
    }));
  }

  /**
   * Prefetch data in background
   */
  async prefetch(endpoints) {
    console.log(`[APIClient] Prefetching ${endpoints.length} endpoints`);

    const requests = endpoints.map(endpoint => ({
      method: 'GET',
      endpoint,
      options: { cache: true },
    }));

    // Execute in background, don't wait for results
    this.batchRequests(requests).catch(error => {
      console.error('[APIClient] Prefetch error:', error);
    });
  }

  /**
   * Get cache statistics
   */
  async getCacheStats() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith(CACHE_PREFIX));

      let totalSize = 0;
      for (const key of cacheKeys) {
        const value = await AsyncStorage.getItem(key);
        totalSize += value ? value.length : 0;
      }

      return {
        enabled: this.cacheEnabled,
        entries: cacheKeys.length,
        totalSizeBytes: totalSize,
        totalSizeKB: (totalSize / 1024).toFixed(2),
      };
    } catch (error) {
      console.error('[APIClient] Cache stats error:', error);
      return null;
    }
  }
}

// Export singleton instance
export default new APIClient();
