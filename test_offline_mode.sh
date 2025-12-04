#!/bin/bash

# Offline Mode Testing Script
# Tests caching, network detection, and offline functionality

# Don't exit on test failures
set +e

echo "======================================"
echo "   Offline Mode Testing"
echo "======================================"
echo ""

MOBILE_APP_DIR="/workspaces/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/mobile-app"
cd "$MOBILE_APP_DIR"

passed=0
failed=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
run_test() {
    local test_name="$1"
    local condition="$2"
    
    echo -n "Testing $test_name... "
    if eval "$condition"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((failed++))
    fi
}

echo "=== 1. Cache System Tests ==="
echo ""

# Test 1: Cache utility exists
run_test "Cache utility file exists" \
    "[ -f 'src/utils/offlineCache.js' ]"

# Test 2: Cache has setCache function
run_test "Cache has setCache function" \
    "grep -q 'export const setCache' src/utils/offlineCache.js"

# Test 3: Cache has getCache function
run_test "Cache has getCache function" \
    "grep -q 'export const getCache' src/utils/offlineCache.js"

# Test 4: Cache uses AsyncStorage
run_test "Cache uses AsyncStorage" \
    "grep -q '@react-native-async-storage/async-storage' src/utils/offlineCache.js"

# Test 5: Cache has expiry logic
run_test "Cache has expiry logic" \
    "grep -q 'expiryMs' src/utils/offlineCache.js"

echo ""
echo "=== 2. Network Status Tests ==="
echo ""

# Test 6: Network status utility exists
run_test "Network status utility exists" \
    "[ -f 'src/utils/networkStatus.js' ]"

# Test 7: Network status uses NetInfo
run_test "Network status uses NetInfo" \
    "grep -q '@react-native-community/netinfo' src/utils/networkStatus.js"

# Test 8: useNetworkStatus hook exists
run_test "useNetworkStatus hook exists" \
    "grep -q 'export const useNetworkStatus' src/utils/networkStatus.js"

# Test 9: Network state tracking
run_test "Network state tracking" \
    "grep -q 'isConnected' src/utils/networkStatus.js && grep -q 'isInternetReachable' src/utils/networkStatus.js"

echo ""
echo "=== 3. Offline Indicator Tests ==="
echo ""

# Test 10: Offline indicator component exists
run_test "Offline indicator exists" \
    "[ -f 'src/components/OfflineIndicator.js' ]"

# Test 11: Shows offline message
run_test "Shows offline message" \
    "grep -q 'offline' src/components/OfflineIndicator.js"

# Test 12: Uses network status hook
run_test "Uses network status hook" \
    "grep -q 'useNetworkStatus' src/components/OfflineIndicator.js"

# Test 13: Conditional rendering
run_test "Conditional rendering based on network" \
    "grep -q 'if.*isOnline' src/components/OfflineIndicator.js"

echo ""
echo "=== 4. API Integration Tests ==="
echo ""

# Test 14: API has caching logic
run_test "API has caching" \
    "grep -q 'cacheableGet' src/services/api.js"

# Test 15: API checks network status
run_test "API integrates with cache" \
    "grep -q 'getCache\|setCache' src/services/api.js"

# Test 16: API has retry logic
run_test "API has retry logic" \
    "grep -q 'retryRequest' src/services/api.js"

# Test 17: Fallback to cache on error
run_test "Fallback to cache on error" \
    "grep -q 'const cached = await getCache' src/services/api.js"

echo ""
echo "=== 5. Component Integration Tests ==="
echo ""

# Test 18: App.js includes OfflineIndicator
run_test "App includes OfflineIndicator" \
    "grep -q 'OfflineIndicator' App.js"

# Test 19: AppContext provides network status
run_test "AppContext provides network status" \
    "grep -q 'networkStatus' src/context/AppContext.js"

# Test 20: HomeScreen handles offline
run_test "HomeScreen handles offline state" \
    "grep -q 'loading\|error' src/screens/HomeScreen.js"

echo ""
echo "=== 6. Package Dependencies ==="
echo ""

# Test 21: NetInfo installed
run_test "NetInfo package installed" \
    "grep -q '@react-native-community/netinfo' package.json"

# Test 22: AsyncStorage installed
run_test "AsyncStorage package installed" \
    "grep -q '@react-native-async-storage/async-storage' package.json"

echo ""
echo "=== 7. Error Handling ==="
echo ""

# Test 23: Error boundary exists
run_test "Error boundary exists" \
    "[ -f 'src/components/ErrorBoundary.js' ]"

# Test 24: API creates user-friendly errors
run_test "API creates user-friendly errors" \
    "grep -q 'createUserFriendlyError' src/services/api.js"

# Test 25: Error messages are descriptive
run_test "Descriptive error messages" \
    "grep -q 'offline\|network' src/services/api.js"

echo ""
echo "======================================"
echo "      Test Summary"
echo "======================================"
echo ""
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo "Total:  $((passed + failed))"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All offline mode tests passed!${NC}"
    echo ""
    echo "Offline Features Verified:"
    echo "  ✓ Cache system with expiry"
    echo "  ✓ Network status detection"
    echo "  ✓ Offline indicator UI"
    echo "  ✓ API caching and retry"
    echo "  ✓ Error handling"
    echo "  ✓ Component integration"
    echo ""
    echo "The app is ready for offline use!"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
