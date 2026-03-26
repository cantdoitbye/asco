#!/bin/bash

set -e

REPO_URL="https://github.com/cantdoitbye/asco.git"
SERVER_IP="135.222.42.174"
DEPLOY_DIR="/home/ai-govt/asco"

FRONTEND_PORT=3081
BACKEND_PORT=8081
POSTGRES_PORT=5481
REDIS_PORT=6381

echo "=========================================="
echo "Ooumph ASCO Deployment Script"
echo "=========================================="
echo "Server IP: $SERVER_IP"
echo "Deploy Directory: $DEPLOY_DIR"
echo "Frontend Port: $FRONTEND_PORT"
echo "Backend Port: $BACKEND_PORT"
echo "PostgreSQL Port: $POSTGRES_PORT"
echo "Redis Port: $REDIS_PORT"
echo "=========================================="

if [ -d "$DEPLOY_DIR" ]; then
    echo "Directory $DEPLOY_DIR already exists. Pulling latest changes..."
    cd "$DEPLOY_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

echo ""
echo "Creating .env file from example if it doesn't exist..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit .env file with your production settings including OPENAI_API_KEY"
    else
        touch .env
    fi
fi

# Export ports so docker-compose uses them without us having to overwrite the file
export FRONTEND_PORT
export BACKEND_PORT
export POSTGRES_PORT
export REDIS_PORT



echo ""
echo "Stopping any existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

echo ""
echo "Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

echo ""
echo "Running database seeders..."
docker-compose -f docker-compose.prod.yml exec backend python -m app.seeders.seed_all

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Access the application at:"
echo "  Frontend: http://${SERVER_IP}:${FRONTEND_PORT}"
echo "  Backend API: http://${SERVER_IP}:${BACKEND_PORT}"
echo "  API Docs: http://${SERVER_IP}:${BACKEND_PORT}/docs"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo "=========================================="
