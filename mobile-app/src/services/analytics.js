/**
 * Analytics Service
 * 
 * Manages analytics data fetching, caching, and real-time updates.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import config from '../config';

class AnalyticsService {
  constructor() {
    this.cache = {
      dashboard: null,
      summary: null,
      lastUpdated: null
    };
    this.observers = [];
    this.refreshInterval = 5 * 60 * 1000; // 5 minutes
    this.isRefreshing = false;
  }

  subscribe(callback) {
    this.observers.push(callback);
    return () => {
      this.observers = this.observers.filter(cb => cb !== callback);
    };
  }

  notifyObservers(data) {
    this.observers.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('Observer notification error:', error);
      }
    });
  }

  async getDashboard(userId = 'default_user', forceRefresh = false) {
    try {
      if (!forceRefresh && this.cache.dashboard && !this.shouldRefresh()) {
        console.log('[Analytics] Returning cached dashboard');
        return this.cache.dashboard;
      }

      const networkState = await NetInfo.fetch();
      if (!networkState.isConnected) {
        console.log('[Analytics] Offline - using cached data');
        return this.cache.dashboard || this.getOfflineData();
      }

      console.log('[Analytics] Fetching dashboard from API');
      const token = await AsyncStorage.getItem('@auth_token') || '';
      
      const response = await fetch(
        `${config.API_URL}/api/v1/analytics/dashboard?user_id=${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          timeout: 10000
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();
      const data = result.data || result;

      this.cache.dashboard = data;
      this.cache.lastUpdated = Date.now();
      
      await AsyncStorage.setItem('@analytics_dashboard', JSON.stringify(data));
      await AsyncStorage.setItem('@analytics_updated', this.cache.lastUpdated.toString());

      this.notifyObservers(data);

      return data;
      
    } catch (error) {
      console.error('[Analytics] Error fetching dashboard:', error);
      
      try {
        const cached = await AsyncStorage.getItem('@analytics_dashboard');
        if (cached) {
          this.cache.dashboard = JSON.parse(cached);
          return this.cache.dashboard;
        }
      } catch (storageError) {
        console.error('[Analytics] Storage error:', storageError);
      }

      return this.getOfflineData();
    }
  }

  shouldRefresh() {
    if (!this.cache.lastUpdated) return true;
    return Date.now() - this.cache.lastUpdated > this.refreshInterval;
  }

  async refresh(userId = 'default_user') {
    if (this.isRefreshing) {
      console.log('[Analytics] Refresh already in progress');
      return this.cache.dashboard;
    }

    this.isRefreshing = true;
    try {
      const data = await this.getDashboard(userId, true);
      return data;
    } finally {
      this.isRefreshing = false;
    }
  }

  async clearCache() {
    this.cache = {
      dashboard: null,
      summary: null,
      lastUpdated: null
    };
    
    try {
      await AsyncStorage.multiRemove([
        '@analytics_dashboard',
        '@analytics_summary_week',
        '@analytics_summary_month',
        '@analytics_updated'
      ]);
    } catch (error) {
      console.error('[Analytics] Error clearing cache:', error);
    }
  }

  getOfflineData() {
    return {
      today: {
        total_focus_time_minutes: 0,
        total_screen_time_minutes: 0,
        breaks_count: 0,
        distractions_count: 0,
        productivity_score: 0,
        hourly_breakdown: {},
        top_apps: []
      },
      week: {
        averages: {
          focus_time_minutes: 0,
          productivity_score: 0,
          distractions_per_day: 0,
          notifications_per_day: 0
        },
        best_day: {
          date: new Date().toISOString().split('T')[0],
          productivity_score: 0,
          focus_time: 0
        },
        trends: {
          productivity: 'stable',
          focus_time: 'stable'
        }
      },
      insights: [],
      tips: [],
      patterns: [],
      top_apps: [],
      wellbeing: {
        overall_score: 0,
        level: 'unknown',
        emoji: '❓',
        components: {
          screen_time_health: 0,
          break_adherence: 0,
          focus_quality: 0,
          work_life_balance: 0,
          notification_management: 0
        },
        recommendations: ['Connect to internet to view analytics']
      }
    };
  }

  getMockSummary(range = 'week') {
    const days = range === 'week' ? 7 : 30;
    const labels = range === 'week'
      ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      : Array.from({length: days}, (_, i) => `${i + 1}`);

    const focusTimeData = Array.from({length: days}, () => Math.floor(Math.random() * 120) + 60);
    const distractionsData = Array.from({length: days}, () => Math.floor(Math.random() * 20) + 10);

    return {
      focusTime: {
        labels,
        datasets: [{ data: focusTimeData }]
      },
      distractions: {
        labels,
        datasets: [{ data: distractionsData }]
      },
      productivity: {
        labels: ['Focus', 'Breaks', 'Goals'],
        data: [0.85, 0.72, 0.68]
      },
      summary: {
        totalFocusMinutes: focusTimeData.reduce((a, b) => a + b, 0),
        totalDistractionsBlocked: distractionsData.reduce((a, b) => a + b, 0),
        averageProductivityScore: 75,
        streakDays: 12,
        goalsCompleted: 8,
        goalsTotal: 12,
        privacyScore: 82,
        wellbeingScore: 78
      },
      trends: {
        focusTime: '+12%',
        distractions: '-18%',
        productivity: '+8%'
      },
      topApps: [
        { name: 'Instagram', blocked: 42, time: 127 },
        { name: 'Twitter', blocked: 38, time: 95 },
        { name: 'TikTok', blocked: 31, time: 88 }
      ]
    };
  }

  async trackEvent(eventType, data) {
    try {
      const token = await AsyncStorage.getItem('@auth_token') || '';
      
      await fetch(`${config.API_URL}/api/v1/analytics/track/${eventType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
    } catch (error) {
      console.error('[Analytics] Error tracking event:', error);
    }
  }
}

const analyticsService = new AnalyticsService();

export default analyticsService;
