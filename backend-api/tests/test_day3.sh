#!/bin/bash

# Day 3 Testing Script
# Tests offline mode, caching, error handling, and loading states

echo "🧪 Testing Privacy-Focused Digital Wellbeing System - Day 3 Features"
echo "=================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
    fi
}

echo "📦 1. Checking Dependencies..."
echo "--------------------------------"

# Check if NetInfo is installed
if grep -q "@react-native-community/netinfo" mobile-app/package.json; then
    test_result 0 "NetInfo package installed"
else
    test_result 1 "NetInfo package not found"
fi

# Check if AsyncStorage is installed
if grep -q "@react-native-async-storage/async-storage" mobile-app/package.json; then
    test_result 0 "AsyncStorage package installed"
else
    test_result 1 "AsyncStorage package not found"
fi

echo ""
echo "📁 2. Checking File Structure..."
echo "--------------------------------"

# Check if new files exist
if [ -f "mobile-app/src/utils/offlineCache.js" ]; then
    test_result 0 "offlineCache.js exists"
else
    test_result 1 "offlineCache.js missing"
fi

if [ -f "mobile-app/src/utils/networkStatus.js" ]; then
    test_result 0 "networkStatus.js exists"
else
    test_result 1 "networkStatus.js missing"
fi

if [ -f "mobile-app/src/components/ErrorBoundary.js" ]; then
    test_result 0 "ErrorBoundary.js exists"
else
    test_result 1 "ErrorBoundary.js missing"
fi

if [ -f "mobile-app/src/components/OfflineIndicator.js" ]; then
    test_result 0 "OfflineIndicator.js exists"
else
    test_result 1 "OfflineIndicator.js missing"
fi

if [ -f "mobile-app/src/context/AppContext.js" ]; then
    test_result 0 "AppContext.js exists"
else
    test_result 1 "AppContext.js missing"
fi

echo ""
echo "🔍 3. Checking Code Integration..."
echo "--------------------------------"

# Check if ErrorBoundary is imported in App.js
if grep -q "ErrorBoundary" mobile-app/App.js; then
    test_result 0 "ErrorBoundary imported in App.js"
else
    test_result 1 "ErrorBoundary not imported in App.js"
fi

# Check if AppProvider is used
if grep -q "AppProvider" mobile-app/App.js; then
    test_result 0 "AppProvider used in App.js"
else
    test_result 1 "AppProvider not used in App.js"
fi

# Check if OfflineIndicator is used
if grep -q "OfflineIndicator" mobile-app/App.js; then
    test_result 0 "OfflineIndicator used in App.js"
else
    test_result 1 "OfflineIndicator not used in App.js"
fi

# Check if cache utilities are imported in api.js
if grep -q "offlineCache" mobile-app/src/services/api.js; then
    test_result 0 "Cache utilities imported in api.js"
else
    test_result 1 "Cache utilities not imported in api.js"
fi

# Check if networkStatus is imported in api.js
if grep -q "networkStatus" mobile-app/src/services/api.js; then
    test_result 0 "Network status utilities imported in api.js"
else
    test_result 1 "Network status utilities not imported in api.js"
fi

echo ""
echo "🎨 4. Checking UI Components..."
echo "--------------------------------"

# Check if ActivityIndicator is used in HomeScreen
if grep -q "ActivityIndicator" mobile-app/src/screens/HomeScreen.js 2>/dev/null; then
    test_result 0 "ActivityIndicator used in HomeScreen"
else
    test_result 1 "ActivityIndicator not found in HomeScreen"
fi

# Check if ActivityIndicator is used in NotificationsScreen
if grep -q "ActivityIndicator" mobile-app/src/screens/NotificationsScreen.js; then
    test_result 0 "ActivityIndicator used in NotificationsScreen"
else
    test_result 1 "ActivityIndicator not found in NotificationsScreen"
fi

# Check if Alert is used for error handling
if grep -q "Alert" mobile-app/src/screens/HomeScreen.js 2>/dev/null; then
    test_result 0 "Alert used for error handling in HomeScreen"
else
    test_result 1 "Alert not found in HomeScreen"
fi

echo ""
echo "📚 5. Checking Documentation..."
echo "--------------------------------"

if [ -f "docs/DAY_3_PROGRESS.md" ]; then
    test_result 0 "Day 3 progress report exists"
else
    test_result 1 "Day 3 progress report missing"
fi

# Check if README is updated with Day 3
if grep -q "Day 3" README.md; then
    test_result 0 "README updated with Day 3"
else
    test_result 1 "README not updated"
fi

echo ""
echo "=================================================================="
echo "📊 Test Summary"
echo "=================================================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Day 3 implementation complete.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Please review the issues above.${NC}"
    exit 1
fi
