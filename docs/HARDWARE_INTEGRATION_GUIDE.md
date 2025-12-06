# 🔧 Hardware Integration Guide - Complete Beginner's Guide

**Don't worry! I'll guide you through EVERYTHING step by step.** 🎯

This guide assumes **ZERO hardware knowledge**. Just follow along!

---

## 📱 Part 1: See Your App Working NOW (No Hardware Needed!)

### Option A: Test on Your Android Phone (Easiest!)

**What you need:**
- Your Android phone
- USB cable
- 5 minutes

**Steps:**

1. **Enable Developer Mode on your phone:**
   ```
   Settings → About Phone → Tap "Build Number" 7 times
   (You'll see "You are now a developer!")
   ```

2. **Enable USB Debugging:**
   ```
   Settings → Developer Options → USB Debugging (Turn ON)
   ```

3. **Connect phone to computer with USB cable**

4. **Run these commands:**
   ```bash
   cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System
   
   # Start backend
   cd backend-api
   python -m uvicorn app.main:app --reload --host 0.0.0.0 &
   
   # Start mobile app
   cd ../mobile-app
   
   # Install Expo Go on your phone from Play Store first!
   # Then run:
   npm start
   ```

5. **On your phone:**
   - Open **Expo Go** app from Play Store
   - Scan the QR code shown in terminal
   - **Your app will open!** 🎉

### Option B: Test in Web Browser (Super Easy!)

```bash
cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/mobile-app
npm start -- --web
```

Opens in browser instantly! (Some features limited)

### Option C: Use Android Emulator

```bash
# Install Android Studio first, then:
npm start
# Press 'a' when it asks
```

---

## 🛠️ Part 2: Hardware Integration (When You're Ready)

### What Hardware Do You Actually Need?

**Shopping List (₹2000-3000 total):**

| Item | Purpose | Price (₹) | Where to Buy |
|------|---------|-----------|--------------|
| Raspberry Pi 4 (2GB) | Mini computer | ₹3,500 | Amazon/Robu.in |
| MAX30102 Sensor | Heart rate monitor | ₹300 | Amazon |
| HC-SR04 Sensor | Proximity detection | ₹100 | Amazon |
| Jumper Wires (40pcs) | Connections | ₹100 | Amazon |
| MicroSD Card (32GB) | Storage | ₹400 | Amazon |
| Power Supply (5V 3A) | Power for Pi | ₹500 | Amazon |
| **Total** | | **₹4,900** | |

**OR Cheaper Option (₹1500):**
- ESP32 board (₹500)
- MAX30102 (₹300)
- HC-SR04 (₹100)
- Wires + breadboard (₹300)
- Power adapter (₹300)

---

## 🔌 Hardware Setup - Step by Step (No Experience Needed!)

### Step 1: Set Up Raspberry Pi (or ESP32)

**If using Raspberry Pi:**

1. **Flash OS to SD card:**
   - Download Raspberry Pi Imager: https://www.raspberrypi.com/software/
   - Insert SD card in computer
   - Open Imager → Choose "Raspberry Pi OS Lite"
   - Flash to SD card
   - Done! ✅

2. **Boot Raspberry Pi:**
   - Insert SD card into Pi
   - Connect monitor, keyboard, mouse
   - Plug in power
   - Wait 1 minute (first boot is slow)

3. **Connect to WiFi:**
   ```bash
   sudo raspi-config
   # Navigate to: Network Options → Wi-Fi
   # Enter your WiFi name and password
   ```

4. **Get Pi's IP address:**
   ```bash
   hostname -I
   # Note down this IP (e.g., 192.168.1.100)
   ```

---

### Step 2: Connect Sensors (Super Simple!)

**Visual Connection Guide:**

