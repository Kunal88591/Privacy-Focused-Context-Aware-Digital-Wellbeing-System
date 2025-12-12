import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  FlatList,
  TextInput,
  Modal,
  Platform,
  RefreshControl,
} from 'react-native';
import privacyService from '../services/privacy';

/**
 * Privacy Dashboard Screen - VPN, Tracker Blocking, Privacy Score
 */
const PrivacyDashboardScreen = () => {
  // State
  const [isVpnConnected, setIsVpnConnected] = useState(false);
  const [vpnStats, setVpnStats] = useState({
    trackersBlocked: 0,
    adsBlocked: 0,
    requestsTotal: 0,
    bytesProtected: 0,
  });
  const [privacyScore, setPrivacyScore] = useState(null);
  const [trackerStats, setTrackerStats] = useState(null);
  const [appPermissions, setAppPermissions] = useState([]);
  const [blockedDomains, setBlockedDomains] = useState([]);
  const [whitelistedDomains, setWhitelistedDomains] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [showAddDomainModal, setShowAddDomainModal] = useState(false);
  const [newDomain, setNewDomain] = useState('');
  const [domainType, setDomainType] = useState('blocked'); // blocked or whitelist
  
  // Initialize
  useEffect(() => {
    loadData();
    
    // Listen for privacy changes
    const unsubscribe = privacyService.addListener(handlePrivacyChange);
    
    return () => {
      unsubscribe();
    };
  }, []);
  
  /**
   * Load all privacy data
   */
  const loadData = async () => {
    setIsLoading(true);
    
    try {
      // Get VPN status
      const vpnStatus = privacyService.getVpnStatus();
      setIsVpnConnected(vpnStatus.isConnected);
      setVpnStats(vpnStatus.stats);
      
      // Calculate privacy score
      const score = await privacyService.calculatePrivacyScore();
      setPrivacyScore(score);
      
      // Get tracker stats
      const stats = await privacyService.getTrackerStats();
      setTrackerStats(stats);
      
      // Get app permissions
      const apps = await privacyService.getAppPermissions();
      setAppPermissions(apps);
      
      // Get custom domains
      setBlockedDomains(privacyService.getCustomBlockedDomains());
      setWhitelistedDomains(privacyService.getWhitelistedDomains());
      
    } catch (error) {
      console.error('Error loading privacy data:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  /**
   * Handle refresh
   */
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, []);
  
  /**
   * Handle privacy change events
   */
  const handlePrivacyChange = (status) => {
    setIsVpnConnected(status.isVpnConnected);
    setVpnStats(status.vpnStats);
    if (status.privacyScore) {
      setPrivacyScore(status.privacyScore);
    }
  };
  
  /**
   * Toggle VPN
   */
  const toggleVpn = async () => {
    try {
      if (isVpnConnected) {
        await privacyService.stopVpn();
      } else {
        // Check permission first
        const hasPermission = await privacyService.checkVpnPermission();
        
        if (!hasPermission) {
          const granted = await privacyService.requestVpnPermission();
          if (!granted) {
            Alert.alert(
              'Permission Required',
              'VPN permission is required to enable tracker blocking.'
            );
            return;
          }
        }
        
        await privacyService.startVpn();
      }
    } catch (error) {
      console.error('Error toggling VPN:', error);
      Alert.alert('Error', 'Failed to toggle VPN protection');
    }
  };
  
  /**
   * Add custom domain
   */
  const addDomain = async () => {
    if (!newDomain.trim()) {
      Alert.alert('Error', 'Please enter a domain');
      return;
    }
    
    const domain = newDomain.toLowerCase().trim();
    
    try {
      if (domainType === 'blocked') {
        await privacyService.addBlockedDomain(domain);
        setBlockedDomains(privacyService.getCustomBlockedDomains());
      } else {
        await privacyService.addWhitelistDomain(domain);
        setWhitelistedDomains(privacyService.getWhitelistedDomains());
      }
      
      setNewDomain('');
      setShowAddDomainModal(false);
    } catch (error) {
      Alert.alert('Error', 'Failed to add domain');
    }
  };
  
  /**
   * Remove domain
   */
  const removeDomain = async (domain, type) => {
    try {
      if (type === 'blocked') {
        await privacyService.removeBlockedDomain(domain);
        setBlockedDomains(privacyService.getCustomBlockedDomains());
      } else {
        await privacyService.removeWhitelistDomain(domain);
        setWhitelistedDomains(privacyService.getWhitelistedDomains());
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to remove domain');
    }
  };
  
  /**
   * Get score color
   */
  const getScoreColor = (score) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FFC107';
    if (score >= 40) return '#FF9800';
    return '#F44336';
  };
  
  /**
   * Get risk level color
   */
  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'LOW': return '#4CAF50';
      case 'MEDIUM': return '#FFC107';
      case 'HIGH': return '#FF9800';
      case 'CRITICAL': return '#F44336';
      default: return '#9E9E9E';
    }
  };
  
  /**
   * Format bytes
   */
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };
  
  /**
   * Render privacy score circle
   */
  const renderScoreCircle = () => {
    const score = privacyScore?.overall || 0;
    const color = getScoreColor(score);
    
    return (
      <View style={styles.scoreContainer}>
        <View style={[styles.scoreCircle, { borderColor: color }]}>
          <Text style={[styles.scoreText, { color }]}>{score}</Text>
          <Text style={styles.scoreLabel}>Privacy Score</Text>
        </View>
        
        <View style={[
          styles.riskBadge,
          { backgroundColor: getRiskLevelColor(privacyScore?.riskLevel) }
        ]}>
          <Text style={styles.riskText}>{privacyScore?.riskLevel || 'UNKNOWN'}</Text>
        </View>
      </View>
    );
  };
  
  /**
   * Render VPN card
   */
  const renderVpnCard = () => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>🛡️ VPN Protection</Text>
        <Switch
          value={isVpnConnected}
          onValueChange={toggleVpn}
          trackColor={{ false: '#E0E0E0', true: '#81C784' }}
          thumbColor={isVpnConnected ? '#4CAF50' : '#BDBDBD'}
        />
      </View>
      
      <Text style={styles.vpnStatus}>
        Status: {isVpnConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </Text>
      
      {isVpnConnected && (
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{vpnStats.trackersBlocked}</Text>
            <Text style={styles.statLabel}>Trackers Blocked</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{vpnStats.adsBlocked}</Text>
            <Text style={styles.statLabel}>Ads Blocked</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{formatBytes(vpnStats.bytesProtected)}</Text>
            <Text style={styles.statLabel}>Data Protected</Text>
          </View>
        </View>
      )}
    </View>
  );
  
  /**
   * Render score breakdown
   */
  const renderScoreBreakdown = () => {
    if (!privacyScore) return null;
    
    const components = [
      { key: 'vpn', label: 'VPN Protection', icon: '🛡️', value: privacyScore.vpn },
      { key: 'permissions', label: 'App Permissions', icon: '📱', value: privacyScore.permissions },
      { key: 'trackers', label: 'Tracker Blocking', icon: '🚫', value: privacyScore.trackers },
      { key: 'encryption', label: 'Data Encryption', icon: '🔐', value: privacyScore.encryption },
      { key: 'dataLeak', label: 'Data Leak Prevention', icon: '🔒', value: privacyScore.dataLeak },
    ];
    
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📊 Score Breakdown</Text>
        
        {components.map(comp => (
          <View key={comp.key} style={styles.breakdownRow}>
            <Text style={styles.breakdownLabel}>{comp.icon} {comp.label}</Text>
            <View style={styles.breakdownBar}>
              <View
                style={[
                  styles.breakdownFill,
                  {
                    width: `${comp.value}%`,
                    backgroundColor: getScoreColor(comp.value),
                  }
                ]}
              />
            </View>
            <Text style={styles.breakdownValue}>{comp.value}%</Text>
          </View>
        ))}
      </View>
    );
  };
  
  /**
   * Render recommendations
   */
  const renderRecommendations = () => {
    if (!privacyScore?.recommendations?.length) return null;
    
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>💡 Recommendations</Text>
        
        {privacyScore.recommendations.map((rec, index) => (
          <View key={index} style={styles.recommendationItem}>
            <Text style={styles.recommendationIcon}>•</Text>
            <Text style={styles.recommendationText}>{rec}</Text>
          </View>
        ))}
      </View>
    );
  };
  
  /**
   * Render tracker stats
   */
  const renderTrackerStats = () => {
    if (!trackerStats) return null;
    
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📈 Tracker Statistics</Text>
        
        <View style={styles.trackerSummary}>
          <View style={styles.trackerStat}>
            <Text style={styles.trackerValue}>{trackerStats.totalBlocked}</Text>
            <Text style={styles.trackerLabel}>Total Blocked</Text>
          </View>
          <View style={styles.trackerStat}>
            <Text style={styles.trackerValue}>{trackerStats.todayBlocked}</Text>
            <Text style={styles.trackerLabel}>Today</Text>
          </View>
          <View style={styles.trackerStat}>
            <Text style={styles.trackerValue}>{trackerStats.weekBlocked}</Text>
            <Text style={styles.trackerLabel}>This Week</Text>
          </View>
        </View>
        
        <Text style={styles.subTitle}>Categories</Text>
        {Object.entries(trackerStats.categories || {}).map(([category, count]) => (
          <View key={category} style={styles.categoryRow}>
            <Text style={styles.categoryName}>{category}</Text>
            <Text style={styles.categoryCount}>{count}</Text>
          </View>
        ))}
        
        {trackerStats.topDomains?.length > 0 && (
          <>
            <Text style={[styles.subTitle, { marginTop: 16 }]}>Top Blocked Domains</Text>
            {trackerStats.topDomains.map((item, index) => (
              <View key={index} style={styles.domainRow}>
                <Text style={styles.domainName}>{item.domain}</Text>
                <Text style={styles.domainCount}>{item.count} blocked</Text>
              </View>
            ))}
          </>
        )}
      </View>
    );
  };
  
  /**
   * Render app permissions tab
   */
  const renderAppPermissions = () => {
    const highRiskApps = appPermissions.filter(app => app.riskScore > 50);
    
    return (
      <View style={styles.tabContent}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>📱 High Risk Apps ({highRiskApps.length})</Text>
          
          {highRiskApps.length === 0 ? (
            <Text style={styles.emptyText}>No high-risk apps detected</Text>
          ) : (
            highRiskApps.slice(0, 10).map((app, index) => (
              <TouchableOpacity
                key={index}
                style={styles.appRow}
                onPress={() => privacyService.openAppSettings(app.packageName)}
              >
                <View style={styles.appInfo}>
                  <Text style={styles.appName}>{app.appName}</Text>
                  <Text style={styles.appPermCount}>
                    {app.permissionCount} permissions
                  </Text>
                </View>
                <View style={[
                  styles.riskScore,
                  { backgroundColor: getScoreColor(100 - app.riskScore) }
                ]}>
                  <Text style={styles.riskScoreText}>{app.riskScore}</Text>
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>
      </View>
    );
  };
  
  /**
   * Render domains tab
   */
  const renderDomainsTab = () => (
    <View style={styles.tabContent}>
      <TouchableOpacity
        style={styles.addButton}
        onPress={() => setShowAddDomainModal(true)}
      >
        <Text style={styles.addButtonText}>+ Add Custom Domain</Text>
      </TouchableOpacity>
      
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🚫 Custom Blocked Domains ({blockedDomains.length})</Text>
        
        {blockedDomains.length === 0 ? (
          <Text style={styles.emptyText}>No custom blocked domains</Text>
        ) : (
          blockedDomains.map((domain, index) => (
            <View key={index} style={styles.customDomainRow}>
              <Text style={styles.customDomainText}>{domain}</Text>
              <TouchableOpacity
                onPress={() => removeDomain(domain, 'blocked')}
              >
                <Text style={styles.removeButton}>✕</Text>
              </TouchableOpacity>
            </View>
          ))
        )}
      </View>
      
      <View style={styles.card}>
        <Text style={styles.cardTitle}>✅ Whitelisted Domains ({whitelistedDomains.length})</Text>
        
        {whitelistedDomains.length === 0 ? (
          <Text style={styles.emptyText}>No whitelisted domains</Text>
        ) : (
          whitelistedDomains.map((domain, index) => (
            <View key={index} style={styles.customDomainRow}>
              <Text style={styles.customDomainText}>{domain}</Text>
              <TouchableOpacity
                onPress={() => removeDomain(domain, 'whitelist')}
              >
                <Text style={styles.removeButton}>✕</Text>
              </TouchableOpacity>
            </View>
          ))
        )}
      </View>
      
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📋 Default Blocked ({privacyService.DEFAULT_TRACKERS.length + privacyService.DEFAULT_ADS.length})</Text>
        <Text style={styles.infoText}>
          {privacyService.DEFAULT_TRACKERS.length} tracker domains and{' '}
          {privacyService.DEFAULT_ADS.length} ad domains are blocked by default.
        </Text>
      </View>
    </View>
  );
  
  /**
   * Render add domain modal
   */
  const renderAddDomainModal = () => (
    <Modal
      visible={showAddDomainModal}
      transparent
      animationType="fade"
      onRequestClose={() => setShowAddDomainModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>Add Domain</Text>
          
          <View style={styles.domainTypeSelector}>
            <TouchableOpacity
              style={[
                styles.domainTypeButton,
                domainType === 'blocked' && styles.domainTypeActive
              ]}
              onPress={() => setDomainType('blocked')}
            >
              <Text style={[
                styles.domainTypeText,
                domainType === 'blocked' && styles.domainTypeTextActive
              ]}>Block</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.domainTypeButton,
                domainType === 'whitelist' && styles.domainTypeActive
              ]}
              onPress={() => setDomainType('whitelist')}
            >
              <Text style={[
                styles.domainTypeText,
                domainType === 'whitelist' && styles.domainTypeTextActive
              ]}>Whitelist</Text>
            </TouchableOpacity>
          </View>
          
          <TextInput
            style={styles.domainInput}
            placeholder="example.com"
            value={newDomain}
            onChangeText={setNewDomain}
            autoCapitalize="none"
            autoCorrect={false}
          />
          
          <View style={styles.modalButtons}>
            <TouchableOpacity
              style={styles.modalCancelButton}
              onPress={() => {
                setShowAddDomainModal(false);
                setNewDomain('');
              }}
            >
              <Text style={styles.modalCancelText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.modalAddButton}
              onPress={addDomain}
            >
              <Text style={styles.modalAddText}>Add</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
  
  /**
   * Render tab buttons
   */
  const renderTabButtons = () => (
    <View style={styles.tabBar}>
      <TouchableOpacity
        style={[styles.tab, activeTab === 'overview' && styles.activeTab]}
        onPress={() => setActiveTab('overview')}
      >
        <Text style={[styles.tabText, activeTab === 'overview' && styles.activeTabText]}>
          Overview
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.tab, activeTab === 'apps' && styles.activeTab]}
        onPress={() => setActiveTab('apps')}
      >
        <Text style={[styles.tabText, activeTab === 'apps' && styles.activeTabText]}>
          Apps
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.tab, activeTab === 'domains' && styles.activeTab]}
        onPress={() => setActiveTab('domains')}
      >
        <Text style={[styles.tabText, activeTab === 'domains' && styles.activeTabText]}>
          Domains
        </Text>
      </TouchableOpacity>
    </View>
  );
  
  /**
   * Render overview tab
   */
  const renderOverviewTab = () => (
    <View style={styles.tabContent}>
      {renderScoreCircle()}
      {renderVpnCard()}
      {renderScoreBreakdown()}
      {renderRecommendations()}
      {renderTrackerStats()}
    </View>
  );
  
  // Loading state
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading privacy data...</Text>
      </View>
    );
  }
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Privacy Dashboard</Text>
      </View>
      
      {renderTabButtons()}
      
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'apps' && renderAppPermissions()}
        {activeTab === 'domains' && renderDomainsTab()}
      </ScrollView>
      
      {renderAddDomainModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    backgroundColor: '#6200EE',
    paddingTop: 48,
    paddingBottom: 16,
    paddingHorizontal: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  tab: {
    flex: 1,
    paddingVertical: 14,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 3,
    borderBottomColor: '#6200EE',
  },
  tabText: {
    fontSize: 14,
    color: '#666',
  },
  activeTabText: {
    color: '#6200EE',
    fontWeight: '600',
  },
  tabContent: {},
  scoreContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  scoreCircle: {
    width: 150,
    height: 150,
    borderRadius: 75,
    borderWidth: 8,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  scoreText: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  riskBadge: {
    marginTop: 12,
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
  },
  riskText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 12,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  vpnStatus: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#6200EE',
  },
  statLabel: {
    fontSize: 11,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  breakdownRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  breakdownLabel: {
    flex: 1,
    fontSize: 13,
    color: '#333',
  },
  breakdownBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    marginHorizontal: 8,
    overflow: 'hidden',
  },
  breakdownFill: {
    height: '100%',
    borderRadius: 4,
  },
  breakdownValue: {
    width: 40,
    fontSize: 12,
    color: '#666',
    textAlign: 'right',
  },
  recommendationItem: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  recommendationIcon: {
    color: '#6200EE',
    marginRight: 8,
    fontSize: 16,
  },
  recommendationText: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  trackerSummary: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  trackerStat: {
    alignItems: 'center',
  },
  trackerValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#6200EE',
  },
  trackerLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  subTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  categoryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  categoryName: {
    fontSize: 14,
    color: '#333',
    textTransform: 'capitalize',
  },
  categoryCount: {
    fontSize: 14,
    color: '#6200EE',
    fontWeight: '600',
  },
  domainRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  domainName: {
    fontSize: 13,
    color: '#333',
  },
  domainCount: {
    fontSize: 12,
    color: '#666',
  },
  appRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  appInfo: {
    flex: 1,
  },
  appName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  appPermCount: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  riskScore: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  riskScoreText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    paddingVertical: 20,
  },
  addButton: {
    backgroundColor: '#6200EE',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  customDomainRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  customDomainText: {
    fontSize: 14,
    color: '#333',
  },
  removeButton: {
    color: '#F44336',
    fontSize: 18,
    padding: 4,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    width: '85%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
    textAlign: 'center',
  },
  domainTypeSelector: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  domainTypeButton: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  domainTypeActive: {
    backgroundColor: '#6200EE',
    borderColor: '#6200EE',
  },
  domainTypeText: {
    fontSize: 14,
    color: '#666',
  },
  domainTypeTextActive: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  domainInput: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    marginBottom: 16,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  modalCancelButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    marginRight: 12,
  },
  modalCancelText: {
    fontSize: 14,
    color: '#666',
  },
  modalAddButton: {
    backgroundColor: '#6200EE',
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  modalAddText: {
    fontSize: 14,
    color: '#FFFFFF',
    fontWeight: '600',
  },
});

export default PrivacyDashboardScreen;
