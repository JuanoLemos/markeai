#!/bin/bash
set -e

echo "━━ MarketAI Deploy ━━"
echo ""

echo "1. git pull..."
git pull origin master

echo "2. docker compose down..."
docker compose down

echo "3. docker compose up -d --build..."
docker compose up -d --build

echo "4. Checking services..."
sleep 5
docker compose ps

echo ""
echo "Deploy complete. Dashboard: http://localhost:8050"
