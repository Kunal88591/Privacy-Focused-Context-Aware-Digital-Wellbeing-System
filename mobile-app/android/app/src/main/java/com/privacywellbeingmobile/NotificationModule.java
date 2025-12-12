package com.privacywellbeingmobile;

import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.provider.Settings;
import android.service.notification.StatusBarNotification;

import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.WritableArray;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.Arguments;

/**
 * React Native Module for Notification Management
 * Provides methods to check permissions, dismiss notifications, and get active notifications
 */
public class NotificationModule extends ReactContextBaseJavaModule {

    private static final String MODULE_NAME = "NotificationModule";
    private final ReactApplicationContext reactContext;

    public NotificationModule(ReactApplicationContext context) {
        super(context);
        this.reactContext = context;
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    /**
     * Check if notification listener permission is granted
     */
    @ReactMethod
    public void checkNotificationPermission(Promise promise) {
        try {
            String enabledListeners = Settings.Secure.getString(
                reactContext.getContentResolver(),
                "enabled_notification_listeners"
            );

            boolean isEnabled = enabledListeners != null && 
                enabledListeners.contains(reactContext.getPackageName());

            promise.resolve(isEnabled);
        } catch (Exception e) {
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Open notification listener settings
     */
    @ReactMethod
    public void openNotificationSettings() {
        Intent intent = new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        reactContext.startActivity(intent);
    }

    /**
     * Dismiss a notification by its key
     */
    @ReactMethod
    public void dismissNotification(String notificationKey, Promise promise) {
        try {
            NotificationListenerService service = NotificationListenerService.getInstance();
            if (service != null) {
                service.cancelNotification(notificationKey);
                promise.resolve(true);
            } else {
                promise.reject("ERROR", "NotificationListenerService not available");
            }
        } catch (Exception e) {
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Get all active notifications
     */
    @ReactMethod
    public void getActiveNotifications(Promise promise) {
        try {
            NotificationListenerService service = NotificationListenerService.getInstance();
            if (service != null) {
                StatusBarNotification[] notifications = service.getActiveNotifications();
                WritableArray notificationArray = Arguments.createArray();

                for (StatusBarNotification sbn : notifications) {
                    String packageName = sbn.getPackageName();
                    
                    // Skip system notifications
                    if (packageName.equals("android") || packageName.equals("com.android.systemui")) {
                        continue;
                    }

                    WritableMap notificationData = Arguments.createMap();
                    notificationData.putString("id", sbn.getKey());
                    notificationData.putString("packageName", packageName);
                    notificationData.putString("title", 
                        sbn.getNotification().extras.getString(android.app.Notification.EXTRA_TITLE));
                    notificationData.putString("text", 
                        sbn.getNotification().extras.getCharSequence(android.app.Notification.EXTRA_TEXT) != null ?
                        sbn.getNotification().extras.getCharSequence(android.app.Notification.EXTRA_TEXT).toString() : "");
                    notificationData.putDouble("timestamp", sbn.getPostTime());

                    notificationArray.pushMap(notificationData);
                }

                promise.resolve(notificationArray);
            } else {
                promise.reject("ERROR", "NotificationListenerService not available");
            }
        } catch (Exception e) {
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Dismiss all notifications
     */
    @ReactMethod
    public void dismissAllNotifications(Promise promise) {
        try {
            NotificationListenerService service = NotificationListenerService.getInstance();
            if (service != null) {
                service.cancelAllNotifications();
                promise.resolve(true);
            } else {
                promise.reject("ERROR", "NotificationListenerService not available");
            }
        } catch (Exception e) {
            promise.reject("ERROR", e.getMessage());
        }
    }
}