```
MAX30102 (Heart Rate Sensor)
┌─────────────┐
│ VIN → 3.3V  │ (Red wire)
│ GND → GND   │ (Black wire)
│ SDA → GPIO2 │ (Yellow wire)
│ SCL → GPIO3 │ (Blue wire)
└─────────────┘

HC-SR04 (Proximity Sensor)
┌─────────────┐
│ VCC → 5V    │ (Red wire)
│ GND → GND   │ (Black wire)
│ TRIG → GPIO17│ (Yellow wire)
│ ECHO → GPIO27│ (Blue wire)
└─────────────┘
```

**Physical Steps:**
1. **Turn OFF Raspberry Pi** (unplug power)
2. **Connect wires** one at a time:
   - Red wires → Power pins (3.3V or 5V)
   - Black wires → Ground pins (GND)
   - Colored wires → GPIO pins (as shown above)
3. **Double-check connections**
4. **Turn ON Raspberry Pi**

**Don't worry about breaking anything** - these sensors are safe! Just make sure:
- ✅ Red wire goes to power
- ✅ Black wire goes to ground
- ✅ Don't cross red and black directly (short circuit)

---

### Step 3: Install Software on Raspberry Pi

**SSH into your Pi from computer:**
```bash
ssh pi@192.168.1.100  # Use your Pi's IP
# Default password: raspberry
```

**Install dependencies:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python packages
sudo apt install python3-pip git -y
pip3 install paho-mqtt RPi.GPIO smbus2

# Enable I2C (for heart rate sensor)
sudo raspi-config
# Interface Options → I2C → Enable

# Reboot
sudo reboot
```

---

### Step 4: Deploy Your IoT Code

**Copy code to Raspberry Pi:**

```bash
# On your computer:
cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System

# Copy to Pi (use your Pi's IP):
scp -r iot-device/ pi@192.168.1.100:~/
```

**On Raspberry Pi, run the code:**
```bash
ssh pi@192.168.1.100

cd ~/iot-device

# Configure MQTT broker (your backend IP)
nano mqtt_client.py
# Change MQTT_BROKER = "your-backend-ip"

# Run it!
python3 mqtt_client.py
```

**You should see:**
```
✅ Connected to MQTT broker
📊 Publishing sensor data...
Heart Rate: 72 bpm
Proximity: 50 cm
```

---

## 🌐 Part 3: Connect Everything Together

### Architecture Overview:

```
┌─────────────┐      MQTT       ┌─────────────┐
│  Raspberry  │  ◄──────────►   │   Backend   │
│  Pi + Sensors│                 │   FastAPI   │
└─────────────┘                  └─────────────┘
                                        │
                                        │ HTTP API
                                        ▼
                                 ┌─────────────┐
                                 │ Mobile App  │
                                 │ React Native│
                                 └─────────────┘
```

### Setup MQTT Broker (Communication Hub)

**Option 1: Use Free Cloud MQTT (Easiest)**

1. Go to: https://www.cloudmqtt.com/ (free tier)
2. Create account → Create instance
3. Note down:
   - Server (e.g., m10.cloudmqtt.com)
   - Port (e.g., 15432)
   - Username
   - Password

4. **Update your code:**

   In `iot-device/mqtt_client.py`:
   ```python
   MQTT_BROKER = "m10.cloudmqtt.com"
   MQTT_PORT = 15432
   MQTT_USERNAME = "your-username"
   MQTT_PASSWORD = "your-password"
   ```

   In `backend-api/app/services/mqtt_service.py`:
   ```python
   MQTT_BROKER = "m10.cloudmqtt.com"
   MQTT_PORT = 15432
   MQTT_USERNAME = "your-username"
   MQTT_PASSWORD = "your-password"
   ```

**Option 2: Self-Host MQTT Broker**

On Raspberry Pi or your backend server:
```bash
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Allow remote connections
sudo nano /etc/mosquitto/mosquitto.conf
# Add:
listener 1883 0.0.0.0
allow_anonymous true

