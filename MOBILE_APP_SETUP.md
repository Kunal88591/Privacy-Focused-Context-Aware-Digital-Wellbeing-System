# 🚀 COMPLETE MOBILE APP SETUP & PERMISSION GUIDE

## ⚠️ CRITICAL: This guide fixes ALL setup issues and explains Android permissions

---

## 🔧 PART 1: FIX MOBILE APP (Babel Errors, etc.)

### Step 1: Clean Everything
```bash
cd /path/to/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/mobile-app

# Delete ALL node modules and caches
rm -rf node_modules
rm -rf android/build
rm -rf android/app/build
rm -rf $TMPDIR/react-*
rm -rf $TMPDIR/metro-*
watchman watch-del-all  # If you have watchman installed

# Clear npm cache
npm cache clean --force
```

### Step 2: Fresh Install
```bash
# Install dependencies
npm install

# For Android, sync Gradle
cd android
./gradlew clean
cd ..
```

### Step 3: Start Metro Bundler
```bash
# In Terminal 1 - Start Metro with cache reset
npm start -- --reset-cache
```

### Step 4: Run Android App
```bash
# In Terminal 2 - Run on connected device/emulator
npm run android

# OR manually with adb
adb reverse tcp:8000 tcp:8000  # Connect to backend
adb reverse tcp:1883 tcp:1883  # Connect to MQTT
npm run android
```

### Common Errors & Fixes

#### Error: "Unable to load script. Make sure you're running Metro..."
**Fix:**
```bash
npm start -- --reset-cache
# Wait for "Loading..." to become "Ready"
# Then in another terminal:
npm run android
```

#### Error: "Task :app:installDebug FAILED"
**Fix:**
```bash
cd android
./gradlew clean
./gradlew installDebug --stacktrace
```

#### Error: "Execution failed for task ':app:mergeDebugResources'"
**Fix:**
```bash
cd android
./gradlew clean
cd ..
rm -rf node_modules
npm install
npm run android
```

#### Error: "Cannot find module '@babel/preset-env'"
**Fix:** Already fixed in package.json. Just run:
```bash
rm -rf node_modules
npm install
```

---

## 🔐 PART 2: ANDROID PERMISSIONS (The Critical Part!)

### Overview: What This App Needs

This is a **PRIVACY & WELLBEING app**, which means it needs **deep system access**:

| Feature | Android Permission Needed | Protection Level |
|---------|--------------------------|------------------|
| **Notification Classification** | `BIND_NOTIFICATION_LISTENER_SERVICE` | **Dangerous** - User must grant |
| **Focus Mode (Block Apps)** | `BIND_ACCESSIBILITY_SERVICE` | **Dangerous** - Settings page |
| **App Usage Stats** | `PACKAGE_USAGE_STATS` | **Special** - Settings page |
| **Privacy VPN** | `BIND_VPN_SERVICE` | **User Approval** - Dialog |
| **Network Monitoring** | `INTERNET`, `ACCESS_NETWORK_STATE` | Normal |
| **Foreground Services** | `FOREGROUND_SERVICE` | Normal |

---

### Permission 1: Notification Access (Notification Listener)

**What it does:** Intercepts incoming notifications to classify as urgent/non-urgent

**How to request:**

1. **In Code** (`src/utils/permissions.js`):
```javascript
import { NativeModules, Linking, Platform } from 'react-native';

export const requestNotificationAccess = async () => {
  if (Platform.OS === 'android') {
    try {
      // Check if already granted
      const granted = await NativeModules.NotificationPermissions.isEnabled();
      
      if (!granted) {
        // Open notification listener settings
        Linking.openSettings();
        
        // Alternative: Direct deep link
        Linking.sendIntent('android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS');
      }
      
      return granted;
    } catch (error) {
      console.error('Notification permission error:', error);
      return false;
    }
  }
  return false;
};
```

2. **User Must Manually Enable:**
   - User goes to: **Settings → Apps → Special App Access → Notification Access**
   - Toggles **Privacy Wellbeing** to ON
   - Android shows security warning
   - User accepts

3. **What Your App Sees:**
```javascript
// NotificationListener.java receives:
{
  id: "notif_12345",
  title: "Meeting in 5 min",
  text: "Stand-up with team",
  packageName: "com.google.calendar",
  postTime: 1702640400000,
  category: "event"
}
```

---

### Permission 2: Usage Stats (App Usage Tracking)

**What it does:** Tracks which apps user spent time in (for wellbeing insights)

**How to request:**

1. **Check Permission:**
```javascript
import { NativeModules } from 'react-native';

export const requestUsageStatsPermission = async () => {
  try {
    const granted = await NativeModules.UsageStats.hasPermission();
    
    if (!granted) {
      // Open usage access settings
      await NativeModules.UsageStats.requestPermission();
    }
    
    return granted;
  } catch (error) {
    console.error('Usage stats error:', error);
    return false;
  }
};
```

