package com.privacywellbeingmobile;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

/**
 * Full-screen overlay shown when user tries to open a blocked app during Focus Mode
 */
public class BlockingOverlayActivity extends Activity {
    private TextView appNameText;
    private TextView messageText;
    private TextView timerText;
    private Button closeButton;
    private Handler handler;
    private Runnable updateRunnable;
    private long remainingTime;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Create simple layout programmatically
        setContentView(createLayout());
        
        // Get blocked app info from intent
        Intent intent = getIntent();
        String blockedApp = intent.getStringExtra("blockedApp");
        remainingTime = intent.getLongExtra("remainingTime", 0);
        
        // Set app name
        String appName = getAppName(blockedApp);
        appNameText.setText(appName);
        
        // Set message
        messageText.setText("This app is blocked during Focus Mode.\nStay focused on your goals!");
        
        // Start timer updates
        handler = new Handler();
        updateRunnable = new Runnable() {
            @Override
            public void run() {
                updateTimer();
                handler.postDelayed(this, 1000);
            }
        };
        handler.post(updateRunnable);
        
        // Close button
        closeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                goHome();
            }
        });
    }
    
    /**
     * Create layout programmatically (no XML needed)
     */
    private View createLayout() {
        // Create root layout
        android.widget.LinearLayout root = new android.widget.LinearLayout(this);
        root.setOrientation(android.widget.LinearLayout.VERTICAL);
        root.setGravity(android.view.Gravity.CENTER);
        root.setBackgroundColor(0xFF1E1E1E); // Dark background
        root.setPadding(40, 40, 40, 40);
        
        // App name text
        appNameText = new TextView(this);
        appNameText.setTextSize(24);
        appNameText.setTextColor(0xFFFFFFFF);
        appNameText.setGravity(android.view.Gravity.CENTER);
        appNameText.setPadding(0, 0, 0, 20);
        root.addView(appNameText);
        
        // Message text
        messageText = new TextView(this);
        messageText.setTextSize(16);
        messageText.setTextColor(0xFFCCCCCC);
        messageText.setGravity(android.view.Gravity.CENTER);
        messageText.setPadding(0, 0, 0, 30);
        root.addView(messageText);
        
        // Timer text
        timerText = new TextView(this);
        timerText.setTextSize(48);
        timerText.setTextColor(0xFF4CAF50); // Green
        timerText.setGravity(android.view.Gravity.CENTER);
        timerText.setPadding(0, 0, 0, 40);
        root.addView(timerText);
        
        // Close button
        closeButton = new Button(this);
        closeButton.setText("Return to Home");
        closeButton.setTextSize(16);
        closeButton.setBackgroundColor(0xFF2196F3); // Blue
        closeButton.setTextColor(0xFFFFFFFF);
        closeButton.setPadding(40, 20, 40, 20);
        root.addView(closeButton);
        
        return root;
    }
    
    /**
     * Update remaining time display
     */
    private void updateTimer() {
        if (remainingTime <= 0) {
            finish();
            return;
        }
        
        remainingTime -= 1000;
        
        long minutes = remainingTime / 1000 / 60;
        long seconds = (remainingTime / 1000) % 60;
        
        timerText.setText(String.format("%02d:%02d", minutes, seconds));
    }
    
    /**
     * Get friendly app name from package name
     */
    private String getAppName(String packageName) {
        if (packageName == null) return "App";
        
        switch (packageName) {
            case "com.instagram.android": return "Instagram";
            case "com.twitter.android": return "Twitter";
            case "com.facebook.katana": return "Facebook";
            case "com.facebook.orca": return "Messenger";
            case "com.snapchat.android": return "Snapchat";
            case "com.zhiliaoapp.musically": return "TikTok";
            case "com.reddit.frontpage": return "Reddit";
            case "com.pinterest": return "Pinterest";
            case "com.linkedin.android": return "LinkedIn";
            case "com.tumblr": return "Tumblr";
            default: return packageName;
        }
    }
    
    /**
     * Return to home screen
     */
    private void goHome() {
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.addCategory(Intent.CATEGORY_HOME);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        finish();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (handler != null) {
            handler.removeCallbacks(updateRunnable);
        }
    }
    
    @Override
    public void onBackPressed() {
        // Prevent back button - force user to use "Return to Home"
        goHome();
    }
}
