/**
 * Recommendations Service
 * 
 * Manages smart, personalized recommendations for digital wellbeing.
 * Features:
 * - AI-powered recommendation generation
 * - Context-aware suggestions
 * - User feedback tracking
 * - Recommendation caching and refresh
 * - Observer pattern for UI updates
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import config from '../config';

class RecommendationsService {
  constructor() {
    if (RecommendationsService.instance) {
      return RecommendationsService.instance;
    }

    this.recommendations = [];
    this.observers = [];
    this.lastFetchTime = null;
    this.refreshInterval = 3600000; // 1 hour
    this.cacheKey = '@recommendations_cache';
    
    RecommendationsService.instance = this;
    this.initialize();
  }

  /**
   * Initialize service with cached data
   */
  async initialize() {
    try {
      const cached = await AsyncStorage.getItem(this.cacheKey);
      if (cached) {
        const data = JSON.parse(cached);
        this.recommendations = data.recommendations || [];
        this.lastFetchTime = data.lastFetchTime ? new Date(data.lastFetchTime) : null;
        this.notifyObservers();
      }
    } catch (error) {
      console.error('Failed to load cached recommendations:', error);
    }
  }

  /**
   * Register observer for recommendation updates
   * @param {Function} callback - Function to call on updates
   * @returns {Function} Unsubscribe function
   */
  subscribe(callback) {
    this.observers.push(callback);
    return () => {
      this.observers = this.observers.filter(obs => obs !== callback);
    };
  }

  /**
   * Notify all observers of updates
   */
  notifyObservers() {
    this.observers.forEach(callback => {
      try {
        callback(this.recommendations);
      } catch (error) {
        console.error('Observer notification error:', error);
      }
    });
  }

  /**
   * Save recommendations to cache
   */
  async saveToCache() {
    try {
      const data = {
        recommendations: this.recommendations,
        lastFetchTime: this.lastFetchTime?.toISOString()
      };
      await AsyncStorage.setItem(this.cacheKey, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to cache recommendations:', error);
    }
  }

  /**
   * Generate personalized recommendations
   * @param {Object} options - Generation options
   * @returns {Promise<Array>} Generated recommendations
   */
  async generateRecommendations(options = {}) {
    try {
      const userId = await this.getUserId();
      const requestData = {
        user_id: userId,
        context: options.context || await this.getCurrentContext(),
        history_days: options.historyDays || 7,
        max_recommendations: options.maxRecommendations || 10,
        types: options.types || null
      };

      const response = await fetch(`${config.API_URL}/recommendations/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`Failed to generate recommendations: ${response.status}`);
      }

      const data = await response.json();
      this.recommendations = data.recommendations || [];
      this.lastFetchTime = new Date();
      
      await this.saveToCache();
      this.notifyObservers();
      
      return this.recommendations;
    } catch (error) {
      console.error('Recommendation generation error:', error);
      throw error;
    }
  }

  /**
   * Get quick recommendations (top 3)
   * @returns {Promise<Array>} Quick recommendations
   */
  async getQuickRecommendations() {
    try {
      const userId = await this.getUserId();
      const response = await fetch(
        `${config.API_URL}/recommendations/quick/${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${await this.getAuthToken()}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch quick recommendations: ${response.status}`);
      }

      const data = await response.json();
      return data.recommendations || [];
    } catch (error) {
      console.error('Quick recommendations error:', error);
      return [];
    }
  }

  /**
   * Get all available recommendation types
   * @returns {Promise<Array>} Recommendation types
   */
  async getRecommendationTypes() {
    try {
      const response = await fetch(`${config.API_URL}/recommendations/types`, {
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch recommendation types: ${response.status}`);
      }

      const data = await response.json();
      return data.types || [];
    } catch (error) {
      console.error('Recommendation types error:', error);
      return [];
    }
  }

  /**
   * Submit feedback for a recommendation
   * @param {string} recommendationId - Recommendation ID
   * @param {string} action - User action (accepted, dismissed, snoozed, completed)
   * @param {Object} metadata - Additional feedback data
   * @returns {Promise<Object>} Feedback result
   */
  async submitFeedback(recommendationId, action, metadata = {}) {
    try {
      const userId = await this.getUserId();
      const feedbackData = {
        user_id: userId,
        recommendation_id: recommendationId,
        action: action,
        timestamp: new Date().toISOString(),
        metadata: metadata
      };

      const response = await fetch(`${config.API_URL}/recommendations/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`
        },
        body: JSON.stringify(feedbackData)
      });

      if (!response.ok) {
        throw new Error(`Failed to submit feedback: ${response.status}`);
      }

      const data = await response.json();
      
      // Update local recommendation status
      const recommendation = this.recommendations.find(r => r.id === recommendationId);
      if (recommendation) {
        recommendation.status = action;
        recommendation.feedback_timestamp = feedbackData.timestamp;
        await this.saveToCache();
        this.notifyObservers();
      }
      
      return data;
    } catch (error) {
      console.error('Feedback submission error:', error);
      throw error;
    }
  }

  /**
   * Accept a recommendation
   * @param {string} recommendationId - Recommendation ID
   * @returns {Promise<Object>} Result
   */
  async acceptRecommendation(recommendationId) {
    return this.submitFeedback(recommendationId, 'accepted');
  }

  /**
   * Dismiss a recommendation
   * @param {string} recommendationId - Recommendation ID
   * @param {string} reason - Dismissal reason
   * @returns {Promise<Object>} Result
   */
  async dismissRecommendation(recommendationId, reason = null) {
    return this.submitFeedback(recommendationId, 'dismissed', { reason });
  }

  /**
   * Snooze a recommendation
   * @param {string} recommendationId - Recommendation ID
   * @param {number} duration - Snooze duration in minutes
   * @returns {Promise<Object>} Result
   */
  async snoozeRecommendation(recommendationId, duration = 60) {
    return this.submitFeedback(recommendationId, 'snoozed', { 
      duration_minutes: duration,
      snooze_until: new Date(Date.now() + duration * 60000).toISOString()
    });
  }

  /**
   * Mark recommendation as completed
   * @param {string} recommendationId - Recommendation ID
   * @returns {Promise<Object>} Result
   */
  async completeRecommendation(recommendationId) {
    return this.submitFeedback(recommendationId, 'completed');
  }

  /**
   * Get current recommendations (cached)
   * @returns {Array} Current recommendations
   */
  getCurrentRecommendations() {
    return this.recommendations;
  }

  /**
   * Filter recommendations by type
   * @param {string} type - Recommendation type
   * @returns {Array} Filtered recommendations
   */
  getByType(type) {
    return this.recommendations.filter(r => r.type === type);
  }

  /**
   * Filter recommendations by category
   * @param {string} category - Category name
   * @returns {Array} Filtered recommendations
   */
  getByCategory(category) {
    return this.recommendations.filter(r => r.category === category);
  }

  /**
   * Get active recommendations (not dismissed or snoozed)
   * @returns {Array} Active recommendations
   */
  getActiveRecommendations() {
    return this.recommendations.filter(r => 
      !r.status || (r.status !== 'dismissed' && !this.isSnoozed(r))
    );
  }

  /**
   * Check if recommendation is snoozed
   * @param {Object} recommendation - Recommendation object
   * @returns {boolean} True if snoozed
   */
  isSnoozed(recommendation) {
    if (recommendation.status !== 'snoozed') return false;
    
    const snoozeUntil = recommendation.feedback_metadata?.snooze_until;
    if (!snoozeUntil) return false;
    
    return new Date(snoozeUntil) > new Date();
  }

  /**
   * Refresh recommendations if needed
   * @param {boolean} force - Force refresh regardless of interval
   * @returns {Promise<Array>} Recommendations
   */
  async refreshIfNeeded(force = false) {
    const now = new Date();
    const shouldRefresh = force || 
      !this.lastFetchTime || 
      (now - this.lastFetchTime) > this.refreshInterval;

    if (shouldRefresh) {
      return this.generateRecommendations();
    }
    
    return this.recommendations;
  }

  /**
   * Get current user context for personalization
   * @returns {Promise<Object>} User context
   */
  async getCurrentContext() {
    try {
      const hour = new Date().getHours();
      
      return {
        time_of_day: this.getTimeOfDay(hour),
        day_of_week: new Date().getDay(),
        is_weekend: [0, 6].includes(new Date().getDay()),
        current_hour: hour
      };
    } catch (error) {
      console.error('Context retrieval error:', error);
      return {};
    }
  }

  /**
   * Get time of day category
   * @param {number} hour - Hour of day (0-23)
   * @returns {string} Time category
   */
  getTimeOfDay(hour) {
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 21) return 'evening';
    return 'night';
  }

  /**
   * Get user ID from storage
   * @returns {Promise<string>} User ID
   */
  async getUserId() {
    try {
      const userId = await AsyncStorage.getItem('@user_id');
      return userId || 'default_user';
    } catch (error) {
      console.error('Failed to get user ID:', error);
      return 'default_user';
    }
  }

  /**
   * Get authentication token
   * @returns {Promise<string>} Auth token
   */
  async getAuthToken() {
    try {
      const token = await AsyncStorage.getItem('@auth_token');
      return token || '';
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return '';
    }
  }

  /**
   * Clear all recommendations
   */
  async clearRecommendations() {
    this.recommendations = [];
    this.lastFetchTime = null;
    await AsyncStorage.removeItem(this.cacheKey);
    this.notifyObservers();
  }

  /**
   * Get statistics about recommendations
   * @returns {Object} Recommendation statistics
   */
  getStats() {
    const total = this.recommendations.length;
    const byType = {};
    const byCategory = {};
    const byStatus = {
      accepted: 0,
      dismissed: 0,
      snoozed: 0,
      completed: 0,
      pending: 0
    };

    this.recommendations.forEach(rec => {
      // Count by type
      byType[rec.type] = (byType[rec.type] || 0) + 1;
      
      // Count by category
      byCategory[rec.category] = (byCategory[rec.category] || 0) + 1;
      
      // Count by status
      if (rec.status) {
        byStatus[rec.status] = (byStatus[rec.status] || 0) + 1;
      } else {
        byStatus.pending++;
      }
    });

    return {
      total,
      active: this.getActiveRecommendations().length,
      byType,
      byCategory,
      byStatus,
      lastFetch: this.lastFetchTime?.toISOString()
    };
  }
}

// Create and export singleton instance
const recommendationsService = new RecommendationsService();
export default recommendationsService;