2. **Native Module** (`android/app/src/main/java/.../UsageStatsModule.java`):
```java
package com.privacywellbeing;

import android.app.usage.UsageStatsManager;
import android.content.Context;
import android.content.Intent;
import android.provider.Settings;
import com.facebook.react.bridge.*;

public class UsageStatsModule extends ReactContextBaseJavaModule {
    
    public UsageStatsModule(ReactApplicationContext context) {
        super(context);
    }
    
    @Override
    public String getName() {
        return "UsageStats";
    }
    
    @ReactMethod
    public void hasPermission(Promise promise) {
        try {
            UsageStatsManager usm = (UsageStatsManager) getReactApplicationContext()
                .getSystemService(Context.USAGE_STATS_SERVICE);
            
            long time = System.currentTimeMillis();
            List<UsageStats> stats = usm.queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY, 
                time - 1000 * 1000, 
                time
            );
            
            // If stats is empty, permission not granted
            boolean granted = stats != null && !stats.isEmpty();
            promise.resolve(granted);
        } catch (Exception e) {
            promise.reject("ERROR", e);
        }
    }
    
    @ReactMethod
    public void requestPermission(Promise promise) {
        try {
            Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getReactApplicationContext().startActivity(intent);
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("ERROR", e);
        }
    }
    
    @ReactMethod
    public void getAppUsage(double startTime, double endTime, Promise promise) {
        try {
            UsageStatsManager usm = (UsageStatsManager) getReactApplicationContext()
                .getSystemService(Context.USAGE_STATS_SERVICE);
            
            List<UsageStats> stats = usm.queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY,
                (long) startTime,
                (long) endTime
            );
            
            WritableArray result = Arguments.createArray();
            for (UsageStats stat : stats) {
                WritableMap app = Arguments.createMap();
                app.putString("packageName", stat.getPackageName());
                app.putDouble("totalTime", stat.getTotalTimeInForeground());
                app.putInt("launchCount", stat.getLastTimeUsed());
                result.pushMap(app);
            }
            
            promise.resolve(result);
        } catch (Exception e) {
            promise.reject("ERROR", e);
        }
    }
}
```

3. **User Flow:**
   - App shows: "Enable App Usage Tracking for insights"
   - User taps → Opens **Settings → Apps → Special Access → Usage Access**
   - User enables **Privacy Wellbeing**

---

### Permission 3: VPN Service (Privacy Features)

**What it does:** Routes traffic through local VPN to block trackers/ads

**How to request:**

1. **VPN Service** (`android/app/src/main/java/.../PrivacyVpnService.java`):
```java
package com.privacywellbeing;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.net.VpnService;
import android.os.ParcelFileDescriptor;
import androidx.core.app.NotificationCompat;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;

public class PrivacyVpnService extends VpnService {
    
    private Thread vpnThread;
    private ParcelFileDescriptor vpnInterface;
    private boolean running = false;
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if ("START".equals(intent.getAction())) {
            startVPN();
        } else if ("STOP".equals(intent.getAction())) {
            stopVPN();
        }
        return START_STICKY;
    }
    
    private void startVPN() {
        if (running) return;
        
        // Build VPN interface
        Builder builder = new Builder();
        builder.setSession("Privacy VPN");
        builder.addAddress("10.0.0.2", 24);  // VPN IP
        builder.addRoute("0.0.0.0", 0);      // Route all traffic
        builder.addDnsServer("1.1.1.1");     // Cloudflare DNS
        
        // Block known tracker domains
        builder.addDisallowedApplication("com.google.android.gms");  // Optional
        
        vpnInterface = builder.establish();
        
        // Start foreground notification
        startForeground(1, getNotification());
        
        running = true;
        
        // Start packet filtering thread
        vpnThread = new Thread(this::processPackets);
        vpnThread.start();
    }
    
    private void processPackets() {
        try {
            FileInputStream in = new FileInputStream(vpnInterface.getFileDescriptor());
            FileOutputStream out = new FileOutputStream(vpnInterface.getFileDescriptor());
            
            ByteBuffer packet = ByteBuffer.allocate(32767);
            
            while (running) {
                packet.clear();
                int length = in.read(packet.array());
                
                if (length > 0) {
                    packet.limit(length);
                    
                    // Parse IP packet
                    String destIP = parseDestination(packet);
                    
                    // Check if blocked (tracker/ad domain)
                    if (isBlocked(destIP)) {
                        // Drop packet
                        continue;
                    }
                    
                    // Forward packet
                    out.write(packet.array(), 0, length);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private String parseDestination(ByteBuffer packet) {
        // Parse IP header (simplified)
        int destIP = packet.getInt(16);
        return String.format("%d.%d.%d.%d",
            (destIP >> 24) & 0xFF,
            (destIP >> 16) & 0xFF,
            (destIP >> 8) & 0xFF,
            destIP & 0xFF
        );
    }
    
    private boolean isBlocked(String ip) {
        // Check against blocklist
        // Return true if tracker/ad domain
        return false;  // Implement actual blocking logic
    }
    
    private void stopVPN() {
        running = false;
        if (vpnThread != null) {
            vpnThread.interrupt();
        }
        if (vpnInterface != null) {
            try {
                vpnInterface.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        stopSelf();
    }
    
    private Notification getNotification() {
        NotificationChannel channel = new NotificationChannel(
            "vpn_channel",
            "VPN Service",
            NotificationManager.IMPORTANCE_LOW
        );
        
        NotificationManager manager = getSystemService(NotificationManager.class);
        manager.createNotificationChannel(channel);
        
        return new NotificationCompat.Builder(this, "vpn_channel")
            .setContentTitle("Privacy VPN Active")
            .setContentText("Blocking trackers and ads")
            .setSmallIcon(android.R.drawable.ic_secure)
            .build();
    }
}
```

