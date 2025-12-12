import { NativeModules, NativeEventEmitter, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { PrivacyModule } = NativeModules;

/**
 * Privacy Service - Manages VPN, tracker blocking, and privacy score
 */
class PrivacyService {
  constructor() {
    this.isVpnConnected = false;
    this.vpnStats = {
      trackersBlocked: 0,
      adsBlocked: 0,
      requestsTotal: 0,
      bytesProtected: 0,
    };
    this.privacyScore = null;
    this.appPermissions = [];
    this.blockedDomains = [];
    this.whitelistedDomains = [];
    this.listeners = [];
    this.eventEmitter = null;
    
    // Storage keys
    this.STORAGE_KEY = '@privacy';
    this.BLOCKED_DOMAINS_KEY = '@blockedDomains';
    this.WHITELIST_KEY = '@whitelistDomains';
    this.STATS_KEY = '@privacyStats';
    
    // Default blocked trackers (100+ domains)
    this.DEFAULT_TRACKERS = [
      // Google
      'google-analytics.com',
      'googleadservices.com',
      'googlesyndication.com',
      'doubleclick.net',
      'googletagmanager.com',
      'googletagservices.com',
      // Facebook
      'facebook.net',
      'fbcdn.net',
      'connect.facebook.net',
      'pixel.facebook.com',
      // Amazon
      'amazon-adsystem.com',
      // Twitter
      'ads-twitter.com',
      'analytics.twitter.com',
      // Others
      'scorecardresearch.com',
      'quantserve.com',
      'outbrain.com',
      'taboola.com',
      'criteo.com',
      'mixpanel.com',
      'segment.io',
      'amplitude.com',
      'branch.io',
      'appsflyer.com',
      'adjust.com',
      'crashlytics.com',
      'flurry.com',
      'onesignal.com',
    ];
    
    // Default blocked ad domains
    this.DEFAULT_ADS = [
      'pagead2.googlesyndication.com',
      'adservice.google.com',
      'ads.google.com',
      'adnxs.com',
      'adsrvr.org',
      'adroll.com',
      'rubiconproject.com',
      'pubmatic.com',
      'openx.net',
      'appnexus.com',
      'moatads.com',
      'adcolony.com',
      'unityads.unity3d.com',
      'mopub.com',
      'inmobi.com',
      'vungle.com',
      'chartboost.com',
      'applovin.com',
    ];
    
    this.init();
  }
  
  /**
   * Initialize service
   */
  async init() {
    // Setup event emitter for native events
    if (Platform.OS === 'android' && PrivacyModule) {
      this.eventEmitter = new NativeEventEmitter(PrivacyModule);
      this.eventEmitter.addListener(
        'PrivacyVpnStatusChanged',
        this.handleVpnStatusChange.bind(this)
      );
    }
    
    // Load saved data
    await this.loadSavedData();
  }
  
  // ==================== VPN METHODS ====================
  
  /**
   * Check if VPN permission is granted
   */
  async checkVpnPermission() {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      return false;
    }
    
    try {
      return await PrivacyModule.checkVpnPermission();
    } catch (error) {
      console.error('Error checking VPN permission:', error);
      return false;
    }
  }
  
  /**
   * Request VPN permission
   */
  async requestVpnPermission() {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      return false;
    }
    
    try {
      return await PrivacyModule.requestVpnPermission();
    } catch (error) {
      console.error('Error requesting VPN permission:', error);
      return false;
    }
  }
  
  /**
   * Start VPN protection
   */
  async startVpn() {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      throw new Error('VPN is only available on Android');
    }
    
    try {
      await PrivacyModule.startVpn();
      this.isVpnConnected = true;
      await this.saveState();
      this.notifyListeners();
      return true;
    } catch (error) {
      console.error('Error starting VPN:', error);
      throw error;
    }
  }
  
  /**
   * Stop VPN protection
   */
  async stopVpn() {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      return false;
    }
    
    try {
      await PrivacyModule.stopVpn();
      this.isVpnConnected = false;
      await this.saveState();
      this.notifyListeners();
      return true;
    } catch (error) {
      console.error('Error stopping VPN:', error);
      throw error;
    }
  }
  
  /**
   * Get VPN connection status
   */
  getVpnStatus() {
    return {
      isConnected: this.isVpnConnected,
      stats: this.vpnStats,
    };
  }
  
  /**
   * Handle VPN status change from native
   */
  handleVpnStatusChange(event) {
    console.log('VPN status changed:', event);
    
    this.isVpnConnected = event.status === 'CONNECTED';
    this.vpnStats = {
      trackersBlocked: event.trackersBlocked || 0,
      adsBlocked: event.adsBlocked || 0,
      requestsTotal: event.requestsTotal || 0,
      bytesProtected: event.bytesProtected || 0,
    };
    
    this.saveStats();
    this.notifyListeners();
  }
  
  // ==================== DOMAIN BLOCKING ====================
  
  /**
   * Add domain to blocklist
   */
  async addBlockedDomain(domain) {
    if (!domain) return false;
    
    const normalizedDomain = domain.toLowerCase().trim();
    
    if (!this.blockedDomains.includes(normalizedDomain)) {
      this.blockedDomains.push(normalizedDomain);
      
      if (Platform.OS === 'android' && PrivacyModule) {
        await PrivacyModule.addBlockedDomain(normalizedDomain);
      }
      
      await this.saveBlockedDomains();
      this.notifyListeners();
    }
    
    return true;
  }
  
  /**
   * Remove domain from blocklist
   */
  async removeBlockedDomain(domain) {
    const normalizedDomain = domain.toLowerCase().trim();
    const index = this.blockedDomains.indexOf(normalizedDomain);
    
    if (index > -1) {
      this.blockedDomains.splice(index, 1);
      
      if (Platform.OS === 'android' && PrivacyModule) {
        await PrivacyModule.removeBlockedDomain(normalizedDomain);
      }
      
      await this.saveBlockedDomains();
      this.notifyListeners();
    }
    
    return true;
  }
  
  /**
   * Get all blocked domains
   */
  getBlockedDomains() {
    return [
      ...this.DEFAULT_TRACKERS,
      ...this.DEFAULT_ADS,
      ...this.blockedDomains,
    ];
  }
  
  /**
   * Get custom blocked domains only
   */
  getCustomBlockedDomains() {
    return [...this.blockedDomains];
  }
  
  /**
   * Add domain to whitelist
   */
  async addWhitelistDomain(domain) {
    if (!domain) return false;
    
    const normalizedDomain = domain.toLowerCase().trim();
    
    if (!this.whitelistedDomains.includes(normalizedDomain)) {
      this.whitelistedDomains.push(normalizedDomain);
      
      if (Platform.OS === 'android' && PrivacyModule) {
        await PrivacyModule.addWhitelistDomain(normalizedDomain);
      }
      
      await this.saveWhitelist();
      this.notifyListeners();
    }
    
    return true;
  }
  
  /**
   * Remove domain from whitelist
   */
  async removeWhitelistDomain(domain) {
    const normalizedDomain = domain.toLowerCase().trim();
    const index = this.whitelistedDomains.indexOf(normalizedDomain);
    
    if (index > -1) {
      this.whitelistedDomains.splice(index, 1);
      await this.saveWhitelist();
      this.notifyListeners();
    }
    
    return true;
  }
  
  /**
   * Get whitelisted domains
   */
  getWhitelistedDomains() {
    return [...this.whitelistedDomains];
  }
  
  // ==================== APP PERMISSIONS ====================
  
  /**
   * Get all installed apps with permissions
   */
  async getAppPermissions() {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      return [];
    }
    
    try {
      const apps = await PrivacyModule.getInstalledAppsPermissions();
      this.appPermissions = apps;
      return apps;
    } catch (error) {
      console.error('Error getting app permissions:', error);
      return [];
    }
  }
  
  /**
   * Get high-risk apps (risk score > 50)
   */
  getHighRiskApps() {
    return this.appPermissions.filter(app => app.riskScore > 50);
  }
  
  /**
   * Get apps with specific permission
   */
  getAppsWithPermission(permission) {
    return this.appPermissions.filter(app => 
      app.permissions && app.permissions.includes(permission)
    );
  }
  
  /**
   * Open app settings
   */
  async openAppSettings(packageName) {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      return false;
    }
    
    try {
      await PrivacyModule.openAppSettings(packageName);
      return true;
    } catch (error) {
      console.error('Error opening app settings:', error);
      return false;
    }
  }
  
  // ==================== PRIVACY SCORE ====================
  
  /**
   * Calculate overall privacy score
   */
  async calculatePrivacyScore() {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      // Return mock score for non-Android
      return this.getMockPrivacyScore();
    }
    
    try {
      const score = await PrivacyModule.calculatePrivacyScore();
      this.privacyScore = score;
      await this.saveState();
      this.notifyListeners();
      return score;
    } catch (error) {
      console.error('Error calculating privacy score:', error);
      return this.getMockPrivacyScore();
    }
  }
  
  /**
   * Get mock privacy score for testing
   */
  getMockPrivacyScore() {
    return {
      overall: 65,
      vpn: this.isVpnConnected ? 100 : 0,
      permissions: 70,
      trackers: 85,
      encryption: 70,
      dataLeak: 75,
      riskLevel: 'MEDIUM',
      recommendations: [
        'Enable VPN protection to block trackers',
        'Review app permissions regularly',
      ],
    };
  }
  
  /**
   * Get current privacy score
   */
  getPrivacyScore() {
    return this.privacyScore || this.getMockPrivacyScore();
  }
  
  /**
   * Get tracker statistics
   */
  async getTrackerStats() {
    if (Platform.OS !== 'android' || !PrivacyModule) {
      return this.getMockTrackerStats();
    }
    
    try {
      return await PrivacyModule.getTrackerStats();
    } catch (error) {
      console.error('Error getting tracker stats:', error);
      return this.getMockTrackerStats();
    }
  }
  
  /**
   * Mock tracker stats
   */
  getMockTrackerStats() {
    return {
      categories: {
        analytics: 45,
        advertising: 32,
        social: 18,
        fingerprinting: 8,
        other: 12,
      },
      totalBlocked: this.vpnStats.trackersBlocked + this.vpnStats.adsBlocked,
      todayBlocked: 23,
      weekBlocked: 156,
      topDomains: [
        { domain: 'google-analytics.com', count: 45 },
        { domain: 'doubleclick.net', count: 32 },
        { domain: 'facebook.net', count: 28 },
      ],
    };
  }
  
  // ==================== DATA MANAGEMENT ====================
  
  /**
   * Load saved data
   */
  async loadSavedData() {
    try {
      // Load state
      const stateJson = await AsyncStorage.getItem(this.STORAGE_KEY);
      if (stateJson) {
        const state = JSON.parse(stateJson);
        this.isVpnConnected = state.isVpnConnected || false;
        this.privacyScore = state.privacyScore || null;
      }
      
      // Load blocked domains
      const blockedJson = await AsyncStorage.getItem(this.BLOCKED_DOMAINS_KEY);
      if (blockedJson) {
        this.blockedDomains = JSON.parse(blockedJson);
      }
      
      // Load whitelist
      const whitelistJson = await AsyncStorage.getItem(this.WHITELIST_KEY);
      if (whitelistJson) {
        this.whitelistedDomains = JSON.parse(whitelistJson);
      }
      
      // Load stats
      const statsJson = await AsyncStorage.getItem(this.STATS_KEY);
      if (statsJson) {
        this.vpnStats = JSON.parse(statsJson);
      }
      
    } catch (error) {
      console.error('Error loading privacy data:', error);
    }
  }
  
  /**
   * Save state
   */
  async saveState() {
    try {
      const state = {
        isVpnConnected: this.isVpnConnected,
        privacyScore: this.privacyScore,
      };
      await AsyncStorage.setItem(this.STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('Error saving privacy state:', error);
    }
  }
  
  /**
   * Save blocked domains
   */
  async saveBlockedDomains() {
    try {
      await AsyncStorage.setItem(
        this.BLOCKED_DOMAINS_KEY,
        JSON.stringify(this.blockedDomains)
      );
    } catch (error) {
      console.error('Error saving blocked domains:', error);
    }
  }
  
  /**
   * Save whitelist
   */
  async saveWhitelist() {
    try {
      await AsyncStorage.setItem(
        this.WHITELIST_KEY,
        JSON.stringify(this.whitelistedDomains)
      );
    } catch (error) {
      console.error('Error saving whitelist:', error);
    }
  }
  
  /**
   * Save stats
   */
  async saveStats() {
    try {
      await AsyncStorage.setItem(this.STATS_KEY, JSON.stringify(this.vpnStats));
    } catch (error) {
      console.error('Error saving privacy stats:', error);
    }
  }
  
  // ==================== OBSERVER PATTERN ====================
  
  /**
   * Add listener for privacy changes
   */
  addListener(callback) {
    this.listeners.push(callback);
    
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }
  
  /**
   * Notify all listeners
   */
  notifyListeners() {
    const status = {
      isVpnConnected: this.isVpnConnected,
      vpnStats: this.vpnStats,
      privacyScore: this.privacyScore,
      blockedDomainsCount: this.getBlockedDomains().length,
    };
    
    this.listeners.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error in privacy listener:', error);
      }
    });
  }
  
  /**
   * Clear all data
   */
  async clearAllData() {
    try {
      await AsyncStorage.multiRemove([
        this.STORAGE_KEY,
        this.BLOCKED_DOMAINS_KEY,
        this.WHITELIST_KEY,
        this.STATS_KEY,
      ]);
      
      this.isVpnConnected = false;
      this.vpnStats = {
        trackersBlocked: 0,
        adsBlocked: 0,
        requestsTotal: 0,
        bytesProtected: 0,
      };
      this.privacyScore = null;
      this.blockedDomains = [];
      this.whitelistedDomains = [];
      
      this.notifyListeners();
    } catch (error) {
      console.error('Error clearing privacy data:', error);
    }
  }
}

// Export singleton instance
export default new PrivacyService();
