# FitTracker Pro - Getting Started Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [First-Time Setup](#first-time-setup)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Common Issues](#common-issues)

## Prerequisites

### Required Software

#### Backend Requirements
- **Java Development Kit (JDK) 17 or higher**
  ```bash
  # Check Java version
  java -version

  # Should show: openjdk version "17.0.x" or higher
  ```
  - Download: https://adoptium.net/
  - Alternative: Oracle JDK, Amazon Corretto

- **Apache Maven 3.8+**
  ```bash
  # Check Maven version
  mvn -version

  # Should show: Apache Maven 3.8.x or higher
  ```
  - Download: https://maven.apache.org/download.cgi

- **PostgreSQL 15+**
  ```bash
  # Check PostgreSQL version
  psql --version

  # Should show: psql (PostgreSQL) 15.x or higher
  ```
  - Download: https://www.postgresql.org/download/

#### Frontend Requirements
- **Node.js 18+ and npm**
  ```bash
  # Check Node version
  node --version

  # Should show: v18.x.x or higher

  # Check npm version
  npm --version

  # Should show: 9.x.x or higher
  ```
  - Download: https://nodejs.org/

#### Optional (for Docker deployment)
- **Docker 20.10+**
  ```bash
  # Check Docker version
  docker --version

  # Should show: Docker version 20.10.x or higher
  ```
  - Download: https://www.docker.com/get-started

- **Docker Compose 2.0+**
  ```bash
  # Check Docker Compose version
  docker-compose --version

  # Should show: Docker Compose version 2.x.x or higher
  ```

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 5 GB free space

**Recommended:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 10 GB free space

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/Projects.git

# Navigate to the project
cd Projects/fittracker-pro-fullstack
```

### Step 2: Database Setup

#### Option A: Local PostgreSQL Installation

1. **Install PostgreSQL** (if not already installed)
   ```bash
   # macOS (using Homebrew)
   brew install postgresql@15
   brew services start postgresql@15

   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   sudo systemctl enable postgresql

   # Windows
   # Download installer from https://www.postgresql.org/download/windows/
   ```

2. **Create Database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres

   # Create databases
   CREATE DATABASE fittracker_user_db;
   CREATE DATABASE fittracker_nutrition_db;
   CREATE DATABASE fittracker_workout_db;
   CREATE DATABASE fittracker_analytics_db;

   # Create user (optional)
   CREATE USER fittracker_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE fittracker_user_db TO fittracker_user;
   GRANT ALL PRIVILEGES ON DATABASE fittracker_nutrition_db TO fittracker_user;
   GRANT ALL PRIVILEGES ON DATABASE fittracker_workout_db TO fittracker_user;
   GRANT ALL PRIVILEGES ON DATABASE fittracker_analytics_db TO fittracker_user;

   # Exit
   \q
   ```

3. **Verify Database Connection**
   ```bash
   psql -U postgres -d fittracker_user_db -c "SELECT version();"
   ```

#### Option B: Docker PostgreSQL

```bash
# Run PostgreSQL in Docker
docker run --name fittracker-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:15-alpine

# Wait a few seconds, then create databases
docker exec -it fittracker-postgres psql -U postgres -c "CREATE DATABASE fittracker_user_db;"
docker exec -it fittracker-postgres psql -U postgres -c "CREATE DATABASE fittracker_nutrition_db;"
docker exec -it fittracker-postgres psql -U postgres -c "CREATE DATABASE fittracker_workout_db;"
docker exec -it fittracker-postgres psql -U postgres -c "CREATE DATABASE fittracker_analytics_db;"
```

### Step 3: Backend Setup

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Install Dependencies**
   ```bash
   # Install all Maven dependencies
   mvn clean install -DskipTests
   ```

3. **Configure Environment Variables**

   Create `.env` file in the backend directory:
   ```bash
   # Database Configuration
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres

   # JWT Configuration
   JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
   JWT_EXPIRATION=86400000

   # Server Configuration
   SERVER_PORT=8080

   # Eureka Server
   EUREKA_SERVER_URL=http://localhost:8761/eureka

   # Redis (optional - for caching)
   REDIS_HOST=localhost
   REDIS_PORT=6379

   # Kafka (optional - for event streaming)
   KAFKA_BOOTSTRAP_SERVERS=localhost:9092
   ```

4. **Update Application Properties** (if not using .env)

   Edit each service's `application.yml`:
   - `user-service/src/main/resources/application.yml`
   - `nutrition-service/src/main/resources/application.yml`
   - `workout-service/src/main/resources/application.yml`
   - `analytics-service/src/main/resources/application.yml`

