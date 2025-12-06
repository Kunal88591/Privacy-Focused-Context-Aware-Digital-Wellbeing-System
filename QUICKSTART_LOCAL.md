# 🚀 Quick Start Guide - Running Locally

## Prerequisites

- Docker & Docker Compose installed
- Git installed
- (Optional) Node.js 18+ for mobile app

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System.git
cd Privacy-Focused-Context-Aware-Digital-Wellbeing-System
```

---

## Step 2: Start Backend with Docker

```bash
# Start all services (backend + MQTT)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Services will be available at:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MQTT Broker: mqtt://localhost:1883
- MQTT WebSocket: ws://localhost:9001

---

## Step 3: Test Backend

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

You should see:
```json
{
  "status": "healthy",
  "services": {
    "api": "online",
    "database": "online",
    "mqtt": "online",
    "ml_models": "loaded"
  }
}
```

---

## Step 4: Run Mobile App (Optional)

```bash
# Navigate to mobile app
cd mobile-app

# Install dependencies
npm install

# Start Expo
npx expo start
```

**On your phone:**
1. Install "Expo Go" from Play Store/App Store
2. Scan the QR code
3. App will load on your phone!

---

## Stop Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Troubleshooting

### Port already in use:
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Backend won't start:
```bash
# View logs
docker-compose logs backend

# Rebuild
docker-compose up --build
```

### MQTT connection issues:
```bash
# Test MQTT
docker-compose exec mosquitto mosquitto_sub -t test

# In another terminal
docker-compose exec mosquitto mosquitto_pub -t test -m "hello"
```

---

## What's Running?

- **Backend (FastAPI)**: Port 8000
- **MQTT Broker (Mosquitto)**: Ports 1883, 9001
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Next Steps

- View API docs at `/docs`
- Test endpoints with Postman/curl
- Run mobile app on your phone
- Read [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production deployment
- Check [HARDWARE_INTEGRATION_GUIDE.md](docs/HARDWARE_INTEGRATION_GUIDE.md) for IoT setup

---

**✅ You're all set!** The system is running locally.
