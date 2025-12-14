#!/bin/bash

echo "🛑 Stopping QCM Generator..."
echo ""

# Stop Docker Compose
docker compose down

echo ""
echo "✅ QCM Generator has been stopped successfully!"
echo ""
echo "To start again, run: ./start.sh"
echo ""
