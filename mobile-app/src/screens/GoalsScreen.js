/**
 * Goals Screen
 * Set and track productivity goals
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Modal,
  Alert,
  ActivityIndicator,
} from 'react-native';
import * as Progress from 'react-native-progress';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const GoalsScreen = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [newGoal, setNewGoal] = useState({
    type: 'daily_focus_time',
    target: '240',
    name: 'Daily Focus Time',
  });

  const userId = 'user123'; // TODO: Get from auth context

  const goalTypes = [
    { type: 'daily_focus_time', name: 'Daily Focus Time', unit: 'minutes', icon: '🎯' },
    { type: 'screen_time_limit', name: 'Screen Time Limit', unit: 'minutes', icon: '📱' },
    { type: 'weekly_focus_hours', name: 'Weekly Focus Hours', unit: 'hours', icon: '📅' },
    { type: 'daily_breaks', name: 'Daily Breaks', unit: 'breaks', icon: '☕' },
    { type: 'productivity_score', name: 'Productivity Score', unit: 'points', icon: '⭐' },
    { type: 'distraction_limit', name: 'Max Distractions', unit: 'count', icon: '🚫' },
  ];

  useEffect(() => {
    loadGoals();
  }, []);

  const loadGoals = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/goals`, {
        params: { user_id: userId }
      });
      setGoals(response.data.data);
    } catch (error) {
      console.error('Failed to load goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const createGoal = async () => {
    try {
      const targetValue = parseFloat(newGoal.target);
      if (isNaN(targetValue) || targetValue <= 0) {
        Alert.alert('Invalid Target', 'Please enter a valid positive number');
        return;
      }

      await axios.post(`${API_BASE_URL}/api/v1/analytics/goals`, {
        user_id: userId,
        goal_type: newGoal.type,
        target_value: targetValue,
        current_value: 0,
      });

      setModalVisible(false);
      setNewGoal({ type: 'daily_focus_time', target: '240', name: 'Daily Focus Time' });
      loadGoals();
      Alert.alert('Success', 'Goal created successfully!');
    } catch (error) {
      console.error('Failed to create goal:', error);
      Alert.alert('Error', 'Failed to create goal');
    }
  };

  const deleteGoal = (goalIndex) => {
    Alert.alert(
      'Delete Goal',
      'Are you sure you want to delete this goal?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            // Remove from local state (backend doesn't have delete endpoint yet)
            const updatedGoals = [...goals];
            updatedGoals.splice(goalIndex, 1);
            setGoals(updatedGoals);
          },
        },
      ]
    );
  };

  const getGoalIcon = (goalType) => {
    const goal = goalTypes.find(g => g.type === goalType);
    return goal ? goal.icon : '🎯';
  };

  const getGoalUnit = (goalType) => {
    const goal = goalTypes.find(g => g.type === goalType);
    return goal ? goal.unit : 'units';
  };

  const getStatusColor = (progressPercent) => {
    if (progressPercent >= 100) return '#4CAF50';
    if (progressPercent >= 75) return '#8BC34A';
    if (progressPercent >= 50) return '#FF9800';
    return '#F44336';
  };

  const getStatusText = (status) => {
    if (status === 'completed') return '✅ Completed';
    if (status === 'active') return '🎯 Active';
    return '⏸️ Inactive';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6200EE" />
        <Text style={styles.loadingText}>Loading goals...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Goals</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setModalVisible(true)}
        >
          <Text style={styles.addButtonText}>+ Add Goal</Text>
        </TouchableOpacity>
      </View>

      {/* Goals List */}
      <ScrollView style={styles.scrollView}>
        {goals.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>🎯</Text>
            <Text style={styles.emptyTitle}>No Goals Yet</Text>
            <Text style={styles.emptyText}>
              Set your first productivity goal to start tracking your progress!
            </Text>
            <TouchableOpacity
              style={styles.emptyButton}
              onPress={() => setModalVisible(true)}
            >
              <Text style={styles.emptyButtonText}>Create Your First Goal</Text>
            </TouchableOpacity>
          </View>
        ) : (
          goals.map((goal, index) => (
            <View key={index} style={styles.goalCard}>
              <View style={styles.goalHeader}>
                <Text style={styles.goalIcon}>{getGoalIcon(goal.goal_type)}</Text>
                <View style={styles.goalHeaderText}>
                  <Text style={styles.goalType}>
                    {goal.goal_type.replace(/_/g, ' ').toUpperCase()}
                  </Text>
                  <Text style={styles.goalStatus}>{getStatusText(goal.status)}</Text>
                </View>
                <TouchableOpacity
                  onPress={() => deleteGoal(index)}
                  style={styles.deleteButton}
                >
                  <Text style={styles.deleteButtonText}>🗑️</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.goalProgress}>
                <View style={styles.progressHeader}>
                  <Text style={styles.progressText}>
                    {goal.current_value.toFixed(0)} / {goal.target_value.toFixed(0)} {getGoalUnit(goal.goal_type)}
                  </Text>
                  <Text style={[
                    styles.progressPercent,
                    { color: getStatusColor(goal.progress_percent) }
                  ]}>
                    {goal.progress_percent.toFixed(0)}%
                  </Text>
                </View>
                <Progress.Bar
                  progress={Math.min(goal.progress_percent / 100, 1)}
                  width={null}
                  height={12}
                  color={getStatusColor(goal.progress_percent)}
                  unfilledColor="#E0E0E0"
                  borderWidth={0}
                  borderRadius={6}
                />
              </View>

              {goal.deadline && (
                <Text style={styles.goalDeadline}>
                  📅 Deadline: {new Date(goal.deadline).toLocaleDateString()}
                </Text>
              )}

              {goal.status === 'completed' && goal.completed_at && (
                <Text style={styles.completedText}>
                  ✅ Completed on {new Date(goal.completed_at).toLocaleDateString()}
                </Text>
              )}
            </View>
          ))
        )}
      </ScrollView>

      {/* Add Goal Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Create New Goal</Text>

            <Text style={styles.label}>Goal Type</Text>
            <ScrollView style={styles.goalTypeList} horizontal>
              {goalTypes.map((type) => (
                <TouchableOpacity
                  key={type.type}
                  style={[
                    styles.goalTypeChip,
                    newGoal.type === type.type && styles.goalTypeChipActive,
                  ]}
                  onPress={() => setNewGoal({ ...newGoal, type: type.type, name: type.name })}
                >
                  <Text style={styles.goalTypeIcon}>{type.icon}</Text>
                  <Text style={[
                    styles.goalTypeText,
                    newGoal.type === type.type && styles.goalTypeTextActive,
                  ]}>
                    {type.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <Text style={styles.label}>Target Value</Text>
            <TextInput
              style={styles.input}
              keyboardType="numeric"
              value={newGoal.target}
              onChangeText={(text) => setNewGoal({ ...newGoal, target: text })}
              placeholder="Enter target value"
            />
            <Text style={styles.hint}>
              Unit: {getGoalUnit(newGoal.type)}
            </Text>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.createButton]}
                onPress={createGoal}
              >
                <Text style={styles.createButtonText}>Create Goal</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#6200EE',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
    paddingHorizontal: 40,
  },
  emptyButton: {
    backgroundColor: '#6200EE',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emptyButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  goalCard: {
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
  goalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  goalIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  goalHeaderText: {
    flex: 1,
  },
  goalType: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginBottom: 4,
  },
  goalStatus: {
    fontSize: 12,
    color: '#666',
  },
  deleteButton: {
    padding: 8,
  },
  deleteButtonText: {
    fontSize: 20,
  },
  goalProgress: {
    marginBottom: 12,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  progressPercent: {
    fontSize: 14,
    fontWeight: '700',
  },
  goalDeadline: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
  },
  completedText: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '600',
    marginTop: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 24,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 16,
  },
  goalTypeList: {
    maxHeight: 120,
  },
  goalTypeChip: {
    flexDirection: 'column',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    marginRight: 12,
    minWidth: 100,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  goalTypeChipActive: {
    backgroundColor: '#E8E0FF',
    borderColor: '#6200EE',
  },
  goalTypeIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  goalTypeText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  goalTypeTextActive: {
    color: '#6200EE',
    fontWeight: '700',
  },
  input: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#FFFFFF',
  },
  hint: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    marginBottom: 24,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#F5F5F5',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  createButton: {
    backgroundColor: '#6200EE',
  },
  createButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});

export default GoalsScreen;
