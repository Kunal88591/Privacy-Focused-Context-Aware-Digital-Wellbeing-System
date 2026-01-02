# 🚀 Setup Guide - Privacy-Focused Digital Wellbeing System

**Quick Setup Time:** 15-30 minutes  
**Difficulty:** Beginner Friendly  
**Last Updated:** January 2, 2026

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Backend Setup](#backend-setup)
3. [Mobile App Setup](#mobile-app-setup)
4. [IoT Device Setup (Optional)](#iot-device-setup-optional)
5. [First-Time Configuration](#first-time-configuration)
6. [Verification & Testing](#verification--testing)
7. [Next Steps](#next-steps)

---

## 💻 System Requirements

### Mobile App

**Android:**
- Android 8.0 (Oreo) or higher
- 2GB RAM minimum (4GB recommended)
- 100MB free storage
- Internet connection (WiFi or mobile data)

**iOS:**
- iOS 13.0 or higher
- iPhone 6S or newer
- 100MB free storage
- Internet connection (WiFi or mobile data)

### Backend Server (Optional - for self-hosting)

- **OS:** Ubuntu 20.04+ / macOS 10.15+ / Windows 10+
- **RAM:** 2GB minimum (4GB recommended)
- **Storage:** 1GB free space
- **Python:** 3.9 or higher
- **Docker:** 20.10+ (optional but recommended)

### IoT Device (Optional)

- **Hardware:** Raspberry Pi 4 (2GB+ RAM)
- **OS:** Raspberry Pi OS (32-bit or 64-bit)
- **Sensors:** DHT22, TSL2561, PIR, USB microphone
- **Network:** WiFi connection

---

## 🖥️ Backend Setup

### Option 1: Docker (Recommended)

**Easiest setup - everything in one command!**

```bash
# Clone repository
git clone https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System.git
cd Privacy-Focused-Context-Aware-Digital-Wellbeing-System

# Start all services with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Services Started:**
- ✅ Backend API (http://localhost:8000)
- ✅ MQTT Broker (mqtt://localhost:1883)
- ✅ PostgreSQL Database
- ✅ API Documentation (http://localhost:8000/docs)

**Check Health:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### Option 2: Manual Installation

**For developers or custom setups**

#### 1. Install Python Dependencies

```bash
# Navigate to backend directory
cd backend-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment

```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/wellbeing
MQTT_BROKER=localhost
MQTT_PORT=1883
JWT_SECRET=your-secret-key-here
ENVIRONMENT=development
EOF
```

#### 3. Start MQTT Broker

```bash
# Install Mosquitto
# Ubuntu/Debian:
sudo apt-get install mosquitto mosquitto-clients

# macOS:
brew install mosquitto

# Start broker
mosquitto -c mosquitto/config/mosquitto.conf
```

#### 4. Start Backend Server

```bash
cd backend-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Backend:**
- Open http://localhost:8000/docs
- You should see the interactive API documentation

---

## 📱 Mobile App Setup

### Option 1: Download Release APK (Android Only)

**Easiest for end users**

```bash
# 1. Download latest APK from GitHub Releases
https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/releases

# 2. Enable "Install from Unknown Sources" on your Android device
Settings → Security → Unknown Sources → Enable

# 3. Install the APK
- Open downloaded APK file
- Tap "Install"
- Wait for installation to complete
- Tap "Open"
```

### Option 2: Build from Source

**For developers**

#### Prerequisites

```bash
# Install Node.js and npm
# Ubuntu/Debian:
sudo apt-get install nodejs npm

# macOS:
brew install node

# Verify installation
node --version  # Should be 16.x or higher
npm --version   # Should be 8.x or higher
```

#### Android Setup

```bash
# 1. Install Android Studio
# Download from: https://developer.android.com/studio

# 2. Install Android SDK (via Android Studio)
# SDK Platform: Android 13.0 (API 33)
# SDK Tools: Android SDK Build-Tools, Platform-Tools

# 3. Set environment variables
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

#### iOS Setup (macOS only)

```bash
# 1. Install Xcode from App Store

# 2. Install Xcode Command Line Tools
xcode-select --install

# 3. Install CocoaPods
sudo gem install cocoapods
```

#### Build Mobile App

```bash
# Navigate to mobile app directory
cd mobile-app

# Install dependencies
npm install

# Configure backend URL
cat > .env << EOF
API_URL=http://your-backend-server:8000
MQTT_BROKER=your-mqtt-broker
EOF

# For Android
npm run android

# For iOS (macOS only)
cd ios && pod install && cd ..
npm run ios
```

### Option 3: Expo Development Build

**For testing during development**

```bash
# Install Expo CLI globally
npm install -g expo-cli

# Navigate to mobile app
cd mobile-app

# Install dependencies
npm install

# Start Expo dev server
npx expo start

# Scan QR code with:
# - Android: Expo Go app
# - iOS: Camera app
```

**Download Expo Go:**
- **Android:** [Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
- **iOS:** [App Store](https://apps.apple.com/app/expo-go/id982107779)

---

## 🤖 IoT Device Setup (Optional)

### Hardware Assembly

**Required Components:**
- Raspberry Pi 4 (4GB RAM)
- MicroSD card (16GB+ Class 10)
- Power supply (5V 3A USB-C)
- DHT22 Temperature/Humidity sensor
- TSL2561 Light sensor
- PIR Motion sensor
- USB Microphone
- Jumper wires
- Breadboard (optional)

**Wiring Diagram:**

```
Raspberry Pi 4 GPIO Pinout:

DHT22 Sensor:
- VCC  → Pin 1 (3.3V)
- DATA → Pin 7 (GPIO 4)
- GND  → Pin 6 (Ground)

TSL2561 Light Sensor (I2C):
- VCC → Pin 1 (3.3V)
- SDA → Pin 3 (GPIO 2 - SDA)
- SCL → Pin 5 (GPIO 3 - SCL)
- GND → Pin 6 (Ground)

PIR Motion Sensor:
- VCC → Pin 2 (5V)
- OUT → Pin 11 (GPIO 17)
- GND → Pin 9 (Ground)

USB Microphone:
- USB → Any USB port
```

### Software Installation

#### 1. Flash Raspberry Pi OS

```bash
# Download Raspberry Pi Imager
https://www.raspberrypi.com/software/

# Flash Raspberry Pi OS Lite (64-bit) to SD card
# Enable SSH and configure WiFi during setup
```

#### 2. Initial Configuration

```bash
# SSH into Pi (default password: raspberry)
ssh pi@raspberrypi.local

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Change default password
passwd

# Configure system
sudo raspi-config
# - Enable I2C (Interface Options → I2C → Yes)
# - Enable SPI (Interface Options → SPI → Yes)
# - Set hostname (System Options → Hostname)
# - Expand filesystem (Advanced → Expand Filesystem)
```

#### 3. Install Dependencies

```bash
# Install Python and pip
sudo apt-get install python3 python3-pip git -y

# Install required libraries
sudo pip3 install paho-mqtt Adafruit-DHT adafruit-circuitpython-tsl2561 RPi.GPIO pyaudio numpy
```

#### 4. Clone and Configure IoT Code

```bash
# Clone repository
git clone https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System.git
cd Privacy-Focused-Context-Aware-Digital-Wellbeing-System/iot-device

# Configure MQTT settings
nano config.json
```

**config.json:**
```json
{
  "mqtt_broker": "your-backend-server",
  "mqtt_port": 1883,
  "device_id": "rpi4-001",
  "location": "home-office",
  "sensors": {
    "dht22_pin": 4,
    "tsl2561_address": "0x39",
    "pir_pin": 17,
    "microphone_device": 0
  },
  "sampling_interval": 60
}
```

#### 5. Test Sensors

```bash
# Test DHT22 (temperature/humidity)
python3 -c "import Adafruit_DHT; sensor = 22; pin = 4; humidity, temperature = Adafruit_DHT.read_retry(sensor, pin); print(f'Temp: {temperature}C, Humidity: {humidity}%')"

# Test TSL2561 (light)
python3 -c "import board; import adafruit_tsl2561; i2c = board.I2C(); sensor = adafruit_tsl2561.TSL2561(i2c); print(f'Light: {sensor.lux} lux')"

# Test PIR (motion)
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN); print(f'Motion: {GPIO.input(17)}')"
```

#### 6. Start IoT Service

```bash
# Run manually (for testing)
python3 mqtt_client.py

# Or setup as service (auto-start on boot)
sudo cp iot-device.service /etc/systemd/system/
sudo systemctl enable iot-device
sudo systemctl start iot-device
sudo systemctl status iot-device
```

**Verify IoT Connection:**
```bash
# Check MQTT messages (from another terminal)
mosquitto_sub -h localhost -t "sensors/#" -v
# Should see sensor data every 60 seconds
```

---

## 🎯 First-Time Configuration

### 1. Create Your Account

**On Mobile App:**
1. Open app
2. Tap **"Register"**
3. Enter:
   - Email: your@email.com
   - Password: (12+ characters)
   - Confirm password
4. Agree to Terms & Privacy Policy
5. Tap **"Create Account"**
6. Verify email (check inbox)

### 2. Grant Required Permissions

**Android Permissions:**

```
✅ Notifications Access
   Settings → Apps → Digital Wellbeing → Notifications → Allow

✅ Usage Access
   Settings → Apps → Special Access → Usage Access → Digital Wellbeing → Allow

✅ Display Over Other Apps
   Settings → Apps → Special Access → Display over other apps → Digital Wellbeing → Allow

⚠️ VPN Service (Optional)
   Prompted when enabling VPN in app

⚠️ Phone (Optional)
   Prompted when enabling caller masking

⚠️ Location (Optional)
   Prompted when using location features
```

**iOS Permissions:**
```
✅ Notifications
   Allow when prompted

✅ Background App Refresh
   Settings → General → Background App Refresh → On

⚠️ VPN Configurations
   Prompted when enabling VPN in app
```

### 3. Configure Basic Settings

**Set Work Hours:**
```
Settings → Work Schedule
- Start Time: 9:00 AM
- End Time: 5:00 PM
- Work Days: Monday - Friday
- Auto-activate focus: ON
```

**Choose Blocked Apps:**
```
Focus Mode → Blocked Apps
Select apps to block:
☑️ Instagram
☑️ Twitter
☑️ TikTok
☑️ Facebook
☑️ YouTube
☑️ Reddit
☐ WhatsApp (keep for work)
☐ Slack (keep for work)
```

**Privacy Settings:**
```
Privacy → Quick Setup Wizard
1. Enable VPN Protection: YES
2. Caller ID Masking: FULL
3. Location Spoofing: RANDOM
4. Data Encryption: ON (default)
5. Auto-wipe threshold: 3 threats
```

### 4. Connect Backend Server (if self-hosting)

```
Settings → Advanced → Server Configuration
- API URL: http://your-server:8000
- MQTT Broker: your-server
- MQTT Port: 1883
- Test Connection → Should show ✅ Connected
```

### 5. Connect IoT Device (if available)

```
Settings → Devices → Add Device
- Device Name: "Office Desk"
- Device ID: rpi4-001
- Location: "Home Office"
- Connect → Wait for pairing
- Status should show: 🟢 Connected
```

---

## ✅ Verification & Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected", "mqtt": "connected"}

# API documentation
open http://localhost:8000/docs
# Should show interactive Swagger UI

# Test endpoints
curl http://localhost:8000/api/v1/auth/status
# Expected: {"status": "ok"}
```

### Test Mobile App

**1. Authentication:**
- Register new account ✅
- Login with credentials ✅
- View profile ✅

**2. Focus Mode:**
- Start 25-min session ✅
- Try opening blocked app → Should see overlay ✅
- End session → Should see stats ✅

**3. Privacy Features:**
- Enable VPN ✅
- Check privacy score ✅
- View blocked trackers ✅

**4. Analytics:**
- View dashboard ✅
- See charts ✅
- Check productivity score ✅

### Test IoT Integration

```bash
# Publish test sensor data
mosquitto_pub -h localhost -t "sensors/test/temperature" -m '{"value": 23.5, "unit": "celsius"}'

# Check if mobile app receives data
# Go to Home → Environment → Should see temperature update

# Trigger automation
mosquitto_pub -h localhost -t "sensors/test/noise" -m '{"value": 75, "unit": "dB"}'
# Should trigger DND notification on mobile
```

---

## 🎊 Next Steps

### Recommended Setup Path

**Day 1: Basic Usage**
1. ✅ Complete setup (done!)
2. Create first focus session (25 min)
3. Check analytics dashboard
4. Enable VPN protection
5. Set daily goal (2 hours focus time)

**Day 2-7: Learning Phase**
- Try different focus durations
- Explore privacy features
- Review weekly analytics
- Adjust blocked apps list
- Fine-tune notification filtering

**Week 2: Optimization**
- Connect IoT device (if available)
- Set up automations
- Customize focus schedules
- Review AI insights
- Optimize settings based on data

**Week 3+: Advanced Usage**
- Deep dive into analytics
- Share progress with team (optional)
- Experiment with advanced features
- Provide feedback
- Contribute to community

### Learning Resources

**Documentation:**
- 📖 [User Manual](USER_MANUAL.md) - Complete feature guide
- 🔒 [Privacy Guide](PRIVACY_GUIDE.md) - Privacy features explained
- 🛠️ [Troubleshooting](TROUBLESHOOTING.md) - Common issues & solutions
- ❓ [FAQ](FAQ.md) - Frequently asked questions

**Video Tutorials:** (Coming Soon)
- Getting Started (5 min)
- Focus Mode Masterclass (10 min)
- Privacy Setup (8 min)
- IoT Device Setup (15 min)

**Community:**
- GitHub Discussions
- Discord Server
- Email Support: support@digitalwellbeing.app

---

## 🆘 Need Help?

**Common Setup Issues:**

| Issue | Solution |
|-------|----------|
| Backend won't start | Check port 8000 not in use: `lsof -i :8000` |
| Mobile app can't connect | Verify backend URL in app settings |
| IoT device offline | Check WiFi, restart device, re-pair |
| VPN not working | Check permissions, try different server |
| Focus mode not blocking | Grant "Display Over Apps" permission |

**Get Support:**
- 📧 Email: support@digitalwellbeing.app
- 💬 GitHub Issues: Report bugs
- 🗨️ Discord: Community help
- 📚 Docs: docs.digitalwellbeing.app

---

## 🎉 Setup Complete!

**Congratulations! Your system is ready to use.**

**Quick Start Checklist:**
- ✅ Backend running
- ✅ Mobile app installed
- ✅ Account created
- ✅ Permissions granted
- ✅ Settings configured
- ✅ First focus session completed

**Now you can:**
- 🎯 Improve your focus and productivity
- 🔒 Protect your privacy
- 📊 Track your wellbeing
- 🤖 Optimize your environment

---

**Last Updated:** January 2, 2026  
**Setup Version:** 1.0.0  
**Support:** setup-help@digitalwellbeing.app

*Happy focusing! 🚀*
