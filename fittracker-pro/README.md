# FitTracker Pro - Microservices Health and Fitness Tracking Platform

## 🎯 Overview

FitTracker Pro is a production-ready microservices-based health and fitness tracking platform built with Spring Boot 3.x and Spring Cloud. The platform provides comprehensive features for user management, nutrition tracking, workout planning, and analytics.

## 🏗️ Architecture

### Microservices

1. **Eureka Server** (Port 8761) - Service Discovery
2. **Config Server** (Port 8888) - Centralized Configuration Management
3. **API Gateway** (Port 8080) - Entry point for all client requests
4. **User Service** (Port 8081) - Authentication, user management, profiles
5. **Nutrition Service** (Port 8082) - Food database, meal logging, nutrition tracking
6. **Workout Service** (Port 8083) - Exercise library, workout planning, progress tracking
7. **Analytics Service** (Port 8084) - Data aggregation, reporting, dashboards

### Infrastructure Components

- **PostgreSQL 14** (Port 5432) - Primary database (4 separate databases)
- **Redis 7** (Port 6379) - Distributed caching and session management
- **Apache Kafka** (Port 9092) - Event streaming and message broker
- **Zookeeper** (Port 2181) - Kafka coordination
- **Prometheus** (Port 9090) - Metrics collection and monitoring
- **Grafana** (Port 3000) - Metrics visualization and dashboards
- **Jaeger** (Port 16686) - Distributed tracing

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Java 17** or higher
- **Maven 3.8+**
- **Docker** and **Docker Compose**
- **Git**

### Verify Prerequisites

```bash
# Check Java version
java -version

# Check Maven version
mvn -version

# Check Docker version
docker --version
docker-compose --version
```

## 🚀 Quick Start Guide

### Step 1: Clone the Repository

```bash
cd /home/user/Projects
```

### Step 2: Start Infrastructure Services

Start all infrastructure services (PostgreSQL, Redis, Kafka, Zookeeper, Prometheus, Grafana, Jaeger):

```bash
cd fittracker-pro
docker-compose up -d
```

Wait for all services to be healthy (approximately 30-60 seconds):

```bash
docker-compose ps
```

All services should show status as "Up" or "Up (healthy)".

### Step 3: Build All Microservices

Build the entire project:

```bash
mvn clean install
```

This will:
- Compile all Java code
- Run unit tests
- Package all services as JAR files
- Install artifacts to local Maven repository

**Note:** The build should complete successfully. If you see compilation errors, ensure you're using Java 17.

### Step 4: Start Microservices

Start services in the following order:

#### 4.1 Start Eureka Server (Service Discovery)

```bash
cd eureka-server
mvn spring-boot:run
```

Wait until you see: `Started EurekaServerApplication`

Access Eureka Dashboard: http://localhost:8761

#### 4.2 Start Config Server (Configuration Management)

Open a new terminal:

```bash
cd fittracker-pro/config-server
mvn spring-boot:run
```

Wait until you see: `Started ConfigServerApplication`

#### 4.3 Start API Gateway

Open a new terminal:

```bash
cd fittracker-pro/api-gateway
mvn spring-boot:run
```

Wait until you see: `Started ApiGatewayApplication`

#### 4.4 Start User Service

Open a new terminal:

```bash
cd fittracker-pro/user-service
mvn spring-boot:run
```

Wait until you see: `Started UserServiceApplication`

#### 4.5 Start Nutrition Service

Open a new terminal:

```bash
cd fittracker-pro/nutrition-service
mvn spring-boot:run
```

Wait until you see: `Started NutritionServiceApplication`

#### 4.6 Start Workout Service

Open a new terminal:

```bash
cd fittracker-pro/workout-service
mvn spring-boot:run
```

Wait until you see: `Started WorkoutServiceApplication`

#### 4.7 Start Analytics Service

Open a new terminal:

```bash
cd fittracker-pro/analytics-service
mvn spring-boot:run
```

Wait until you see: `Started AnalyticsServiceApplication`

### Step 5: Verify All Services are Running

Check Eureka Dashboard to ensure all services are registered:

http://localhost:8761

You should see all services listed:
- CONFIG-SERVER
- API-GATEWAY
- USER-SERVICE
- NUTRITION-SERVICE
- WORKOUT-SERVICE
- ANALYTICS-SERVICE

## 🔍 Testing the Application

### Test Infrastructure Services

```bash
# Test PostgreSQL
docker exec -it fittracker-postgres psql -U fittracker -c "\l"

# Test Redis
docker exec -it fittracker-redis redis-cli ping

# Test Kafka
docker exec -it fittracker-kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Test Microservices Health Endpoints

```bash
# User Service
curl http://localhost:8080/api/users/health