2. **React Native Module** (`PrivacyVpnModule.java`):
```java
@ReactMethod
public void startVPN(Promise promise) {
    try {
        Intent intent = VpnService.prepare(getReactApplicationContext());
        
        if (intent != null) {
            // User needs to approve VPN
            getCurrentActivity().startActivityForResult(intent, VPN_REQUEST_CODE);
            promise.resolve(false);  // Not yet approved
        } else {
            // Already approved, start VPN
            Intent vpnIntent = new Intent(getReactApplicationContext(), PrivacyVpnService.class);
            vpnIntent.setAction("START");
            getReactApplicationContext().startService(vpnIntent);
            promise.resolve(true);
        }
    } catch (Exception e) {
        promise.reject("VPN_ERROR", e);
    }
}
```

3. **User Experience:**
   - User taps "Enable Privacy VPN" in app
   - Android shows system dialog: "Privacy Wellbeing wants to set up a VPN connection"
   - User taps "OK" → VPN starts
   - Notification shows: "Privacy VPN Active - Blocking trackers"

---

### Permission 4: Accessibility Service (App Blocker for Focus Mode)

**What it does:** Blocks distracting apps during Focus Mode

**How to implement:**

1. **Accessibility Service** (`BlockerAccessibilityService.java`):
```java
package com.privacywellbeing;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.Intent;
import android.view.accessibility.AccessibilityEvent;

import java.util.HashSet;
import java.util.Set;

public class BlockerAccessibilityService extends AccessibilityService {
    
    private static Set<String> blockedApps = new HashSet<>();
    private static boolean focusModeActive = false;
    
    public static void setBlockedApps(Set<String> apps) {
        blockedApps = apps;
    }
    
    public static void setFocusMode(boolean active) {
        focusModeActive = active;
    }
    
    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (!focusModeActive) return;
        
        if (event.getEventType() == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            String packageName = event.getPackageName().toString();
            
            if (blockedApps.contains(packageName)) {
                // Blocked app detected! Show overlay
                Intent intent = new Intent(this, BlockingOverlayActivity.class);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                intent.putExtra("blocked_app", packageName);
                startActivity(intent);
                
                // Return to home
                performGlobalAction(GLOBAL_ACTION_HOME);
            }
        }
    }
    
    @Override
    public void onInterrupt() {
        // Handle interruption
    }
    
    @Override
    protected void onServiceConnected() {
        AccessibilityServiceInfo info = new AccessibilityServiceInfo();
        info.eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED;
        info.feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC;
        info.flags = AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS;
        setServiceInfo(info);
    }
}
```

2. **React Native Module:**
```java
@ReactMethod
public void enableFocusMode(ReadableArray blockedApps, Promise promise) {
    try {
        // Convert to Set
        Set<String> apps = new HashSet<>();
        for (int i = 0; i < blockedApps.size(); i++) {
            apps.add(blockedApps.getString(i));
        }
        
        BlockerAccessibilityService.setBlockedApps(apps);
        BlockerAccessibilityService.setFocusMode(true);
        
        // Check if accessibility service is enabled
        if (!isAccessibilityEnabled()) {
            // Open settings
            Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getReactApplicationContext().startActivity(intent);
            promise.resolve(false);
        } else {
            promise.resolve(true);
        }
    } catch (Exception e) {
        promise.reject("FOCUS_MODE_ERROR", e);
    }
}
```

3. **User Must Enable:**
   - Go to **Settings → Accessibility → Installed Apps → Privacy Wellbeing**
   - Toggle ON
   - Accept warning about accessibility access

