/**
 * Analytics Screen
 * Comprehensive analytics dashboard with charts and insights
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { LineChart, BarChart, ProgressChart, PieChart } from 'react-native-chart-kit';
import * as Progress from 'react-native-progress';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const screenWidth = Dimensions.get('window').width;

const AnalyticsScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState('today'); // today, week, insights
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);

  const userId = 'user123'; // TODO: Get from auth context

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/dashboard`, {
        params: { user_id: userId }
      });
      
      setDashboardData(response.data.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const renderTodayTab = () => {
    if (!dashboardData?.today) return null;

    const today = dashboardData.today;
    const wellbeing = dashboardData.wellbeing;

    return (
      <View style={styles.tabContent}>
        {/* Key Metrics Cards */}
        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {Math.floor(today.total_focus_time_minutes / 60)}h {today.total_focus_time_minutes % 60}m
            </Text>
            <Text style={styles.metricLabel}>Focus Time</Text>
            <Text style={styles.metricSubtext}>Today</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>{today.productivity_score.toFixed(0)}</Text>
            <Text style={styles.metricLabel}>Productivity</Text>
            <Progress.Bar 
              progress={today.productivity_score / 100} 
              width={100}
              color="#4CAF50"
              style={styles.progressBar}
            />
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>{today.distractions_count}</Text>
            <Text style={styles.metricLabel}>Distractions</Text>
            <Text style={styles.metricSubtext}>Blocked</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>{today.breaks_count}</Text>
            <Text style={styles.metricLabel}>Breaks</Text>
            <Text style={styles.metricSubtext}>Taken</Text>
          </View>
        </View>

        {/* Wellbeing Score */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Wellbeing Score {wellbeing.emoji}</Text>
          <View style={styles.wellbeingContainer}>
            <ProgressChart
              data={{
                labels: ['Screen', 'Breaks', 'Focus', 'Balance', 'Notifications'],
                data: [
                  wellbeing.components.screen_time_health / 100,
                  wellbeing.components.break_adherence / 100,
                  wellbeing.components.focus_quality / 100,
                  wellbeing.components.work_life_balance / 100,
                  wellbeing.components.notification_management / 100,
                ]
              }}
              width={screenWidth - 60}
              height={200}
              strokeWidth={12}
              radius={24}
              chartConfig={chartConfig}
              hideLegend={false}
            />
            <Text style={styles.wellbeingScore}>
              {wellbeing.overall_score.toFixed(0)}/100 - {wellbeing.level.replace('_', ' ').toUpperCase()}
            </Text>
          </View>
          {wellbeing.recommendations.map((rec, idx) => (
            <Text key={idx} style={styles.recommendation}>• {rec}</Text>
          ))}
        </View>

        {/* Hourly Activity */}
        {today.hourly_breakdown && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>📊 Today's Activity by Hour</Text>
            <LineChart
              data={{
                labels: ['6AM', '9AM', '12PM', '3PM', '6PM', '9PM'],
                datasets: [{
                  data: [
                    today.hourly_breakdown[6]?.minutes || 0,
                    today.hourly_breakdown[9]?.minutes || 0,
                    today.hourly_breakdown[12]?.minutes || 0,
                    today.hourly_breakdown[15]?.minutes || 0,
                    today.hourly_breakdown[18]?.minutes || 0,
                    today.hourly_breakdown[21]?.minutes || 0,
                  ]
                }]
              }}
              width={screenWidth - 60}
              height={200}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </View>
        )}

        {/* Top Apps */}
        {today.top_apps && today.top_apps.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>📱 Top Apps Today</Text>
            {today.top_apps.map((app, idx) => (
              <View key={idx} style={styles.appItem}>
                <Text style={styles.appName}>{app.app}</Text>
                <View style={styles.appStats}>
                  <Text style={styles.appTime}>{app.minutes.toFixed(0)}m</Text>
                  <Progress.Bar 
                    progress={app.minutes / (today.total_screen_time_minutes || 1)} 
                    width={100}
                    color="#2196F3"
                  />
                </View>
              </View>
            ))}
          </View>
        )}
      </View>
    );
  };

  const renderWeekTab = () => {
    if (!dashboardData?.week) return null;

    const week = dashboardData.week;
    const { averages, best_day, trends } = week;

    return (
      <View style={styles.tabContent}>
        {/* Weekly Averages */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>📈 Weekly Averages</Text>
          <View style={styles.averagesGrid}>
            <View style={styles.averageItem}>
              <Text style={styles.averageValue}>
                {Math.floor(averages.focus_time_minutes / 60)}h {Math.floor(averages.focus_time_minutes % 60)}m
              </Text>
              <Text style={styles.averageLabel}>Avg Focus Time</Text>
            </View>
            <View style={styles.averageItem}>
              <Text style={styles.averageValue}>{averages.productivity_score.toFixed(0)}</Text>
              <Text style={styles.averageLabel}>Avg Productivity</Text>
            </View>
            <View style={styles.averageItem}>
              <Text style={styles.averageValue}>{averages.distractions_per_day.toFixed(0)}</Text>
              <Text style={styles.averageLabel}>Distractions/Day</Text>
            </View>
            <View style={styles.averageItem}>
              <Text style={styles.averageValue}>{averages.notifications_per_day.toFixed(0)}</Text>
              <Text style={styles.averageLabel}>Notifications/Day</Text>
            </View>
          </View>
        </View>

        {/* Trends */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>📊 Trends</Text>
          <View style={styles.trendItem}>
            <Text style={styles.trendLabel}>Productivity:</Text>
            <Text style={[styles.trendValue, getTrendStyle(trends.productivity)]}>
              {getTrendIcon(trends.productivity)} {trends.productivity.toUpperCase()}
            </Text>
          </View>
          <View style={styles.trendItem}>
            <Text style={styles.trendLabel}>Focus Time:</Text>
            <Text style={[styles.trendValue, getTrendStyle(trends.focus_time)]}>
              {getTrendIcon(trends.focus_time)} {trends.focus_time.toUpperCase()}
            </Text>
          </View>
        </View>

        {/* Best Day */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🏆 Best Day This Week</Text>
          <Text style={styles.bestDayDate}>{best_day.date}</Text>
          <View style={styles.bestDayStats}>
            <Text style={styles.bestDayStat}>
              Productivity: {best_day.productivity_score.toFixed(0)}/100
            </Text>
            <Text style={styles.bestDayStat}>
              Focus Time: {Math.floor(best_day.focus_time / 60)}h {Math.floor(best_day.focus_time % 60)}m
            </Text>
          </View>
        </View>

        {/* Top Apps (Weekly) */}
        {dashboardData.top_apps && dashboardData.top_apps.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>📱 Top Apps This Week</Text>
            <PieChart
              data={dashboardData.top_apps.slice(0, 5).map((app, idx) => ({
                name: app.app,
                population: app.minutes,
                color: pieColors[idx % pieColors.length],
                legendFontColor: '#333',
                legendFontSize: 12,
              }))}
              width={screenWidth - 60}
              height={200}
              chartConfig={chartConfig}
              accessor="population"
              backgroundColor="transparent"
              paddingLeft="15"
              absolute
            />
          </View>
        )}
      </View>
    );
  };

  const renderInsightsTab = () => {
    if (!dashboardData?.insights || !dashboardData?.tips) return null;

    const { insights, tips, patterns } = dashboardData;

    return (
      <View style={styles.tabContent}>
        {/* Insights */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>💡 Insights</Text>
          {insights.map((insight, idx) => (
            <View key={idx} style={[styles.insightCard, getInsightStyle(insight.type)]}>
              <Text style={styles.insightIcon}>{insight.icon}</Text>
              <View style={styles.insightContent}>
                <Text style={styles.insightTitle}>{insight.title}</Text>
                <Text style={styles.insightMessage}>{insight.message}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Personalized Tips */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🎯 Personalized Tips</Text>
          {tips.map((tip, idx) => (
            <View key={idx} style={[styles.tipCard, getPriorityStyle(tip.priority)]}>
              <View style={styles.tipHeader}>
                <Text style={styles.tipIcon}>{tip.icon}</Text>
                <Text style={styles.tipCategory}>{tip.category.toUpperCase()}</Text>
                {tip.priority === 'high' && <Text style={styles.priorityBadge}>HIGH</Text>}
              </View>
              <Text style={styles.tipText}>{tip.tip}</Text>
            </View>
          ))}
        </View>

        {/* Patterns */}
        {patterns && patterns.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>🔍 Detected Patterns</Text>
            {patterns.map((pattern, idx) => (
              <View key={idx} style={styles.patternCard}>
                <Text style={styles.patternIcon}>{pattern.icon}</Text>
                <View style={styles.patternContent}>
                  <Text style={styles.patternType}>{pattern.type.replace(/_/g, ' ').toUpperCase()}</Text>
                  <Text style={styles.patternMessage}>{pattern.message}</Text>
                  <Text style={styles.patternStrength}>Strength: {pattern.strength}</Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </View>
    );
  };

  const getTrendIcon = (trend) => {
    if (trend === 'improving') return '📈';
    if (trend === 'declining') return '📉';
    return '➡️';
  };

  const getTrendStyle = (trend) => {
    if (trend === 'improving') return { color: '#4CAF50' };
    if (trend === 'declining') return { color: '#F44336' };
    return { color: '#FF9800' };
  };

  const getInsightStyle = (type) => {
    if (type === 'positive') return { backgroundColor: '#E8F5E9', borderLeftColor: '#4CAF50' };
    if (type === 'warning') return { backgroundColor: '#FFF3E0', borderLeftColor: '#FF9800' };
    return { backgroundColor: '#E3F2FD', borderLeftColor: '#2196F3' };
  };

  const getPriorityStyle = (priority) => {
    if (priority === 'high') return { borderLeftColor: '#F44336', borderLeftWidth: 4 };
    if (priority === 'medium') return { borderLeftColor: '#FF9800', borderLeftWidth: 4 };
    return { borderLeftColor: '#4CAF50', borderLeftWidth: 4 };
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6200EE" />
        <Text style={styles.loadingText}>Loading analytics...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>❌ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadDashboardData}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Tab Selector */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'today' && styles.activeTab]}
          onPress={() => setSelectedTab('today')}
        >
          <Text style={[styles.tabText, selectedTab === 'today' && styles.activeTabText]}>
            Today
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, selectedTab === 'week' && styles.activeTab]}
          onPress={() => setSelectedTab('week')}
        >
          <Text style={[styles.tabText, selectedTab === 'week' && styles.activeTabText]}>
            Week
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, selectedTab === 'insights' && styles.activeTab]}
          onPress={() => setSelectedTab('insights')}
        >
          <Text style={[styles.tabText, selectedTab === 'insights' && styles.activeTabText]}>
            Insights
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {selectedTab === 'today' && renderTodayTab()}
        {selectedTab === 'week' && renderWeekTab()}
        {selectedTab === 'insights' && renderInsightsTab()}
      </ScrollView>
    </View>
  );
};

// Chart configuration
const chartConfig = {
  backgroundColor: '#ffffff',
  backgroundGradientFrom: '#ffffff',
  backgroundGradientTo: '#ffffff',
  decimalPlaces: 0,
  color: (opacity = 1) => `rgba(98, 0, 238, ${opacity})`,
  labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
  style: {
    borderRadius: 16,
  },
  propsForDots: {
    r: '6',
    strokeWidth: '2',
    stroke: '#6200EE',
  },
};

const pieColors = ['#6200EE', '#03DAC6', '#FF9800', '#4CAF50', '#F44336'];

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#F44336',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#6200EE',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  tab: {
    flex: 1,
    paddingVertical: 16,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#6200EE',
  },
  tabText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
  },
  activeTabText: {
    color: '#6200EE',
    fontWeight: '700',
  },
  scrollView: {
    flex: 1,
  },
  tabContent: {
    padding: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  metricValue: {
    fontSize: 28,
    fontWeight: '700',
    color: '#6200EE',
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  metricSubtext: {
    fontSize: 12,
    color: '#666',
  },
  progressBar: {
    marginTop: 8,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 16,
  },
  wellbeingContainer: {
    alignItems: 'center',
  },
  wellbeingScore: {
    fontSize: 20,
    fontWeight: '700',
    color: '#6200EE',
    marginTop: 16,
    marginBottom: 8,
  },
  recommendation: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
    paddingLeft: 8,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  appItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  appName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  appStats: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  appTime: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    minWidth: 40,
    textAlign: 'right',
  },
  averagesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  averageItem: {
    width: '48%',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    marginBottom: 8,
  },
  averageValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#6200EE',
    marginBottom: 4,
  },
  averageLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  trendItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  trendLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  trendValue: {
    fontSize: 16,
    fontWeight: '700',
  },
  bestDayDate: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6200EE',
    marginBottom: 12,
  },
  bestDayStats: {
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 8,
  },
  bestDayStat: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  insightCard: {
    flexDirection: 'row',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
  },
  insightIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  insightContent: {
    flex: 1,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginBottom: 4,
  },
  insightMessage: {
    fontSize: 14,
    color: '#666',
  },
  tipCard: {
    padding: 12,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    marginBottom: 12,
  },
  tipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tipIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  tipCategory: {
    fontSize: 12,
    fontWeight: '700',
    color: '#666',
    flex: 1,
  },
  priorityBadge: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFFFFF',
    backgroundColor: '#F44336',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  tipText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  patternCard: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    marginBottom: 12,
  },
  patternIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  patternContent: {
    flex: 1,
  },
  patternType: {
    fontSize: 14,
    fontWeight: '700',
    color: '#6200EE',
    marginBottom: 4,
  },
  patternMessage: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  patternStrength: {
    fontSize: 12,
    color: '#666',
  },
});

export default AnalyticsScreen;