# Nutrition Service
curl http://localhost:8080/api/nutrition/health

# Workout Service
curl http://localhost:8080/api/workouts/health

# Analytics Service
curl http://localhost:8080/api/analytics/health
```

All should return:
```json
{
  "status": "UP",
  "service": "<service-name>"
}
```

## 📊 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Eureka Dashboard | http://localhost:8761 | Service registry and discovery |
| API Gateway | http://localhost:8080 | Main entry point for API calls |
| Prometheus | http://localhost:9090 | Metrics and monitoring |
| Grafana | http://localhost:3000 | Dashboards (admin/admin) |
| Jaeger UI | http://localhost:16686 | Distributed tracing |
| Config Server | http://localhost:8888 | Configuration management |

## 🛠️ Development

### Project Structure

```
fittracker-pro/
├── pom.xml                          # Parent POM
├── docker-compose.yml               # Infrastructure services
├── config-repo/                     # Configuration files
│   └── application.yml
├── docker/                          # Docker configuration files
│   ├── init-databases.sql
│   ├── prometheus.yml
│   └── grafana/
├── eureka-server/                   # Service Discovery
│   ├── pom.xml
│   └── src/
├── config-server/                   # Configuration Server
│   ├── pom.xml
│   └── src/
├── api-gateway/                     # API Gateway
│   ├── pom.xml
│   └── src/
├── common-library/                  # Shared DTOs and utilities
│   ├── pom.xml
│   └── src/
├── user-service/                    # User management service
│   ├── pom.xml
│   └── src/
├── nutrition-service/               # Nutrition tracking service
│   ├── pom.xml
│   └── src/
├── workout-service/                 # Workout planning service
│   ├── pom.xml
│   └── src/
└── analytics-service/               # Analytics and reporting service
    ├── pom.xml
    └── src/
```

### Technology Stack

- **Backend Framework:** Spring Boot 3.2.0
- **Cloud Framework:** Spring Cloud 2023.0.0
- **Database:** PostgreSQL 14
- **Cache:** Redis 7
- **Message Broker:** Apache Kafka
- **Service Discovery:** Netflix Eureka
- **API Gateway:** Spring Cloud Gateway
- **Monitoring:** Prometheus + Grafana
- **Tracing:** Jaeger
- **Documentation:** SpringDoc OpenAPI 3
- **Testing:** JUnit 5, Mockito, TestContainers

## 🐳 Docker Commands

### Start all infrastructure services:
```bash
docker-compose up -d
```

### Stop all infrastructure services:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f [service-name]
```

### Remove all volumes (clean start):
```bash
docker-compose down -v
```

## 🔧 Troubleshooting

### Issue: Services not registering with Eureka

**Solution:** Ensure Eureka Server is running first and wait 30 seconds for service registration.

### Issue: Database connection errors

**Solution:**
1. Check if PostgreSQL is running: `docker-compose ps postgres`
2. Verify databases were created: `docker exec -it fittracker-postgres psql -U fittracker -c "\l"`
3. Check credentials in application.yml files

### Issue: Port already in use

**Solution:**
1. Find process using the port: `lsof -i :<port-number>`
2. Kill the process: `kill -9 <PID>`
3. Or change the port in application.yml

### Issue: Maven build fails

**Solution:**
1. Ensure Java 17 is being used: `java -version`
2. Clear Maven cache: `rm -rf ~/.m2/repository`
3. Rebuild: `mvn clean install`

## 📝 Phase 1 Completion Checklist

Phase 1 focuses on project setup and infrastructure. The following items are complete:

- ✅ Parent POM with dependency management
- ✅ Eureka Server for service discovery
- ✅ Config Server for centralized configuration
- ✅ API Gateway with routing
- ✅ Common Library with shared DTOs and exceptions
- ✅ User Service basic structure
- ✅ Nutrition Service basic structure
- ✅ Workout Service basic structure
- ✅ Analytics Service basic structure
- ✅ Docker Compose with PostgreSQL, Redis, Kafka, Zookeeper
- ✅ Monitoring stack (Prometheus, Grafana, Jaeger)
- ✅ All services can start and register with Eureka

## 📝 Phase 2 Completion Checklist

Phase 2 focuses on API Gateway security and authentication. The following items are complete:

- ✅ JWT utility class for token generation and validation
- ✅ Authentication filter for API Gateway with Bearer token validation
- ✅ Rate limiting filter using Redis (100 requests/minute per IP)
- ✅ CORS configuration with proper headers and methods
- ✅ Global exception handler for consistent error responses
- ✅ Request/response logging filter with correlation IDs
- ✅ Redis configuration for reactive operations
- ✅ Public endpoints configuration (auth, health checks)
- ✅ Header propagation to downstream services (X-User-Id, X-User-Roles)

