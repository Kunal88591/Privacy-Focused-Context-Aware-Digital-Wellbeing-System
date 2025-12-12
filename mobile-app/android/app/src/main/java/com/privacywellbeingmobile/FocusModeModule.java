package com.privacywellbeingmobile;

import android.app.AppOpsManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;

import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableArray;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.modules.core.DeviceEventManagerModule;

/**
 * React Native bridge module for Focus Mode functionality
 */
public class FocusModeModule extends ReactContextBaseJavaModule {
    private static final String TAG = "FocusModeModule";
    private final ReactApplicationContext reactContext;
    private BroadcastReceiver statusReceiver;
    
    public FocusModeModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
        registerStatusReceiver();
    }
    
    @Override
    public String getName() {
        return "FocusModeModule";
    }
    
    /**
     * Check if app has PACKAGE_USAGE_STATS permission
     */
    @ReactMethod
    public void checkUsageStatsPermission(Promise promise) {
        try {
            AppOpsManager appOps = (AppOpsManager) reactContext.getSystemService(Context.APP_OPS_SERVICE);
            
            if (appOps == null) {
                promise.resolve(false);
                return;
            }
            
            int mode = appOps.checkOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                android.os.Process.myUid(),
                reactContext.getPackageName()
            );
            
            boolean granted = (mode == AppOpsManager.MODE_ALLOWED);
            promise.resolve(granted);
            
        } catch (Exception e) {
            Log.e(TAG, "Error checking usage stats permission", e);
            promise.reject("PERMISSION_ERROR", e.getMessage());
        }
    }
    
    /**
     * Open usage stats settings screen
     */
    @ReactMethod
    public void openUsageStatsSettings() {
        try {
            Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            reactContext.startActivity(intent);
        } catch (Exception e) {
            Log.e(TAG, "Error opening usage stats settings", e);
        }
    }
    
    /**
     * Start Focus Mode session
     * @param durationMinutes Duration in minutes (25, 50, or 90)
     */
    @ReactMethod
    public void startFocusMode(int durationMinutes, Promise promise) {
        try {
            Intent serviceIntent = new Intent(reactContext, FocusModeService.class);
            serviceIntent.setAction("START_FOCUS");
            serviceIntent.putExtra("duration", durationMinutes * 60 * 1000L);
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                reactContext.startForegroundService(serviceIntent);
            } else {
                reactContext.startService(serviceIntent);
            }
            
            promise.resolve(true);
            Log.d(TAG, "Focus Mode started: " + durationMinutes + " minutes");
            
        } catch (Exception e) {
            Log.e(TAG, "Error starting Focus Mode", e);
            promise.reject("START_ERROR", e.getMessage());
        }
    }
    
    /**
     * Stop Focus Mode session
     */
    @ReactMethod
    public void stopFocusMode(Promise promise) {
        try {
            Intent serviceIntent = new Intent(reactContext, FocusModeService.class);
            serviceIntent.setAction("STOP_FOCUS");
            reactContext.startService(serviceIntent);
            
            promise.resolve(true);
            Log.d(TAG, "Focus Mode stopped");
            
        } catch (Exception e) {
            Log.e(TAG, "Error stopping Focus Mode", e);
            promise.reject("STOP_ERROR", e.getMessage());
        }
    }
    
    /**
     * Update list of blocked apps
     */
    @ReactMethod
    public void updateBlockedApps(ReadableArray apps, Promise promise) {
        try {
            String[] appArray = new String[apps.size()];
            for (int i = 0; i < apps.size(); i++) {
                appArray[i] = apps.getString(i);
            }
            
            Intent serviceIntent = new Intent(reactContext, FocusModeService.class);
            serviceIntent.setAction("UPDATE_BLOCKED_APPS");
            serviceIntent.putExtra("apps", appArray);
            reactContext.startService(serviceIntent);
            
            promise.resolve(true);
            Log.d(TAG, "Updated blocked apps: " + apps.size() + " apps");
            
        } catch (Exception e) {
            Log.e(TAG, "Error updating blocked apps", e);
            promise.reject("UPDATE_ERROR", e.getMessage());
        }
    }
    
    /**
     * Get Focus Mode status
     */
    @ReactMethod
    public void getFocusModeStatus(Promise promise) {
        try {
            // This would ideally query the service directly
            // For now, return a basic status
            WritableMap status = Arguments.createMap();
            status.putBoolean("isActive", false);
            status.putDouble("remainingTime", 0);
            status.putDouble("endTime", 0);
            
            promise.resolve(status);
            
        } catch (Exception e) {
            Log.e(TAG, "Error getting Focus Mode status", e);
            promise.reject("STATUS_ERROR", e.getMessage());
        }
    }
    
    /**
     * Get default blocked apps list
     */
    @ReactMethod
    public void getDefaultBlockedApps(Promise promise) {
        try {
            WritableMap result = Arguments.createMap();
            
            // Return default blocked apps
            String[] apps = {
                "com.instagram.android",
                "com.twitter.android",
                "com.facebook.katana",
                "com.facebook.orca",
                "com.snapchat.android",
                "com.zhiliaoapp.musically",
                "com.reddit.frontpage",
                "com.pinterest",
                "com.linkedin.android",
                "com.tumblr"
            };
            
            result.putInt("count", apps.length);
            promise.resolve(result);
            
        } catch (Exception e) {
            Log.e(TAG, "Error getting default blocked apps", e);
            promise.reject("GET_ERROR", e.getMessage());
        }
    }
    
    /**
     * Register broadcast receiver for Focus Mode status updates
     */
    private void registerStatusReceiver() {
        statusReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String status = intent.getStringExtra("status");
                long duration = intent.getLongExtra("duration", 0);
                long endTime = intent.getLongExtra("endTime", 0);
                
                WritableMap params = Arguments.createMap();
                params.putString("status", status);
                params.putDouble("duration", duration);
                params.putDouble("endTime", endTime);
                params.putDouble("remainingTime", endTime - System.currentTimeMillis());
                
                sendEvent("FocusModeStatusChanged", params);
            }
        };
        
        IntentFilter filter = new IntentFilter("FOCUS_MODE_STATUS");
        reactContext.registerReceiver(statusReceiver, filter);
    }
    
    /**
     * Send event to React Native
     */
    private void sendEvent(String eventName, WritableMap params) {
        reactContext
            .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter.class)
            .emit(eventName, params);
    }
    
    /**
     * Cleanup when module is destroyed
     */
    @Override
    public void onCatalystInstanceDestroy() {
        super.onCatalystInstanceDestroy();
        
        try {
            if (statusReceiver != null) {
                reactContext.unregisterReceiver(statusReceiver);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error unregistering receiver", e);
        }
    }
}
