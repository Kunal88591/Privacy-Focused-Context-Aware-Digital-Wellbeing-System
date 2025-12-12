package com.privacywellbeingmobile;

import android.content.Intent;

import com.facebook.react.HeadlessJsTaskService;
import com.facebook.react.bridge.Arguments;
import com.facebook.react.jstasks.HeadlessJsTaskConfig;

import javax.annotation.Nullable;

/**
 * Headless JS Service for handling notifications in background
 */
public class NotificationEventService extends HeadlessJsTaskService {

    @Override
    protected @Nullable HeadlessJsTaskConfig getTaskConfig(Intent intent) {
        if (intent.getExtras() != null) {
            return new HeadlessJsTaskConfig(
                "NotificationReceived",
                Arguments.fromBundle(intent.getExtras()),
                5000, // timeout in milliseconds
                true // allow in foreground
            );
        }
        return null;
    }
}