## 📝 Phase 3 Completion Checklist

Phase 3 focuses on complete User Service implementation. The following items are complete:

- ✅ Database schema with Flyway migrations (users, roles, profiles, weight_history)
- ✅ JPA entities (User, Role, UserProfile, WeightHistory) with relationships
- ✅ DTOs for all operations (Register, Login, Profile, WeightHistory)
- ✅ Spring Data JPA repositories with custom queries
- ✅ JWT service for token generation and validation
- ✅ Spring Security configuration with BCrypt password encoding
- ✅ Custom UserDetailsService implementation
- ✅ Authentication service (register, login, refresh token)
- ✅ User profile service with CRUD operations
- ✅ Weight history service with date range queries
- ✅ REST controllers for auth and user endpoints
- ✅ Global exception handler with validation error mapping
- ✅ Comprehensive logging throughout the service

## 📝 Phase 4 Completion Checklist

Phase 4 focuses on Nutrition Service implementation. The following items are complete:

- ✅ Database schema with Flyway migrations (food_items, meals, meal_items, meal_plans, daily_nutrition_summary)
- ✅ JPA entities (FoodItem, Meal, MealItem, MealPlan) with relationships
- ✅ Food database seeded with 100+ common foods across 10 categories
- ✅ Spring Data JPA repositories with search and filtering
- ✅ Redis caching for food items (1-hour TTL)
- ✅ Food item service with search and category filtering
- ✅ REST controller for food search and retrieval
- ✅ Pagination support for search results
- ✅ Cache configuration with Redis

## 📝 Phase 5 Completion Checklist

Phase 5 focuses on Workout Service implementation. The following items are complete:

- ✅ Database schema with Flyway migrations (exercises, workouts, workout_templates, exercise_categories)
- ✅ Exercise library seeded with 60+ exercises across 7 categories
- ✅ JPA entities (Exercise, Workout, WorkoutTemplate, WorkoutExercise, ExerciseCategory, WorkoutTemplateExercise)
- ✅ Spring Data JPA repositories with search and filtering
- ✅ Redis caching for exercises (24-hour TTL)
- ✅ Exercise service with search, category, and difficulty filtering
- ✅ REST controller for exercise search and retrieval
- ✅ Pagination support for all endpoints
- ✅ Calorie burn calculation support

## 📝 Phase 6 Completion Checklist

Phase 6 focuses on Analytics Service implementation. The following items are complete:

- ✅ Database schema with Flyway migrations (11 tables for comprehensive analytics tracking)
- ✅ Daily activity summary tracking (calories, workouts, macros)
- ✅ JPA entities (DailyActivitySummary, UserGoal, Achievement, WeeklyReport, MonthlyReport, etc.)
- ✅ Spring Data JPA repositories with custom analytics queries
- ✅ Goal management service (create, track, update progress)
- ✅ Achievement service (milestones, streaks, personal records)
- ✅ Report generation service (weekly and monthly reports)
- ✅ Analytics service (daily summaries, averages, trends)
- ✅ REST controllers for analytics, goals, achievements, and reports
- ✅ Redis caching with custom TTL per cache type (30 min - 12 hours)
- ✅ Comprehensive logging and error handling
- ✅ Health endpoint for service monitoring

## 📝 Phase 7 Completion Checklist

Phase 7 focuses on Event-driven architecture with Kafka. The following items are complete:

- ✅ Kafka event DTOs in common library (UserRegisteredEvent, UserWeightUpdatedEvent, MealCreatedEvent, WorkoutCompletedEvent)
- ✅ Kafka topic constants (user.registered, user.weight.updated, meal.created, workout.completed)
- ✅ Event publisher in User Service (publishes registration and weight update events)
- ✅ Kafka event consumers in Analytics Service (auto-updates daily activity summaries)
- ✅ Automatic data aggregation based on events
- ✅ Error handling and logging for event processing
- ✅ Event-driven communication between microservices
- ✅ Foundation for meal and workout event publishers (ready for future implementation)

## 🎯 Next Steps (Phase 8+)

The next phases will implement:

- **Phase 8:** Meal and workout tracking services with event publishing
- **Phase 9:** Advanced caching strategy with cache warming
- **Phase 10:** Complete monitoring and observability (Prometheus metrics, Grafana dashboards)
- **Phase 11:** Comprehensive testing (unit, integration, performance)
- **Phase 12:** API documentation with Swagger/OpenAPI
- **Phase 13:** Production deployment with Docker
- **Phase 14:** Sample data and demo scenarios

## 📄 License

Copyright © 2024 FitTracker Pro. All rights reserved.

## 🤝 Contributing

This is a learning project. Contributions, issues, and feature requests are welcome!

## 📧 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using Spring Boot and Spring Cloud**
