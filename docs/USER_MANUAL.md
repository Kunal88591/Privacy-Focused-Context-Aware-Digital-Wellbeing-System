# 📱 User Manual - Privacy-Focused Digital Wellbeing System

**Version:** 1.0.0  
**Last Updated:** January 2, 2026  
**Audience:** End Users

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Mobile App Features](#mobile-app-features)
4. [Privacy Controls](#privacy-controls)
5. [Focus Mode](#focus-mode)
6. [Analytics & Insights](#analytics--insights)
7. [IoT Integration](#iot-integration)
8. [Settings & Customization](#settings--customization)
9. [Tips & Best Practices](#tips--best-practices)

---

## 🎯 Introduction

### What is This System?

The Privacy-Focused Digital Wellbeing System is your personal digital bodyguard and focus coach. It helps you:

- **Protect Your Privacy** - Block trackers, mask caller ID, secure your data
- **Improve Focus** - Block distracting apps, manage notifications intelligently
- **Monitor Wellbeing** - Track productivity, get personalized recommendations
- **Smart Environment** - IoT sensors detect poor conditions and alert you

### Who Should Use This?

- **Professionals** who need focused work time without distractions
- **Privacy-conscious users** who want control over their data
- **Anyone** seeking better work-life balance and digital wellbeing

### Key Benefits

✅ **All-in-One Solution** - Privacy, productivity, and wellbeing in one app  
✅ **Smart & Adaptive** - AI learns your patterns and suggests improvements  
✅ **Privacy First** - Your data stays on your device, no cloud tracking  
✅ **Context-Aware** - Responds to your environment automatically

---

## 🚀 Getting Started

### First Time Setup

#### 1. Install the Mobile App

**Android:**
```bash
# Download APK from releases page
# Or install via Expo Go during beta
npm install -g expo-cli
expo start
# Scan QR code with Expo Go app
```

**iOS:**
```bash
# Install via TestFlight (beta) or App Store
# Or use Expo Go for development builds
```

#### 2. Create Your Account

1. Open the app
2. Tap **"Register"**
3. Enter your email and password
4. Agree to privacy policy
5. Tap **"Create Account"**

#### 3. Grant Permissions

The app needs these permissions to function:

| Permission | Why Needed | Required? |
|------------|------------|-----------|
| **Notifications** | Classification and smart filtering | ✅ Yes |
| **Usage Stats** | Track app usage and focus time | ✅ Yes |
| **Display Over Apps** | Show focus mode blocking overlay | ✅ Yes |
| **VPN Service** | Privacy protection and tracker blocking | ⚠️ For Privacy Features |
| **Phone** | Caller ID masking | ⚠️ For Privacy Features |
| **Location** | Location spoofing | ⚠️ Optional |

**To grant permissions:**
1. Go to **Settings** → **Permissions**
2. Enable required permissions
3. Follow on-screen instructions

#### 4. Initial Configuration

**Set Your Work Hours:**
1. Go to **Settings** → **Work Schedule**
2. Set your typical work hours (e.g., 9 AM - 5 PM)
3. Enable **"Auto-activate focus mode during work hours"**

**Choose Apps to Block:**
1. Go to **Focus Mode** → **Blocked Apps**
2. Select distracting apps (Instagram, Twitter, TikTok, etc.)
3. Save your selection

**Connect IoT Device (Optional):**
1. Ensure IoT device is powered on and connected to WiFi
2. Go to **Settings** → **Devices**
3. Tap **"Add Device"**
4. Enter device ID or scan QR code

---

## 📱 Mobile App Features

### Home Screen

The home screen shows your daily overview:

**Metrics Cards:**
- **Focus Time Today** - Total minutes in focus mode
- **Productivity Score** - 0-100 scale based on focus and distractions
- **Notifications** - Urgent vs. filtered notifications
- **Privacy Score** - Your privacy protection level

**Quick Actions:**
- **Start Focus Session** - Begin 25/50/90 minute session
- **Check Privacy** - View privacy status and threats
- **View Analytics** - See detailed statistics

### Navigation

Bottom tab bar with 6 screens:

1. **🏠 Home** - Dashboard and quick actions
2. **🔔 Notifications** - Smart notification feed
3. **🔒 Privacy** - Privacy controls and status
4. **🎯 Focus** - Focus mode and app blocking
5. **📊 Analytics** - Charts and insights
6. **⚙️ Settings** - App configuration

---

## 🔒 Privacy Controls

### VPN Protection

**What It Does:**
- Routes all traffic through secure VPN
- Blocks known trackers and ads (110+ domains)
- Encrypts your internet connection

**How to Use:**
1. Go to **Privacy** tab
2. Toggle **"VPN Protection"** ON
3. Choose server location (Auto, US, EU, Asia)
4. Tap **"Connect"**

**Status Indicators:**
- 🟢 **Connected** - VPN active, traffic encrypted
- 🟡 **Connecting** - Establishing connection
- 🔴 **Disconnected** - No VPN protection
- ⚠️ **Error** - Connection failed, check settings

**Blocked Content:**
- Ad trackers (Google Analytics, Facebook Pixel, etc.)
- Known malware domains
- Suspicious data collectors

### Caller ID Masking

**What It Does:**
- Hides caller information from incoming calls
- Protects your identity in call logs
- Prevents caller ID leakage

**How to Use:**
1. Go to **Privacy** → **Caller Masking**
2. Toggle **"Enable Masking"** ON
3. Choose masking level:
   - **Full** - Hide all caller info
   - **Partial** - Show only first 3 digits
   - **Contacts Only** - Mask unknown callers

**Incoming Call Display:**
- Unknown Number → "Private Caller"
- Known Contact → Name shown (if enabled)
- Spam → "Potential Spam" (auto-blocked)

### Location Spoofing

**What It Does:**
- Randomizes GPS coordinates
- Prevents location tracking by apps
- Protects your actual location

**How to Use:**
1. Go to **Privacy** → **Location**
2. Toggle **"Spoof Location"** ON
3. Choose mode:
   - **Random** - Generate random coordinates
   - **Fixed** - Use specific coordinates
   - **Nearby** - Stay within 5km radius
4. Set update interval (5min, 15min, 30min)

**When to Use:**
- Using social media apps
- Checking in at locations
- Using navigation (use "Nearby" mode)

### Data Encryption

**What It Does:**
- Encrypts local database with AES-256
- Protects stored notifications and logs
- Auto-wipe on threat detection

**Always Encrypted:**
- Notification history
- Focus session logs
- Privacy activity logs
- User preferences

**Auto-Wipe Triggers:**
- 3 untrusted network detections
- Manual trigger in settings
- Device theft detection (optional)

### Privacy Score

**How It's Calculated:**

| Component | Weight | Description |
|-----------|--------|-------------|
| **VPN Status** | 30% | VPN active and connected |
| **App Permissions** | 25% | Low-risk permissions only |
| **Tracker Blocking** | 20% | Blocked trackers count |
| **Data Encryption** | 15% | Local data encrypted |
| **Network Security** | 10% | Secure networks only |

**Score Ranges:**
- **90-100** 🟢 Excellent - Maximum protection
- **70-89** 🟡 Good - Adequate protection
- **50-69** 🟠 Fair - Some vulnerabilities
- **0-49** 🔴 Poor - Significant risks

---

## 🎯 Focus Mode

### Starting a Focus Session

**Quick Start:**
1. Go to **Focus** tab
2. Tap **"Start Focus Session"**
3. Choose duration:
   - **Pomodoro** - 25 minutes
   - **Deep Work** - 50 minutes
   - **Extended** - 90 minutes
4. Tap **"Start"**

**Advanced Options:**
1. Tap **"Custom Session"**
2. Set duration (1-240 minutes)
3. Select apps to block
4. Choose notification handling:
   - **Block All** - Silent mode
   - **Urgent Only** - Allow critical notifications
   - **Custom** - Select allowed apps
5. Enable **"Break Reminder"** (optional)
6. Tap **"Start Session"**

### During Focus Mode

**What Happens:**
- ✅ Selected apps are blocked
- ✅ Notifications are filtered or silent
- ✅ Blocking overlay shows when you try to open blocked apps
- ✅ Timer shows remaining focus time
- ✅ IoT device notified (if connected)

**Blocking Overlay:**
When you try to open a blocked app:
```
🚫 Focus Mode Active

"Instagram" is blocked during focus time

Time Remaining: 18 minutes

[End Focus Mode]  [I Really Need This App]
```

**Emergency Access:**
- Tap **"I Really Need This App"** 3 times
- Enter reason (logged for analytics)
- App unlocked for 2 minutes

### Ending Focus Mode

**Automatic End:**
- Session timer expires
- Notification shown: "Great work! Session complete"
- Statistics saved

**Manual End:**
1. Tap **"End Focus Mode"** button
2. Confirm: "End session early?"
3. Option to save or discard statistics

**Post-Session:**
- See session summary:
  - Duration completed
  - Apps blocked
  - Distractions resisted
  - Productivity score
- Option to take 5-minute break
- Suggestion for next session time

### Focus Statistics

**View Your Stats:**
1. Go to **Focus** → **Statistics**
2. Choose time period:
   - Today
   - This Week
   - This Month
   - All Time

**Metrics Shown:**
- **Total Focus Time** - Minutes in focus mode
- **Session Count** - Number of sessions completed
- **Average Duration** - Average session length
- **Apps Blocked** - Total blocking attempts
- **Completion Rate** - % of sessions finished
- **Best Streak** - Consecutive days with focus sessions

**Charts:**
- Daily focus time trend (line chart)
- Focus time by hour (bar chart)
- Top distraction apps (pie chart)

---

## 📊 Analytics & Insights

### Dashboard Overview

**Today Tab:**
- Focus time today
- Productivity score
- Screen time
- Top apps used
- Wellbeing score

**Week Tab:**
- Weekly averages
- Trend indicators (↑↓)
- Best day of week
- App usage distribution

**Insights Tab:**
- AI-generated insights
- Personalized tips
- Pattern detection
- Recommendations

### Productivity Score

**How It's Calculated:**

```
Productivity Score = 
  (Focus Time × 0.30) +
  (Quality Score × 0.25) +
  (Consistency × 0.20) +
  (Low Distractions × 0.15) +
  (Break Adherence × 0.10)
```

**Score Interpretation:**
- **90-100** 🌟 Exceptional - Peak performance
- **80-89** 🎯 Excellent - Highly productive
- **70-79** ✅ Good - On track
- **60-69** 📈 Fair - Room for improvement
- **0-59** ⚠️ Needs Attention - Low productivity

**Improving Your Score:**
- Increase focus time (aim for 4+ hours daily)
- Complete full focus sessions (don't end early)
- Maintain consistent schedule
- Resist app unlocking during focus
- Take regular breaks

### Goal Tracking

**Setting Goals:**
1. Go to **Analytics** → **Goals**
2. Tap **"Add Goal"**
3. Choose goal type:
   - Daily Focus Time (minutes)
   - Screen Time Limit (minutes)
   - Weekly Focus Hours (hours)
   - Daily Breaks (count)
   - Productivity Score (points)
   - Max Distractions (count)
4. Set target value
5. Choose reminder time
6. Tap **"Create Goal"**

**Tracking Progress:**
- Progress bars show completion %
- Daily/weekly view available
- Notifications when goals achieved
- Streak counter for consistency

**Goal Recommendations:**
- **Beginners:** 2 hours focus time daily
- **Intermediate:** 4 hours focus time daily
- **Advanced:** 6+ hours focus time daily
- **Screen Time:** < 4 hours daily
- **Breaks:** 4-6 breaks per workday

### AI Insights

**Pattern Detection:**
The system learns your patterns:
- Peak productivity hours (e.g., "You're most focused 9-11 AM")
- Distraction triggers (e.g., "Instagram usage peaks after lunch")
- Break timing (e.g., "You're more productive after 10-min breaks")
- Weekly trends (e.g., "Mondays are your most focused days")

**Personalized Tips:**
Based on your data, you get tips like:
- "Schedule deep work sessions between 9-11 AM"
- "Take a break every 90 minutes for peak performance"
- "Block Instagram before 12 PM to avoid morning distractions"
- "Your productivity drops after 3 PM - consider lighter tasks"

---

## 🤖 IoT Integration

### Connecting Your IoT Device

**Hardware Requirements:**
- Raspberry Pi 4 (4GB RAM recommended)
- Temperature/Humidity sensor (DHT22)
- Light sensor (TSL2561)
- Sound sensor (USB microphone)
- Motion sensor (PIR)
- WiFi connection

**Setup Steps:**
1. **Prepare Device:**
   - Flash Raspberry Pi OS
   - Install required libraries
   - Configure WiFi
   - Run `python mqtt_client.py`

2. **Connect to App:**
   - Open mobile app
   - Go to **Settings** → **Devices**
   - Tap **"Add Device"**
   - Enter device details:
     - Device Name: "My Office Desk"
     - Device ID: (shown on Pi screen)
     - Location: "Home Office"
   - Tap **"Connect"**

3. **Verify Connection:**
   - Device status shows 🟢 Connected
   - Sensor data starts appearing
   - Test automation triggers

### Sensor Monitoring

**Real-Time Sensor Data:**

View in app at **Home** → **Environment**:

| Sensor | Current Value | Status | Normal Range |
|--------|---------------|--------|--------------|
| 🌡️ **Temperature** | 23.5°C | ✅ Comfortable | 18-26°C |
| 💧 **Humidity** | 45% | ✅ Good | 30-60% |
| 💡 **Light** | 320 lux | ✅ Adequate | 200-500 lux |
| 🔊 **Noise** | 42 dB | ✅ Quiet | < 60 dB |
| 🚶 **Motion** | No motion 15m | ⚠️ Sitting | - |

**Status Indicators:**
- 🟢 **Optimal** - Ideal conditions
- 🟡 **Acceptable** - Slightly off, minor adjustments
- 🟠 **Poor** - Not ideal, action recommended
- 🔴 **Critical** - Immediate action needed

### Smart Automations

**Automatic Actions:**

1. **High Noise Detection**
   - **Trigger:** Noise > 70 dB for 5 minutes
   - **Action:** Enable Do Not Disturb mode
   - **Notification:** "High noise detected - DND activated"

2. **Poor Lighting**
   - **Trigger:** Light < 200 lux (too dark)
   - **Action:** Suggest increasing brightness
   - **Notification:** "Low light detected - adjust screen brightness"

3. **Break Reminders**
   - **Trigger:** No motion for 90 minutes
   - **Action:** Suggest taking a break
   - **Notification:** "You've been sitting for 90 min - take a break!"

4. **Scheduled Focus Mode**
   - **Trigger:** Work hours start (e.g., 9 AM)
   - **Action:** Auto-activate focus mode
   - **Notification:** "Focus time! Your session has started"

5. **Temperature Alerts**
   - **Trigger:** Temperature > 26°C or < 18°C
   - **Action:** Alert about uncomfortable temperature
   - **Notification:** "Room temperature uncomfortable - adjust AC"

**Customizing Automations:**
1. Go to **Settings** → **Automations**
2. Toggle automations ON/OFF
3. Adjust thresholds:
   - Noise threshold: 60-80 dB
   - Light threshold: 150-300 lux
   - Break interval: 60-120 minutes
   - Temperature range: 18-28°C
4. Set notification preferences
5. Save changes

---

## ⚙️ Settings & Customization

### Account Settings

**Profile:**
- Edit name and email
- Change password
- Profile picture
- Work hours
- Time zone

**Privacy:**
- Data retention period
- Export your data
- Delete account
- Privacy preferences

**Notifications:**
- Enable/disable push notifications
- Notification sound
- Vibration
- LED color (Android)
- Quiet hours (e.g., 10 PM - 7 AM)

### App Preferences

**Focus Mode:**
- Default session duration
- Default blocked apps
- Break reminder interval
- Session end sound
- Show motivational quotes

**Analytics:**
- Data collection (opt-out available)
- Weekly summary emails
- Goal reminder times
- Chart types to show

**Appearance:**
- Dark/Light theme
- Accent color
- Font size
- Animation speed

### Advanced Settings

**Developer Options:**
- Enable debug logging
- View API requests
- Test mode
- Reset app data

**Experimental Features:**
- Beta features toggle
- AI model version
- Advanced privacy options

---

## 💡 Tips & Best Practices

### Maximizing Productivity

**Morning Routine:**
1. Check yesterday's productivity score
2. Review today's schedule
3. Plan 2-3 focus sessions
4. Set a daily goal
5. Start with hardest task first

**Focus Session Strategy:**
- **Pomodoro (25 min):** Quick tasks, emails, admin work
- **Deep Work (50 min):** Complex problems, creative work
- **Extended (90 min):** Major projects, deep research

**Break Timing:**
- **5-minute breaks:** Every 25-30 minutes
- **10-minute breaks:** Every 50-90 minutes
- **30-minute breaks:** Every 2-3 hours
- **Lunch break:** 30-60 minutes

### Privacy Best Practices

**Daily Habits:**
- ✅ Keep VPN enabled always
- ✅ Review blocked trackers weekly
- ✅ Check privacy score daily
- ✅ Update app permissions monthly
- ✅ Use location spoofing on social media

**Security Checklist:**
- [ ] Strong password (12+ characters)
- [ ] Two-factor authentication enabled
- [ ] Regular data backups
- [ ] Review connected devices monthly
- [ ] Update app when prompted

### Wellbeing Optimization

**Healthy Digital Habits:**
- 🎯 Limit screen time to < 6 hours daily
- 🎯 Take breaks every 90 minutes
- 🎯 No screens 1 hour before bed
- 🎯 Check phone < 50 times daily
- 🎯 Batch notifications (check 3x daily)

**Environment Setup:**
- **Lighting:** 300-500 lux for computer work
- **Noise:** < 50 dB for focused work
- **Temperature:** 20-24°C optimal
- **Humidity:** 40-60% comfortable
- **Posture:** Eye level with top of screen

### Troubleshooting Common Issues

**App Not Blocking Apps:**
1. Check **Usage Stats** permission granted
2. Enable **Display Over Apps** permission
3. Restart focus session
4. Reinstall app if persistent

**VPN Not Connecting:**
1. Check internet connection
2. Try different server location
3. Restart app
4. Check firewall settings
5. Contact support if unresolved

**IoT Device Offline:**
1. Check WiFi connection
2. Restart IoT device
3. Verify MQTT broker running
4. Re-pair device in app
5. Check firewall rules

**Notifications Not Filtering:**
1. Grant Notification Access permission
2. Enable ML model in settings
3. Wait for model to learn (24-48 hours)
4. Manually classify some notifications
5. Update app to latest version

---

## 📞 Support & Resources

### Getting Help

**In-App Help:**
- **Settings** → **Help & Support**
- **Chat Support:** Available 9 AM - 5 PM EST
- **FAQ:** Common questions answered

**Documentation:**
- [Setup Guide](SETUP_GUIDE.md)
- [Privacy Features](PRIVACY_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [FAQ](FAQ.md)

**Community:**
- GitHub Issues: Bug reports and feature requests
- Discord Server: Community discussions
- Email: support@digitalwellbeing.app

### Feedback

We love hearing from users!

**Report Bugs:**
- Go to **Settings** → **Report Bug**
- Describe the issue
- Include screenshots if possible
- Submit report

**Request Features:**
- Go to **Settings** → **Feature Request**
- Describe desired feature
- Explain use case
- Submit request

**Rate the App:**
- Go to **Settings** → **Rate App**
- Leave a review (App Store/Play Store)
- Share your experience

---

## 🎓 Learning Resources

### Video Tutorials

- **Getting Started** (5 min)
- **Focus Mode Deep Dive** (10 min)
- **Privacy Features** (8 min)
- **Analytics Dashboard** (7 min)
- **IoT Setup** (15 min)

### Quick Reference Cards

- [Focus Mode Quick Reference](focus-quick-ref.pdf)
- [Privacy Controls Cheat Sheet](privacy-cheat-sheet.pdf)
- [Keyboard Shortcuts](shortcuts.pdf)

---

**Last Updated:** January 2, 2026  
**App Version:** 1.0.0  
**Support:** support@digitalwellbeing.app

---

*Your privacy, focus, and wellbeing matter. We're here to help you take control of your digital life.*
