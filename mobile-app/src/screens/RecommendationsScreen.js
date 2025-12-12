/**
 * Recommendations Screen
 * 
 * Displays personalized AI-powered recommendations for digital wellbeing.
 * Features:
 * - Smart recommendation cards
 * - Category filtering
 * - Action buttons (accept, dismiss, snooze)
 * - Real-time updates via observer pattern
 * - Detailed recommendation view
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  StyleSheet,
  Modal,
  Dimensions,
  Alert
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import recommendationsService from '../services/recommendations';

const { width } = Dimensions.get('window');

const RecommendationsScreen = ({ navigation }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [filteredRecommendations, setFilteredRecommendations] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});

  // Categories for filtering
  const categories = [
    { id: 'all', name: 'All', icon: 'view-grid' },
    { id: 'productivity', name: 'Focus', icon: 'brain' },
    { id: 'health', name: 'Health', icon: 'heart' },
    { id: 'privacy', name: 'Privacy', icon: 'shield' },
    { id: 'balance', name: 'Balance', icon: 'scale-balance' }
  ];

  useEffect(() => {
    loadRecommendations();
    
    // Subscribe to recommendation updates
    const unsubscribe = recommendationsService.subscribe(handleRecommendationsUpdate);
    
    return () => {
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    filterRecommendations();
  }, [recommendations, selectedCategory]);

  /**
   * Handle recommendations update from service
   */
  const handleRecommendationsUpdate = (updatedRecommendations) => {
    setRecommendations(updatedRecommendations);
    updateStats();
  };

  /**
   * Load recommendations from service
   */
  const loadRecommendations = async () => {
    try {
      setLoading(true);
      await recommendationsService.refreshIfNeeded();
      const recs = recommendationsService.getActiveRecommendations();
      setRecommendations(recs);
      updateStats();
    } catch (error) {
      console.error('Failed to load recommendations:', error);
      Alert.alert('Error', 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Refresh recommendations (pull to refresh)
   */
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await recommendationsService.generateRecommendations();
      const recs = recommendationsService.getActiveRecommendations();
      setRecommendations(recs);
      updateStats();
    } catch (error) {
      console.error('Failed to refresh recommendations:', error);
      Alert.alert('Error', 'Failed to refresh recommendations');
    } finally {
      setRefreshing(false);
    }
  };

  /**
   * Filter recommendations by category
   */
  const filterRecommendations = () => {
    if (selectedCategory === 'all') {
      setFilteredRecommendations(recommendations);
    } else {
      const filtered = recommendations.filter(
        rec => rec.category === selectedCategory
      );
      setFilteredRecommendations(filtered);
    }
  };

  /**
   * Update statistics
   */
  const updateStats = () => {
    const newStats = recommendationsService.getStats();
    setStats(newStats);
  };

  /**
   * Handle accept recommendation
   */
  const handleAccept = async (recommendation) => {
    try {
      await recommendationsService.acceptRecommendation(recommendation.id);
      Alert.alert('Success', 'Recommendation accepted!');
      
      // Navigate to relevant screen if needed
      if (recommendation.action?.screen) {
        navigation.navigate(recommendation.action.screen);
      }
    } catch (error) {
      console.error('Failed to accept recommendation:', error);
      Alert.alert('Error', 'Failed to accept recommendation');
    }
  };

  /**
   * Handle dismiss recommendation
   */
  const handleDismiss = async (recommendation) => {
    Alert.alert(
      'Dismiss Recommendation',
      'Are you sure you want to dismiss this recommendation?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Dismiss',
          style: 'destructive',
          onPress: async () => {
            try {
              await recommendationsService.dismissRecommendation(recommendation.id);
            } catch (error) {
              console.error('Failed to dismiss recommendation:', error);
              Alert.alert('Error', 'Failed to dismiss recommendation');
            }
          }
        }
      ]
    );
  };

  /**
   * Handle snooze recommendation
   */
  const handleSnooze = async (recommendation) => {
    Alert.alert(
      'Snooze Recommendation',
      'Remind me in:',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: '1 Hour',
          onPress: async () => {
            try {
              await recommendationsService.snoozeRecommendation(recommendation.id, 60);
              Alert.alert('Success', 'Snoozed for 1 hour');
            } catch (error) {
              console.error('Failed to snooze:', error);
            }
          }
        },
        {
          text: '4 Hours',
          onPress: async () => {
            try {
              await recommendationsService.snoozeRecommendation(recommendation.id, 240);
              Alert.alert('Success', 'Snoozed for 4 hours');
            } catch (error) {
              console.error('Failed to snooze:', error);
            }
          }
        },
        {
          text: 'Tomorrow',
          onPress: async () => {
            try {
              await recommendationsService.snoozeRecommendation(recommendation.id, 1440);
              Alert.alert('Success', 'Snoozed until tomorrow');
            } catch (error) {
              console.error('Failed to snooze:', error);
            }
          }
        }
      ]
    );
  };

  /**
   * Get icon for recommendation type
   */
  const getTypeIcon = (type) => {
    const icons = {
      focus_time: 'brain',
      break_time: 'coffee',
      app_limit: 'timer-sand',
      bedtime: 'sleep',
      morning_routine: 'weather-sunset-up',
      notification_control: 'bell-off',
      privacy_improvement: 'shield-check',
      wellbeing_boost: 'emoticon-happy'
    };
    return icons[type] || 'lightbulb';
  };

  /**
   * Get color for recommendation priority
   */
  const getPriorityColor = (priority) => {
    if (priority >= 0.8) return '#E74C3C';
    if (priority >= 0.6) return '#F39C12';
    if (priority >= 0.4) return '#3498DB';
    return '#95A5A6';
  };

  /**
   * Get display name for recommendation type
   */
  const getTypeDisplayName = (type) => {
    const names = {
      focus_time: 'Focus Time',
      break_time: 'Take a Break',
      app_limit: 'App Limit',
      bedtime: 'Bedtime Routine',
      morning_routine: 'Morning Routine',
      notification_control: 'Notification Control',
      privacy_improvement: 'Privacy Improvement',
      wellbeing_boost: 'Wellbeing Boost'
    };
    return names[type] || type.replace(/_/g, ' ');
  };

  /**
   * Render recommendation card
   */
  const renderRecommendationCard = (recommendation) => {
    const priorityColor = getPriorityColor(recommendation.priority);
    const typeIcon = getTypeIcon(recommendation.type);

    return (
      <TouchableOpacity
        key={recommendation.id}
        style={[styles.card, { borderLeftColor: priorityColor }]}
        onPress={() => setSelectedRecommendation(recommendation)}
      >
        <View style={styles.cardHeader}>
          <View style={styles.iconContainer}>
            <Icon name={typeIcon} size={24} color={priorityColor} />
          </View>
          <View style={styles.headerText}>
            <Text style={styles.cardType}>
              {getTypeDisplayName(recommendation.type)}
            </Text>
            <Text style={styles.cardCategory}>{recommendation.category}</Text>
          </View>
          <View style={styles.priorityBadge}>
            <Text style={styles.priorityText}>
              {Math.round(recommendation.priority * 100)}%
            </Text>
          </View>
        </View>

        <Text style={styles.cardTitle}>{recommendation.title}</Text>
        <Text style={styles.cardDescription} numberOfLines={2}>
          {recommendation.description}
        </Text>

        <View style={styles.cardActions}>
          <TouchableOpacity
            style={[styles.actionButton, styles.acceptButton]}
            onPress={() => handleAccept(recommendation)}
          >
            <Icon name="check" size={18} color="#fff" />
            <Text style={styles.actionButtonText}>Accept</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.snoozeButton]}
            onPress={() => handleSnooze(recommendation)}
          >
            <Icon name="clock-outline" size={18} color="#fff" />
            <Text style={styles.actionButtonText}>Snooze</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.dismissButton]}
            onPress={() => handleDismiss(recommendation)}
          >
            <Icon name="close" size={18} color="#fff" />
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    );
  };

  /**
   * Render recommendation detail modal
   */
  const renderDetailModal = () => {
    if (!selectedRecommendation) return null;

    const priorityColor = getPriorityColor(selectedRecommendation.priority);
    const typeIcon = getTypeIcon(selectedRecommendation.type);

    return (
      <Modal
        visible={selectedRecommendation !== null}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setSelectedRecommendation(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <View style={[styles.modalIcon, { backgroundColor: priorityColor }]}>
                <Icon name={typeIcon} size={32} color="#fff" />
              </View>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setSelectedRecommendation(null)}
              >
                <Icon name="close" size={24} color="#2C3E50" />
              </TouchableOpacity>
            </View>

            <Text style={styles.modalType}>
              {getTypeDisplayName(selectedRecommendation.type)}
            </Text>
            <Text style={styles.modalTitle}>{selectedRecommendation.title}</Text>
            <Text style={styles.modalDescription}>
              {selectedRecommendation.description}
            </Text>

            {selectedRecommendation.reason && (
              <View style={styles.reasonSection}>
                <Text style={styles.reasonTitle}>Why this recommendation?</Text>
                <Text style={styles.reasonText}>{selectedRecommendation.reason}</Text>
              </View>
            )}

            {selectedRecommendation.metadata && (
              <View style={styles.metadataSection}>
                <Text style={styles.metadataTitle}>Details</Text>
                {Object.entries(selectedRecommendation.metadata).map(([key, value]) => (
                  <View key={key} style={styles.metadataRow}>
                    <Text style={styles.metadataKey}>
                      {key.replace(/_/g, ' ')}:
                    </Text>
                    <Text style={styles.metadataValue}>{String(value)}</Text>
                  </View>
                ))}
              </View>
            )}

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={[styles.modalActionButton, styles.modalAcceptButton]}
                onPress={() => {
                  handleAccept(selectedRecommendation);
                  setSelectedRecommendation(null);
                }}
              >
                <Icon name="check" size={20} color="#fff" />
                <Text style={styles.modalActionText}>Accept</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalActionButton, styles.modalSnoozeButton]}
                onPress={() => {
                  handleSnooze(selectedRecommendation);
                  setSelectedRecommendation(null);
                }}
              >
                <Icon name="clock-outline" size={20} color="#fff" />
                <Text style={styles.modalActionText}>Snooze</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalActionButton, styles.modalDismissButton]}
                onPress={() => {
                  handleDismiss(selectedRecommendation);
                  setSelectedRecommendation(null);
                }}
              >
                <Icon name="close" size={20} color="#fff" />
                <Text style={styles.modalActionText}>Dismiss</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Smart Recommendations</Text>
        <Text style={styles.headerSubtitle}>
          {filteredRecommendations.length} personalized suggestions
        </Text>
      </View>

      {/* Category Filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoryScroll}
        contentContainerStyle={styles.categoryContainer}
      >
        {categories.map(category => (
          <TouchableOpacity
            key={category.id}
            style={[
              styles.categoryChip,
              selectedCategory === category.id && styles.categoryChipActive
            ]}
            onPress={() => setSelectedCategory(category.id)}
          >
            <Icon
              name={category.icon}
              size={18}
              color={selectedCategory === category.id ? '#fff' : '#2C3E50'}
            />
            <Text
              style={[
                styles.categoryChipText,
                selectedCategory === category.id && styles.categoryChipTextActive
              ]}
            >
              {category.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Recommendations List */}
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#3498DB']}
          />
        }
      >
        {loading ? (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Loading recommendations...</Text>
          </View>
        ) : filteredRecommendations.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Icon name="emoticon-happy" size={64} color="#BDC3C7" />
            <Text style={styles.emptyText}>No recommendations right now</Text>
            <Text style={styles.emptySubtext}>
              {selectedCategory === 'all'
                ? "You're doing great! Check back later for new suggestions."
                : 'Try selecting a different category.'}
            </Text>
          </View>
        ) : (
          <View style={styles.cardsContainer}>
            {filteredRecommendations.map(renderRecommendationCard)}
          </View>
        )}
      </ScrollView>

      {/* Detail Modal */}
      {renderDetailModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ECF0F1'
  },
  header: {
    backgroundColor: '#fff',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0'
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 5
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#7F8C8D'
  },
  categoryScroll: {
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0'
  },
  categoryContainer: {
    paddingHorizontal: 15,
    paddingVertical: 15
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECF0F1',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10
  },
  categoryChipActive: {
    backgroundColor: '#3498DB'
  },
  categoryChipText: {
    marginLeft: 5,
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50'
  },
  categoryChipTextActive: {
    color: '#fff'
  },
  scrollView: {
    flex: 1
  },
  cardsContainer: {
    padding: 15
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#ECF0F1',
    justifyContent: 'center',
    alignItems: 'center'
  },
  headerText: {
    flex: 1,
    marginLeft: 12
  },
  cardType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 2
  },
  cardCategory: {
    fontSize: 12,
    color: '#7F8C8D',
    textTransform: 'capitalize'
  },
  priorityBadge: {
    backgroundColor: '#ECF0F1',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12
  },
  priorityText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#2C3E50'
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8
  },
  cardDescription: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
    marginBottom: 15
  },
  cardActions: {
    flexDirection: 'row',
    gap: 10
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 5
  },
  acceptButton: {
    backgroundColor: '#27AE60',
    flex: 1
  },
  snoozeButton: {
    backgroundColor: '#F39C12',
    flex: 1
  },
  dismissButton: {
    backgroundColor: '#E74C3C',
    paddingHorizontal: 12
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60
  },
  loadingText: {
    fontSize: 16,
    color: '#7F8C8D'
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
    paddingHorizontal: 40
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginTop: 20,
    marginBottom: 10,
    textAlign: 'center'
  },
  emptySubtext: {
    fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
    lineHeight: 20
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '80%'
  },
  modalHeader: {
    alignItems: 'center',
    marginBottom: 20
  },
  modalIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15
  },
  closeButton: {
    position: 'absolute',
    right: 0,
    top: 0,
    padding: 8
  },
  modalType: {
    fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
    marginBottom: 5
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#2C3E50',
    textAlign: 'center',
    marginBottom: 15
  },
  modalDescription: {
    fontSize: 16,
    color: '#2C3E50',
    lineHeight: 24,
    textAlign: 'center',
    marginBottom: 20
  },
  reasonSection: {
    backgroundColor: '#ECF0F1',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15
  },
  reasonTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8
  },
  reasonText: {
    fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20
  },
  metadataSection: {
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    paddingTop: 15,
    marginBottom: 20
  },
  metadataTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 10
  },
  metadataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6
  },
  metadataKey: {
    fontSize: 14,
    color: '#7F8C8D',
    textTransform: 'capitalize'
  },
  metadataValue: {
    fontSize: 14,
    color: '#2C3E50',
    fontWeight: '500'
  },
  modalActions: {
    flexDirection: 'row',
    gap: 10
  },
  modalActionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8
  },
  modalAcceptButton: {
    backgroundColor: '#27AE60'
  },
  modalSnoozeButton: {
    backgroundColor: '#F39C12'
  },
  modalDismissButton: {
    backgroundColor: '#E74C3C'
  },
  modalActionText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  }
});

export default RecommendationsScreen;
