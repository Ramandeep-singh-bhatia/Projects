# FitTracker Pro - Getting Started Guide

## Table of Contents

1. [Introduction](#introduction)
2. [What is FitTracker Pro?](#what-is-fittracker-pro)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [First-Time Setup](#first-time-setup)
6. [Running the Application](#running-the-application)
7. [Your First API Calls](#your-first-api-calls)
8. [Understanding the Architecture](#understanding-the-architecture)
9. [Next Steps](#next-steps)

---

## Introduction

Welcome to **FitTracker Pro**, a production-ready microservices-based health and fitness tracking platform. This guide will walk you through everything you need to know to get started with the application, from installation to making your first API calls.

**Time to complete:** 30-45 minutes
**Skill level:** Intermediate (basic knowledge of Java, Spring Boot, and Docker helpful)

---

## What is FitTracker Pro?

FitTracker Pro is a comprehensive health and fitness tracking platform that helps users:

- **Track Nutrition**: Log meals, track calories and macronutrients, browse food database
- **Monitor Workouts**: Plan workouts, log exercises, track progress and calories burned
- **Analyze Progress**: View daily/weekly/monthly analytics, track goals, monitor trends
- **Manage Profile**: Set fitness goals, update activity levels, customize targets

### Key Features

✅ **Microservices Architecture**: 8 independent, scalable services
✅ **Event-Driven**: Real-time updates using Apache Kafka
✅ **High Performance**: Redis caching with cache warming
✅ **Secure**: JWT-based authentication and authorization
✅ **Observable**: Prometheus metrics, Grafana dashboards, Jaeger tracing
✅ **Well-Documented**: Swagger/OpenAPI for all APIs
✅ **Production-Ready**: Docker containerization, health checks, auto-scaling

### Technology Stack

**Backend Framework:**
- Java 17
- Spring Boot 3.2.0
- Spring Cloud 2023.0.0

**Databases & Caching:**
- PostgreSQL 14 (4 separate databases)
- Redis 7 (distributed caching)

**Messaging:**
- Apache Kafka 7.5.0 (event streaming)
- Zookeeper 7.5.0 (coordination)

**Monitoring:**
- Prometheus (metrics collection)
- Grafana (visualization)
- Jaeger (distributed tracing)

**Containerization:**
- Docker
- Docker Compose

---

## System Requirements

### Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB free space

**Recommended:**
- CPU: 8 cores
- RAM: 16 GB
- Disk: 50 GB free space (SSD recommended)

### Software Requirements

**Required:**

1. **Java Development Kit (JDK) 17 or higher**
   - Download: https://adoptium.net/ or https://www.oracle.com/java/technologies/downloads/
   - Verify: `java -version` should show 17 or higher

2. **Apache Maven 3.8 or higher**
   - Download: https://maven.apache.org/download.cgi
   - Verify: `mvn -version`

3. **Docker Desktop (or Docker Engine + Docker Compose)**
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version` and `docker-compose --version`

4. **Git**
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

**Optional (but recommended):**

- **Postman** or **Insomnia** (for API testing)
- **IntelliJ IDEA** or **Eclipse** (for code exploration)
- **curl** (for command-line API testing)

### Operating System

- **Linux** (Ubuntu 20.04+, CentOS 7+, etc.)
- **macOS** (10.15+)
- **Windows** (10/11 with WSL2 recommended for Docker)

---

## Installation

### Step 1: Verify Prerequisites

Open a terminal and verify all prerequisites are installed:

```bash
# Check Java version (must be 17+)
java -version

# Expected output:
# openjdk version "17.0.x" or higher

# Check Maven version
mvn -version

# Expected output:
# Apache Maven 3.8.x or higher

# Check Docker version
docker --version
docker-compose --version

# Expected output:
# Docker version 20.x or higher
# Docker Compose version 2.x or higher

# Check Git version
git --version

# Expected output:
# git version 2.x or higher
```

### Step 2: Clone the Repository

```bash
# Navigate to your projects directory
cd ~/Projects
# Or on Windows: cd C:\Projects

# Clone the repository
git clone <repository-url> fittracker-pro
cd fittracker-pro
```

### Step 3: Explore the Project Structure

```bash
# View the project structure
tree -L 2 -d

# Or just list directories
ls -la
```

**Project Structure:**
```
fittracker-pro/
├── analytics-service/       # Analytics microservice
├── api-gateway/            # API Gateway
├── common/                 # Shared DTOs and utilities
├── config-server/          # Configuration server
├── docker/                 # Docker configuration files
├── eureka-server/          # Service discovery
├── nutrition-service/      # Nutrition tracking service
├── sample-data/            # Sample data for testing
├── user-service/           # User management service
├── workout-service/        # Workout tracking service
├── docker-compose.yml      # Development infrastructure
├── docker-compose.prod.yml # Production configuration
├── pom.xml                # Parent Maven POM
└── README.md              # Project overview
```

---

## First-Time Setup

### Step 1: Build the Project

Build all microservices using Maven:

```bash
# Navigate to project root
cd fittracker-pro

# Clean and build all services
mvn clean install

# This will:
# - Download all dependencies (~500 MB)
# - Compile all Java code
# - Run unit tests
# - Package services as JAR files
# - Takes ~5-10 minutes on first run
```

**Expected Output:**
```
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary:
[INFO] ------------------------------------------------------------------------
[INFO] fittracker-pro ..................................... SUCCESS
[INFO] common ............................................. SUCCESS
[INFO] eureka-server ...................................... SUCCESS
[INFO] config-server ...................................... SUCCESS
[INFO] api-gateway ........................................ SUCCESS
[INFO] user-service ....................................... SUCCESS
[INFO] nutrition-service .................................. SUCCESS
[INFO] workout-service .................................... SUCCESS
[INFO] analytics-service .................................. SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```

**If build fails**, see the [Troubleshooting Guide](TROUBLESHOOTING.md).

### Step 2: Start Infrastructure Services

Start PostgreSQL, Redis, Kafka, and monitoring tools:

```bash
# Start all infrastructure containers
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
# Watch the logs
docker-compose logs -f
```

**Press Ctrl+C** to stop watching logs once you see:
```
fittracker-postgres    | database system is ready to accept connections
fittracker-redis       | Ready to accept connections
fittracker-kafka       | [KafkaServer id=1] started
```

### Step 3: Verify Infrastructure

Check that all containers are running:

```bash
docker-compose ps
```

**Expected Output:**
```
NAME                      STATUS
fittracker-postgres       Up (healthy)
fittracker-redis          Up (healthy)
fittracker-kafka          Up (healthy)
fittracker-zookeeper      Up
fittracker-prometheus     Up
fittracker-grafana        Up
fittracker-jaeger         Up
```

All services should show **"Up"** or **"Up (healthy)"**.

### Step 4: Load Sample Data (Optional but Recommended)

Load sample data for testing:

```bash
cd sample-data

# Make script executable (Linux/Mac)
chmod +x load-all-data.sh

# Run the loader
./load-all-data.sh
```

**On Windows (PowerShell):**
```powershell
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_users -f sample-data/01_users_sample_data.sql
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_nutrition -f sample-data/02_nutrition_sample_data.sql
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_workouts -f sample-data/03_workout_sample_data.sql
```

**Sample data includes:**
- 5 user accounts (password: `Password123!`)
- 17+ food items across 7 categories
- 15+ exercises across 5 categories
- 7 days of meal history for test user
- 5 completed workouts for test user

---

## Running the Application

You have two options to run the application:

### Option 1: Run Microservices Locally (Development Mode)

**Recommended for**: Development, debugging, hot-reloading

Start each service in a separate terminal:

**Terminal 1: Eureka Server**
```bash
cd eureka-server
mvn spring-boot:run
# Wait for: "Started EurekaServerApplication"
# Access: http://localhost:8761
```

**Terminal 2: Config Server**
```bash
cd config-server
mvn spring-boot:run
# Wait for: "Started ConfigServerApplication"
```

**Terminal 3: API Gateway**
```bash
cd api-gateway
mvn spring-boot:run
# Wait for: "Started ApiGatewayApplication"
# Access: http://localhost:8080
```

**Terminal 4: User Service**
```bash
cd user-service
mvn spring-boot:run
# Wait for: "Started UserServiceApplication"
# Access: http://localhost:8081
```

**Terminal 5: Nutrition Service**
```bash
cd nutrition-service
mvn spring-boot:run
# Wait for: "Started NutritionServiceApplication"
# Access: http://localhost:8082
```

**Terminal 6: Workout Service**
```bash
cd workout-service
mvn spring-boot:run
# Wait for: "Started WorkoutServiceApplication"
# Access: http://localhost:8083
```

**Terminal 7: Analytics Service**
```bash
cd analytics-service
mvn spring-boot:run
# Wait for: "Started AnalyticsServiceApplication"
# Access: http://localhost:8084
```

**Startup Time:** Each service takes ~30-60 seconds to start.

### Option 2: Run Everything with Docker (Production Mode)

**Recommended for**: Testing production configuration, demos, simplified setup

```bash
# Build Docker images for all services
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Watch logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop watching logs: Ctrl+C

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

**Startup Time:** 2-3 minutes for all services.

### Verify Services are Running

**Check Eureka Dashboard:**

Open browser: http://localhost:8761

You should see all services registered:
- API-GATEWAY
- USER-SERVICE
- NUTRITION-SERVICE
- WORKOUT-SERVICE
- ANALYTICS-SERVICE

**Check Service Health:**

```bash
# User Service
curl http://localhost:8081/actuator/health

# Nutrition Service
curl http://localhost:8082/actuator/health

# Workout Service
curl http://localhost:8083/actuator/health

# Analytics Service
curl http://localhost:8084/actuator/health
```

All should return: `{"status":"UP"}`

---

## Your First API Calls

Now that everything is running, let's make some API calls!

### 1. Register a New User

```bash
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "password": "SecurePassword123!",
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-15",
    "gender": "MALE",
    "heightCm": 180.0,
    "weightKg": 85.0
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "your.email@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Save the JWT token!** You'll need it for authenticated requests.

### 2. Login (Using Sample User)

```bash
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "Password123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email": "john.doe@example.com",
      "firstName": "John",
      "lastName": "Doe"
    }
  }
}
```

**Copy the token value** and export it as an environment variable:

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Get User Profile

```bash
curl http://localhost:8080/api/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1990-05-15",
    "gender": "MALE",
    "heightCm": 180.0,
    "weightKg": 85.5,
    "profile": {
      "activityLevel": "MODERATELY_ACTIVE",
      "fitnessGoal": "WEIGHT_LOSS",
      "targetWeightKg": 80.0,
      "targetCaloriesPerDay": 2200,
      "targetProteinGrams": 150,
      "targetCarbsGrams": 220,
      "targetFatGrams": 70
    }
  }
}
```

### 4. Browse Food Items

```bash
curl "http://localhost:8080/api/nutrition/food-items?verified=true&page=0&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 1,
        "name": "Chicken Breast",
        "brand": "Generic",
        "category": "Proteins",
        "servingSize": 100,
        "servingUnit": "grams",
        "caloriesPerServing": 165,
        "proteinGrams": 31.0,
        "carbsGrams": 0.0,
        "fatGrams": 3.6,
        "isVerified": true
      }
    ],
    "totalElements": 17,
    "totalPages": 2
  }
}
```

### 5. Log a Meal

```bash
curl -X POST http://localhost:8080/api/nutrition/meals \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": 1,
    "mealType": "BREAKFAST",
    "mealDate": "2024-01-15",
    "mealTime": "08:30:00",
    "notes": "Healthy breakfast",
    "items": [
      {
        "foodItemId": 7,
        "servings": 1.5
      },
      {
        "foodItemId": 11,
        "servings": 1.0
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Meal created successfully",
  "data": {
    "id": 1,
    "userId": 1,
    "mealType": "BREAKFAST",
    "mealDate": "2024-01-15",
    "mealTime": "08:30:00",
    "totalCalories": 314,
    "totalProtein": 8.6,
    "totalCarbs": 63.3,
    "totalFat": 4.8,
    "items": [...]
  }
}
```

### 6. View Today's Analytics

```bash
curl "http://localhost:8080/api/analytics/daily/2024-01-15" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "date": "2024-01-15",
    "totalCaloriesConsumed": 2143,
    "totalCaloriesBurned": 450,
    "netCalories": 1693,
    "totalProteinGrams": 152,
    "totalCarbsGrams": 218,
    "totalFatGrams": 68,
    "workoutDurationMinutes": 75,
    "targetCalories": 2200,
    "calorieProgress": 97.4
  }
}
```

---

## Understanding the Architecture

### Service Ports Reference

| Service | Port | Access URL |
|---------|------|------------|
| Eureka Dashboard | 8761 | http://localhost:8761 |
| API Gateway | 8080 | http://localhost:8080 |
| User Service | 8081 | http://localhost:8081 |
| Nutrition Service | 8082 | http://localhost:8082 |
| Workout Service | 8083 | http://localhost:8083 |
| Analytics Service | 8084 | http://localhost:8084 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Kafka | 9092 | localhost:9092 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |
| Jaeger UI | 16686 | http://localhost:16686 |

### Request Flow

```
User → API Gateway (8080) → Eureka (service discovery) → Microservice
                          ↓
                     JWT Validation
                          ↓
                     Load Balancing
                          ↓
                  Selected Service Instance
