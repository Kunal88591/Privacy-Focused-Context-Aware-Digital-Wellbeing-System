package com.privacywellbeingmobile;

import android.app.Service;
import android.app.usage.UsageStats;
import android.app.usage.UsageStatsManager;
import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.SortedMap;

/**
 * Android Service that monitors app usage and blocks distracting apps during Focus Mode
 */
public class FocusModeService extends Service {
    private static final String TAG = "FocusModeService";
    private static final long CHECK_INTERVAL = 1000; // Check every 1 second
    
    private Handler handler;
    private Runnable checkRunnable;
    private Set<String> blockedApps;
    private boolean isFocusModeActive = false;
    private long sessionEndTime = 0;
    
    // Default blocked apps (can be customized)
    private static final Set<String> DEFAULT_BLOCKED_APPS = new HashSet<>(Arrays.asList(
        "com.instagram.android",
        "com.twitter.android",
        "com.facebook.katana",
        "com.facebook.orca", // Facebook Messenger
        "com.snapchat.android",
        "com.zhiliaoapp.musically", // TikTok
        "com.reddit.frontpage",
        "com.pinterest",
        "com.linkedin.android",
        "com.tumblr"
    ));
    
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "FocusModeService created");
        
        blockedApps = new HashSet<>(DEFAULT_BLOCKED_APPS);
        handler = new Handler(Looper.getMainLooper());
        
        // Runnable to check for blocked apps
        checkRunnable = new Runnable() {
            @Override
            public void run() {
                if (isFocusModeActive) {
                    checkForBlockedApps();
                    
                    // Check if session expired
                    if (System.currentTimeMillis() >= sessionEndTime) {
                        stopFocusMode();
                        return;
                    }
                }
                
                // Schedule next check
                handler.postDelayed(this, CHECK_INTERVAL);
            }
        };
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "FocusModeService started");
        
        if (intent != null) {
            String action = intent.getAction();
            
            if ("START_FOCUS".equals(action)) {
                long duration = intent.getLongExtra("duration", 25 * 60 * 1000); // Default 25 min
                startFocusMode(duration);
            } else if ("STOP_FOCUS".equals(action)) {
                stopFocusMode();
            } else if ("UPDATE_BLOCKED_APPS".equals(action)) {
                String[] apps = intent.getStringArrayExtra("apps");
                if (apps != null) {
                    updateBlockedApps(apps);
                }
            }
        }
        
        return START_STICKY;
    }
    
    /**
     * Start Focus Mode session
     */
    private void startFocusMode(long durationMs) {
        Log.d(TAG, "Starting Focus Mode for " + (durationMs / 1000 / 60) + " minutes");
        
        isFocusModeActive = true;
        sessionEndTime = System.currentTimeMillis() + durationMs;
        
        // Start monitoring
        handler.post(checkRunnable);
        
        // Broadcast status
        broadcastStatus("STARTED", durationMs);
    }
    
    /**
     * Stop Focus Mode session
     */
    private void stopFocusMode() {
        Log.d(TAG, "Stopping Focus Mode");
        
        isFocusModeActive = false;
        sessionEndTime = 0;
        
        // Stop monitoring
        handler.removeCallbacks(checkRunnable);
        
        // Broadcast status
        broadcastStatus("STOPPED", 0);
    }
    
    /**
     * Update the list of blocked apps
     */
    private void updateBlockedApps(String[] apps) {
        blockedApps.clear();
        blockedApps.addAll(Arrays.asList(apps));
        Log.d(TAG, "Updated blocked apps: " + blockedApps.size() + " apps");
    }
    
    /**
     * Check if any blocked app is currently in foreground
     */
    private void checkForBlockedApps() {
        String currentApp = getForegroundApp();
        
        if (currentApp != null && blockedApps.contains(currentApp)) {
            Log.d(TAG, "Blocked app detected: " + currentApp);
            showBlockingOverlay(currentApp);
        }
    }
    
    /**
     * Get the package name of the foreground app
     */
    private String getForegroundApp() {
        try {
            UsageStatsManager usageStatsManager = (UsageStatsManager) getSystemService(Context.USAGE_STATS_SERVICE);
            
            if (usageStatsManager == null) {
                return null;
            }
            
            long currentTime = System.currentTimeMillis();
            // Query last 10 seconds
            SortedMap<Long, UsageStats> statsMap = usageStatsManager.queryAndAggregateUsageStats(
                currentTime - 10000, 
                currentTime
            );
            
            if (statsMap.isEmpty()) {
                return null;
            }
            
            // Get most recently used app
            UsageStats recentStats = null;
            for (UsageStats stats : statsMap.values()) {
                if (recentStats == null || 
                    stats.getLastTimeUsed() > recentStats.getLastTimeUsed()) {
                    recentStats = stats;
                }
            }
            
            return recentStats != null ? recentStats.getPackageName() : null;
            
        } catch (Exception e) {
            Log.e(TAG, "Error getting foreground app", e);
            return null;
        }
    }
    
    /**
     * Show blocking overlay when user tries to open blocked app
     */
    private void showBlockingOverlay(String packageName) {
        Intent overlayIntent = new Intent(this, BlockingOverlayActivity.class);
        overlayIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        overlayIntent.putExtra("blockedApp", packageName);
        overlayIntent.putExtra("remainingTime", sessionEndTime - System.currentTimeMillis());
        startActivity(overlayIntent);
    }
    
    /**
     * Broadcast Focus Mode status to React Native
     */
    private void broadcastStatus(String status, long duration) {
        Intent intent = new Intent("FOCUS_MODE_STATUS");
        intent.putExtra("status", status);
        intent.putExtra("duration", duration);
        intent.putExtra("endTime", sessionEndTime);
        sendBroadcast(intent);
    }
    
    /**
     * Get remaining session time in milliseconds
     */
    public long getRemainingTime() {
        if (!isFocusModeActive) {
            return 0;
        }
        return Math.max(0, sessionEndTime - System.currentTimeMillis());
    }
    
    /**
     * Check if Focus Mode is currently active
     */
    public boolean isActive() {
        return isFocusModeActive;
    }
    
    /**
     * Get list of blocked apps
     */
    public Set<String> getBlockedApps() {
        return new HashSet<>(blockedApps);
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "FocusModeService destroyed");
        
        if (handler != null) {
            handler.removeCallbacks(checkRunnable);
        }
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
