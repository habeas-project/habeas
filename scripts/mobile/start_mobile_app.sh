#!/bin/bash

echo "=== Habeas Mobile App Startup Script ==="
echo ""

# Auto-update WSL IP configuration
echo "🔄 Updating WSL IP configuration..."
~/habeas/scripts/development/update_wsl_ip.sh

# Check if backend is running
WSL_IP=$(hostname -I | awk '{print $1}')
echo "Checking backend connectivity at $WSL_IP:8000..."

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running and accessible"
else
    echo "❌ Backend is not accessible. Please start backend first with:"
    echo "   ~/habeas/scripts/development/start_manual_testing.sh"
    exit 1
fi

echo ""
echo "Backend API accessible at: http://$WSL_IP:8000"
echo "API Documentation: http://$WSL_IP:8000/docs"
echo ""

# Navigate to mobile directory
cd ~/habeas/apps/mobile

echo "🧹 Clearing Expo and Metro caches for fresh start..."
echo "This ensures the latest code changes are loaded properly."

# Clear Expo and Metro caches (based on Expo documentation)
rm -rf .expo
rm -rf node_modules/.cache
rm -rf $TMPDIR/haste-map-* 2>/dev/null || true
rm -rf $TMPDIR/metro-cache 2>/dev/null || true

echo "✅ Cache cleared successfully"
echo ""

echo "🚀 Starting Expo development server with tunnel mode..."
echo ""
echo "=== Important Instructions ==="
echo "1. Ensure your Android emulator is running in Windows"
echo "2. When the QR code appears, press 'a' to run on Android"
echo "3. Tunnel mode creates a public URL for reliable connections"
echo "4. The app is configured to connect to: http://$WSL_IP:8000"
echo "5. Mock authentication is enabled for easy testing"
echo ""
echo "=== New Features Available ==="
echo "- 🎉 Welcome Screen: 4-step onboarding experience"
echo "- 🏠 Redesigned Home Screen: Human-centered messaging"
echo "- ⚖️ Unified Signup Flow: Single entry point for all users"
echo "- 🤝 Multi-Profile Support: Help multiple family members"
echo "- 🚨 Enhanced Emergency Features: Improved visual design"
echo ""
echo "=== Cache Management ==="
echo "- Expo cache cleared (.expo directory)"
echo "- Metro bundler cache cleared"
echo "- Node modules cache cleared"
echo "- Using tunnel mode for reliable connections"
echo ""

# Start Expo with cache clearing and tunnel mode
npx expo start --clear --tunnel
