#!/bin/bash

# Integration Test Script
# Tests the complete Privacy Wellbeing System

echo "🧪 Privacy Wellbeing System - Integration Tests"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=${4:-}
    
    echo -n "Testing $name... "
    
    if [ -z "$data" ]; then
        http_code=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$url")
    else
        http_code=$(curl -s -o /dev/null -w "%{http_code}" -X $method -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 1. Backend API Tests
echo "1️⃣  Backend API Tests"
echo "-------------------"

test_endpoint "Health Check" "http://localhost:8000/health"
test_endpoint "API Root" "http://localhost:8000/"

echo ""

# 2. Authentication API Tests
echo "2️⃣  Authentication API Tests"
echo "-------------------------"

test_endpoint "Register User" "http://localhost:8000/api/v1/auth/register" "POST" \
    '{"email":"test@example.com","password":"testpass123","name":"Test User"}'

test_endpoint "Login" "http://localhost:8000/api/v1/auth/login" "POST" \
    '{"email":"test@example.com","password":"testpass123"}'

echo ""

# 3. Notification API Tests
echo "3️⃣  Notification API Tests"
echo "----------------------"

test_endpoint "Get Notifications" "http://localhost:8000/api/v1/notifications/classified"

test_endpoint "Classify Notification" "http://localhost:8000/api/v1/notifications/classify" "POST" \
    '{"title":"Meeting Reminder","body":"Team standup in 15 minutes","app":"calendar","sender":"work"}'

echo ""

# 4. Privacy API Tests
echo "4️⃣  Privacy API Tests"
echo "-----------------"

test_endpoint "Get Privacy Status" "http://localhost:8000/api/v1/privacy/status"

test_endpoint "Toggle VPN" "http://localhost:8000/api/v1/privacy/vpn/toggle" "POST" \
    '{"enabled":true}'

test_endpoint "Toggle Caller ID Masking" "http://localhost:8000/api/v1/privacy/caller-id/toggle" "POST" \
    '{"enabled":true}'

test_endpoint "Configure Location Spoofing" "http://localhost:8000/api/v1/privacy/location/spoof" "POST" \
    '{"enabled":true,"latitude":37.7749,"longitude":-122.4194}'

echo ""

# 5. Wellbeing API Tests
echo "5️⃣  Wellbeing API Tests"
echo "-------------------"

test_endpoint "Get Today Stats" "http://localhost:8000/api/v1/wellbeing/stats/today"
test_endpoint "Get Weekly Stats" "http://localhost:8000/api/v1/wellbeing/stats/week"
test_endpoint "Get Focus Status" "http://localhost:8000/api/v1/wellbeing/focus/status"

test_endpoint "Activate Focus Mode" "http://localhost:8000/api/v1/wellbeing/focus/activate" "POST" \
    '{"duration_minutes":90,"blocked_apps":["instagram","twitter","facebook"]}'

test_endpoint "Deactivate Focus Mode" "http://localhost:8000/api/v1/wellbeing/focus/deactivate" "POST"

echo ""

# 6. Device API Tests
echo "6️⃣  Device API Tests"
echo "----------------"

test_endpoint "Get Devices" "http://localhost:8000/api/v1/devices"

test_endpoint "Send Device Command" "http://localhost:8000/api/v1/devices/command" "POST" \
    '{"device_id":"iot-device-001","command":"get_sensor_data","params":{}}'

echo ""

# 7. AI/ML Model Tests
echo "7️⃣  AI/ML Model Tests"
echo "-----------------"

if [ -f "ai-models/models/notification_classifier.pkl" ]; then
    echo -e "${GREEN}✓ PASS${NC} Model file exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} Model file not found"
    ((TESTS_FAILED++))
fi

if [ -f "ai-models/models/vectorizer.pkl" ]; then
    echo -e "${GREEN}✓ PASS${NC} Vectorizer file exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} Vectorizer file not found"
    ((TESTS_FAILED++))
fi

echo ""

# 8. IoT Device Tests
echo "8️⃣  IoT Device Tests (Mock Mode)"
echo "------------------------------"

if [ -f "iot-device/mqtt_client.py" ]; then
    echo -e "${GREEN}✓ PASS${NC} IoT client exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} IoT client not found"
    ((TESTS_FAILED++))
fi

if [ -d "iot-device/sensors" ]; then
    sensor_count=$(ls -1 iot-device/sensors/*.py 2>/dev/null | wc -l)
    if [ "$sensor_count" -ge 4 ]; then
        echo -e "${GREEN}✓ PASS${NC} All sensor modules present ($sensor_count modules)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} Missing sensor modules (found $sensor_count, need 4+)"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗ FAIL${NC} Sensors directory not found"
    ((TESTS_FAILED++))
fi

echo ""

# 9. Mobile App Tests
echo "9️⃣  Mobile App Tests"
echo "-----------------"

if [ -f "mobile-app/src/navigation/AppNavigator.js" ]; then
    echo -e "${GREEN}✓ PASS${NC} Navigation configured"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} Navigation not found"
    ((TESTS_FAILED++))
fi

if [ -f "mobile-app/src/services/api.js" ]; then
    echo -e "${GREEN}✓ PASS${NC} API service exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} API service not found"
    ((TESTS_FAILED++))
fi

if [ -f "mobile-app/src/services/mqtt.js" ]; then
    echo -e "${GREEN}✓ PASS${NC} MQTT service exists"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} MQTT service not found"
    ((TESTS_FAILED++))
fi

screen_count=$(ls -1 mobile-app/src/screens/*.js 2>/dev/null | wc -l)
if [ "$screen_count" -ge 4 ]; then
    echo -e "${GREEN}✓ PASS${NC} All screens present ($screen_count screens)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} Missing screens (found $screen_count, need 4)"
    ((TESTS_FAILED++))
fi

echo ""

# Summary
echo "================================================"
echo "📊 Test Summary"
echo "================================================"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed. Please review the output above.${NC}"
    exit 1
fi
