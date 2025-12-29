#!/bin/bash

# Day 22: System Integration Test Runner
# Runs comprehensive end-to-end tests across all system components

set -e  # Exit on error

echo "🚀 Day 22: System Integration Tests"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    local url=$3
    
    echo -n "Checking $service_name on port $port... "
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        return 1
    fi
}

# Function to run test suite
run_test_suite() {
    local test_name=$1
    local test_command=$2
    
    echo ""
    echo "📋 Running: $test_name"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ $test_name PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ $test_name FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Step 1: Check Prerequisites
echo "📦 Step 1: Checking Prerequisites"
echo "----------------------------------------"

# Check if backend is running
if ! check_service "Backend API" 8000 "http://localhost:8000/health"; then
    echo -e "${YELLOW}⚠️  Backend not running. Starting...${NC}"
    cd backend-api
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
    pip install -q -r requirements.txt
    PYTHONPATH=. uvicorn app.main:app --reload &
    BACKEND_PID=$!
    echo "Backend starting... (PID: $BACKEND_PID)"
    sleep 5
    cd ..
fi

# Check if MQTT broker is running
if ! check_service "MQTT Broker" 1883; then
    echo -e "${YELLOW}⚠️  MQTT broker not running${NC}"
    echo "Please start mosquitto: mosquitto -c /path/to/mosquitto.conf"
fi

echo ""

# Step 2: Backend Integration Tests
echo "🔧 Step 2: Backend Integration Tests"
echo "========================================"

cd backend-api

run_test_suite "Notification Flow Tests" \
    "pytest tests/test_integration.py::TestNotificationFlow -v"

run_test_suite "Focus Mode Flow Tests" \
    "pytest tests/test_integration.py::TestFocusModeFlow -v"

run_test_suite "Sensor Alert Flow Tests" \
    "pytest tests/test_integration.py::TestSensorAlertFlow -v"

run_test_suite "Privacy Flow Tests" \
    "pytest tests/test_integration.py::TestPrivacyFlow -v"

run_test_suite "Analytics Flow Tests" \
    "pytest tests/test_integration.py::TestAnalyticsFlow -v"

run_test_suite "Recommendations Flow Tests" \
    "pytest tests/test_integration.py::TestRecommendationsFlow -v"

run_test_suite "System Health Tests" \
    "pytest tests/test_integration.py::TestSystemHealth -v"

run_test_suite "Performance Tests" \
    "pytest tests/test_integration.py::TestPerformance -v"

cd ..

# Step 3: Mobile Integration Tests
echo ""
echo "📱 Step 3: Mobile Integration Tests"
echo "========================================"

cd mobile-app

run_test_suite "Mobile API Integration" \
    "npm test -- __tests__/integration/api.test.js"

run_test_suite "Mobile Offline Mode" \
    "npm test -- __tests__/integration/offline.test.js"

run_test_suite "Mobile Notifications" \
    "npm test -- __tests__/integration/notifications.test.js"

cd ..

# Step 4: End-to-End Scenarios
echo ""
echo "🔄 Step 4: End-to-End Scenario Tests"
echo "========================================"

echo ""
echo "Scenario 1: Complete Notification Journey"
echo "  Notification arrives → ML classifies → Displays in app → User dismisses"
run_test_suite "E2E: Notification Journey" \
    "cd backend-api && pytest tests/test_integration.py::TestNotificationFlow::test_notification_classification_flow -v"

echo ""
echo "Scenario 2: Focus Mode Lifecycle"
echo "  User activates → Apps blocked → Session ends → Stats updated"
run_test_suite "E2E: Focus Mode Lifecycle" \
    "cd backend-api && pytest tests/test_integration.py::TestFocusModeFlow::test_focus_mode_activation -v"

echo ""
echo "Scenario 3: Sensor Alert Pipeline"
echo "  Sensor reads data → Threshold exceeded → Alert generated → Mobile notified"
run_test_suite "E2E: Sensor Alert Pipeline" \
    "cd backend-api && pytest tests/test_integration.py::TestSensorAlertFlow::test_noise_detection_alert -v"

echo ""
echo "Scenario 4: Privacy Protection Flow"
echo "  VPN enabled → Trackers blocked → Privacy score updated"
run_test_suite "E2E: Privacy Protection" \
    "cd backend-api && pytest tests/test_integration.py::TestPrivacyFlow::test_vpn_activation -v"

# Step 5: Performance Benchmarks
echo ""
echo "⚡ Step 5: Performance Benchmarks"
echo "========================================"

cd backend-api

echo ""
echo "Testing API Response Time (target: <100ms)..."
run_test_suite "API Response Time" \
    "pytest tests/test_integration.py::TestPerformance::test_api_response_time -v"

echo ""
echo "Testing ML Inference Time (target: <100ms)..."
run_test_suite "ML Inference Time" \
    "pytest tests/test_integration.py::TestPerformance::test_ml_inference_time -v"

cd ..

# Step 6: Summary
echo ""
echo "📊 Test Summary"
echo "========================================"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests:  $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL INTEGRATION TESTS PASSED!${NC}"
    echo ""
    echo "🎉 Day 22 Complete: System Integration Verified"
    echo ""
    echo "Next Steps:"
    echo "  - Day 23: Privacy Flow Testing"
    echo "  - Day 24: IoT Automation Testing"
    echo "  - Day 25: Bug Fixes & Optimization"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failures above and fix them."
    echo ""
    echo "Common issues:"
    echo "  - Backend not running (start with: cd backend-api && uvicorn app.main:app)"
    echo "  - MQTT broker not running (start with: mosquitto)"
    echo "  - Missing dependencies (run: ./setup.sh)"
    exit 1
fi
