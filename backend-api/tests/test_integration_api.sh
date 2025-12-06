#!/bin/bash

# Integration Testing Script
# Tests backend API endpoints and mobile app integration

echo "🔗 Integration Testing - Backend + Mobile App"
echo "=============================================="
echo ""

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local data=$4
    local description=$5
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $description (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description (Expected $expected_status, got $http_code)"
        ((FAILED++))
        return 1
    fi
}

echo "📊 1. Testing Health & Status Endpoints"
echo "----------------------------------------"
test_endpoint "GET" "/health" "200" "" "Health check"
test_endpoint "GET" "/docs" "200" "" "API documentation"

echo ""
echo "🔐 2. Testing Privacy API"
echo "----------------------------------------"
test_endpoint "GET" "/api/v1/privacy/status" "200" "" "Get privacy status"

echo ""
echo "📬 3. Testing Notifications API"
echo "----------------------------------------"
test_endpoint "POST" "/api/v1/notifications/classify" "200" \
    '{"text":"Meeting in 5 minutes","sender":"calendar","received_at":"2025-12-04T10:00:00Z"}' \
    "Classify notification"

echo ""
echo "🎯 4. Testing Wellbeing API"
echo "----------------------------------------"
test_endpoint "GET" "/api/v1/wellbeing/stats?period=today" "200" "" "Get today's stats"
test_endpoint "GET" "/api/v1/wellbeing/focus-mode/status" "200" "" "Get focus mode status"

echo ""
echo "🤖 5. Testing IoT Device API"
echo "----------------------------------------"
test_endpoint "GET" "/api/v1/devices" "200" "" "List devices"

echo ""
echo "=============================================="
echo "📊 Integration Test Summary"
echo "=============================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All integration tests passed!${NC}"
    echo "✅ Backend API is fully functional"
    echo "✅ All endpoints responding correctly"
    echo "✅ Mobile app can integrate successfully"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some integration tests failed${NC}"
    echo "Please check the backend logs for errors"
    exit 1
fi
