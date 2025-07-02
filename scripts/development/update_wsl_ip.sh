#!/bin/bash

echo "=== WSL IP Address Update Script ==="

# Get current WSL IP
WSL_IP=$(hostname -I | awk '{print $1}')
echo "Current WSL IP: $WSL_IP"

# Update .env file
if [ -f ".env" ]; then
    # Update .env with current IP
    sed -i "s|EXPO_PUBLIC_API_BASE_URL=http://[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*:8000|EXPO_PUBLIC_API_BASE_URL=http://$WSL_IP:8000|" .env
    echo "✅ Updated .env file"
else
    echo "❌ .env file not found"
fi

# Update mobile app client.ts with current IP (as fallback)
CLIENT_FILE="apps/mobile/src/api/client.ts"
if [ -f "$CLIENT_FILE" ]; then
    # Update the fallback IP in client.ts
    sed -i "s|return 'http://[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*:8000';  // Current WSL IP|return 'http://$WSL_IP:8000';  // Current WSL IP|" "$CLIENT_FILE"
    echo "✅ Updated mobile app fallback IP"
else
    echo "❌ client.ts file not found at $CLIENT_FILE"
fi

echo ""
echo "=== Updated Configuration ==="
echo "WSL IP: $WSL_IP"
echo "Backend URL: http://$WSL_IP:8000"
echo ""
echo "🔄 Restart Expo development server to apply changes"
echo "📱 App will automatically use the updated IP address"
