package com.privacywellbeingmobile;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.net.VpnService;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.ParcelFileDescriptor;
import android.util.Log;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * VPN Service for privacy protection - blocks trackers and ads at network level
 */
public class PrivacyVpnService extends VpnService {
    private static final String TAG = "PrivacyVpnService";
    private static final String CHANNEL_ID = "privacy_vpn_channel";
    private static final int NOTIFICATION_ID = 1001;
    
    private ParcelFileDescriptor vpnInterface;
    private Thread vpnThread;
    private AtomicBoolean isRunning = new AtomicBoolean(false);
    private Handler handler;
    
    // Statistics
    private long trackersBlocked = 0;
    private long adsBlocked = 0;
    private long requestsTotal = 0;
    private long bytesProtected = 0;
    
    // Blocked domains - trackers
    private static final Set<String> TRACKER_DOMAINS = new HashSet<>(Arrays.asList(
        // Google Analytics & Ads
        "google-analytics.com",
        "googleadservices.com",
        "googlesyndication.com",
        "doubleclick.net",
        "googletagmanager.com",
        "googletagservices.com",
        
        // Facebook
        "facebook.net",
        "fbcdn.net",
        "connect.facebook.net",
        "pixel.facebook.com",
        "graph.facebook.com",
        
        // Amazon
        "amazon-adsystem.com",
        "aax.amazon-adsystem.com",
        
        // Twitter
        "ads-twitter.com",
        "analytics.twitter.com",
        
        // Other trackers
        "scorecardresearch.com",
        "quantserve.com",
        "outbrain.com",
        "taboola.com",
        "criteo.com",
        "criteo.net",
        "mixpanel.com",
        "segment.io",
        "segment.com",
        "amplitude.com",
        "branch.io",
        "appsflyer.com",
        "adjust.com",
        "kochava.com",
        "mparticle.com",
        "newrelic.com",
        "crashlytics.com",
        "flurry.com",
        "appboy.com",
        "braze.com",
        "urbanairship.com",
        "onesignal.com",
        "leanplum.com",
        "localytics.com"
    ));
    
    // Blocked domains - ads
    private static final Set<String> AD_DOMAINS = new HashSet<>(Arrays.asList(
        "pagead2.googlesyndication.com",
        "adservice.google.com",
        "ads.google.com",
        "adsense.google.com",
        "adnxs.com",
        "adsrvr.org",
        "adroll.com",
        "advertising.com",
        "rubiconproject.com",
        "pubmatic.com",
        "openx.net",
        "casalemedia.com",
        "33across.com",
        "indexexchange.com",
        "spotxchange.com",
        "contextweb.com",
        "appnexus.com",
        "moatads.com",
        "serving-sys.com",
        "adcolony.com",
        "unity3d.com/ads",
        "unityads.unity3d.com",
        "mopub.com",
        "inmobi.com",
        "vungle.com",
        "chartboost.com",
        "tapjoy.com",
        "ironsrc.com",
        "applovin.com"
    ));
    
    // User's custom blocked domains
    private Set<String> customBlockedDomains = new HashSet<>();
    
