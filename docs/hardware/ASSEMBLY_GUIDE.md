# Hardware Assembly Guide

## 🔧 Complete Hardware Setup for IoT Device

This guide provides step-by-step instructions to assemble your Privacy-Focused Digital Wellbeing IoT device using Raspberry Pi and sensors.

---

## 📦 What You'll Receive/Buy

### Required Components (Total: ~$133)

| Item | Specifications | Where to Buy | Price |
|------|---------------|--------------|-------|
| Raspberry Pi 4 | 4GB RAM model | Amazon, Adafruit, PiShop | $55 |
| Official Power Supply | 5V 3A USB-C | Same as above | $10 |
| MicroSD Card | 32GB, Class 10, U1 rated | Amazon, Best Buy | $10 |
| PIR Motion Sensor | HC-SR501 | Amazon, AliExpress | $5 |
| DHT22 Sensor | Temperature & Humidity | Amazon, Adafruit | $10 |
| TSL2561 Light Sensor | I2C digital luminosity | Amazon, Adafruit | $8 |
| USB Microphone | Any basic USB mic | Amazon | $15 |
| Jumper Wires | Male-Female, 20cm, 40pcs | Amazon | $5 |
| Breadboard | 400 tie-points | Amazon | $5 |
| Raspberry Pi Case | Official or compatible | Amazon | $10 |

### Optional Components

