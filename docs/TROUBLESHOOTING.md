# 🛠️ Troubleshooting Guide

**Quick solutions to common issues**  
**Last Updated:** January 2, 2026

---

## 📱 Mobile App Issues

### App Won't Start / Crashes on Launch

**Symptoms:** App closes immediately after opening

**Solutions:**
1. Clear app cache:
   - Android: Settings → Apps → Digital Wellbeing → Storage → Clear Cache
   - iOS: Delete and reinstall app

2. Check permissions:
   - Grant all required permissions
   - Settings → Apps → Digital Wellbeing → Permissions

3. Update app:
   - Check for updates in Play Store / App Store

4. Reinstall app:
   - Backup data first
   - Uninstall → Reinstall → Restore

### Focus Mode Not Blocking Apps

**Symptoms:** Can still open blocked apps during focus mode

**Solutions:**
1. Grant "Display Over Apps" permission:
   - Settings → Apps → Special Access → Display over apps → Enable

2. Grant "Usage Stats" permission:
   - Settings → Apps → Special Access → Usage Stats → Enable

3. Disable battery optimization:
   - Settings → Battery → Battery Optimization → Digital Wellbeing → Don't optimize

4. Check blocked app list:
   - Focus Mode → Blocked Apps → Verify apps are selected

### VPN Won't Connect

**Symptoms:** VPN shows "Connecting" or "Failed"

**Solutions:**
1. Check internet connection:
   - Verify WiFi/mobile data is working
   - Try opening a website

2. Try different server:
   - Privacy → VPN → Server Location → Select different server

3. Grant VPN permission:
   - System will prompt when enabling VPN
   - Grant permission

4. Restart app and device:
   - Force close app
   - Restart phone
   - Try connecting again

---

## 🔒 Privacy Issues

### Trackers Not Being Blocked

**Symptoms:** Privacy score low, trackers still loading

**Solutions:**
1. Enable VPN:
   - VPN must be active for DNS blocking
   - Privacy → VPN → Enable

2. Update block lists:
   - Privacy → Tracker Blocking → Update Lists

3. Check app exceptions:
   - Privacy → VPN → Split Tunneling
   - Remove apps from exceptions

### Caller ID Still Showing

**Symptoms:** Caller information visible despite masking

**Solutions:**
1. Verify masking enabled:
   - Privacy → Caller ID Masking → Toggle ON

2. Check masking level:
   - Set to "Full Masking" for complete protection

3. Grant phone permission:
   - Required to intercept calls
   - Settings → Apps → Permissions → Phone

4. Check exceptions:
   - Privacy → Caller Masking → Exceptions
   - Remove unwanted exceptions

---

## 🤖 IoT Device Issues

### Device Shows Offline

**Symptoms:** IoT device not connecting to app

**Solutions:**
1. Check WiFi connection:
   ```bash
   # On Raspberry Pi
   ping google.com
   ifconfig wlan0
   ```

2. Verify MQTT broker:
   ```bash
   # Check if mosquitto is running
   systemctl status mosquitto
   # Restart if needed
   sudo systemctl restart mosquitto
   ```

3. Check device configuration:
   ```bash
   # Verify config.json
   cat ~/iot-device/config.json
   # Ensure broker address is correct
   ```

4. Re-pair device:
   - App: Settings → Devices → Remove Device
   - Add device again with correct ID

### Sensor Data Not Updating

**Symptoms:** Sensor readings stuck or not changing

**Solutions:**
1. Check sensor connections:
   - Verify wiring matches pinout diagram
   - Check for loose connections

2. Test sensors individually:
   ```bash
   # Test DHT22
   python3 test_dht22.py
   
   # Test TSL2561
   python3 test_tsl2561.py
   ```

3. Restart IoT service:
   ```bash
   sudo systemctl restart iot-device
   sudo systemctl status iot-device
   ```

4. Check logs:
   ```bash
   journalctl -u iot-device -f
   ```

---

## 📊 Analytics & Performance

### Analytics Not Showing Data

**Symptoms:** Empty charts, no statistics

**Solutions:**
1. Use app for 24 hours:
   - System needs time to collect data
   - Complete at least one focus session

2. Check data collection:
   - Settings → Privacy → Data Collection → Enable

3. Sync data:
   - Pull down to refresh on Analytics screen

### Slow App Performance

**Symptoms:** App laggy, slow to respond

**Solutions:**
1. Clear cache:
   - Settings → Storage → Clear Cache

2. Reduce animation:
   - Settings → Appearance → Animation Speed → Reduce

3. Close background apps:
   - Free up device memory

4. Update app:
   - Check for performance improvements in updates

---

## 🔧 Backend Server Issues

### Backend Won't Start

**Symptoms:** Server fails to start, API not accessible

**Solutions:**
1. Check port availability:
   ```bash
   lsof -i :8000
   # Kill process if port in use
   kill -9 <PID>
   ```

2. Check dependencies:
   ```bash
   cd backend-api
   pip install -r requirements.txt
   ```

3. Verify database:
   ```bash
   # Check PostgreSQL is running
   systemctl status postgresql
   ```

4. Check logs:
   ```bash
   # View backend logs
   tail -f backend-api/logs/app.log
   ```

### Database Connection Failed

**Symptoms:** "Database connection error" in logs

**Solutions:**
1. Check PostgreSQL is running:
   ```bash
   sudo systemctl start postgresql
   sudo systemctl status postgresql
   ```

2. Verify database exists:
   ```bash
   psql -U postgres -c "\l"
   # Create if missing:
   createdb wellbeing
   ```

3. Check connection string in .env:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/wellbeing
   ```

---

## ⚠️ Common Error Messages

### "Permission Denied"

**Cause:** Missing required permissions

**Fix:**
1. Go to Settings → Apps → Digital Wellbeing → Permissions
2. Enable all required permissions
3. Restart app

### "VPN Configuration Failed"

**Cause:** VPN permission not granted

**Fix:**
1. Privacy → VPN → Enable VPN
2. Grant VPN permission when prompted
3. If prompt doesn't appear, reinstall app

### "Network Error - Please Check Connection"

**Cause:** No internet or backend not reachable

**Fix:**
1. Check internet connection
2. Verify backend URL in Settings → Server Configuration
3. Check firewall settings

### "Auto-Wipe Warning: 2 More Attempts"

**Cause:** Multiple untrusted network connections detected

**Fix:**
1. Connect to trusted WiFi network
2. Enable VPN immediately
3. Review network trust settings
4. Reset counter if false alarm: Settings → Security → Reset Wipe Counter

---

## 📞 Getting More Help

**Can't find your issue?**

1. Check FAQ: [FAQ.md](FAQ.md)
2. Search GitHub Issues
3. Ask on Discord: #support channel
4. Email: support@digitalwellbeing.app

**When reporting issues, include:**
- App version
- Device model and OS version
- Steps to reproduce
- Screenshots (if applicable)
- Relevant logs

---

**Last Updated:** January 2, 2026
