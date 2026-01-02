# ❓ Frequently Asked Questions (FAQ)

**Quick answers to common questions**  
**Last Updated:** January 2, 2026

---

## 🔍 General Questions

### What is this system?

A comprehensive privacy-focused digital wellbeing platform that helps you:
- Protect your privacy with VPN, caller masking, and encryption
- Improve focus with app blocking and smart notifications
- Monitor wellbeing with analytics and AI insights
- Optimize environment with IoT sensor integration

### Is it free?

Yes! The system is open-source and free to use. No subscriptions, no hidden costs.

### What platforms are supported?

- **Mobile:** Android 8.0+, iOS 13.0+
- **Backend:** Self-hosted on any server (Linux, macOS, Windows)
- **IoT:** Raspberry Pi 4 with sensor kit

### Do I need technical knowledge?

No! The mobile app is user-friendly. Self-hosting the backend requires basic technical skills, but Docker makes it easy.

---

## 🔒 Privacy Questions

### Is my data safe?

Yes! All sensitive data is encrypted with AES-256 on your device. We follow a "local-first" approach - your data never leaves your device unless you explicitly sync it.

### Can you see my data?

No! We have zero access to your data. It's encrypted on your device with a key only you control.

### Does the VPN log my activity?

No! We operate a strict no-logs policy. The VPN only knows you're connected, not what you're doing.

### What trackers do you block?

110+ domains including Google Analytics, Facebook Pixel, ad networks, and data brokers. Full list in Privacy → Tracker Blocking.

### Can location spoofing be detected?

Some apps may detect it, but most cannot. Dating apps and fitness apps are increasingly sophisticated at detection.

---

## 🎯 Focus Mode Questions

### Why can I still see notifications?

Focus mode filters but doesn't block all notifications. Urgent calls and critical alerts still come through. Adjust in Focus Mode → Notification Settings.

### Can I unlock blocked apps during focus?

Yes, but it's discouraged. Tap "I Really Need This App" 3 times, but it will negatively impact your productivity score.

### Does focus mode drain battery?

Minimal impact (~2-5% extra). The blocking overlay is lightweight.

### Can I schedule focus sessions?

Yes! Settings → Focus Mode → Auto-Schedule. Set daily focus times (e.g., 9-11 AM weekdays).

---

## 📊 Analytics Questions

### Why is my productivity score low?

Common reasons:
- Not enough focus time (aim for 4+ hours daily)
- Ending sessions early
- Frequently unlocking blocked apps
- Irregular schedule

### How is wellbeing score calculated?

Based on 5 factors:
- Sleep quality (8 hours recommended)
- Break frequency (every 90 min)
- Screen time (< 6 hours daily)
- Physical activity
- Stress levels (from IoT sensors)

### Can I export my data?

Yes! Analytics → Export → Choose format (CSV/JSON/PDF). Data is encrypted if you set a password.

---

## 🤖 IoT Questions

### Do I need an IoT device?

No, it's optional. The mobile app works perfectly without it. IoT adds environmental monitoring and automations.

### What sensors do I need?

Minimum: Temperature, light, motion  
Recommended: + Humidity, noise (microphone)  
Advanced: + Air quality, CO2

### How much does the IoT setup cost?

~$60-100:
- Raspberry Pi 4: $35-45
- Sensor kit: $20-30
- Power supply & accessories: $10-20
- Optional case: $5-10

### Can I use a different device?

Yes! Any device that can run Python and MQTT. ESP32, Arduino, or custom setups work.

### How often does it send data?

Default: Every 60 seconds  
Configurable: 10 seconds to 10 minutes  
Privacy: Data stays local, optionally synced to your backend

---

## ⚡ Performance Questions

### Why is the app using so much battery?

Common causes:
- VPN always-on
- Location spoofing (GPS override)
- Background sync
- Focus mode overlay

Solutions:
- Adjust VPN to "On Demand" mode
- Use location spoofing only when needed
- Reduce sync frequency
- Battery usage ~10-15% daily is normal

### The app is slow/laggy. Help?

Try:
1. Clear cache (Settings → Storage → Clear Cache)
2. Reduce animations (Settings → Appearance → Animation Speed)
3. Update to latest version
4. Free up device storage (need 500MB+ free)

### Backend server is slow

Optimize:
- Use Docker (better performance)
- Increase server resources (4GB RAM recommended)
- Enable Redis caching
- Optimize database queries

---

## 🔧 Technical Questions

