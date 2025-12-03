# 📱 How to Run the Mobile App - Step by Step

## Option 1: Web Preview (Easiest - See UI in Browser)

### Using Expo (Recommended for quick preview)

1. **Install Expo CLI:**
```bash
npm install -g expo-cli
```

2. **Start the app:**
```bash
cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/mobile-app
npx expo start --web
```

3. **See the UI in browser!** It will open automatically at http://localhost:19006

---

## Option 2: React Native Web (Alternative)

```bash
cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/mobile-app

# Install react-native-web
npm install react-native-web react-dom --legacy-peer-deps

# Start web server
npx react-native start --web
```

---

## Option 3: Android Emulator (If you have it)

1. **Start Metro bundler:**
```bash
cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/mobile-app
npm start
```

2. **In another terminal, run Android:**
```bash
npm run android
```

---

## What You'll See:

### Bottom Tab Navigation
```
┌─────────────────────────────────────┐
│                                     │
│         MAIN CONTENT                │
│                                     │
│  [Your screen content here]         │
│                                     │
│                                     │
└─────────────────────────────────────┘
┌───────┬─────────┬─────────┬─────────┐
│ 🏠    │ 📬      │ 🔒      │ ⚙️      │
│ Home  │ Notify  │ Privacy │ Settings│
└───────┴─────────┴─────────┴─────────┘
```

### Home Screen Shows:
- 🌡️ Temperature: 22.5°C
- 💧 Humidity: 45%
- 💡 Light: 350 lux
- 🔊 Noise: 40 dB
- 🎯 Focus Mode Button
- 📊 Stats: Focus time, Blocked apps
- 🔒 Privacy Status

### Notifications Screen:
- Filter buttons: ALL | URGENT | NORMAL
- List of notifications with badges
- Swipe to delete

### Privacy Screen:
- VPN Toggle
- Caller ID Masking Toggle
- Location Spoofing Toggle
- Privacy Score: 0-100%
- Auto-wipe counter (0/3)

### Settings Screen:
- API URL input
- MQTT Broker settings
- Preferences toggles
- Save/Reset buttons

---

## Quick Test (See Mobile App Code)

Since we're in Codespaces, you can **see the code** right now:

```bash
# Open mobile app screens
code mobile-app/src/screens/HomeScreen.js
code mobile-app/src/screens/NotificationsScreen.js
code mobile-app/src/screens/PrivacyScreen.js
code mobile-app/src/screens/SettingsScreen.js
```

**Look at the code** - you'll see all the UI components, buttons, and styling!

