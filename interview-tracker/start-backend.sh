#!/bin/bash

echo "======================================"
echo "Starting Interview Tracker Backend..."
echo "======================================"

cd backend

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "Error: Maven is not installed. Please install Maven first."
    exit 1
fi

# Build and run the Spring Boot application
echo "Building and starting Spring Boot application..."
mvn spring-boot:run

echo ""
echo "Backend stopped."