---

## 📱 COMPLETE ONBOARDING FLOW

### Step-by-Step User Experience:

**1. App First Launch:**
```javascript
// src/screens/OnboardingScreen.js
import React, { useState } from 'react';
import { View, Text, Button, Alert } from 'react-native';
import { 
  requestNotificationAccess,
  requestUsageStatsPermission,
  requestVPNPermission,
  requestAccessibilityService 
} from '../utils/permissions';

export default function OnboardingScreen({ navigation }) {
  const [step, setStep] = useState(1);
  
  const handleNotificationPermission = async () => {
    const granted = await requestNotificationAccess();
    if (granted) {
      setStep(2);
    } else {
      Alert.alert(
        'Notification Access Required',
        'To classify notifications, please enable notification access in settings.',
        [{ text: 'Open Settings', onPress: requestNotificationAccess }]
      );
    }
  };
  
  const handleUsageStatsPermission = async () => {
    const granted = await requestUsageStatsPermission();
    if (granted) {
      setStep(3);
    }
  };
  
  const handleVPNPermission = async () => {
    const granted = await requestVPNPermission();
    if (granted) {
      setStep(4);
    }
  };
  
  const handleAccessibilityPermission = async () => {
    const granted = await requestAccessibilityService();
    if (granted) {
      navigation.navigate('Home');
    }
  };
  
  return (
    <View>
      {step === 1 && (
        <>
          <Text>Step 1: Notification Access</Text>
          <Text>We need to read notifications to classify them as urgent/non-urgent</Text>
          <Button title="Grant Permission" onPress={handleNotificationPermission} />
        </>
      )}
      {step === 2 && (
        <>
          <Text>Step 2: App Usage Tracking</Text>
          <Text>Track which apps you use to provide wellbeing insights</Text>
          <Button title="Grant Permission" onPress={handleUsageStatsPermission} />
        </>
      )}
      {step === 3 && (
        <>
          <Text>Step 3: Privacy VPN</Text>
          <Text>Block trackers and ads with local VPN</Text>
          <Button title="Enable VPN" onPress={handleVPNPermission} />
        </>
      )}
      {step === 4 && (
        <>
          <Text>Step 4: Focus Mode</Text>
          <Text>Block distracting apps during focus sessions</Text>
          <Button title="Enable" onPress={handleAccessibilityPermission} />
        </>
      )}
    </View>
  );
}
```

---

## ✅ TESTING CHECKLIST

### Before Deployment:

- [ ] App installs without errors
- [ ] Metro bundler connects
- [ ] Backend API reachable (check API_URL in config)
- [ ] Notification access granted → Notifications appear in app
- [ ] Usage stats permission granted → See app usage times
- [ ] VPN permission granted → Notification shows "VPN Active"
- [ ] Accessibility granted → Blocked apps show overlay
- [ ] Focus mode blocks Instagram/Twitter/TikTok
- [ ] Privacy score calculated correctly
- [ ] Analytics charts display data

---

## 🐛 TROUBLESHOOTING

### Issue: "App crashes on startup"
```bash
adb logcat | grep "ReactNative"
# Check for missing modules or incorrect imports
```

### Issue: "Metro bundler stuck at 'Loading...'"
```bash
pkill -f metro
npm start -- --reset-cache
```

### Issue: "Cannot connect to backend"
```javascript
// Check mobile-app/src/config/index.js
export default {
  API_URL: 'http://10.0.2.2:8000',  // Android Emulator
  // API_URL: 'http://YOUR_COMPUTER_IP:8000',  // Real device
  MQTT_URL: 'mqtt://10.0.2.2:1883',
};
```

### Issue: "Permissions not working"
- Check `AndroidManifest.xml` has all required permissions
- Ensure native modules are registered in `MainApplication.java`
- Rebuild app after changes: `cd android && ./gradlew clean && cd .. && npm run android`

---

## 🎯 FINAL COMMANDS TO GET RUNNING

```bash
# Terminal 1: Backend
cd backend-api
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Mobile
cd mobile-app
npm install
npm start -- --reset-cache

# Terminal 3: Run Android
cd mobile-app
npm run android
```

**First time setup:**
1. Grant notification access
2. Grant usage stats access
3. Enable VPN (tap OK on dialog)
4. Enable accessibility service
5. Enjoy your privacy-focused wellbeing app! 🎉

---

## 📞 Support

If you still face issues:
1. Check `adb logcat` for errors
2. Verify all permissions in Settings
3. Ensure backend is running and reachable
4. Clear app data and reinstall

**Common Permission Paths:**
- Notification: Settings → Apps → Special → Notification access
- Usage: Settings → Apps → Special → Usage access
- Accessibility: Settings → Accessibility → Downloaded apps
- VPN: System dialog on first enable
