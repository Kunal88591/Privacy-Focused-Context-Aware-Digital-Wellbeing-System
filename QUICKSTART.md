# 🚀 Quick Start Guide

## Prerequisites

Make sure you have:
- Python 3.9+
- Node.js 18+
- Git

## Installation

```bash
# Install backend dependencies
pip3 install fastapi uvicorn pydantic paho-mqtt python-dotenv 'pydantic[email]' --user

# Install IoT dependencies
pip3 install paho-mqtt python-dotenv --user

# Install AI/ML dependencies
pip3 install scikit-learn numpy pandas --user

# Install mobile app dependencies (if running mobile app)
cd mobile-app
npm install
```

## Running the System

### 1. Start Backend API

```bash
cd backend-api
PYTHONPATH=. python3 -m app.main
```

**Server will start at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs

### 2. Start IoT Device (Optional)

```bash
cd iot-device
python3 mqtt_client.py
```

**Note:** Works in mock mode without actual hardware

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Classify notification
curl -X POST http://localhost:8000/api/v1/notifications/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "URGENT: Meeting starts in 5 minutes",
    "sender": "calendar",
    "received_at": "2025-12-03T16:00:00Z"
  }'

# Get wellbeing stats
curl "http://localhost:8000/api/v1/wellbeing/stats?period=today"

# Check privacy status
curl http://localhost:8000/api/v1/privacy/status
```

## Training ML Model

```bash
cd ai-models
python3 training/train_notification_classifier.py
```

**Output:**
- Trained model saved to `models/notification_classifier.pkl`
- Vectorizer saved to `models/vectorizer.pkl`
- Metadata saved to `models/model_metadata.json`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Notifications
- `POST /api/v1/notifications/classify` - Classify notification
- `GET /api/v1/notifications` - Get notification history
- `DELETE /api/v1/notifications/{id}` - Delete notification

### Privacy
- `POST /api/v1/privacy/vpn/enable` - Enable VPN
- `POST /api/v1/privacy/vpn/disable` - Disable VPN
- `POST /api/v1/privacy/mask-caller` - Toggle caller ID masking
- `GET /api/v1/privacy/status` - Get privacy status

### Wellbeing
- `POST /api/v1/wellbeing/focus-mode` - Activate/deactivate focus mode
- `GET /api/v1/wellbeing/focus-mode/status` - Get focus mode status
- `GET /api/v1/wellbeing/stats` - Get productivity stats
- `GET /api/v1/wellbeing/insights` - Get AI insights

### Devices
- `POST /api/v1/devices/register` - Register IoT device
- `GET /api/v1/devices` - List all devices
- `POST /api/v1/devices/{id}/command` - Send command to device

## Environment Variables

Create `.env` files in each directory:

### backend-api/.env
```
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
DATABASE_URL=sqlite:///./wellbeing.db
```

### iot-device/.env
```
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TOPIC_PREFIX=wellbeing
DEVICE_ID=iot-device-001
```

## Troubleshooting

### Backend won't start
```bash
# Make sure dependencies are installed
pip3 install fastapi uvicorn pydantic paho-mqtt python-dotenv 'pydantic[email]' --user

# Run with PYTHONPATH set
cd backend-api
PYTHONPATH=. python3 -m app.main
```

### IoT device connection issues
```bash
# Check if MQTT broker is running (if using external broker)
mosquitto -v

# Or use backend's built-in MQTT support
# (Currently not implemented, will connect to external broker)
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in backend-api/app/main.py
```

## Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Test Classification**: Send sample notifications
3. **Check Stats**: View productivity metrics
4. **Train Model**: Customize ML model with your data
5. **Integrate Mobile**: Connect mobile app to backend

## Documentation

- **README.md** - Full project documentation
- **PROJECT_STATUS.md** - Current implementation status
- **docs/SOFTWARE.md** - Software implementation details
- **docs/hardware/ASSEMBLY_GUIDE.md** - Hardware setup

## Support

For issues or questions:
1. Check documentation in `/docs`
2. Review API docs at http://localhost:8000/docs
3. Open an issue on GitHub

---

**Happy building! 🎉**