### Can I self-host the backend?

Yes! See [SETUP_GUIDE.md](SETUP_GUIDE.md) for instructions. Requires basic Docker knowledge or Python/PostgreSQL setup.

### What's the tech stack?

- **Backend:** Python (FastAPI), PostgreSQL, MQTT (Mosquitto)
- **Mobile:** React Native, Expo
- **AI:** TensorFlow Lite
- **IoT:** Python, Raspberry Pi

### Can I contribute?

Yes! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. We welcome:
- Bug reports
- Feature requests
- Code contributions
- Documentation improvements

### Is there an API?

Yes! Full REST API documented at http://your-backend:8000/docs (Swagger UI)

---

## 🚨 Emergency Questions

### I forgot my master password!

Use recovery codes generated during setup. Without recovery codes, data cannot be decrypted. This is by design for maximum security.

### Auto-wipe triggered accidentally!

If countdown is active, enter PIN to cancel. If already wiped, restore from encrypted backup (Settings → Backup → Restore).

### My device was stolen!

1. Remote wipe (if setup)
2. Wait for auto-wipe trigger (3 untrusted networks)
3. Change all passwords immediately
4. Contact authorities

### VPN not working, need urgent privacy!

Quick fallback:
1. Disable WiFi/mobile data temporarily
2. Use Tor Browser for urgent tasks
3. Troubleshoot VPN (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md))
4. Contact support

---

## 💡 Best Practices Questions

### How do I maximize productivity?

1. Schedule 2-3 focus sessions daily
2. Use Pomodoro technique (25 min + 5 min break)
3. Block all social media during work hours
4. Review analytics weekly to find patterns
5. Set realistic daily goals

### How do I maximize privacy?

1. Keep VPN enabled always
2. Use full caller ID masking
3. Enable location spoofing for social media
4. Review app permissions monthly
5. Maintain 90+ privacy score

### Recommended daily routine?

**Morning (8 AM):**
- Check privacy score
- Review yesterday's analytics
- Plan 2-3 focus sessions

**Work (9 AM - 5 PM):**
- Focus session 1 (9-10:30 AM)
- Break (15 min)
- Focus session 2 (11 AM-12:30 PM)
- Lunch (60 min)
- Focus session 3 (2-3:30 PM)

**Evening:**
- Review accomplishments
- Adjust tomorrow's goals
- Enable "Sleep Mode" (10 PM)

---

## 🌐 Compatibility Questions

### Works with my smartwatch?

Limited. Focus mode notifications sync to most smartwatches. Full app not available yet.

### Can I use multiple devices?

Yes! One account works on multiple devices. Data syncs via backend (if self-hosted) or locally (encrypted backups).

### Compatible with other apps?

Yes! Works alongside:
- Productivity apps (Todoist, Notion)
- Health apps (Google Fit, Apple Health)
- Meditation apps (Headspace, Calm)

May conflict with:
- Other VPN apps (only one VPN at a time)
- Other app blockers (may interfere with focus mode)

---

## 📞 Support Questions

### How do I get help?

1. Check this FAQ
2. Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Search GitHub Issues
4. Ask on Discord (#support)
5. Email: support@digitalwellbeing.app

### How do I report a bug?

GitHub Issues: Include:
- App version
- Device/OS
- Steps to reproduce
- Screenshots
- Logs (if applicable)

### How do I request a feature?

GitHub Discussions or Settings → Feature Request in app

### Is there a community?

Yes!
- Discord Server
- GitHub Discussions
- Reddit: r/DigitalWellbeing

---

## 📈 Roadmap Questions

### What's coming next?

**Short-term (Q1 2026):**
- iOS app beta
- Desktop companion app
- Advanced AI insights
- Team/family features

**Long-term (2026):**
- Browser extensions
- Smartwatch apps
- API for third-party integrations
- Premium features (optional)

### Can I beta test new features?

Yes! Settings → Advanced → Beta Program → Join

---

## 📚 More Questions?

**Didn't find your answer?**

- 📖 [User Manual](USER_MANUAL.md)
- 🔒 [Privacy Guide](PRIVACY_GUIDE.md)
- 🚀 [Setup Guide](SETUP_GUIDE.md)
- 🛠️ [Troubleshooting](TROUBLESHOOTING.md)
- 📧 Email: faq@digitalwellbeing.app

---

**Last Updated:** January 2, 2026  
**FAQ Version:** 1.0.0

*Got a question not answered here? Let us know!*
