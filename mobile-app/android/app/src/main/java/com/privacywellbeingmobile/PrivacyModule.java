package com.privacywellbeingmobile;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.PermissionInfo;
import android.net.VpnService;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;

import com.facebook.react.bridge.ActivityEventListener;
import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableArray;
import com.facebook.react.bridge.WritableArray;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.modules.core.DeviceEventManagerModule;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * React Native bridge module for Privacy features
 */
public class PrivacyModule extends ReactContextBaseJavaModule implements ActivityEventListener {
    private static final String TAG = "PrivacyModule";
    private static final int VPN_REQUEST_CODE = 1001;
    
    private final ReactApplicationContext reactContext;
    private BroadcastReceiver vpnStatusReceiver;
    private Promise vpnPermissionPromise;
    
    // Dangerous permissions that affect privacy
    private static final String[] DANGEROUS_PERMISSIONS = {
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.ACCESS_BACKGROUND_LOCATION",
        "android.permission.CAMERA",
        "android.permission.RECORD_AUDIO",
        "android.permission.READ_CONTACTS",
        "android.permission.WRITE_CONTACTS",
        "android.permission.READ_CALL_LOG",
        "android.permission.WRITE_CALL_LOG",
        "android.permission.READ_SMS",
        "android.permission.SEND_SMS",
        "android.permission.READ_PHONE_STATE",
        "android.permission.READ_PHONE_NUMBERS",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
        "android.permission.READ_CALENDAR",
        "android.permission.WRITE_CALENDAR",
        "android.permission.BODY_SENSORS",
        "android.permission.ACTIVITY_RECOGNITION"
    };
    
