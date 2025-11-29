# Data Flow Diagrams

## 1. Notification Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOTIFICATION ARRIVES                          │
│                  (SMS, Email, App Push, Call)                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MOBILE APP                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Intercept Notification                                 │ │
│  │     Extract: text, sender, time, type                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  2. Local Classification (TF Lite Model)                   │ │
│  │     • Check against urgent keywords                        │ │
│  │     • Analyze sender importance                            │ │
│  │     • Time-based priority                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                    ┌───────┴───────┐                            │
│                    │               │                            │
│            High Confidence    Low Confidence                    │
│                    │               │                            │
└────────────────────┼───────────────┼────────────────────────────┘
                     │               │
        ┌────────────┘               └────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────┐                    ┌─────────────────────────┐
│   3a. URGENT     │                    │  3b. UNCERTAIN          │
│   Show Now       │                    │  Send to Backend        │
│   • Alert User   │                    └───────────┬─────────────┘
│   • Sound/Vibrate│                                │
│   • Bypass DND   │                                │
└──────────────────┘                                │
        │                                           ▼
        │                            ┌─────────────────────────────┐
        │                            │   BACKEND API SERVER        │
        │                            │  ┌─────────────────────────┐│
        │                            │  │ 4. Advanced ML Model    ││
        │                            │  │    • Context analysis   ││
        │                            │  │    • Historical patterns││
        │                            │  │    • User preferences   ││
        │                            │  └──────────┬──────────────┘│
        │                            └─────────────┼───────────────┘
        │                                          │
        │                    ┌─────────────────────┼─────────────────────┐
        │                    │                     │                     │
        │                URGENT              NON-URGENT             SPAM/BLOCK
        │                    │                     │                     │
        └────────────────────┘                     ▼                     ▼
                │                         ┌──────────────────┐  ┌─────────────┐
                │                         │ 5b. Batch Queue  │  │  5c. Block  │
                │                         │  • Hold until    │  │  • Silent   │
                ▼                         │    break time    │  │  • Log only │
     ┌──────────────────────┐            │  • Group similar │  └─────────────┘
     │ 5a. Display          │            │  • Summarize     │
     │  • Full notification │            └────────┬─────────┘
     │  • Action buttons    │                     │
     │  • Quick reply       │                     │
     └──────────────────────┘                     ▼
                │                       ┌──────────────────────┐
                │                       │ 6. Scheduled Display │
                │                       │  • During breaks     │
                │                       │  • After focus time  │
                │                       │  • Digest format     │
                │                       └──────────────────────┘
                │                                  │
                └──────────────────────────────────┘
                                │
                                ▼
                      ┌──────────────────────┐
                      │ 7. Log & Analytics   │
                      │  • Track patterns    │
                      │  • Improve model     │
                      │  • User insights     │
                      └──────────────────────┘
