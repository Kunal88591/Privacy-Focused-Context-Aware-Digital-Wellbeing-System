/**
 * Privacy Screen
 * Control privacy features (VPN, caller masking, etc.)
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Switch,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { privacyAPI } from '../services/api';

const PrivacyScreen = () => {
  const [privacyStatus, setPrivacyStatus] = useState({
    vpn_enabled: false,
    caller_id_masked: false,
    location_spoofed: false,
    auto_wipe_armed: true,
    untrusted_network_count: 0,
    encryption_status: 'active',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPrivacyStatus();
  }, []);

  const loadPrivacyStatus = async () => {
    try {
      const status = await privacyAPI.getStatus();
      setPrivacyStatus(status);
    } catch (error) {
      console.error('Error loading privacy status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVPNToggle = async (value) => {
    try {
      if (value) {
        await privacyAPI.enableVPN();
      } else {
        await privacyAPI.disableVPN();
      }
      setPrivacyStatus({ ...privacyStatus, vpn_enabled: value });
    } catch (error) {
      console.error('Error toggling VPN:', error);
      Alert.alert('Error', 'Failed to toggle VPN');
    }
  };

  const handleCallerMaskToggle = async (value) => {
    try {
      await privacyAPI.toggleCallerMask(value);
      setPrivacyStatus({ ...privacyStatus, caller_id_masked: value });
    } catch (error) {
      console.error('Error toggling caller mask:', error);
      Alert.alert('Error', 'Failed to toggle caller ID masking');
    }
  };

  const handleLocationSpoofToggle = async (value) => {
    try {
      await privacyAPI.toggleLocationSpoof(value);
      setPrivacyStatus({ ...privacyStatus, location_spoofed: value });
    } catch (error) {
      console.error('Error toggling location spoof:', error);
      Alert.alert('Error', 'Failed to toggle location spoofing');
    }
  };

  const getPrivacyScore = () => {
    let score = 0;
    if (privacyStatus.vpn_enabled) score += 25;
    if (privacyStatus.caller_id_masked) score += 25;
    if (privacyStatus.location_spoofed) score += 25;
    if (privacyStatus.encryption_status === 'active') score += 25;
    return score;
  };

  const privacyScore = getPrivacyScore();

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🔒 Privacy Controls</Text>
        <Text style={styles.subtitle}>Your Digital Bodyguard</Text>
      </View>

      {/* Privacy Score */}
      <View style={styles.scoreCard}>
        <Text style={styles.scoreLabel}>Privacy Score</Text>
        <Text style={[styles.scoreValue, { color: privacyScore >= 75 ? '#4CAF50' : privacyScore >= 50 ? '#FF9800' : '#F44336' }]}>
          {privacyScore}%
        </Text>
        <View style={styles.scoreBar}>
          <View style={[styles.scoreBarFill, { width: `${privacyScore}%`, backgroundColor: privacyScore >= 75 ? '#4CAF50' : privacyScore >= 50 ? '#FF9800' : '#F44336' }]} />
        </View>
      </View>

      {/* VPN Control */}
      <View style={styles.controlCard}>
        <View style={styles.controlHeader}>
          <View style={styles.controlInfo}>
            <Text style={styles.controlTitle}>🌐 VPN Protection</Text>
            <Text style={styles.controlDescription}>
              Secure all network traffic through encrypted tunnel
            </Text>
          </View>
          <Switch
            value={privacyStatus.vpn_enabled}
            onValueChange={handleVPNToggle}
            trackColor={{ false: '#ccc', true: '#4CAF50' }}
          />
        </View>
        {privacyStatus.vpn_enabled && (
          <View style={styles.statusInfo}>
            <Text style={styles.statusText}>✅ Connected to US-West-1</Text>
            <Text style={styles.statusSubtext}>IP: 10.8.0.5</Text>
          </View>
        )}
      </View>

      {/* Caller ID Masking */}
      <View style={styles.controlCard}>
        <View style={styles.controlHeader}>
          <View style={styles.controlInfo}>
            <Text style={styles.controlTitle}>🎭 Caller ID Masking</Text>
            <Text style={styles.controlDescription}>
              Hide your phone number from outgoing calls
            </Text>
          </View>
          <Switch
            value={privacyStatus.caller_id_masked}
            onValueChange={handleCallerMaskToggle}
            trackColor={{ false: '#ccc', true: '#4CAF50' }}
          />
        </View>
      </View>

      {/* Location Spoofing */}
      <View style={styles.controlCard}>
        <View style={styles.controlHeader}>
          <View style={styles.controlInfo}>
            <Text style={styles.controlTitle}>📍 Location Spoofing</Text>
            <Text style={styles.controlDescription}>
              Randomize GPS data to protect location privacy
            </Text>
          </View>
          <Switch
            value={privacyStatus.location_spoofed}
            onValueChange={handleLocationSpoofToggle}
            trackColor={{ false: '#ccc', true: '#4CAF50' }}
          />
        </View>
      </View>

      {/* Auto-Wipe Status */}
      <View style={styles.controlCard}>
        <View style={styles.controlHeader}>
          <View style={styles.controlInfo}>
            <Text style={styles.controlTitle}>🔥 Auto-Wipe Protection</Text>
            <Text style={styles.controlDescription}>
              Automatically erase data after 3 untrusted networks
            </Text>
          </View>
          <View style={styles.autoWipeStatus}>
            <Text style={styles.autoWipeText}>
              {privacyStatus.untrusted_network_count}/3
            </Text>
          </View>
        </View>
        {privacyStatus.untrusted_network_count > 0 && (
          <View style={styles.warningInfo}>
            <Text style={styles.warningText}>
              ⚠️ Warning: {privacyStatus.untrusted_network_count} untrusted network(s) detected
            </Text>
          </View>
        )}
      </View>

      {/* Encryption Status */}
      <View style={styles.controlCard}>
        <View style={styles.controlHeader}>
          <View style={styles.controlInfo}>
            <Text style={styles.controlTitle}>🔐 Data Encryption</Text>
            <Text style={styles.controlDescription}>
              End-to-end encryption for all data
            </Text>
          </View>
          <View style={[styles.statusBadge, styles.activeBadge]}>
            <Text style={styles.statusBadgeText}>Active</Text>
          </View>
        </View>
      </View>

      {/* Privacy Tips */}
      <View style={styles.tipsCard}>
        <Text style={styles.tipsTitle}>💡 Privacy Tips</Text>
        <Text style={styles.tipText}>• Enable VPN on public Wi-Fi</Text>
        <Text style={styles.tipText}>• Use caller ID masking for unknown contacts</Text>
        <Text style={styles.tipText}>• Monitor auto-wipe counter regularly</Text>
        <Text style={styles.tipText}>• Keep encryption always active</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: 'white',
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  scoreCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 20,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  scoreLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  scoreBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  scoreBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  controlCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 20,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 2,
  },
  controlHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  controlInfo: {
    flex: 1,
    marginRight: 16,
  },
  controlTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  controlDescription: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
  },
  statusInfo: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  statusText: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '600',
  },
  statusSubtext: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  warningInfo: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#FFE0B2',
    backgroundColor: '#FFF3E0',
    padding: 8,
    borderRadius: 4,
  },
  warningText: {
    fontSize: 13,
    color: '#F57C00',
  },
  autoWipeStatus: {
    backgroundColor: '#FFF3E0',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  autoWipeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#F57C00',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  activeBadge: {
    backgroundColor: '#E8F5E9',
  },
  statusBadgeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4CAF50',
  },
  tipsCard: {
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 20,
    marginBottom: 20,
    marginTop: 8,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1976D2',
    marginBottom: 12,
  },
  tipText: {
    fontSize: 14,
    color: '#1565C0',
    lineHeight: 24,
  },
});

export default PrivacyScreen;
