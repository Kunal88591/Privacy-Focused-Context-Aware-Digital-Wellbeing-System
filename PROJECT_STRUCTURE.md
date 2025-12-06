# 📁 Project Structure

```
Privacy-Focused-Context-Aware-Digital-Wellbeing-System/
│
├── 📱 Mobile App (React Native + Expo)
│   └── mobile-app/
│       ├── App.js                    # Main app entry point
│       ├── package.json              # Mobile dependencies
│       ├── .env.example              # Environment variables template
│       ├── babel.config.js           # Babel configuration
│       └── src/
│           ├── screens/              # App screens (4 screens)
│           │   ├── HomeScreen.js
│           │   ├── NotificationsScreen.js
│           │   ├── PrivacyScreen.js
│           │   └── SettingsScreen.js
│           ├── components/           # Reusable UI components
│           │   ├── ErrorBoundary.js
│           │   ├── SkeletonLoader.js
│           │   └── OfflineIndicator.js
│           ├── contexts/             # React Context providers
│           │   └── UserContext.js
│           ├── services/             # API and service layers
│           │   ├── api.js
│           │   ├── offlineStorage.js
│           │   └── mqttClient.js
│           └── config/               # App configuration
│               └── index.js
│
├── 🔧 Backend API (FastAPI + Python)
│   └── backend-api/
│       ├── app/
│       │   ├── main.py               # FastAPI application entry
│       │   ├── models/               # Database models
│       │   │   ├── user.py
│       │   │   ├── notification.py
│       │   │   ├── device.py
│       │   │   └── sensor_data.py
│       │   ├── api/                  # API route handlers
│       │   │   ├── auth.py
│       │   │   ├── notifications.py
│       │   │   ├── privacy.py
│       │   │   ├── wellbeing.py
│       │   │   └── devices.py
│       │   └── services/             # Business logic
│       │       ├── ml_classifier.py
│       │       ├── privacy_manager.py
│       │       └── mqtt_handler.py
│       ├── tests/                    # Backend tests
│       │   ├── conftest.py           # Pytest configuration
│       │   ├── test_auth.py          # 5 tests
│       │   ├── test_notifications.py # 5 tests
│       │   ├── test_devices.py       # 6 tests
│       │   ├── RUN_DEMO.sh
│       │   ├── test_day3.sh
│       │   ├── test_integration.sh
│       │   ├── test_integration_api.sh
│       │   └── test_offline_mode.sh
│       ├── requirements.txt          # Python dependencies (39 packages)
│       ├── Dockerfile                # Docker container config
│       ├── Procfile                  # Heroku deployment
│       ├── runtime.txt               # Python version (3.9.18)
│       └── .dockerignore
│
├── 🤖 AI/ML Models
│   └── ai-models/
│       ├── training/
│       │   └── train_notification_classifier.py
│       ├── models/
│       │   └── notification_classifier.pkl
│       └── requirements.txt
│
├── 📡 IoT Device Code
│   └── iot-device/
│       ├── mqtt_client.py            # MQTT client for sensors
│       └── requirements.txt
│
├── 🐳 Docker & Deployment
│   ├── docker-compose.yml            # Multi-service orchestration
│   ├── mosquitto/                    # MQTT broker config
│   │   └── config/
│   │       └── mosquitto.conf
│   └── .github/
│       └── workflows/                # CI/CD pipelines
│           ├── backend-ci.yml        # Backend automation
│           ├── mobile-ci.yml         # Mobile app automation
│           ├── ai-models-ci.yml      # ML automation
│           ├── docker-compose-ci.yml # Infrastructure tests
│           └── code-quality.yml      # Quality checks
│
├── 📚 Documentation
│   └── docs/
│       ├── DAY_6_PROGRESS.md         # Day 6 report (Docker)
│       ├── DAY_7_PROGRESS.md         # Day 7 report (CI/CD)
│       ├── DEPLOYMENT_GUIDE.md       # Cloud deployment (400+ lines)
│       ├── CI_CD_GUIDE.md            # CI/CD documentation
│       ├── GITHUB_SECRETS_SETUP.md   # Secrets configuration
│       ├── HARDWARE_INTEGRATION_GUIDE.md
│       ├── DATA_FLOWS.md             # System architecture
│       ├── hardware/
│       │   └── ASSEMBLY_GUIDE.md
│       └── software/
│           └── IMPLEMENTATION.md
│
├── 📄 Root Files (Organized)
│   ├── README.md                     # Main project documentation
│   ├── PROJECT_PROGRESS.md           # 30-day progress tracker
│   ├── QUICKSTART_LOCAL.md           # Quick setup guide
│   ├── WHERE_TO_SEE_PROGRESS.md      # Progress visibility
│   ├── LICENSE                       # Proprietary license
│   ├── CONTRIBUTING.md               # Contribution guidelines
│   ├── Makefile                      # Build automation
│   ├── setup.sh                      # Setup script
│   ├── start_mobile.sh               # Mobile app launcher
│   └── .gitignore
│
└── 🗄️ Archive (Old/Deprecated Files)
    └── .archive/
        ├── CURRENT_STATUS.md
        ├── DAY2_REPORT.md
        ├── DAY_4_COMPLETE.md
        ├── HOW_TO_SEE_PROJECT.md
        ├── HOW_TO_VIEW_APP.md
        ├── MOBILE_APP_UI_PREVIEW.md
        ├── PROJECT_STATUS.md
        ├── QUICKSTART.md
        ├── SOFTWARE_ROADMAP.md
        └── WHEN_APP_WORKS.md
```

