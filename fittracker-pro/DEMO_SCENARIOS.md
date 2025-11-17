# FitTracker Pro - Demo Scenarios

This guide provides step-by-step demo scenarios to showcase the features of FitTracker Pro.

## Prerequisites

1. All services are running (see DEPLOYMENT.md)
2. Sample data has been loaded (see sample-data/README.md)
3. API client (Postman, curl, or use Swagger UI)

## Test Credentials

**Primary Test User:**
- Email: `john.doe@example.com`
- Password: `Password123!`
- Pre-loaded with 7 days of meals and 5 workouts

**Additional Test Users:**
- `jane.smith@example.com` / `Password123!`
- `mike.johnson@example.com` / `Password123!`

## Scenario 1: User Authentication and Profile

### 1.1 User Registration

**POST** `http://localhost:8080/api/users/register`

```json
{
  "email": "demo.user@example.com",
  "password": "SecurePass123!",
  "firstName": "Demo",
  "lastName": "User",
  "dateOfBirth": "1995-01-15",
  "gender": "MALE"
}
```

**Expected Result:** User created successfully with JWT token

### 1.2 User Login

**POST** `http://localhost:8080/api/users/login`

```json
{
  "email": "john.doe@example.com",
  "password": "Password123!"
}
```

**Expected Result:** JWT token returned
**Save the token** for subsequent requests!

### 1.3 Get User Profile

**GET** `http://localhost:8080/api/users/profile`

**Headers:**
```
Authorization: Bearer {your-jwt-token}
```

**Expected Result:** User profile with fitness goals and activity level

### 1.4 Update User Profile

**PUT** `http://localhost:8080/api/users/profile`

```json
{
  "activityLevel": "VERY_ACTIVE",
  "fitnessGoal": "MUSCLE_GAIN",
  "targetWeightKg": 88.0,
  "targetCaloriesPerDay": 3000
}
```

**Expected Result:** Updated profile with new fitness goals

## Scenario 2: Nutrition Tracking

### 2.1 Browse Food Database

**GET** `http://localhost:8080/api/nutrition/food-items?verified=true&page=0&size=20`

**Expected Result:** List of verified food items with nutrition info

### 2.2 Search for Specific Food

**GET** `http://localhost:8080/api/nutrition/food-items/search?query=chicken`

**Expected Result:** Food items matching "chicken"

### 2.3 Log a Meal

**POST** `http://localhost:8080/api/nutrition/meals`

```json
{
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
}
```

**Expected Result:**
- Meal created successfully
- Total calories calculated automatically
- `MealCreatedEvent` published to Kafka
- Analytics service updates daily summary

### 2.4 View Today's Meals

**GET** `http://localhost:8080/api/nutrition/meals/date/2024-01-15`

**Expected Result:** All meals logged for the specified date

### 2.5 View Nutrition Summary

**GET** `http://localhost:8080/api/nutrition/meals/summary?startDate=2024-01-08&endDate=2024-01-15`

**Expected Result:** Aggregated nutrition data for the week

## Scenario 3: Workout Tracking

### 3.1 Browse Exercise Library

**GET** `http://localhost:8080/api/workouts/exercises?verified=true`

**Expected Result:** List of verified exercises with instructions

### 3.2 Search Exercises by Muscle Group

**GET** `http://localhost:8080/api/workouts/exercises/muscle-group/CHEST`

**Expected Result:** Chest exercises (Bench Press, etc.)

### 3.3 Start a Workout Session

**POST** `http://localhost:8080/api/workouts`

```json
{
  "userId": 1,
  "workoutName": "Upper Body Strength",
  "workoutDate": "2024-01-15",
  "startTime": "18:00:00",
  "notes": "Evening workout",
  "exercises": [
    {
      "exerciseId": 1,
      "plannedSets": 4,
      "plannedReps": 10,
      "actualSets": 4,
      "actualReps": 10,
      "weightKg": 80.0
    },
    {
      "exerciseId": 7,
      "plannedSets": 3,
      "plannedReps": 8,
      "actualSets": 3,
      "actualReps": 8,
      "weightKg": 0.0
    }
  ]
}
```

**Expected Result:** Workout created with status IN_PROGRESS

### 3.4 Complete a Workout

**POST** `http://localhost:8080/api/workouts/{workoutId}/complete`

```json
{
  "endTime": "19:15:00"
}
```

**Expected Result:**
- Workout marked as COMPLETED
- Duration calculated automatically
- Total calories burned calculated
- `WorkoutCompletedEvent` published to Kafka
- Analytics service updates daily summary

### 3.5 View Workout History

**GET** `http://localhost:8080/api/workouts/history?startDate=2024-01-08&endDate=2024-01-15`

**Expected Result:** All workouts in the date range

## Scenario 4: Analytics and Insights

### 4.1 View Today's Summary

**GET** `http://localhost:8080/api/analytics/daily/2024-01-15`

**Expected Result:** Daily summary showing:
- Total calories consumed (from meals)
- Total calories burned (from workouts)
- Net calorie balance
- Macronutrient breakdown
- Workout duration

### 4.2 View Weekly Progress

**GET** `http://localhost:8080/api/analytics/weekly?startDate=2024-01-08`

**Expected Result:** Aggregated data for the week

### 4.3 View Monthly Trends