```

### Data Flow (Event-Driven)

```
Meal Logged → Nutrition Service → Kafka (MealCreatedEvent) → Analytics Service → Update Daily Summary

Workout Completed → Workout Service → Kafka (WorkoutCompletedEvent) → Analytics Service → Update Daily Summary
```

### Exploring APIs with Swagger

Each service has interactive API documentation:

- **User Service**: http://localhost:8081/swagger-ui.html
- **Nutrition Service**: http://localhost:8082/swagger-ui.html
- **Workout Service**: http://localhost:8083/swagger-ui.html
- **Analytics Service**: http://localhost:8084/swagger-ui.html

**Using Swagger:**
1. Open Swagger UI URL
2. Click "Authorize" button
3. Enter: `Bearer {your-jwt-token}`
4. Click "Authorize"
5. Try out endpoints interactively

---

## Next Steps

Congratulations! You now have FitTracker Pro up and running. Here's what to explore next:

### 1. Try More Features

- **Update your profile** with fitness goals
- **Search for food items** by name
- **Browse the exercise library** by muscle group
- **Create a workout session** and complete it
- **View weekly analytics** and trends

### 2. Explore Monitoring

- **Prometheus**: http://localhost:9090 - Query metrics
- **Grafana**: http://localhost:3000 - View dashboards (admin/admin)
- **Jaeger**: http://localhost:16686 - Trace requests across services

### 3. Understand Event-Driven Architecture

Watch events in real-time:

```bash
# Monitor meal events
docker exec -it fittracker-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic meal-events \
  --from-beginning

