#!/bin/bash

echo "=== Habeas Manual Testing Startup Script ==="
echo "WSL IP Address: $(hostname -I | awk '{print $1}')"
echo "Windows Host IP: $(ip route show | grep -i default | awk '{ print $3}' | head -1)"
echo ""

echo "1. Starting PostgreSQL database..."
cd ~/habeas/apps
docker compose up -d db

echo "2. Waiting for database to be ready..."
sleep 10

echo "3. Running database migrations..."
docker compose run --rm migration

echo "4. Starting backend API server..."
docker compose up -d backend

echo "5. Waiting for backend to start..."
sleep 15

echo "6. Testing backend connectivity..."
curl -f http://localhost:8000/health || echo "Backend health check failed"

echo ""
echo "=== Backend Services Started ==="
echo "API Server: http://$(hostname -I | awk '{print $1}'):8000"
echo "API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "Database: postgresql://postgres:habeas_dev_password@localhost:5432/habeas"
echo ""
echo "Next steps:"
echo "1. Ensure Android Studio emulator is running in Windows"
echo "2. Start the mobile app with: cd apps/mobile && npm start"
echo "3. Press 'a' to run on Android device/emulator"
echo ""
echo "=== Available API Endpoints for Testing ==="
echo "- POST /signup/attorney - Register as attorney"
echo "- POST /signup/client - Register as client"
echo "- GET /health - Health check"
echo "- GET /docs - API documentation"