---

## 📊 File Count by Category

| Category | Files | Lines of Code |
|----------|-------|---------------|
| Backend API | 20+ | ~2,000 |
| Mobile App | 15+ | ~2,500 |
| AI/ML Models | 3 | ~300 |
| IoT Device | 2 | ~200 |
| Tests | 9 | ~800 |
| Docker/CI/CD | 10 | ~600 |
| Documentation | 13+ | ~3,000 |
| **Total** | **70+** | **~9,400+** |

---

## 🔑 Key Directories

### `/mobile-app` - React Native Mobile Application
- 4 main screens with bottom tab navigation
- Offline mode with local caching
- Error boundaries and skeleton loaders
- MQTT integration for real-time updates
- 42 tests (17 + 25 offline)

### `/backend-api` - FastAPI Backend Server
- 5 API modules (auth, notifications, privacy, wellbeing, devices)
- 20+ REST endpoints
- ML-powered notification classification
- MQTT message handling
- 16 automated tests
- Docker containerized

### `/ai-models` - Machine Learning Models
- Notification classifier (scikit-learn)
- Training scripts and pipelines
- Model persistence (joblib)
- 100% accuracy on test data

### `/iot-device` - IoT Device Code
- MQTT client for ESP32/Raspberry Pi
- Sensor data collection and publishing
- Mock sensors for development
- Real-time data streaming

### `/docs` - Comprehensive Documentation
- Day-by-day progress reports
- Deployment guides (400+ lines)
- CI/CD setup instructions
- Hardware integration guides
- Architecture diagrams

### `/.github/workflows` - CI/CD Automation
- 5 GitHub Actions workflows
- 12 automated jobs
- Test automation on every push
- Docker builds and publishing
- Code quality and security scanning

---

## 🚀 Quick Navigation

**Start Here:**
- 📖 [README.md](README.md) - Project overview
- ⚡ [QUICKSTART_LOCAL.md](QUICKSTART_LOCAL.md) - 5-minute setup
- 📊 [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md) - 30-day tracker

**Development:**
- 🔧 [backend-api/](backend-api/) - Backend development
- 📱 [mobile-app/](mobile-app/) - Mobile app development
- 🤖 [ai-models/](ai-models/) - ML model training

**Deployment:**
- 🐳 [docker-compose.yml](docker-compose.yml) - Local deployment
- 📚 [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Cloud deployment
- 🔄 [docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md) - Automation setup

**Testing:**
- ✅ [backend-api/tests/](backend-api/tests/) - Backend tests (16 tests)
- 📱 Mobile tests in app code (42 tests)

---

## 📁 File Organization Principles

1. **Separation of Concerns**: Backend, mobile, AI, IoT in separate directories
2. **Documentation First**: Comprehensive docs in `/docs`
3. **Test Co-location**: Tests next to the code they test
4. **Archive Old Files**: Deprecated docs in `/.archive`
5. **CI/CD Integration**: Workflows in `/.github/workflows`
6. **Docker Ready**: All deployment configs at root level

---

## 🔄 Recent Reorganization (Day 7)

**Moved to `.archive/`:**
- Old progress reports (10 files)
- Deprecated quickstart guides
- Outdated status files

**Moved to `backend-api/tests/`:**
- Test shell scripts (5 files)
- Integration test runners

**Result:** Clean, professional project structure! ✨

---

**Last Updated:** Day 7 - December 6, 2024