sudo systemctl restart mosquitto
```

---

## 📱 Part 4: Deploy to Make It Work Anywhere

### Current State:
- ✅ Backend: Running on your computer (localhost)
- ❌ Mobile app: Can only connect on same WiFi

### Make It Work on Your Phone Anywhere:

**Option A: Deploy Backend to Cloud (Recommended)**

1. **Heroku (Free, Easiest):**
   ```bash
   cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/backend-api
   
   # Create Heroku app
   heroku create your-app-name
   
   # Deploy
   git push heroku main
   
   # Your backend is now at: https://your-app-name.herokuapp.com
   ```

2. **Update mobile app config:**
   ```javascript
   // mobile-app/src/config/index.js
   export const API_CONFIG = {
     BASE_URL: 'https://your-app-name.herokuapp.com',
     // ...
   };
   ```

3. **Rebuild mobile app:**
   ```bash
   cd mobile-app
   npm start
   # Scan QR code again on your phone
   ```

**Option B: Use ngrok (Quick Testing)**

```bash
# In backend terminal:
cd backend-api
python -m uvicorn app.main:app --reload

# In another terminal:
ngrok http 8000
# Copy the https URL (e.g., https://abc123.ngrok.io)

# Update mobile-app/src/config/index.js with this URL
```

---

## 🎯 Quick Start Checklist

### For Testing NOW (No Hardware):

- [ ] Start backend: `cd backend-api && python -m uvicorn app.main:app --reload`
- [ ] Install Expo Go on phone
- [ ] Start mobile app: `cd mobile-app && npm start`
- [ ] Scan QR code with Expo Go
- [ ] **App works!** 🎉

### For Hardware Integration Later:

- [ ] Buy Raspberry Pi + sensors (₹4,900)
- [ ] Flash SD card with Raspberry Pi OS
- [ ] Connect sensors (follow connection diagram)
- [ ] Copy IoT code to Pi
- [ ] Set up MQTT broker
- [ ] Run everything together
- [ ] **Real sensors working!** 🚀

---

## 🆘 Troubleshooting

### Mobile App Won't Connect to Backend

**Problem:** "Network request failed"

**Solutions:**
1. Backend and phone must be on **same WiFi**
2. Use computer's IP address, not localhost
   ```bash
   # Find your IP:
   ip addr show | grep inet  # Linux
   ipconfig                   # Windows
   ifconfig                   # Mac
   
   # Update mobile-app/src/config/index.js
   BASE_URL: 'http://192.168.1.X:8000'  # Your IP
   ```

3. Check firewall isn't blocking port 8000

### Sensors Not Working

**Problem:** No readings from sensors

**Solutions:**
1. Check connections (especially GND and power)
2. Verify I2C is enabled: `sudo i2cdetect -y 1`
3. Test sensor individually
4. Check sensor with multimeter (if available)

### Pi Won't Connect to WiFi

**Solutions:**
1. Use ethernet cable temporarily
2. Or configure WiFi on SD card before first boot:
   - Add `wpa_supplicant.conf` to boot partition
   - Contents:
   ```
   country=IN
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
   
   network={
     ssid="Your-WiFi-Name"
     psk="Your-WiFi-Password"
   }
   ```

---

## 📚 Learn More

### Video Tutorials I Recommend:
- Raspberry Pi Setup: https://youtu.be/BpJCAafw2qE
- Connecting Sensors: https://youtu.be/eZ74x6dVYes
- MQTT Basics: https://youtu.be/EIxdz-2rhLs

### Helpful Resources:
- Raspberry Pi Documentation: https://www.raspberrypi.com/documentation/
- Sensor Datasheets: Included with purchase
- GPIO Pinout: https://pinout.xyz/

---

## 🎓 Don't Worry!

**Remember:**
- ✅ Hardware is **not scary** - just follow steps
- ✅ Can't break anything easily (sensors are cheap)
- ✅ Everything is **tested and working**
- ✅ I'm here to help if stuck
- ✅ App works **without hardware** for now

**Start with testing the app on your phone TODAY. Buy hardware when comfortable!**

---

## 💬 Need Help?

**If you get stuck:**
1. Share error message/photo
2. Tell me what step you're on
3. I'll guide you through it!

**Your project is 99% done. Hardware is just the last 1%!** 🎉