### Step 4: Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd ../frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment Variables**

   Create `.env.development` file:
   ```bash
   VITE_API_BASE_URL=http://localhost:8080
   ```

   Create `.env.production` file:
   ```bash
   VITE_API_BASE_URL=https://your-production-domain.com
   ```

## Configuration

### Backend Configuration Details

#### 1. Database Configuration

Each microservice has its own database. Update the `application.yml` files:

**user-service/src/main/resources/application.yml:**
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/fittracker_user_db
    username: postgres
    password: postgres
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: update  # Use 'validate' in production
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
```

#### 2. JWT Configuration

**application.yml:**
```yaml
jwt:
  secret: ${JWT_SECRET:your-super-secret-jwt-key-change-this-in-production}
  expiration: ${JWT_EXPIRATION:86400000}  # 24 hours in milliseconds
```

#### 3. CORS Configuration

**application.yml:**
```yaml
cors:
  allowed-origins:
    - http://localhost:5173
    - http://localhost:3000
  allowed-methods:
    - GET
    - POST
    - PUT
    - DELETE
    - OPTIONS
  allowed-headers: "*"
  allow-credentials: true
```

### Frontend Configuration Details

#### Environment Variables

**.env.development:**
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8080

# Optional: Enable debug mode
VITE_DEBUG=true

# Optional: API timeout (milliseconds)
VITE_API_TIMEOUT=15000
```

**.env.production:**
```bash
# API Configuration
VITE_API_BASE_URL=https://api.fittrackerpro.com

# Disable debug in production
VITE_DEBUG=false

# Production timeout
VITE_API_TIMEOUT=30000
```

## Running the Application

### Option 1: Development Mode (Recommended for Development)

#### Start Backend Services

**Terminal 1: Start Eureka Server (Service Discovery)**
```bash
cd backend/eureka-server
mvn spring-boot:run
```
Wait until you see: `Started EurekaServerApplication in X seconds`
Access: http://localhost:8761

**Terminal 2: Start User Service**
```bash
cd backend/user-service
mvn spring-boot:run
```
Access: http://localhost:8081

**Terminal 3: Start Nutrition Service**
```bash
cd backend/nutrition-service
mvn spring-boot:run
```
Access: http://localhost:8082

**Terminal 4: Start Workout Service**
```bash
cd backend/workout-service
mvn spring-boot:run
```
Access: http://localhost:8083

**Terminal 5: Start Analytics Service**
```bash
cd backend/analytics-service
mvn spring-boot:run
```
Access: http://localhost:8084

**Terminal 6: Start API Gateway**
```bash
cd backend/api-gateway
mvn spring-boot:run
```
Access: http://localhost:8080

#### Start Frontend

**Terminal 7: Start React Dev Server**
```bash
cd frontend
npm run dev
```
Access: http://localhost:5173

### Option 2: Using Docker Compose (Recommended for Testing)

1. **Build and Start All Services**
   ```bash
   # From the root directory
   docker-compose up -d

   # Or build first, then start
   docker-compose build
   docker-compose up -d
   ```

2. **Check Service Status**
   ```bash
   # View all running containers
   docker-compose ps

   # View logs
   docker-compose logs -f

   # View specific service logs
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - Eureka Dashboard: http://localhost:8761

4. **Stop Services**
   ```bash
   # Stop all services
   docker-compose down

   # Stop and remove volumes (clears database)
   docker-compose down -v
   ```

### Option 3: Production Build

#### Build Backend
```bash
cd backend
mvn clean package -DskipTests

# JAR files will be in target/ directories
# user-service/target/user-service-0.0.1-SNAPSHOT.jar
# nutrition-service/target/nutrition-service-0.0.1-SNAPSHOT.jar
# etc.
```

#### Build Frontend
```bash
cd frontend
npm run build

# Production files will be in dist/ directory
```

#### Run Production Build
```bash
# Backend (example with user-service)
cd backend/user-service
java -jar target/user-service-0.0.1-SNAPSHOT.jar

