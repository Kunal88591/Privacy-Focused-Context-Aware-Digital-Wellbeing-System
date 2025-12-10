#!/bin/bash

echo "🧹 Cleaning up Privacy-Focused Digital Wellbeing System..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove duplicate/unused service files (using the active ones)
echo "Removing duplicate service files..."
rm -f backend-api/app/services/caller_id_service.py
rm -f backend-api/app/services/location_service.py
rm -f backend-api/app/services/vpn_service.py
rm -f backend-api/app/services/network_security_service.py
rm -f backend-api/app/services/privacy_score_service.py

# Remove node_modules if exists (will be reinstalled)
if [ -d "mobile-app/node_modules" ]; then
    echo "Node modules exist (not removing - too large, already in .gitignore)"
fi

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf backend-api/dist/
rm -rf backend-api/build/
rm -rf mobile-app/.expo/
rm -rf mobile-app/android/app/build/

# Remove log files
find . -name "*.log" -type f -delete 2>/dev/null

echo "✅ Cleanup complete!"
echo ""
echo "Removed:"
echo "- Python cache files (__pycache__, *.pyc)"
echo "- Pytest cache directories"
echo "- Duplicate service files (5 files)"
echo "- Build artifacts"
echo "- Log files"
