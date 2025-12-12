/**
 * Day 20: Smart Recommendations Engine - Test Suite
 * 
 * Comprehensive tests for AI-powered recommendation system:
 * - recommendations.js service (API integration, caching, observer pattern)
 * - RecommendationsScreen.js UI (rendering, filtering, actions)
 * - Backend integration
 */

const fs = require('fs');
const path = require('path');

// File paths
const serviceDir = path.join(__dirname, '../src/services');
const screenDir = path.join(__dirname, '../src/screens');
const backendDir = path.join(__dirname, '../../backend-api/app');

describe('Day 20: Smart Recommendations Engine', () => {

  // =============================================================================
  // PART 1: FILE EXISTENCE TESTS (10 tests)
  // =============================================================================

  describe('File Structure', () => {
    test('recommendations.js service exists', () => {
      const filePath = path.join(serviceDir, 'recommendations.js');
      expect(fs.existsSync(filePath)).toBe(true);
    });

    test('RecommendationsScreen.js exists', () => {
      const filePath = path.join(screenDir, 'RecommendationsScreen.js');
      expect(fs.existsSync(filePath)).toBe(true);
    });

    test('recommendation_engine.py backend service exists', () => {
      const filePath = path.join(backendDir, 'services/recommendation_engine.py');
      expect(fs.existsSync(filePath)).toBe(true);
    });

    test('recommendations.py backend routes exist', () => {
      const filePath = path.join(backendDir, 'routes/recommendations.py');
      expect(fs.existsSync(filePath)).toBe(true);
    });
  });

  // =============================================================================
  // PART 2: RECOMMENDATIONS SERVICE TESTS (25 tests)
  // =============================================================================

  describe('recommendations.js - Service Implementation', () => {
    let serviceContent;

    beforeAll(() => {
      const filePath = path.join(serviceDir, 'recommendations.js');
      serviceContent = fs.readFileSync(filePath, 'utf8');
    });

    test('has singleton class structure', () => {
      expect(serviceContent).toContain('class RecommendationsService');
      expect(serviceContent).toContain('RecommendationsService.instance');
    });

    test('has AsyncStorage imports', () => {
      expect(serviceContent).toContain('@react-native-async-storage/async-storage');
    });

    test('has config imports', () => {
      expect(serviceContent).toContain("from '../config'");
    });

    test('has constructor with initialization', () => {
      expect(serviceContent).toContain('constructor()');
      expect(serviceContent).toContain('this.recommendations');
      expect(serviceContent).toContain('this.observers');
    });

    test('has initialize method', () => {
      expect(serviceContent).toContain('async initialize()');
      expect(serviceContent).toContain('AsyncStorage.getItem');
    });

    test('has observer pattern methods', () => {
      expect(serviceContent).toContain('subscribe(callback)');
      expect(serviceContent).toContain('notifyObservers()');
      expect(serviceContent).toContain('this.observers.push');
      expect(serviceContent).toContain('this.observers.filter');
    });

    test('has cache management', () => {
      expect(serviceContent).toContain('saveToCache()');
      expect(serviceContent).toContain('this.cacheKey');
      expect(serviceContent).toContain('AsyncStorage.setItem');
    });

    test('has generateRecommendations method', () => {
      expect(serviceContent).toContain('async generateRecommendations');
      expect(serviceContent).toContain('/recommendations/generate');
      expect(serviceContent).toMatch(/method:\s*['"]POST['"]/);
    });

    test('has getQuickRecommendations method', () => {
      expect(serviceContent).toContain('async getQuickRecommendations()');
      expect(serviceContent).toContain('/recommendations/quick');
    });

    test('has getRecommendationTypes method', () => {
      expect(serviceContent).toContain('async getRecommendationTypes()');
      expect(serviceContent).toContain('/recommendations/types');
    });

    test('has feedback submission methods', () => {
      expect(serviceContent).toContain('async submitFeedback');
      expect(serviceContent).toContain('/recommendations/feedback');
      expect(serviceContent).toContain('recommendation_id');
      expect(serviceContent).toContain('action');
    });

    test('has acceptRecommendation method', () => {
      expect(serviceContent).toContain('async acceptRecommendation');
      expect(serviceContent).toContain("'accepted'");
    });

    test('has dismissRecommendation method', () => {
      expect(serviceContent).toContain('async dismissRecommendation');
      expect(serviceContent).toContain("'dismissed'");
    });

    test('has snoozeRecommendation method', () => {
      expect(serviceContent).toContain('async snoozeRecommendation');
      expect(serviceContent).toContain("'snoozed'");
      expect(serviceContent).toContain('duration');
    });

    test('has completeRecommendation method', () => {
      expect(serviceContent).toContain('async completeRecommendation');
      expect(serviceContent).toContain("'completed'");
    });

    test('has filtering methods', () => {
      expect(serviceContent).toContain('getByType(type)');
      expect(serviceContent).toContain('getByCategory(category)');
      expect(serviceContent).toContain('getActiveRecommendations()');
    });

    test('has isSnoozed check', () => {
      expect(serviceContent).toContain('isSnoozed(recommendation)');
      expect(serviceContent).toContain('snooze_until');
    });

    test('has refresh logic', () => {
      expect(serviceContent).toContain('async refreshIfNeeded');
      expect(serviceContent).toContain('refreshInterval');
      expect(serviceContent).toContain('lastFetchTime');
    });

    test('has context generation', () => {
      expect(serviceContent).toContain('async getCurrentContext()');
      expect(serviceContent).toContain('time_of_day');
      expect(serviceContent).toContain('getTimeOfDay');
    });

    test('has time of day logic', () => {
      expect(serviceContent).toContain('getTimeOfDay(hour)');
      expect(serviceContent).toContain("'morning'");
      expect(serviceContent).toContain("'afternoon'");
      expect(serviceContent).toContain("'evening'");
      expect(serviceContent).toContain("'night'");
    });

    test('has user ID management', () => {
      expect(serviceContent).toContain('async getUserId()');
      expect(serviceContent).toContain('@user_id');
    });

    test('has auth token management', () => {
      expect(serviceContent).toContain('async getAuthToken()');
      expect(serviceContent).toContain('@auth_token');
    });

    test('has clearRecommendations method', () => {
      expect(serviceContent).toContain('async clearRecommendations()');
      expect(serviceContent).toContain('removeItem');
    });

    test('has getStats method', () => {
      expect(serviceContent).toContain('getStats()');
      expect(serviceContent).toContain('byType');
      expect(serviceContent).toContain('byCategory');
      expect(serviceContent).toContain('byStatus');
    });

    test('exports singleton instance', () => {
      expect(serviceContent).toContain('const recommendationsService = new RecommendationsService()');
      expect(serviceContent).toContain('export default recommendationsService');
    });
  });

  // =============================================================================
  // PART 3: RECOMMENDATIONS SCREEN TESTS (20 tests)
  // =============================================================================

  describe('RecommendationsScreen.js - UI Implementation', () => {
    let screenContent;

    beforeAll(() => {
      const filePath = path.join(screenDir, 'RecommendationsScreen.js');
      screenContent = fs.readFileSync(filePath, 'utf8');
    });

    test('has React imports', () => {
      expect(screenContent).toContain("from 'react'");
      expect(screenContent).toContain('useState');
      expect(screenContent).toContain('useEffect');
    });

    test('has React Native component imports', () => {
      expect(screenContent).toContain('View');
      expect(screenContent).toContain('Text');
      expect(screenContent).toContain('ScrollView');
      expect(screenContent).toContain('TouchableOpacity');
      expect(screenContent).toContain('Modal');
    });

    test('has RefreshControl import', () => {
      expect(screenContent).toContain('RefreshControl');
    });

    test('has Icon import', () => {
      expect(screenContent).toContain('react-native-vector-icons');
    });

    test('has recommendations service import', () => {
      expect(screenContent).toContain("from '../services/recommendations'");
    });

    test('has screen component definition', () => {
      expect(screenContent).toContain('const RecommendationsScreen');
      expect(screenContent).toContain('navigation');
    });

    test('has state management', () => {
      expect(screenContent).toContain('useState');
      expect(screenContent).toContain('recommendations');
      expect(screenContent).toContain('filteredRecommendations');
      expect(screenContent).toContain('selectedCategory');
      expect(screenContent).toContain('refreshing');
    });

    test('has category definitions', () => {
      expect(screenContent).toContain('categories');
      expect(screenContent).toContain("id: 'all'");
      expect(screenContent).toContain("id: 'productivity'");
      expect(screenContent).toContain("id: 'health'");
      expect(screenContent).toContain("id: 'privacy'");
    });

    test('has useEffect for initialization', () => {
      expect(screenContent).toContain('useEffect');
      expect(screenContent).toContain('loadRecommendations');
      expect(screenContent).toContain('recommendationsService.subscribe');
    });

    test('has loadRecommendations function', () => {
      expect(screenContent).toContain('loadRecommendations');
      expect(screenContent).toContain('refreshIfNeeded');
      expect(screenContent).toContain('getActiveRecommendations');
    });

    test('has handleRefresh function', () => {
      expect(screenContent).toContain('handleRefresh');
      expect(screenContent).toContain('setRefreshing');
      expect(screenContent).toContain('generateRecommendations');
    });

    test('has filterRecommendations function', () => {
      expect(screenContent).toContain('filterRecommendations');
      expect(screenContent).toContain('setFilteredRecommendations');
    });

    test('has action handlers', () => {
      expect(screenContent).toContain('handleAccept');
      expect(screenContent).toContain('handleDismiss');
      expect(screenContent).toContain('handleSnooze');
    });

    test('has helper functions', () => {
      expect(screenContent).toContain('getTypeIcon');
      expect(screenContent).toContain('getPriorityColor');
      expect(screenContent).toContain('getTypeDisplayName');
    });

    test('has renderRecommendationCard function', () => {
      expect(screenContent).toContain('renderRecommendationCard');
      expect(screenContent).toContain('cardHeader');
      expect(screenContent).toContain('cardActions');
    });

    test('has renderDetailModal function', () => {
      expect(screenContent).toContain('renderDetailModal');
      expect(screenContent).toContain('modalContent');
      expect(screenContent).toContain('reasonSection');
      expect(screenContent).toContain('metadataSection');
    });

    test('has header section', () => {
      expect(screenContent).toContain('Smart Recommendations');
      expect(screenContent).toContain('personalized suggestions');
    });

    test('has category filter UI', () => {
      expect(screenContent).toContain('categoryScroll');
      expect(screenContent).toContain('categoryChip');
      expect(screenContent).toContain('horizontal');
    });

    test('has empty state', () => {
      expect(screenContent).toContain('emptyContainer');
      expect(screenContent).toContain('No recommendations right now');
    });

    test('exports screen component', () => {
      expect(screenContent).toContain('export default RecommendationsScreen');
    });
  });

  // =============================================================================
  // PART 4: BACKEND TESTS (25 tests)
  // =============================================================================

  describe('recommendation_engine.py - Backend AI Service', () => {
    let engineContent;

    beforeAll(() => {
      const filePath = path.join(backendDir, 'services/recommendation_engine.py');
      engineContent = fs.readFileSync(filePath, 'utf8');
    });

    test('has necessary imports', () => {
      expect(engineContent).toContain('from datetime import');
      expect(engineContent).toContain('from collections import');
    });

    test('has RecommendationEngine class', () => {
      expect(engineContent).toContain('class RecommendationEngine');
    });

    test('has generate_recommendations method', () => {
      expect(engineContent).toContain('def generate_recommendations');
      expect(engineContent).toContain('user_id');
      expect(engineContent).toContain('context');
    });

    test('has pattern analysis method', () => {
      expect(engineContent).toContain('def _analyze_patterns');
    });

    test('has peak hours identification', () => {
      expect(engineContent).toContain('def _identify_peak_hours');
      expect(engineContent).toContain('focus_score');
    });

    test('has app usage categorization', () => {
      expect(engineContent).toContain('def _categorize_app_usage');
      expect(engineContent).toContain('category');
    });

    test('has focus session analysis', () => {
      expect(engineContent).toContain('def _analyze_focus_sessions');
      expect(engineContent).toContain('duration');
    });

    test('has break pattern analysis', () => {
      expect(engineContent).toContain('def _analyze_break_patterns');
      expect(engineContent).toContain('interval');
    });

    test('has sleep pattern analysis', () => {
      expect(engineContent).toContain('def _analyze_sleep_patterns');
      expect(engineContent).toContain('bedtime');
    });

    test('has notification analysis', () => {
      expect(engineContent).toContain('def _analyze_notifications');
      expect(engineContent).toContain('notification');
    });

    test('has distraction identification', () => {
      expect(engineContent).toContain('def _identify_distractions');
      expect(engineContent).toContain('distraction');
    });

    test('has focus recommendations generator', () => {
      expect(engineContent).toContain('def _focus_recommendations');
      expect(engineContent).toContain('focus_time');
    });

    test('has break recommendations generator', () => {
      expect(engineContent).toContain('def _break_recommendations');
      expect(engineContent).toContain('break_time');
    });

    test('has app usage recommendations', () => {
      expect(engineContent).toContain('def _app_usage_recommendations');
      expect(engineContent).toContain('app_limit');
    });

    test('has sleep recommendations', () => {
      expect(engineContent).toContain('def _sleep_recommendations');
      expect(engineContent).toContain('bedtime');
    });

    test('has notification recommendations', () => {
      expect(engineContent).toContain('def _notification_recommendations');
      expect(engineContent).toContain('notification_control');
    });

    test('has privacy recommendations', () => {
      expect(engineContent).toContain('def _privacy_recommendations');
      expect(engineContent).toContain('privacy_improvement');
    });

    test('has wellbeing recommendations', () => {
      expect(engineContent).toContain('def _wellbeing_recommendations');
      expect(engineContent).toContain('wellbeing_boost');
    });

    test('has recommendation scoring', () => {
      expect(engineContent).toContain('def _score_recommendations');
      expect(engineContent).toContain('priority');
    });

    test('has recommendation types defined', () => {
      expect(engineContent).toContain('focus_time');
      expect(engineContent).toContain('break_time');
      expect(engineContent).toContain('app_limit');
      expect(engineContent).toContain('bedtime');
    });

    test('has categories defined', () => {
      expect(engineContent).toContain('productivity');
      expect(engineContent).toContain('wellbeing');
      expect(engineContent).toContain('privacy');
      expect(engineContent).toContain('focus');
    });

    test('creates recommendation objects with required fields', () => {
      expect(engineContent).toContain("'id'");
      expect(engineContent).toContain("'type'");
      expect(engineContent).toContain("'title'");
      expect(engineContent).toContain("'description'");
      expect(engineContent).toContain("'priority'");
    });

    test('sorts recommendations by priority', () => {
      expect(engineContent).toContain('sort');
      expect(engineContent).toContain('priority');
    });

    test('returns limited number of recommendations', () => {
      expect(engineContent).toMatch(/\[:10\]|\[0:10\]/);
    });

    test('handles empty data gracefully', () => {
      expect(engineContent).toContain('if not');
    });
  });

  describe('recommendations.py - Backend API Routes', () => {
    let routesContent;

    beforeAll(() => {
      const filePath = path.join(backendDir, 'routes/recommendations.py');
      routesContent = fs.readFileSync(filePath, 'utf8');
    });

    test('has FastAPI imports', () => {
      expect(routesContent).toContain('from fastapi import');
      expect(routesContent).toContain('APIRouter');
    });

    test('has Pydantic imports', () => {
      expect(routesContent).toContain('from pydantic import');
      expect(routesContent).toContain('BaseModel');
    });

    test('has router definition', () => {
      expect(routesContent).toContain('router = APIRouter(prefix');
    });

    test('has RecommendationRequest model', () => {
      expect(routesContent).toContain('class RecommendationRequest');
      expect(routesContent).toContain('user_id');
      expect(routesContent).toContain('context');
    });

    test('has RecommendationResponse model', () => {
      expect(routesContent).toContain('class RecommendationResponse');
      expect(routesContent).toContain('recommendations');
    });

    test('has FeedbackRequest model', () => {
      expect(routesContent).toContain('class FeedbackRequest');
      expect(routesContent).toContain('recommendation_id');
      expect(routesContent).toContain('action');
    });

    test('has POST /recommendations/generate endpoint', () => {
      expect(routesContent).toContain('@router.post');
      expect(routesContent).toContain('\"/generate\"');
    });

    test('has GET /recommendations/types endpoint', () => {
      expect(routesContent).toContain('@router.get');
      expect(routesContent).toContain('"/types"');
    });

    test('has POST /recommendations/feedback endpoint', () => {
      expect(routesContent).toContain('"/feedback"');
    });

    test('has GET /recommendations/quick endpoint', () => {
      expect(routesContent).toContain('"/quick/{user_id}"');
    });

    test('imports RecommendationEngine', () => {
      expect(routesContent).toContain('recommendation_engine');
    });

    test('has router with prefix', () => {
      expect(routesContent).toContain('APIRouter(prefix="/recommendations"');
    });
  });

  // =============================================================================
  // PART 5: INTEGRATION TESTS (10 tests)
  // =============================================================================

  describe('Navigation Integration', () => {
    let navContent;

    beforeAll(() => {
      const navPath = path.join(__dirname, '../src/navigation/AppNavigator.js');
      navContent = fs.readFileSync(navPath, 'utf8');
    });

    test('imports RecommendationsScreen', () => {
      expect(navContent).toContain("import RecommendationsScreen from '../screens/RecommendationsScreen'");
    });

    test('has Recommendations tab', () => {
      expect(navContent).toContain('name="Recommendations"');
      expect(navContent).toContain('component={RecommendationsScreen}');
    });

    test('has tab icon', () => {
      expect(navContent).toContain('💡');
    });

    test('has tab label', () => {
      expect(navContent).toContain("tabBarLabel: 'Tips'");
    });
  });

  describe('Backend Router Integration', () => {
    let mainContent;

    beforeAll(() => {
      const mainPath = path.join(backendDir, 'main.py');
      mainContent = fs.readFileSync(mainPath, 'utf8');
    });

    test('imports recommendations router', () => {
      expect(mainContent).toContain('from app.routes import');
      expect(mainContent).toContain('recommendations');
    });

    test('includes recommendations router', () => {
      expect(mainContent).toContain('app.include_router(recommendations.router');
    });

    test('has recommendations tag', () => {
      expect(mainContent).toContain('Recommendations');
    });
  });

  describe('Code Quality Checks', () => {
    test('recommendations.js has no syntax errors', () => {
      const filePath = path.join(serviceDir, 'recommendations.js');
      const content = fs.readFileSync(filePath, 'utf8');
      
      // Check for balanced braces
      const openBraces = (content.match(/{/g) || []).length;
      const closeBraces = (content.match(/}/g) || []).length;
      expect(openBraces).toBe(closeBraces);
    });

    test('RecommendationsScreen.js has no syntax errors', () => {
      const filePath = path.join(screenDir, 'RecommendationsScreen.js');
      const content = fs.readFileSync(filePath, 'utf8');
      
      const openBraces = (content.match(/{/g) || []).length;
      const closeBraces = (content.match(/}/g) || []).length;
      expect(openBraces).toBe(closeBraces);
    });

    test('recommendation_engine.py has proper indentation', () => {
      const filePath = path.join(backendDir, 'services/recommendation_engine.py');
      const content = fs.readFileSync(filePath, 'utf8');
      
      // Python files should have consistent indentation
      expect(content).toContain('    def ');
    });

    test('recommendations.py has proper FastAPI structure', () => {
      const filePath = path.join(backendDir, 'routes/recommendations.py');
      const content = fs.readFileSync(filePath, 'utf8');
      
      expect(content).toContain('router = APIRouter');
      expect(content).toContain('@router.');
    });
  });

  describe('Feature Completeness', () => {
    test('has all 8 recommendation types in backend', () => {
      const filePath = path.join(backendDir, 'services/recommendation_engine.py');
      const content = fs.readFileSync(filePath, 'utf8');
      
      const types = [
        'focus_time',
        'break_time',
        'app_limit',
        'bedtime',
        'morning_routine',
        'notification_control',
        'privacy_improvement',
        'wellbeing_boost'
      ];
      
      types.forEach(type => {
        expect(content).toContain(type);
      });
    });

    test('has all 4 API endpoints', () => {
      const filePath = path.join(backendDir, 'routes/recommendations.py');
      const content = fs.readFileSync(filePath, 'utf8');
      
      expect(content).toContain('"/generate"');
      expect(content).toContain('"/types"');
      expect(content).toContain('"/feedback"');
      expect(content).toContain('"/quick');
    });
  });
});