    // User's whitelisted domains
    private Set<String> whitelistedDomains = new HashSet<>();
    
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "PrivacyVpnService created");
        handler = new Handler(Looper.getMainLooper());
        createNotificationChannel();
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            String action = intent.getAction();
            
            if ("START_VPN".equals(action)) {
                startVpn();
            } else if ("STOP_VPN".equals(action)) {
                stopVpn();
            } else if ("ADD_BLOCKED_DOMAIN".equals(action)) {
                String domain = intent.getStringExtra("domain");
                if (domain != null) {
                    customBlockedDomains.add(domain.toLowerCase());
                }
            } else if ("REMOVE_BLOCKED_DOMAIN".equals(action)) {
                String domain = intent.getStringExtra("domain");
                if (domain != null) {
                    customBlockedDomains.remove(domain.toLowerCase());
                }
            } else if ("ADD_WHITELIST".equals(action)) {
                String domain = intent.getStringExtra("domain");
                if (domain != null) {
                    whitelistedDomains.add(domain.toLowerCase());
                }
            } else if ("REMOVE_WHITELIST".equals(action)) {
                String domain = intent.getStringExtra("domain");
                if (domain != null) {
                    whitelistedDomains.remove(domain.toLowerCase());
                }
            }
        }
        
        return START_STICKY;
    }
    
    /**
     * Start VPN protection
     */
    private void startVpn() {
        if (isRunning.get()) {
            Log.d(TAG, "VPN already running");
            return;
        }
        
        Log.d(TAG, "Starting VPN protection");
        
        try {
            // Configure VPN interface
            Builder builder = new Builder();
            builder.setSession("Privacy Shield")
                   .addAddress("10.0.0.2", 24)
                   .addDnsServer("8.8.8.8")
                   .addDnsServer("8.8.4.4")
                   .addRoute("0.0.0.0", 0)
                   .setMtu(1500)
                   .setBlocking(true);
            
            // Exclude our own app from VPN
            try {
                builder.addDisallowedApplication(getPackageName());
            } catch (Exception e) {
                Log.e(TAG, "Error excluding app from VPN", e);
            }
            
            vpnInterface = builder.establish();
            
            if (vpnInterface == null) {
                Log.e(TAG, "Failed to establish VPN interface");
                return;
            }
            
            isRunning.set(true);
            
            // Start foreground service
            startForeground(NOTIFICATION_ID, createNotification());
            
            // Start packet processing thread
            vpnThread = new Thread(this::processPackets);
            vpnThread.start();
            
            // Broadcast status
            broadcastStatus("CONNECTED");
            
            Log.d(TAG, "VPN protection started");
            
        } catch (Exception e) {
            Log.e(TAG, "Error starting VPN", e);
            broadcastStatus("ERROR");
        }
    }
    
    /**
     * Stop VPN protection
     */
    private void stopVpn() {
        Log.d(TAG, "Stopping VPN protection");
        
        isRunning.set(false);
        
        if (vpnThread != null) {
            vpnThread.interrupt();
            vpnThread = null;
        }
        
        if (vpnInterface != null) {
            try {
                vpnInterface.close();
            } catch (IOException e) {
                Log.e(TAG, "Error closing VPN interface", e);
            }
            vpnInterface = null;
        }
        
        stopForeground(true);
        broadcastStatus("DISCONNECTED");
        
        Log.d(TAG, "VPN protection stopped");
    }
    
    /**
     * Process network packets - filter trackers and ads
     */
    private void processPackets() {
        Log.d(TAG, "Starting packet processing");
        
        FileInputStream in = new FileInputStream(vpnInterface.getFileDescriptor());
        FileOutputStream out = new FileOutputStream(vpnInterface.getFileDescriptor());
        
        ByteBuffer packet = ByteBuffer.allocate(32767);
        
        try {
            DatagramChannel tunnel = DatagramChannel.open();
            tunnel.connect(new InetSocketAddress("127.0.0.1", 8087));
            protect(tunnel.socket());
            
            while (isRunning.get()) {
                packet.clear();
                
                // Read packet from VPN interface
                int length = in.read(packet.array());
                
                if (length > 0) {
                    requestsTotal++;
                    bytesProtected += length;
                    
                    packet.limit(length);
                    
                    // Check if packet should be blocked
                    String destHost = extractDestinationHost(packet);
                    
                    if (destHost != null && shouldBlock(destHost)) {
                        // Packet blocked - don't forward
                        if (isTracker(destHost)) {
                            trackersBlocked++;
                        } else if (isAd(destHost)) {
                            adsBlocked++;
                        }
                        
                        Log.d(TAG, "Blocked: " + destHost);
                        continue;
                    }
                    
                    // Forward allowed packets
                    packet.rewind();
                    out.write(packet.array(), 0, length);
                }
            }
            
        } catch (Exception e) {
            if (isRunning.get()) {
                Log.e(TAG, "Error processing packets", e);
            }
        } finally {
            try {
                in.close();
                out.close();
            } catch (IOException e) {
                Log.e(TAG, "Error closing streams", e);
            }
        }
        
        Log.d(TAG, "Packet processing stopped");
    }
    
    /**
     * Extract destination host from packet (simplified)
     */
    private String extractDestinationHost(ByteBuffer packet) {
        // Simplified DNS extraction - in production would parse full packet
        try {
            if (packet.limit() < 20) return null;
            
            // Skip IP header (20 bytes minimum)
            int headerLength = (packet.get(0) & 0x0F) * 4;
            if (packet.limit() < headerLength + 8) return null;
            
            // Check if UDP (protocol 17) and port 53 (DNS)
            int protocol = packet.get(9) & 0xFF;
            if (protocol != 17) return null; // Not UDP
            
            int destPort = ((packet.get(headerLength + 2) & 0xFF) << 8) | 
                          (packet.get(headerLength + 3) & 0xFF);
            if (destPort != 53) return null; // Not DNS
            
            // Parse DNS query name (simplified)
            int dnsStart = headerLength + 8;
            if (packet.limit() < dnsStart + 12) return null;
            
            StringBuilder domain = new StringBuilder();
            int pos = dnsStart + 12; // Skip DNS header
            
            while (pos < packet.limit()) {
                int labelLen = packet.get(pos++) & 0xFF;
                if (labelLen == 0) break;
                
                if (domain.length() > 0) domain.append(".");
                
                for (int i = 0; i < labelLen && pos < packet.limit(); i++) {
                    domain.append((char) (packet.get(pos++) & 0xFF));
                }
            }
            
            return domain.toString().toLowerCase();
            
        } catch (Exception e) {
            return null;
        }
    }
    
    /**
     * Check if domain should be blocked
     */
    private boolean shouldBlock(String domain) {
        // Check whitelist first
        if (isWhitelisted(domain)) {
            return false;
        }
        
        // Check blocklists
        return isTracker(domain) || isAd(domain) || isCustomBlocked(domain);
    }
    
    /**
     * Check if domain is a tracker
     */
    private boolean isTracker(String domain) {
        for (String tracker : TRACKER_DOMAINS) {
            if (domain.equals(tracker) || domain.endsWith("." + tracker)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Check if domain is an ad server
     */
    private boolean isAd(String domain) {
        for (String ad : AD_DOMAINS) {
            if (domain.equals(ad) || domain.endsWith("." + ad)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Check if domain is in custom blocklist
     */
    private boolean isCustomBlocked(String domain) {
        for (String blocked : customBlockedDomains) {
            if (domain.equals(blocked) || domain.endsWith("." + blocked)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Check if domain is whitelisted
     */
    private boolean isWhitelisted(String domain) {
        for (String white : whitelistedDomains) {
            if (domain.equals(white) || domain.endsWith("." + white)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Get blocking statistics
     */
    public long getTrackersBlocked() { return trackersBlocked; }
    public long getAdsBlocked() { return adsBlocked; }
    public long getRequestsTotal() { return requestsTotal; }
    public long getBytesProtected() { return bytesProtected; }
    public boolean isVpnRunning() { return isRunning.get(); }
    
    /**
     * Create notification channel
     */
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Privacy Protection",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Privacy VPN is protecting your data");
            
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }
    
    /**
     * Create foreground notification
     */
    private Notification createNotification() {
        Intent intent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
            this, 0, intent, 
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        
        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(this, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }
        
        return builder
            .setContentTitle("Privacy Shield Active")
            .setContentText("Blocking trackers and ads")
            .setSmallIcon(android.R.drawable.ic_lock_lock)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build();
    }
    
    /**
     * Broadcast VPN status to React Native
     */
    private void broadcastStatus(String status) {
        Intent intent = new Intent("PRIVACY_VPN_STATUS");
        intent.putExtra("status", status);
        intent.putExtra("trackersBlocked", trackersBlocked);
        intent.putExtra("adsBlocked", adsBlocked);
        intent.putExtra("requestsTotal", requestsTotal);
        intent.putExtra("bytesProtected", bytesProtected);
        sendBroadcast(intent);
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        stopVpn();
        Log.d(TAG, "PrivacyVpnService destroyed");
    }
    
    @Override
    public void onRevoke() {
        super.onRevoke();
        stopVpn();
        Log.d(TAG, "VPN permission revoked");
    }
}
