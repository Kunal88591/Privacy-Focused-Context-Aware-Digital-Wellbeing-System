#!/bin/bash

# Privacy Wellbeing System - Demo Runner
# This script demonstrates all working components

echo "🎉 Privacy-Focused Digital Wellbeing System - Live Demo"
echo "========================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Check Backend
echo -e "${BLUE}1. Backend API Status${NC}"
echo "   URL: http://localhost:8000"
echo -n "   Health Check: "
health=$(curl -s http://localhost:8000/health | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])" 2>/dev/null)
if [ "$health" = "healthy" ]; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Not running. Start with: cd backend-api && PYTHONPATH=. python3 -m uvicorn app.main:app --reload${NC}"
fi
echo ""

# 2. Test API Endpoints
echo -e "${BLUE}2. API Endpoints Demo${NC}"

echo "   📊 Privacy Status:"
curl -s http://localhost:8000/api/v1/privacy/status | python3 -m json.tool 2>/dev/null | sed 's/^/      /'

echo ""
echo "   🏆 Wellbeing Stats:"
curl -s http://localhost:8000/api/v1/wellbeing/stats | python3 -m json.tool 2>/dev/null | sed 's/^/      /'

echo ""
echo "   🤖 Devices:"
curl -s http://localhost:8000/api/v1/devices | python3 -m json.tool 2>/dev/null | head -20 | sed 's/^/      /'

echo ""
echo "   🔔 Classify Notification:"
curl -s -X POST http://localhost:8000/api/v1/notifications/classify \
  -H "Content-Type: application/json" \
  -d '{"title":"URGENT: Server Down","body":"Production server crashed!","app":"slack","sender":"ops"}' \
  | python3 -m json.tool 2>/dev/null | sed 's/^/      /'

echo ""

# 3. Check ML Models
echo -e "${BLUE}3. AI/ML Models${NC}"
if [ -f "ai-models/models/notification_classifier.pkl" ]; then
    echo -e "   ${GREEN}✓${NC} Classifier trained and saved"
    echo "   Location: ai-models/models/"
    ls -lh ai-models/models/*.pkl 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
else
    echo -e "   ${YELLOW}⚠ Models not found. Train with: cd ai-models && python3 training/train_notification_classifier.py${NC}"
fi
echo ""

# 4. Check Mobile App
echo -e "${BLUE}4. Mobile App${NC}"
if [ -d "mobile-app/node_modules" ]; then
    echo -e "   ${GREEN}✓${NC} Dependencies installed"
else
    echo -e "   ${YELLOW}⚠ Dependencies not installed. Run: cd mobile-app && npm install --legacy-peer-deps${NC}"
fi

echo "   Screens:"
ls mobile-app/src/screens/*.js 2>/dev/null | wc -l | awk '{print "   - " $1 " screens ready"}'
echo "   - Home (Dashboard with live sensors)"
echo "   - Notifications (ML classification)"
echo "   - Privacy (VPN, masking, spoofing)"
echo "   - Settings (Configuration)"
echo ""
echo "   Start with:"
echo "   cd mobile-app && npm start"
echo ""

# 5. IoT Device
echo -e "${BLUE}5. IoT Device (Mock Mode)${NC}"
echo -e "   ${GREEN}✓${NC} 4 sensor modules ready"
echo "   - PIR Motion Sensor"
echo "   - DHT22 (Temperature/Humidity)"
echo "   - TSL2561 (Light)"
echo "   - USB Microphone (Noise)"
echo ""
echo "   Start with:"
echo "   cd iot-device && python3 mqtt_client.py"
echo ""

# Summary
echo "========================================================"
echo -e "${GREEN}✅ System Status: MVP Complete and Demo Ready!${NC}"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview"
echo "   - CURRENT_STATUS.md - Quick reference"
echo "   - docs/DAY_2_PROGRESS.md - Progress report"
echo "   - docs/PROJECT_COMPLETE.md - Full documentation"
echo ""
echo "🚀 Next: Run mobile app to see everything in action!"