# Frontend (serve with nginx or any static file server)
cd frontend
npx serve -s dist -l 3000
```

## First-Time Setup

### 1. Initialize Sample Data

The application will automatically create tables on first run (if `ddl-auto: update` is set).

**Load Sample Food Items:**
```bash
# The nutrition service will load sample food items on startup
# from: nutrition-service/src/main/resources/db/migration/V2__Seed_food_database.sql
```

**Load Sample Exercises:**
```bash
# The workout service will load sample exercises on startup
# from: workout-service/src/main/resources/db/migration/V2__Seed_exercise_library.sql
```

### 2. Create Your First User

**Option A: Using Frontend**
1. Navigate to http://localhost:5173
2. Click "Register"
3. Fill in the registration form
4. Submit

**Option B: Using API (cURL)**
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "fullName": "John Doe",
    "dateOfBirth": "1990-01-01",
    "gender": "MALE",
    "heightCm": 175,
    "currentWeightKg": 75,
    "targetWeightKg": 70,
    "activityLevel": "MODERATELY_ACTIVE",
    "fitnessGoal": "WEIGHT_LOSS"
  }'
```

### 3. Login and Explore

**Login:**
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Response will include a JWT token:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "fullName": "John Doe"
  }
}
```

Save this token for authenticated requests!

## Development Workflow

### Backend Development

1. **Make Changes**
   - Edit Java files in `src/main/java`
   - Modify configurations in `src/main/resources`

2. **Hot Reload (Spring DevTools)**
   ```bash
   # Spring DevTools is included - just save files
   # The application will auto-restart
   ```

3. **Run Tests**
   ```bash
   # Run all tests
   mvn test

   # Run specific test
   mvn test -Dtest=UserServiceTest

   # Run with coverage
   mvn test jacoco:report
   ```

4. **Format Code**
   ```bash
   # Format using Maven
   mvn spotless:apply
   ```

### Frontend Development

1. **Make Changes**
   - Edit files in `src/`
   - Vite provides hot module replacement (HMR)

2. **Check for Errors**
   ```bash
   # Type checking
   npm run type-check

   # Linting
   npm run lint

   # Fix linting issues
   npm run lint:fix
   ```

3. **Build and Preview**
   ```bash
   # Build for production
   npm run build

   # Preview production build
   npm run preview
   ```

## Testing

### Backend Tests

```bash
# Unit tests
cd backend/user-service
mvn test

# Integration tests
mvn verify

# Test coverage report
mvn test jacoco:report
# Report will be in target/site/jacoco/index.html
```

### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Manual Testing

**Health Checks:**
```bash
# Check if services are running
curl http://localhost:8081/actuator/health  # User Service
curl http://localhost:8082/actuator/health  # Nutrition Service
curl http://localhost:8083/actuator/health  # Workout Service
curl http://localhost:8084/actuator/health  # Analytics Service
```

**Test API Endpoints:**
```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}' \
  | jq -r '.token')

# Get user profile
curl http://localhost:8080/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"

# Get meals for today
curl http://localhost:8080/api/meals/date/$(date +%Y-%m-%d) \
  -H "Authorization: Bearer $TOKEN"
```

## Common Issues

### Issue: Port Already in Use

**Error:**
```
Port 8080 is already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or change port in application.yml
server:
  port: 8081
```

### Issue: Database Connection Failed

**Error:**
```
Connection refused: connect
```

**Solution:**
1. Check if PostgreSQL is running:
   ```bash
   # macOS/Linux
   pg_isready

   # Or check service
   sudo systemctl status postgresql
   ```

2. Check connection settings in `application.yml`

3. Verify database exists:
   ```bash
   psql -U postgres -l
   ```

### Issue: Frontend Cannot Connect to Backend

**Error:**
```
Network Error / CORS Error
```

**Solution:**
1. Check if backend is running:
   ```bash
   curl http://localhost:8080/actuator/health
   ```

2. Verify VITE_API_BASE_URL in `.env.development`

3. Check CORS configuration in backend

### Issue: Maven Build Fails

**Error:**
```
Failed to execute goal
```

**Solution:**
```bash
# Clear Maven cache
rm -rf ~/.m2/repository

# Clean and rebuild
mvn clean install -U

# Skip tests if needed
mvn clean install -DskipTests
```

### Issue: Node Modules Issues

**Error:**
```
Module not found
```

**Solution:**
```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Or use fresh install
npm ci
```

## Next Steps

- Read the [Architecture Documentation](./ARCHITECTURE.md) to understand the system design
- Check the [API Documentation](./API_DOCUMENTATION.md) for all available endpoints
- Review the [Deployment Guide](./DEPLOYMENT.md) for production deployment
- See the [User Guide](./USER_GUIDE.md) to learn about application features

## Getting Help

- **Issues:** Create an issue on GitHub
- **Questions:** Check the documentation or create a discussion
- **Contributions:** See CONTRIBUTING.md

---

**Last Updated:** November 2024
**Version:** 1.0.0
