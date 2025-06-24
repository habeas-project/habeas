#!/bin/bash

echo "=== Habeas Mobile Cache Clearing Script ==="
echo ""
echo "This script clears all Expo and Metro caches to resolve common issues:"
echo "- App showing old screens after code changes"
echo "- 'No apps connected' errors when reloading"
echo "- Stale JavaScript bundles"
echo "- Connection issues with development server"
echo ""

# Navigate to mobile directory
cd ~/habeas/apps/mobile

echo "🧹 Clearing comprehensive cache..."

# Kill any running Expo/Metro processes
echo "1. Stopping any running Expo processes..."
pkill -f "expo" 2>/dev/null || true
pkill -f "metro" 2>/dev/null || true
sleep 2

# Clear Expo-specific caches
echo "2. Clearing Expo caches..."
rm -rf .expo
rm -rf node_modules/.cache

# Clear Metro bundler caches (based on Expo documentation)
echo "3. Clearing Metro bundler caches..."
rm -rf $TMPDIR/haste-map-* 2>/dev/null || true
rm -rf $TMPDIR/metro-cache 2>/dev/null || true

# Clear npm cache
echo "4. Clearing npm cache..."
npm cache clean --force 2>/dev/null || true

# Clear watchman cache if available
echo "5. Clearing watchman cache (if available)..."
watchman watch-del-all 2>/dev/null || echo "   Watchman not installed (optional)"

echo ""
echo "✅ All caches cleared successfully!"
echo ""
echo "=== Next Steps ==="
echo "1. Run: ~/habeas/scripts/mobile/start_mobile_app.sh"
echo "2. Or manually: cd ~/habeas/apps/mobile && npx expo start --clear --tunnel"
echo "3. In Android emulator: Close Expo Go completely and reopen"
echo "4. Scan QR code or press 'a' in terminal"
echo ""
echo "=== If Still Having Issues ==="
echo "- Uninstall and reinstall Expo Go app in Android emulator"
echo "- Restart Android emulator completely"
echo "- Check that backend is running: ~/habeas/scripts/development/start_manual_testing.sh"
echo ""
