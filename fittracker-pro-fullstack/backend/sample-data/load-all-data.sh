#!/bin/bash

# FitTracker Pro - Load All Sample Data Script
# This script loads all sample data into the FitTracker Pro databases

set -e

echo "🎯 FitTracker Pro - Loading Sample Data"
echo "========================================"

# Check if PostgreSQL container is running
if ! docker ps | grep -q fittracker-postgres; then
    echo "❌ Error: PostgreSQL container is not running"
    echo "   Please start the services first: docker-compose up -d"
    exit 1
fi

echo ""
echo "📊 Loading Users data..."
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_users < 01_users_sample_data.sql
echo "✅ Users data loaded successfully"

echo ""
echo "🥗 Loading Nutrition data..."
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_nutrition < 02_nutrition_sample_data.sql
echo "✅ Nutrition data loaded successfully"

echo ""
echo "💪 Loading Workout data..."
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_workouts < 03_workout_sample_data.sql
echo "✅ Workout data loaded successfully"

echo ""
echo "========================================"
echo "✨ All sample data loaded successfully!"
echo ""
echo "📝 Test Credentials:"
echo "   Email: john.doe@example.com"
echo "   Password: Password123!"
echo ""
echo "🌐 Access the application at:"
echo "   API Gateway: http://localhost:8080"
echo "   Eureka Dashboard: http://localhost:8761"
echo ""
echo "📚 See sample-data/README.md for more information"