**GET** `http://localhost:8080/api/analytics/range?startDate=2024-01-01&endDate=2024-01-31`

**Expected Result:** Month-long analytics showing trends

### 4.4 View Goal Progress

**GET** `http://localhost:8080/api/analytics/goals/progress`

**Expected Result:**
- Progress towards calorie goals
- Protein/carbs/fat targets
- Workout frequency goals

## Scenario 5: Event-Driven Architecture Demo

This scenario demonstrates the event-driven architecture and real-time updates.

### 5.1 Monitor Kafka Events

In a terminal, monitor Kafka topics:

```bash
# Monitor meal events
docker exec -it fittracker-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic meal-events \
  --from-beginning

# Monitor workout events (in another terminal)
docker exec -it fittracker-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic workout-events \
  --from-beginning
```

### 5.2 Create a Meal and Watch Events

1. Create a meal using Scenario 2.3
2. Observe `MealCreatedEvent` in the meal-events topic
3. Query Analytics API to see updated daily summary
4. Verify event contains correct user ID, calories, macros

### 5.3 Complete a Workout and Watch Events

1. Create and complete a workout using Scenario 3.3-3.4
2. Observe `WorkoutCompletedEvent` in the workout-events topic
3. Query Analytics API to see updated daily summary
4. Verify calories burned is reflected in the summary

## Scenario 6: Caching Performance

### 6.1 Test Cache Warming

**Restart a service** and check logs for cache warming:

```bash
docker-compose restart nutrition-service
docker-compose logs -f nutrition-service | grep "cache warming"
```

**Expected Result:** See cache warming logs on startup

### 6.2 Clear and Refresh Cache

**POST** `http://localhost:8082/cache/clear`

**Expected Result:** Caches cleared successfully

**POST** `http://localhost:8082/cache/warm`

**Expected Result:** Caches reloaded with frequently accessed data

## Scenario 7: Monitoring and Observability

### 7.1 Service Health Checks

**GET** `http://localhost:8081/actuator/health`
**GET** `http://localhost:8082/actuator/health`
**GET** `http://localhost:8083/actuator/health`
**GET** `http://localhost:8084/actuator/health`

**Expected Result:** All services showing UP status

### 7.2 Prometheus Metrics

Visit: `http://localhost:9090`

Sample queries:
- `http_server_requests_seconds_count` - Request counts
- `jvm_memory_used_bytes` - Memory usage
- `hikaricp_connections_active` - Database connections

### 7.3 Grafana Dashboards

Visit: `http://localhost:3000`
- Username: `admin`
- Password: `admin` (or your configured password)

Explore pre-configured dashboards for:
- Service metrics
- Database performance
- JVM statistics

### 7.4 Jaeger Distributed Tracing

Visit: `http://localhost:16686`

1. Select a service (e.g., nutrition-service)
2. Click "Find Traces"
3. Explore request flows across microservices
4. View detailed timing for each operation

## Scenario 8: API Documentation

### 8.1 Explore Swagger UI

Visit:
- User Service: `http://localhost:8081/swagger-ui.html`
- Nutrition Service: `http://localhost:8082/swagger-ui.html`
- Workout Service: `http://localhost:8083/swagger-ui.html`
- Analytics Service: `http://localhost:8084/swagger-ui.html`

### 8.2 Test Endpoints via Swagger

1. Click "Authorize" button
2. Enter JWT token from login
3. Try out endpoints interactively
4. View request/response examples

## Scenario 9: Service Discovery

### 9.1 View Eureka Dashboard

Visit: `http://localhost:8761`

**Expected Result:** All services registered and showing UP status:
- API-GATEWAY
- USER-SERVICE
- NUTRITION-SERVICE
- WORKOUT-SERVICE
- ANALYTICS-SERVICE

### 9.2 Test Service Discovery

**Scale a service:**

```bash
docker-compose up -d --scale nutrition-service=2
```

**Refresh Eureka Dashboard:** See multiple instances registered

**Make API calls:** Load-balanced across instances automatically

## Troubleshooting

### Services Won't Start
- Check Docker logs: `docker-compose logs -f {service-name}`
- Verify Eureka registration: Visit http://localhost:8761
- Check database connections: `docker-compose ps postgres`

### Events Not Processing
- Check Kafka is running: `docker-compose ps kafka`
- Verify topics exist: `docker exec -it fittracker-kafka kafka-topics --list --bootstrap-server localhost:9092`
- Check consumer logs: `docker-compose logs -f analytics-service`

### Cache Issues
- Clear Redis: `docker exec -it fittracker-redis redis-cli FLUSHALL`
- Restart services: `docker-compose restart {service-name}`

## Performance Testing

### Load Test with Sample Data

```bash
# Use Apache Bench or similar tool
ab -n 1000 -c 10 -H "Authorization: Bearer {token}" \
  http://localhost:8080/api/nutrition/food-items
```

**Expected Result:** Sub-100ms response times with caching

## Next Steps

After completing these scenarios, you should understand:
- ✅ User authentication and profile management
- ✅ Meal logging with automatic nutrition calculation
- ✅ Workout tracking with calorie burn estimation
- ✅ Event-driven analytics updates
- ✅ Cache performance optimization
- ✅ Comprehensive monitoring and observability
- ✅ Microservices architecture benefits

Explore the codebase to understand implementation details and extend the functionality!
