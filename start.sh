#!/bin/bash

echo "🚀 Starting QCM Generator..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker is not running."
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed."
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Start Docker Compose
echo "📦 Building and starting containers..."
docker compose up --build -d

# Wait a moment for the service to start
sleep 3

echo ""
echo "✅ QCM Generator is now running!"
echo ""
echo "🌐 Open your browser and go to: http://localhost:5000"
echo ""
echo "To stop the application, run: ./stop.sh"
echo ""
