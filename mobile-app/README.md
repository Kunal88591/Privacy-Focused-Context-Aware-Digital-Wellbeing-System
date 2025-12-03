# Privacy Wellbeing Mobile App

React Native mobile app for the Privacy-Focused Context-Aware Digital Wellbeing System.

## Features

### 📱 Screens
- **HomeScreen**: Dashboard with real-time stats, privacy status, and environment sensors
- **NotificationsScreen**: ML-classified notification management with urgent/normal filters
- **PrivacyScreen**: Comprehensive privacy controls (VPN, caller masking, location spoofing, auto-wipe)
- **SettingsScreen**: App configuration (API URL, MQTT broker, preferences)

### 🔄 Real-Time Features
- MQTT integration for live sensor data (temperature, humidity, light, noise, motion)
- Real-time notification alerts
- Live privacy status updates
- Environment monitoring dashboard

### 🎯 Core Functionality
- Focus mode activation/deactivation
- Distraction blocking
- Productivity tracking
- Privacy score calculation
- Data encryption status

## Tech Stack

- **Framework**: React Native 0.73
- **Navigation**: React Navigation 6 (Bottom Tabs)
- **State**: AsyncStorage for persistence
- **API**: Axios for REST calls
- **Real-Time**: react-native-mqtt for pub/sub messaging
- **Encryption**: react-native-encrypted-storage

## Setup Instructions

### 1. Install Dependencies

```bash
cd mobile-app
npm install
```

### 2. Install Additional Packages

```bash
# iOS (requires CocoaPods)
cd ios && pod install && cd ..

# React Navigation dependencies
npm install @react-navigation/native @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context

# MQTT
npm install react-native-mqtt

# Storage
npm install @react-native-async-storage/async-storage
npm install react-native-encrypted-storage
```

### 3. Configure API and MQTT

Edit `src/config/index.js`:

```javascript
export default {
  API_URL: 'http://localhost:8000',  // Backend API
  MQTT_HOST: 'localhost',             // MQTT broker
  MQTT_PORT: '1883',
};
```

Or configure via Settings screen in the app.

### 4. Run the App

#### Android
```bash
npm run android
```

#### iOS
```bash
npm run ios
```

#### Metro Bundler
```bash
npm start
```

## Project Structure

```
mobile-app/
├── src/
│   ├── navigation/
│   │   └── AppNavigator.js       # Bottom tab navigation
│   ├── screens/
│   │   ├── HomeScreen.js         # Main dashboard
│   │   ├── NotificationsScreen.js # Notification list
│   │   ├── PrivacyScreen.js      # Privacy controls
│   │   └── SettingsScreen.js     # Configuration
│   ├── services/
│   │   ├── api.js                # REST API client
│   │   └── mqtt.js               # MQTT service
│   └── config/
│       └── index.js              # App configuration
├── App.js                         # Entry point
└── package.json
```

## API Integration

### Endpoints Used

**Wellbeing API**
- `GET /wellbeing/stats/{period}` - Get focus time, distractions blocked, productivity score
- `GET /wellbeing/focus/status` - Check focus mode status
- `POST /wellbeing/focus/activate` - Start focus mode
- `POST /wellbeing/focus/deactivate` - Stop focus mode

**Privacy API**
- `GET /privacy/status` - Get VPN, caller masking, encryption status
- `POST /privacy/vpn/toggle` - Enable/disable VPN
- `POST /privacy/caller-id/toggle` - Toggle caller ID masking
- `POST /privacy/location/spoof` - Configure location spoofing
- `POST /privacy/auto-wipe/configure` - Set auto-wipe threshold

**Notifications API**
- `GET /notifications/classified` - Get ML-classified notifications
- `POST /notifications/classify` - Classify new notification
- `DELETE /notifications/{id}` - Delete notification

**Device API**
- `GET /devices` - List registered IoT devices
- `POST /devices/command` - Send command to device

## MQTT Topics

### Subscribed Topics
- `sensors/environment` - Temperature and humidity data
- `sensors/motion` - Motion detection events
- `sensors/light` - Light level measurements
- `sensors/noise` - Noise level readings
- `alerts/urgent` - High-priority alerts
- `commands/response` - Device command responses

### Published Topics
- `commands/device` - Send commands to IoT device

## State Management

Currently using local component state with AsyncStorage for persistence:
- API URL configuration
- MQTT broker settings
- User preferences (notifications, dark mode, auto-sync)

Future: Consider Context API or Redux for global state.

## Testing

```bash
# Unit tests
npm test

# E2E tests (requires Detox)
npm run test:e2e
```

## Troubleshooting

### MQTT Connection Issues
- Ensure MQTT broker is running: `mosquitto -v`
- Check firewall settings for port 1883
- Verify MQTT_HOST is correct (use device IP for physical devices, not localhost)

### API Connection Issues
- Backend must be running: `cd backend-api && python3 -m uvicorn app.main:app --reload`
- For physical devices, use computer's IP address instead of localhost
- Check CORS settings in backend

### Build Issues
- Clear Metro cache: `npm start -- --reset-cache`
- Clean build: `cd android && ./gradlew clean && cd ..`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## Next Steps

- [ ] Add Context API for global state management
- [ ] Implement push notifications
- [ ] Add charts for analytics dashboard
- [ ] Create onboarding flow
- [ ] Add biometric authentication
- [ ] Implement offline mode with sync
- [ ] Add unit and integration tests
- [ ] Polish UI/UX with animations
- [ ] Add dark mode support
- [ ] Optimize performance with React.memo

## Screenshots

(Coming soon)

## License

See LICENSE file in root directory.