# Monitor workout events (new terminal)
docker exec -it fittracker-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic workout-events \
  --from-beginning
```

Then create a meal or complete a workout and watch the events!

### 4. Read Detailed Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep dive into system design
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - For code contributions
- **[OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)** - Running in production
- **[DEMO_SCENARIOS.md](DEMO_SCENARIOS.md)** - 9 testing scenarios

### 5. Run the Demo Scenarios

Follow the comprehensive testing guide:

```bash
# Read the demo guide
cat DEMO_SCENARIOS.md
```

This includes 9 detailed scenarios covering every feature.

---

## Getting Help

### Documentation

- **README.md** - Project overview
- **DEPLOYMENT.md** - Production deployment
- **TROUBLESHOOTING.md** - Common issues and solutions
- **sample-data/README.md** - Sample data information

### Troubleshooting

**Services won't start?**
- Check Docker is running: `docker ps`
- Check ports aren't in use: `lsof -i :8080` (Linux/Mac)
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Build fails?**
- Verify Java 17+: `java -version`
- Clean Maven cache: `mvn clean`
- Check internet connection (Maven downloads dependencies)

**API returns 401 Unauthorized?**
- Check JWT token is valid
- Ensure token is passed in header: `Authorization: Bearer {token}`
- Token expires after 24 hours by default

### Community & Support

- **GitHub Issues**: Report bugs or request features
- **Documentation**: All docs in the project root
- **Sample Data**: Pre-loaded test scenarios available

---

## Quick Reference

### Start Everything (Docker)
```bash
docker-compose up -d                              # Infrastructure
docker-compose -f docker-compose.prod.yml up -d   # All services
```

### Stop Everything
```bash
docker-compose -f docker-compose.prod.yml down    # Services
docker-compose down                               # Infrastructure
```

### Check Logs
```bash
docker-compose logs -f {service-name}
```

### Rebuild After Code Changes
```bash
mvn clean install
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Load Sample Data
```bash
cd sample-data && ./load-all-data.sh
```

### Login and Get Token
```bash
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"Password123!"}'
```

---

**Congratulations!** You're now ready to use FitTracker Pro. Happy tracking! 🎉

For detailed API documentation, see [API_REFERENCE.md](API_REFERENCE.md).
For architectural deep-dive, see [ARCHITECTURE.md](ARCHITECTURE.md).