- OLED Display (0.96" I2C): $8 - Display sensor readings
- Active Buzzer: $3 - Audio feedback
- RGB LED: $2 - Visual status indicator
- 10kΩ Resistors (pack of 100): $5 - Pull-up resistors

### Tools Needed

- Small Phillips screwdriver
- Wire strippers (optional)
- Multimeter (optional, for debugging)
- Laptop/Desktop with SD card reader
- Ethernet cable or WiFi

---

## 🖼️ Visual Wiring Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 4 (Top View)                     │
│                                                                  │
│    USB  USB  ETH  USB  USB                                      │
│    [■]  [■]  [■]  [■]  [■]                                      │
│    ┌──────────────────────────────────────────────────────┐    │
│    │  ┌─────────────────────────────────────────────┐     │    │
│    │  │  3.3V ● ● 5V       GPIO Pins (40-pin)       │     │    │
│    │  │  GPIO2● ● 5V                                │     │    │
│    │  │  GPIO3● ● GND                               │     │    │
│    │  │  GPIO4● ● GPIO14    ← DHT22 Data           │     │    │
│    │  │  GND  ● ● GPIO15                            │     │    │
│    │  │  GPIO17●● GPIO18    ← PIR Sensor           │     │    │
│    │  │  GPIO27●● GND                               │     │    │
│    │  │  GPIO22●● GPIO23                            │     │    │
│    │  │  3.3V ● ● GPIO24                            │     │    │
│    │  │  GPIO10●● GND                               │     │    │
│    │  │  GPIO9● ● GPIO25                            │     │    │
│    │  │  GPIO11●● GPIO8                             │     │    │
│    │  │  GND  ● ● GPIO7                             │     │    │
│    │  │  SDA  ● ● GPIO1     ← TSL2561 SDA          │     │    │
│    │  │  SCL  ● ● GPIO12    ← TSL2561 SCL          │     │    │
│    │  └─────────────────────────────────────────────┘     │    │
│    └──────────────────────────────────────────────────────┘    │
│                                                                  │
│    Power: [USB-C]  ← 5V 3A Power Supply                        │
│    USB:   [USB Port] ← USB Microphone                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Step-by-Step Wiring

### Step 1: Prepare Raspberry Pi

1. **Flash OS to SD Card**
   ```bash
   # Download Raspberry Pi Imager
   # https://www.raspberrypi.org/software/
   
   # Select: Raspberry Pi OS Lite (64-bit)
   # Enable SSH in advanced settings
   # Set hostname: wellbeing-iot
   # Set username: pi, password: your_password
   # Configure WiFi (optional)
   ```

2. **Insert SD card into Raspberry Pi**
3. **DO NOT power on yet!**

### Step 2: Wire PIR Motion Sensor (HC-SR501)

**PIR Sensor Pins:**
```
 ┌─────────────┐
 │   HC-SR501  │
 │   ┌─────┐   │
 │   │ PIR │   │
 │   │Sensor│  │
 │   └─────┘   │
 │             │
 │ VCC OUT GND │
 │  ●   ●   ●  │
 └──┬───┬───┬──┘
    │   │   │
```

**Connections:**
```
PIR Sensor          Raspberry Pi
──────────────────────────────────
VCC (Red wire)   →  5V (Pin 2)
OUT (Yellow)     →  GPIO 17 (Pin 11)
GND (Black)      →  GND (Pin 6)
```

**Wire Routing:**
1. Take a Male-Female jumper wire (Red)
2. Connect Female end to PIR VCC pin
3. Connect Male end to Pi Pin 2 (5V)
4. Repeat for OUT (Yellow to GPIO 17)
5. Repeat for GND (Black to GND)

### Step 3: Wire DHT22 Sensor

**DHT22 Pins (looking at front):**
```
  ┌─────────┐
  │ DHT22   │
  │ ┌─────┐ │
  │ │Grille││
  │ └─────┘ │
  │         │
  │ 1 2 3 4 │
  └─┬─┬─┬─┬─┘
    │ │ │ │
   VCC Data NC GND
```

**Connections:**
```
DHT22              Raspberry Pi
──────────────────────────────────
Pin 1 (VCC)    →   3.3V (Pin 1)
Pin 2 (Data)   →   GPIO 4 (Pin 7)
Pin 3 (NC)     →   Not connected
Pin 4 (GND)    →   GND (Pin 9)
```

**Important: Add Pull-Up Resistor**
```
Connect a 10kΩ resistor between:
- DHT22 Pin 1 (VCC)
- DHT22 Pin 2 (Data)

This ensures stable readings.
```

### Step 4: Wire TSL2561 Light Sensor (I2C)

**TSL2561 Pins:**
```
 ┌──────────┐
 │ TSL2561  │
 │  Light   │
 │  Sensor  │
 │          │
 │ VCC GND  │
 │ SDA SCL  │
 └─┬───┬────┘
   ● ● ● ●
```

**Connections:**
```
TSL2561            Raspberry Pi
──────────────────────────────────
VCC            →   3.3V (Pin 1)
GND            →   GND (Pin 9)
SDA            →   GPIO 2/SDA (Pin 3)
SCL            →   GPIO 3/SCL (Pin 5)
```

**Note:** Multiple I2C devices can share SDA/SCL lines.

### Step 5: Connect USB Microphone

**Simply plug into any USB port on Raspberry Pi.**

No wiring needed! The microphone will be auto-detected.

---

## 🔋 Power Up & Initial Setup

### 1. First Boot

```bash
# Connect power supply to Raspberry Pi USB-C port
# LEDs should light up:
#  - Red LED (power): Solid ON
#  - Green LED (activity): Blinking

# Wait ~30 seconds for first boot

# Find Pi's IP address on your network
# Option 1: Check your router's DHCP client list
# Option 2: Use network scanner
nmap -sn 192.168.1.0/24 | grep wellbeing-iot

# Connect via SSH
ssh pi@wellbeing-iot.local
# or
ssh pi@192.168.1.XXX

# Default password: your_password (set during imaging)
```

### 2. Enable Required Interfaces

```bash
# Run configuration tool
sudo raspi-config

# Navigate to:
# 3. Interface Options
#    → P5 I2C → Enable
#    → P4 SPI → Enable (optional, for future sensors)

# Select "Finish" and reboot
sudo reboot
```

### 3. Update System

```bash
# After reboot, SSH again
ssh pi@wellbeing-iot.local

# Update package lists
sudo apt update

# Upgrade installed packages (takes 5-10 minutes)
sudo apt upgrade -y

# Install essential tools
sudo apt install -y git python3-pip i2c-tools vim
```

---

## ✅ Testing Each Sensor

### Test 1: PIR Motion Sensor

```bash
# Install GPIO library
pip3 install RPi.GPIO

# Create test script
cat > test_pir.py << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

print("PIR Test - Wave your hand in front of sensor...")
print("Press Ctrl+C to exit\n")

try:
    while True:
        if GPIO.input(17):
            print("🚶 MOTION DETECTED!")
        else:
            print("   No motion")
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nTest finished!")
EOF

# Run test
python3 test_pir.py

# Expected output:
# Wave hand → "MOTION DETECTED!" appears
# Stay still → "No motion" appears
```

### Test 2: DHT22 Temperature & Humidity

```bash
# Install DHT library
pip3 install adafruit-circuitpython-dht
sudo apt install -y libgpiod2

# Create test script
cat > test_dht22.py << 'EOF'
import adafruit_dht
import board
import time

dht = adafruit_dht.DHT22(board.D4)

print("DHT22 Test - Reading temperature and humidity...")
print("Press Ctrl+C to exit\n")

try:
    while True:
        try:
            temperature = dht.temperature
            humidity = dht.humidity
            print(f"🌡️  Temp: {temperature:.1f}°C  |  💧 Humidity: {humidity:.1f}%")
        except RuntimeError as e:
            print(f"Reading error: {e}")
        time.sleep(2)
except KeyboardInterrupt:
    dht.exit()
    print("\nTest finished!")
EOF

# Run test
python3 test_dht22.py

# Expected output:
# Temp: 22.5°C  |  Humidity: 45.2%
# (Values should be reasonable for your environment)
```

### Test 3: TSL2561 Light Sensor

```bash
# Install I2C tools and library
sudo apt install -y python3-smbus i2c-tools
pip3 install adafruit-circuitpython-tsl2561

# Verify I2C device detected
sudo i2cdetect -y 1

# Should show device at address 0x39:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- 39 -- -- -- -- -- --
# ...

# Create test script
cat > test_light.py << 'EOF'
import board
import adafruit_tsl2561
import time

i2c = board.I2C()
sensor = adafruit_tsl2561.TSL2561(i2c)

print("TSL2561 Test - Measuring light levels...")
print("Try covering/uncovering the sensor")
print("Press Ctrl+C to exit\n")

try:
    while True:
        lux = sensor.lux
        if lux is not None:
            print(f"💡 Light: {lux:.2f} lux")
        else:
            print("💡 Light: Overexposed or too dark")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nTest finished!")
EOF

# Run test
python3 test_light.py

# Expected output:
# Light: 250.34 lux (typical indoor lighting)
# Cover sensor → value decreases
# Shine light → value increases
```

### Test 4: USB Microphone

```bash
# Install audio tools
sudo apt install -y alsa-utils

# List audio devices
arecord -l

# Expected output:
# card 1: Device [USB Audio Device], device 0: USB Audio [USB Audio]

# Record 5-second test
arecord -D plughw:1,0 -d 5 -f cd test.wav

# Make noise while recording!

# Play back
aplay test.wav

# Test noise level detection
cat > test_microphone.py << 'EOF'
import pyaudio
import numpy as np
import time

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

print("Microphone Test - Measuring noise levels...")
print("Try making sounds (talk, clap, etc.)")
print("Press Ctrl+C to exit\n")

try:
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        rms = np.sqrt(np.mean(data**2))
        db = 20 * np.log10(rms) if rms > 0 else 0
        
        bars = '█' * int(db / 5)
        print(f"🔊 Noise: {db:.1f} dB {bars}")
        time.sleep(0.2)
except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\nTest finished!")
EOF

# Run test
pip3 install pyaudio numpy
python3 test_microphone.py

# Expected output:
# Quiet room: ~30-40 dB
# Normal conversation: ~50-60 dB
# Loud sounds: ~70-80 dB
```

---

## 🏗️ Final Assembly in Case

1. **Mount Raspberry Pi in case**
   - Follow case instructions
   - Ensure good ventilation

2. **Route sensor wires**
   - PIR sensor: Mount facing outward through case opening
   - DHT22: Keep exposed to air (not enclosed)
   - TSL2561: Position where it can sense ambient light
   - USB mic: Keep accessible

3. **Secure wiring**
   - Use zip ties or tape to bundle wires neatly
   - Ensure no loose connections
   - Test that nothing shorts

4. **Label everything**
   - Mark which sensor is which
   - Note GPIO pin numbers on case

5. **Cable management**
   - Power cable
   - Ethernet (if not using WiFi)
   - Sensor wires grouped together

---

## 🔥 Troubleshooting

### Problem: PIR sensor always detects motion

**Solution:**
- Adjust sensitivity potentiometer on PIR module (small screws on board)
- Turn clockwise to decrease sensitivity
- Wait 30 seconds between adjustments

### Problem: DHT22 returns "Checksum error"

**Solutions:**
- Check pull-up resistor is connected (10kΩ between VCC and Data)
- Try using 5V instead of 3.3V for VCC
- Add `time.sleep(2)` between readings
- Ensure wires are not too long (< 30cm recommended)

### Problem: TSL2561 not detected (no 0x39 in i2cdetect)

**Solutions:**
- Check I2C is enabled (`sudo raspi-config`)
- Verify wiring (SDA to Pin 3, SCL to Pin 5)
- Try different I2C address: 0x29 or 0x49 (check sensor jumpers)
- Test with another I2C device to verify bus works

### Problem: USB microphone not recognized

**Solutions:**
- Check `lsusb` - device should appear
- Try different USB port
- Check power supply is adequate (3A recommended)
- Verify `arecord -l` shows the device

### Problem: Raspberry Pi won't boot (no green LED)

**Solutions:**
- Re-flash SD card
- Try different SD card (Class 10, 32GB max recommended)
- Check power supply (must be 5V 3A)
- Inspect SD card slot for damage

---

## 📊 Expected Sensor Readings

| Sensor | Typical Range | Your Environment |
|--------|---------------|------------------|
| **Motion (PIR)** | 0 or 1 (boolean) | Test: Wave hand |
| **Temperature** | 18-28°C (indoor) | ___°C |
| **Humidity** | 30-70% (comfortable) | ___%  |
| **Light** | 50-500 lux (office) | ___ lux |
| **Noise** | 30-50 dB (quiet), 60-70 dB (normal) | ___ dB |

Fill in your baseline readings for reference!

---

## 🎯 Next Steps

Once all sensors are working:

1. **Clone project repository**
   ```bash
   cd ~
   git clone https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System.git
   ```

2. **Set up IoT device software** (see README.md)

3. **Configure MQTT connection**

4. **Start sensing!**

---

## 📸 Photos (Add Your Own)

Document your build:
- [ ] Components laid out
- [ ] Wiring in progress
- [ ] Completed breadboard connections
- [ ] Final assembled device
- [ ] Running sensor tests

---

**Hardware assembly complete! 🎉**  
Your IoT device is now ready for software configuration.