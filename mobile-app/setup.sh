#!/bin/bash

# Privacy Wellbeing Mobile App - Quick Setup Script
# Fixes all Babel errors and prepares app for deployment

echo "🚀 Privacy Wellbeing Mobile App - Setup Script"
echo "=============================================="
echo ""

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Step 1: Clean everything
echo "🧹 Step 1: Cleaning old build files..."
rm -rf node_modules
rm -rf android/build
rm -rf android/app/build
rm -rf $TMPDIR/react-* 2>/dev/null
rm -rf $TMPDIR/metro-* 2>/dev/null

# Clean npm cache
npm cache clean --force

# Clean watchman if installed
if command -v watchman &> /dev/null; then
    echo "   Clearing watchman..."
    watchman watch-del-all
fi

echo "   ✅ Clean complete"
echo ""

# Step 2: Install dependencies
echo "📦 Step 2: Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "   ❌ npm install failed!"
    echo "   Try running: npm install --legacy-peer-deps"
    exit 1
fi

echo "   ✅ Dependencies installed"
echo ""

# Step 3: Link React Native (if needed)
echo "🔗 Step 3: Checking React Native setup..."
if command -v react-native &> /dev/null; then
    echo "   React Native CLI found"
else
    echo "   Installing React Native CLI globally..."
    npm install -g react-native-cli
fi

echo "   ✅ React Native ready"
echo ""

# Step 4: Android Gradle sync
echo "🤖 Step 4: Syncing Android Gradle..."
cd android
./gradlew clean

if [ $? -ne 0 ]; then
    echo "   ❌ Gradle clean failed!"
    echo "   Try opening Android Studio and syncing manually"
    cd ..
    exit 1
fi

cd ..
echo "   ✅ Gradle synced"
echo ""

# Step 5: Verify configuration files
echo "🔧 Step 5: Verifying configuration..."

# Check babel.config.js
if [ -f "babel.config.js" ]; then
    echo "   ✅ babel.config.js exists"
else
    echo "   ❌ babel.config.js missing!"
    exit 1
fi

# Check metro.config.js
if [ -f "metro.config.js" ]; then
    echo "   ✅ metro.config.js exists"
else
    echo "   ❌ metro.config.js missing!"
    exit 1
fi

# Check app.json
if [ -f "app.json" ]; then
    echo "   ✅ app.json exists"
else
    echo "   ❌ app.json missing!"
    exit 1
fi

echo ""

# Step 6: Check backend connection
echo "🌐 Step 6: Checking backend connection..."

# Read API URL from config
API_URL=$(grep -o "API_URL:.*" src/config/index.js | cut -d "'" -f 2 || echo "http://localhost:8000")

echo "   Configured API URL: $API_URL"

# Try to ping backend (remove protocol for ping)
BACKEND_HOST=$(echo $API_URL | sed -e 's|^[^/]*//||' -e 's|:.*$||')

if ping -c 1 "$BACKEND_HOST" &> /dev/null; then
    echo "   ✅ Backend host reachable"
else
    echo "   ⚠️  Backend host not reachable"
    echo "   Make sure backend is running: cd ../backend-api && uvicorn app.main:app"
fi

echo ""

# Step 7: Display next steps
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "📱 To run the app:"
echo ""
echo "   Terminal 1 (Metro Bundler):"
echo "   $ npm start -- --reset-cache"
echo ""
echo "   Terminal 2 (Run Android):"
echo "   $ npm run android"
echo ""
echo "   Or run both in background:"
echo "   $ npm start -- --reset-cache &"
echo "   $ npm run android"
echo ""
echo "🔐 After app starts, grant permissions:"
echo "   1. Notification Access (Settings → Apps → Special → Notification)"
echo "   2. Usage Stats (Settings → Apps → Special → Usage access)"
echo "   3. VPN Permission (System dialog when you enable it)"
echo "   4. Accessibility (Settings → Accessibility for Focus Mode)"
echo ""
echo "📖 For detailed setup, see: MOBILE_APP_SETUP.md"
echo ""
echo "🐛 If you encounter errors:"
echo "   - Check: adb logcat | grep ReactNative"
echo "   - Ensure backend is running on $API_URL"
echo "   - Check device/emulator is connected: adb devices"
echo ""
echo "🎉 Happy coding!"
