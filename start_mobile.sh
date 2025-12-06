#!/bin/bash

echo "========================================="
echo "  Starting Your Mobile App on Android"
echo "========================================="
echo ""

# Step 1: Check backend
echo "Step 1: Checking backend..."
BACKEND_STATUS=$(curl -s http://localhost:8000/health 2>&1)
if [[ $BACKEND_STATUS == *"healthy"* ]]; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend not running. Starting it..."
    cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/backend-api
    nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
    sleep 5
    echo "✅ Backend started"
fi

echo ""
echo "Step 2: Starting mobile app..."
cd /workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/mobile-app

# Kill any existing expo processes
pkill -f "expo" 2>/dev/null
pkill -f "metro" 2>/dev/null
sleep 2

echo ""
echo "========================================="
echo "  Mobile App Starting..."
echo "========================================="
echo ""
echo "📱 ON YOUR ANDROID PHONE:"
echo "   1. Open Play Store"
echo "   2. Install 'Expo Go' app"
echo "   3. Open Expo Go"
echo "   4. Tap 'Scan QR Code'"
echo "   5. Scan the QR code below"
echo ""
echo "⏳ Starting Expo server..."
echo ""

# Start expo
npx expo start