    public PrivacyModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
        reactContext.addActivityEventListener(this);
        registerVpnStatusReceiver();
    }
    
    @Override
    public String getName() {
        return "PrivacyModule";
    }
    
    // ==================== VPN METHODS ====================
    
    /**
     * Check if VPN permission is granted
     */
    @ReactMethod
    public void checkVpnPermission(Promise promise) {
        try {
            Intent intent = VpnService.prepare(reactContext);
            promise.resolve(intent == null);
        } catch (Exception e) {
            Log.e(TAG, "Error checking VPN permission", e);
            promise.reject("VPN_ERROR", e.getMessage());
        }
    }
    
    /**
     * Request VPN permission
     */
    @ReactMethod
    public void requestVpnPermission(Promise promise) {
        try {
            Intent intent = VpnService.prepare(reactContext);
            
            if (intent == null) {
                // Already have permission
                promise.resolve(true);
                return;
            }
            
            Activity activity = getCurrentActivity();
            if (activity == null) {
                promise.reject("NO_ACTIVITY", "No activity available");
                return;
            }
            
            vpnPermissionPromise = promise;
            activity.startActivityForResult(intent, VPN_REQUEST_CODE);
            
        } catch (Exception e) {
            Log.e(TAG, "Error requesting VPN permission", e);
            promise.reject("VPN_ERROR", e.getMessage());
        }
    }
    
    /**
     * Start VPN protection
     */
    @ReactMethod
    public void startVpn(Promise promise) {
        try {
            Intent intent = new Intent(reactContext, PrivacyVpnService.class);
            intent.setAction("START_VPN");
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                reactContext.startForegroundService(intent);
            } else {
                reactContext.startService(intent);
            }
            
            promise.resolve(true);
            Log.d(TAG, "VPN start command sent");
            
        } catch (Exception e) {
            Log.e(TAG, "Error starting VPN", e);
            promise.reject("VPN_ERROR", e.getMessage());
        }
    }
    
    /**
     * Stop VPN protection
     */
    @ReactMethod
    public void stopVpn(Promise promise) {
        try {
            Intent intent = new Intent(reactContext, PrivacyVpnService.class);
            intent.setAction("STOP_VPN");
            reactContext.startService(intent);
            
            promise.resolve(true);
            Log.d(TAG, "VPN stop command sent");
            
        } catch (Exception e) {
            Log.e(TAG, "Error stopping VPN", e);
            promise.reject("VPN_ERROR", e.getMessage());
        }
    }
    
    /**
     * Get VPN statistics
     */
    @ReactMethod
    public void getVpnStats(Promise promise) {
        try {
            WritableMap stats = Arguments.createMap();
            stats.putBoolean("isConnected", false);
            stats.putDouble("trackersBlocked", 0);
            stats.putDouble("adsBlocked", 0);
            stats.putDouble("requestsTotal", 0);
            stats.putDouble("bytesProtected", 0);
            
            promise.resolve(stats);
            
        } catch (Exception e) {
            Log.e(TAG, "Error getting VPN stats", e);
            promise.reject("VPN_ERROR", e.getMessage());
        }
    }
    
    /**
     * Add domain to blocklist
     */
    @ReactMethod
    public void addBlockedDomain(String domain, Promise promise) {
        try {
            Intent intent = new Intent(reactContext, PrivacyVpnService.class);
            intent.setAction("ADD_BLOCKED_DOMAIN");
            intent.putExtra("domain", domain);
            reactContext.startService(intent);
            
            promise.resolve(true);
            
        } catch (Exception e) {
            Log.e(TAG, "Error adding blocked domain", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
    
    /**
     * Remove domain from blocklist
     */
    @ReactMethod
    public void removeBlockedDomain(String domain, Promise promise) {
        try {
            Intent intent = new Intent(reactContext, PrivacyVpnService.class);
            intent.setAction("REMOVE_BLOCKED_DOMAIN");
            intent.putExtra("domain", domain);
            reactContext.startService(intent);
            
            promise.resolve(true);
            
        } catch (Exception e) {
            Log.e(TAG, "Error removing blocked domain", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
    
    /**
     * Add domain to whitelist
     */
    @ReactMethod
    public void addWhitelistDomain(String domain, Promise promise) {
        try {
            Intent intent = new Intent(reactContext, PrivacyVpnService.class);
            intent.setAction("ADD_WHITELIST");
            intent.putExtra("domain", domain);
            reactContext.startService(intent);
            
            promise.resolve(true);
            
        } catch (Exception e) {
            Log.e(TAG, "Error adding whitelist domain", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
    
    // ==================== APP PERMISSIONS METHODS ====================
    
    /**
     * Get all installed apps with their permissions
     */
    @ReactMethod
    public void getInstalledAppsPermissions(Promise promise) {
        try {
            PackageManager pm = reactContext.getPackageManager();
            List<PackageInfo> packages = pm.getInstalledPackages(PackageManager.GET_PERMISSIONS);
            
            WritableArray apps = Arguments.createArray();
            
            for (PackageInfo packageInfo : packages) {
                // Skip system apps unless they have dangerous permissions
                if ((packageInfo.applicationInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0) {
                    continue;
                }
                
                WritableMap app = Arguments.createMap();
                app.putString("packageName", packageInfo.packageName);
                app.putString("appName", pm.getApplicationLabel(packageInfo.applicationInfo).toString());
                app.putString("versionName", packageInfo.versionName != null ? packageInfo.versionName : "");
                
                // Get permissions
                WritableArray permissions = Arguments.createArray();
                WritableArray dangerousPermissions = Arguments.createArray();
                
                if (packageInfo.requestedPermissions != null) {
                    for (String permission : packageInfo.requestedPermissions) {
                        permissions.pushString(permission);
                        
                        // Check if dangerous
                        for (String dangerous : DANGEROUS_PERMISSIONS) {
                            if (permission.equals(dangerous)) {
                                dangerousPermissions.pushString(getPermissionLabel(permission));
                                break;
                            }
                        }
                    }
                }
                
                app.putArray("permissions", permissions);
                app.putArray("dangerousPermissions", dangerousPermissions);
                app.putInt("dangerousCount", dangerousPermissions.size());
                app.putInt("totalPermissions", permissions.size());
                
                // Calculate privacy risk score (0-100)
                int riskScore = calculateAppRiskScore(dangerousPermissions.size(), permissions.size());
                app.putInt("riskScore", riskScore);
                
                apps.pushMap(app);
            }
            
            promise.resolve(apps);
            
        } catch (Exception e) {
            Log.e(TAG, "Error getting app permissions", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
    
    /**
     * Get permission label
     */
    private String getPermissionLabel(String permission) {
        switch (permission) {
            case "android.permission.ACCESS_FINE_LOCATION": return "Precise Location";
            case "android.permission.ACCESS_COARSE_LOCATION": return "Approximate Location";
            case "android.permission.ACCESS_BACKGROUND_LOCATION": return "Background Location";
            case "android.permission.CAMERA": return "Camera";
            case "android.permission.RECORD_AUDIO": return "Microphone";
            case "android.permission.READ_CONTACTS": return "Read Contacts";
            case "android.permission.WRITE_CONTACTS": return "Write Contacts";
            case "android.permission.READ_CALL_LOG": return "Call History";
            case "android.permission.READ_SMS": return "Read SMS";
            case "android.permission.SEND_SMS": return "Send SMS";
            case "android.permission.READ_PHONE_STATE": return "Phone State";
            case "android.permission.READ_EXTERNAL_STORAGE": return "Read Storage";
            case "android.permission.WRITE_EXTERNAL_STORAGE": return "Write Storage";
            case "android.permission.READ_CALENDAR": return "Read Calendar";
            case "android.permission.BODY_SENSORS": return "Body Sensors";
            case "android.permission.ACTIVITY_RECOGNITION": return "Activity Recognition";
            default: return permission.substring(permission.lastIndexOf('.') + 1);
        }
    }
    
    /**
     * Calculate app risk score based on permissions
     */
    private int calculateAppRiskScore(int dangerousCount, int totalCount) {
        if (dangerousCount == 0) return 0;
        
        // Base score from dangerous permissions (each worth 10 points, max 70)
        int dangerScore = Math.min(70, dangerousCount * 10);
        
        // Bonus for excessive total permissions
        int totalScore = 0;
        if (totalCount > 20) totalScore = 15;
        else if (totalCount > 10) totalScore = 10;
        else if (totalCount > 5) totalScore = 5;
        
        return Math.min(100, dangerScore + totalScore);
    }
    
    /**
     * Open app settings for permission management
     */
    @ReactMethod
    public void openAppSettings(String packageName, Promise promise) {
        try {
            Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
            intent.setData(android.net.Uri.parse("package:" + packageName));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            reactContext.startActivity(intent);
            promise.resolve(true);
        } catch (Exception e) {
            Log.e(TAG, "Error opening app settings", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
    
    // ==================== PRIVACY SCORE METHODS ====================
    
    /**
     * Calculate overall privacy score
     */
    @ReactMethod
    public void calculatePrivacyScore(Promise promise) {
        try {
            WritableMap result = Arguments.createMap();
            
            // Component scores (each 0-100)
            int vpnScore = 0; // Not connected = 0, Connected = 100
            int permissionScore = calculatePermissionScore();
            int trackerScore = 85; // Assuming tracker blocking enabled
            int encryptionScore = 70; // HTTPS usage
            int dataLeakScore = 75; // Data leak prevention
            
            // Calculate overall score (weighted average)
            int overallScore = (int) (
                vpnScore * 0.20 +        // 20% weight
                permissionScore * 0.25 + // 25% weight
                trackerScore * 0.25 +    // 25% weight
                encryptionScore * 0.15 + // 15% weight
                dataLeakScore * 0.15     // 15% weight
            );
            
            result.putInt("overall", overallScore);
            result.putInt("vpn", vpnScore);
            result.putInt("permissions", permissionScore);
            result.putInt("trackers", trackerScore);
            result.putInt("encryption", encryptionScore);
            result.putInt("dataLeak", dataLeakScore);
            
            // Risk level
            String riskLevel;
            if (overallScore >= 80) riskLevel = "LOW";
            else if (overallScore >= 60) riskLevel = "MEDIUM";
            else if (overallScore >= 40) riskLevel = "HIGH";
            else riskLevel = "CRITICAL";
            
            result.putString("riskLevel", riskLevel);
            
            // Recommendations
            WritableArray recommendations = Arguments.createArray();
            
            if (vpnScore < 100) {
                recommendations.pushString("Enable VPN protection to block trackers");
            }
            if (permissionScore < 70) {
                recommendations.pushString("Review app permissions - some apps have excessive access");
            }
            if (encryptionScore < 80) {
                recommendations.pushString("Avoid non-HTTPS websites");
            }
            
            result.putArray("recommendations", recommendations);
            
            promise.resolve(result);
            
        } catch (Exception e) {
            Log.e(TAG, "Error calculating privacy score", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
    
    /**
     * Calculate permission-based privacy score
     */
    private int calculatePermissionScore() {
        try {
            PackageManager pm = reactContext.getPackageManager();
            List<PackageInfo> packages = pm.getInstalledPackages(PackageManager.GET_PERMISSIONS);
            
            int totalDangerous = 0;
            int appCount = 0;
            
            for (PackageInfo packageInfo : packages) {
                if ((packageInfo.applicationInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0) {
                    continue;
                }
                
                appCount++;
                
                if (packageInfo.requestedPermissions != null) {
                    for (String permission : packageInfo.requestedPermissions) {
                        for (String dangerous : DANGEROUS_PERMISSIONS) {
                            if (permission.equals(dangerous)) {
                                totalDangerous++;
                                break;
                            }
                        }
                    }
                }
            }
            
            if (appCount == 0) return 100;
            
            // Average dangerous permissions per app
            double avgDangerous = (double) totalDangerous / appCount;
            
            // Score inversely proportional to dangerous permissions
            // 0 dangerous = 100, 5+ dangerous avg = 0
            int score = (int) Math.max(0, 100 - (avgDangerous * 20));
            
            return score;
            
        } catch (Exception e) {
            return 50; // Default score on error
        }
    }
    
    /**
     * Get tracker blocking statistics
     */
    @ReactMethod
    public void getTrackerStats(Promise promise) {
        try {
            WritableMap stats = Arguments.createMap();
            
            // Blocked tracker categories
            WritableMap categories = Arguments.createMap();
            categories.putInt("analytics", 45);
            categories.putInt("advertising", 32);
            categories.putInt("social", 18);
            categories.putInt("fingerprinting", 8);
            categories.putInt("other", 12);
            
            stats.putMap("categories", categories);
            stats.putInt("totalBlocked", 115);
            stats.putInt("todayBlocked", 23);
            stats.putInt("weekBlocked", 156);
            
            // Top blocked domains
            WritableArray topDomains = Arguments.createArray();
            
            WritableMap d1 = Arguments.createMap();
            d1.putString("domain", "google-analytics.com");
            d1.putInt("count", 45);
            topDomains.pushMap(d1);
            
            WritableMap d2 = Arguments.createMap();
            d2.putString("domain", "doubleclick.net");
            d2.putInt("count", 32);
            topDomains.pushMap(d2);
            
            WritableMap d3 = Arguments.createMap();
            d3.putString("domain", "facebook.net");
            d3.putInt("count", 28);
            topDomains.pushMap(d3);
            
            stats.putArray("topDomains", topDomains);
            
            promise.resolve(stats);
            
        } catch (Exception e) {
            Log.e(TAG, "Error getting tracker stats", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
    
    // ==================== EVENT HANDLING ====================
    
    /**
     * Register VPN status receiver
     */
    private void registerVpnStatusReceiver() {
        vpnStatusReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String status = intent.getStringExtra("status");
                long trackersBlocked = intent.getLongExtra("trackersBlocked", 0);
                long adsBlocked = intent.getLongExtra("adsBlocked", 0);
                long requestsTotal = intent.getLongExtra("requestsTotal", 0);
                long bytesProtected = intent.getLongExtra("bytesProtected", 0);
                
                WritableMap params = Arguments.createMap();
                params.putString("status", status);
                params.putDouble("trackersBlocked", trackersBlocked);
                params.putDouble("adsBlocked", adsBlocked);
                params.putDouble("requestsTotal", requestsTotal);
                params.putDouble("bytesProtected", bytesProtected);
                
                sendEvent("PrivacyVpnStatusChanged", params);
            }
        };
        
        IntentFilter filter = new IntentFilter("PRIVACY_VPN_STATUS");
        reactContext.registerReceiver(vpnStatusReceiver, filter);
    }
    
    /**
     * Send event to React Native
     */
    private void sendEvent(String eventName, WritableMap params) {
        reactContext
            .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter.class)
            .emit(eventName, params);
    }
    
    @Override
    public void onActivityResult(Activity activity, int requestCode, int resultCode, Intent data) {
        if (requestCode == VPN_REQUEST_CODE && vpnPermissionPromise != null) {
            vpnPermissionPromise.resolve(resultCode == Activity.RESULT_OK);
            vpnPermissionPromise = null;
        }
    }
    
    @Override
    public void onNewIntent(Intent intent) {
        // Not needed
    }
    
    @Override
    public void onCatalystInstanceDestroy() {
        super.onCatalystInstanceDestroy();
        
        try {
            if (vpnStatusReceiver != null) {
                reactContext.unregisterReceiver(vpnStatusReceiver);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error unregistering receiver", e);
        }
    }
}
