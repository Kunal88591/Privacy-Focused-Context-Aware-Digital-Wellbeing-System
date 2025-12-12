package com.privacywellbeingmobile;

import android.app.Notification;
import android.content.Intent;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.util.Log;

import com.facebook.react.HeadlessJsTaskService;
import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.WritableMap;

/**
 * NotificationListener Service
 * Intercepts all notifications and sends them to React Native
 */
public class NotificationListener extends NotificationListenerService {

    private static final String TAG = "NotificationListener";
    private static NotificationListener instance;

    public static NotificationListener getInstance() {
        return instance;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        instance = null;
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        try {
            Bundle extras = sbn.getNotification().extras;
            
            String packageName = sbn.getPackageName();
            String title = extras.getString(Notification.EXTRA_TITLE);
            String text = extras.getCharSequence(Notification.EXTRA_TEXT) != null ? 
                extras.getCharSequence(Notification.EXTRA_TEXT).toString() : "";
            String subText = extras.getString(Notification.EXTRA_SUB_TEXT);
            long timestamp = sbn.getPostTime();

            // Skip system notifications
            if (packageName.equals("android") || packageName.equals("com.android.systemui")) {
                return;
            }

            // Create notification data
            WritableMap notificationData = Arguments.createMap();
            notificationData.putString("id", sbn.getKey());
            notificationData.putString("packageName", packageName);
            notificationData.putString("title", title != null ? title : "");
            notificationData.putString("text", text);
            notificationData.putString("subText", subText != null ? subText : "");
            notificationData.putDouble("timestamp", timestamp);

            Log.d(TAG, "Notification received: " + title + " from " + packageName);

            // Send to React Native via Headless JS
            Intent service = new Intent(getApplicationContext(), NotificationEventService.class);
            Bundle bundle = new Bundle();
            bundle.putString("notificationData", notificationData.toString());
            service.putExtras(bundle);

            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                getApplicationContext().startForegroundService(service);
            } else {
                getApplicationContext().startService(service);
            }

        } catch (Exception e) {
            Log.e(TAG, "Error processing notification: " + e.getMessage());
        }
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        Log.d(TAG, "Notification removed: " + sbn.getKey());
    }
}