```

---

## 2. Focus Mode Activation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRIGGER CONDITIONS                            │
│  • Manual user activation                                        │
│  • Scheduled deep work time                                      │
│  • Poor environment detected                                     │
│  • High stress indicators                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MOBILE APP: FOCUS MODE                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Activate Focus Mode                                    │ │
│  │     • Block distracting apps                               │ │
│  │     • Enable notification batching                         │ │
│  │     • Start focus timer                                    │ │
│  │     • Set DND mode                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  2. Send State to Backend                                  │ │
│  │     POST /api/v1/wellbeing/focus-mode                      │ │
│  │     { "status": "active", "duration": 90 }                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API SERVER                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  3. Process Focus Mode Request                             │ │
│  │     • Update user state                                    │ │
│  │     • Trigger environment optimization                     │ │
│  │     • Schedule break reminder                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  4. Publish MQTT Command                                   │ │
│  │     Topic: wellbeing/commands/device-001/focus_mode        │ │
│  │     Payload: { "action": "activate", "duration": 90 }      │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IOT DEVICE (Raspberry Pi)                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  5. Receive Command                                        │ │
│  │     • Parse MQTT message                                   │ │
│  │     • Validate command                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  6. Read Current Environment                               │ │
│  │     • Noise level: 75 dB                                   │ │
│  │     • Light level: 200 lux                                 │ │
│  │     • Motion: Active                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  7. Execute Automation                                     │ │
│  │     IF noise > 70 dB → Suggest noise cancellation         │ │
│  │     IF light < 200 lux → Increase smart lights            │ │
│  │     Send status update to backend                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER EXPERIENCE                               │
│  • Phone blocks Instagram, Twitter, TikTok                      │
│  • Notifications batched for later                              │
│  • Smart lights adjust for optimal focus                        │
│  • Noise suggestion appears on phone                            │
│  • Timer shows remaining focus time                             │
│  • Break reminder after 90 minutes                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Environmental Monitoring Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              IOT DEVICE - CONTINUOUS MONITORING                  │
│                      (Every 5 seconds)                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
                  ▼                   ▼
        ┌──────────────────┐  ┌──────────────────┐
        │  Read Sensors    │  │  Read Sensors    │
        │  • Noise (Mic)   │  │  • Temp (DHT)    │
        │  • Light (TSL)   │  │  • Humidity (DHT)│
        │  • Motion (PIR)  │  │  • Time          │
        └────────┬─────────┘  └────────┬─────────┘
                 │                     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Aggregate Data      │
                 │  {                   │
                 │    noise: 65,        │
                 │    light: 300,       │
                 │    motion: true,     │
                 │    temp: 22,         │
                 │    humidity: 45      │
                 │  }                   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Publish to MQTT     │
                 │  Topic:              │
                 │  wellbeing/sensors/  │
                 │  device-001          │
                 └──────────┬───────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API SERVER                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Subscribe to MQTT                                         │ │
│  │  Topic: wellbeing/sensors/#                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Analyze Environment                                       │ │
│  │  • Compare to thresholds                                   │ │
│  │  • Detect patterns                                         │ │
│  │  • Check user state (focus mode?)                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                    ┌───────┴────────┐                           │
│            Good Environment    Poor Environment                 │
│                    │               │                            │
│                    │               ▼                            │
│                    │    ┌──────────────────────┐               │
│                    │    │  Generate Suggestion │               │
│                    │    │  • Reduce noise      │               │
│                    │    │  • Adjust lighting   │               │
│                    │    │  • Take break        │               │
│                    │    └──────────┬───────────┘               │
│                    │               │                            │
└────────────────────┼───────────────┼────────────────────────────┘
                     │               │
                     │               ▼
                     │    ┌──────────────────────┐
                     │    │  Send to Mobile App  │
                     │    │  (MQTT or Push)      │
                     │    └──────────┬───────────┘
                     │               │
                     └───────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │   MOBILE APP         │
                     │   Show Suggestion:   │
                     │   "Environment is    │
                     │   too noisy for      │
                     │   focus work.        │
                     │   [Enable NC]        │
                     │   [Take Break]"      │
                     └──────────────────────┘
```

---

## 4. Privacy Protection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INCOMING COMMUNICATION                        │
│                  (Call, SMS, Email, Message)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MOBILE APP                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Privacy Check                                          │ │
│  │     • Is privacy mode enabled?                             │ │
│  │     • Is caller ID masking active?                         │ │
│  │     • Is location spoofing enabled?                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                  ┌─────────┴─────────┐                          │
│                  │                   │                          │
│         Privacy Mode ON     Privacy Mode OFF                    │
│                  │                   │                          │
│                  ▼                   ▼                          │
│  ┌──────────────────────┐  ┌──────────────────┐               │
│  │  2a. Apply Privacy   │  │  2b. Normal      │               │
│  │  • Mask caller ID    │  │  • Show caller   │               │
│  │  • Strip metadata    │  │  • Full info     │               │
│  │  • Route via VPN     │  │  • Direct conn   │               │
│  │  • Spoof location    │  └──────────────────┘               │
│  └──────────┬───────────┘                                      │
│             │                                                   │
│             ▼                                                   │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  3. Display Protected                                      ││
│  │     Caller: "Unknown Number"                               ││
│  │     Location: <spoofed>                                    ││
│  │     Via: Secure VPN                                        ││
│  └────────────────────────────────────────────────────────────┘│
│             │                                                   │
│             ▼                                                   │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  4. Network Monitor                                        ││
│  │     • Check WiFi trust level                               ││
│  │     • Detect public/untrusted networks                     ││
│  │     • Count security events                                ││
│  └────────────────────────────────────────────────────────────┘│
│             │                                                   │
│      Untrusted Network Detected                                │
│             │                                                   │
│             ▼                                                   │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  5. Auto-Wipe Trigger?                                     ││
│  │     IF untrusted_count >= 3:                               ││
│  │        → Trigger security protocol                         ││
│  │        → Encrypt and wipe sensitive data                   ││
│  │        → Notify user                                       ││
│  │        → Log event                                         ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

1. **Notification Flow**: Two-tier classification (local + backend) for accuracy
2. **Focus Mode**: Coordinated action across mobile, backend, and IoT
3. **Monitoring**: Continuous environmental sensing with smart suggestions
4. **Privacy**: Multi-layer protection with auto-wipe failsafe

These flows demonstrate the **context-aware** and **privacy-first** nature of your system!
