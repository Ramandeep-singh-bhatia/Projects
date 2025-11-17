# Pull Request: FitTracker Pro - Phase 8: Meal and Workout Tracking with Event Publishing

## Summary

This PR implements complete meal tracking in the Nutrition Service and workout session tracking in the Workout Service, with full Kafka event publishing integration. The implementation enables real-time analytics updates through event-driven architecture, creating a seamless data flow from user activities to automated analytics aggregation.

## Changes Made

### Nutrition Service - Meal Tracking

**Enhanced Repository**:
- Updated `MealRepository` with custom queries:
  - `findByUserIdOrderByMealDateDescMealTimeDesc()` - All user meals sorted
  - `findRecentMeals(userId, startDate)` - Recent meals query
  - `getTotalCaloriesForDate(userId, date)` - Aggregate calories calculation
  - Existing methods retained for backward compatibility

**DTOs (2 new classes)**:

1. **CreateMealRequest**:
   - User ID validation
   - Meal type enum (BREAKFAST, LUNCH, DINNER, SNACK)
   - Meal date and optional meal time
   - List of MealItemRequest (validated)
   - Optional notes (max 500 characters)
   - Jakarta Validation annotations

2. **MealItemRequest**:
   - Food item ID (must exist in database)
   - Servings (minimum 0.1)
   - Validation ensures positive values

**Service Layer**:

**MealService** - Complete meal management:
- `createMeal(CreateMealRequest)`:
  - Validates all food items exist
  - Creates meal with items
  - Calculates calories/macros per item (base nutrition × servings)
  - Automatically recalculates meal totals
  - Saves to database
  - Publishes MealCreatedEvent to Kafka
  - Returns saved meal entity
- `getMealById(Long)` - Retrieve with exception handling
- `getUserMeals(Long)` - All meals for user, sorted by date/time desc
- `getMealsForDate(Long, LocalDate)` - Meals for specific date
- `getMealsInRange(Long, LocalDate, LocalDate)` - Date range query
- `getRecentMeals(Long, int)` - Last N days
- `deleteMeal(Long)` - Delete with validation
- `getTotalCaloriesForDate(Long, LocalDate)` - Aggregate calculation

All service methods:
- Transactional (@Transactional or readOnly)
- Comprehensive logging
- Custom exception handling

**Controller Layer**:

**MealController** - RESTful API endpoints:
- `POST /api/nutrition/meals` - Create meal (201 CREATED)
- `GET /api/nutrition/meals/{mealId}` - Get meal details
- `GET /api/nutrition/meals/user/{userId}` - All user meals
- `GET /api/nutrition/meals/user/{userId}/date/{date}` - Meals for date
- `GET /api/nutrition/meals/user/{userId}/range?startDate=X&endDate=Y` - Range
- `GET /api/nutrition/meals/user/{userId}/recent?days=7` - Recent (default 7 days)
- `GET /api/nutrition/meals/user/{userId}/calories/{date}` - Total calories
- `DELETE /api/nutrition/meals/{mealId}` - Delete meal

All endpoints:
- Use ApiResponse wrapper
- Proper HTTP status codes
- @DateTimeFormat for date parameters
- Comprehensive logging
- Validation with @Valid

**Kafka Integration**:

**EventPublisher**:
```java
public void publishMealCreatedEvent(MealCreatedEvent event) {
    kafkaTemplate.send(KafkaTopics.MEAL_CREATED, userId.toString(), event);
}
```
- User ID as partition key (ordering guarantee)
- Try-catch prevents failures from breaking main flow
- Comprehensive logging (info, debug, error)

**MealService Integration**:
- Creates event after successful meal save
- Event includes:
  - Meal ID, user ID, meal type, meal date
  - Total calories (as integer)
  - Total macros: protein, carbs, fat (BigDecimal)
  - Event ID and timestamp
- Analytics Service consumes event automatically

### Workout Service - Session Tracking

**DTOs (3 new classes)**:

1. **CreateWorkoutRequest**:
   - User ID, workout name (required, max 255 chars)
   - Workout date and start time
   - List of WorkoutExerciseRequest (min 1 exercise)
   - Optional notes (max 500 chars)
   - Full Jakarta Validation

2. **WorkoutExerciseRequest**:
   - Exercise ID (must exist)
   - Planned sets/reps/duration
   - Actual sets/reps/duration
   - Weight in kg (BigDecimal)
   - Optional notes
   - Min value validation (1 for sets/reps)

3. **CompleteWorkoutRequest**:
   - End time (required)
   - Used to finalize workout session

**Service Layer**:

**WorkoutService** - Complete workout session management:
- `createWorkout(CreateWorkoutRequest)`:
  - Validates all exercises exist
  - Creates workout with IN_PROGRESS status
  - Adds exercises in specified order
  - Calculates calories for each exercise:
    - Uses exercise.caloriesPerMinute × (actualDurationSeconds / 60)
    - Stores in WorkoutExercise.caloriesBurned
  - Saves to database
  - Returns workout entity (event sent on completion, not creation)

- `completeWorkout(Long, CompleteWorkoutRequest)`:
  - Validates workout exists
  - Checks not already completed
  - Sets end time and COMPLETED status
  - Calculates total duration (Duration.between)
  - Sums total calories from all exercises
  - Saves updated workout
  - Publishes WorkoutCompletedEvent to Kafka
  - Returns completed workout

- `getWorkoutById(Long)` - Retrieve with exception handling
- `getUserWorkouts(Long)` - All workouts sorted by date desc
- `getWorkoutsForDate(Long, LocalDate)` - Workouts for specific date
- `getWorkoutsInRange(Long, LocalDate, LocalDate)` - Date range
- `deleteWorkout(Long)` - Delete with validation
- `determineWorkoutType(Workout)` - Helper to categorize workout

**Controller Layer**:

**WorkoutController** - Enhanced with session endpoints:

New endpoints:
- `POST /api/workouts` - Create workout (201 CREATED)
- `POST /api/workouts/{workoutId}/complete` - Complete workout
- `GET /api/workouts/{workoutId}` - Get workout details
- `GET /api/workouts/user/{userId}` - All user workouts
- `GET /api/workouts/user/{userId}/date/{date}` - Workouts for date
- `GET /api/workouts/user/{userId}/range?startDate=X&endDate=Y` - Range
- `DELETE /api/workouts/{workoutId}` - Delete workout

Existing exercise endpoints retained:
- GET /api/workouts/exercises/search
- GET /api/workouts/exercises/{id}
- GET /api/workouts/exercises/category/{categoryId}
- GET /api/workouts/exercises/difficulty/{difficulty}

**Kafka Integration**:

**EventPublisher**:
```java
public void publishWorkoutCompletedEvent(WorkoutCompletedEvent event) {
    kafkaTemplate.send(KafkaTopics.WORKOUT_COMPLETED, userId.toString(), event);
}
```
- Published only when workout is completed
- User ID as partition key
- Error handling prevents main flow breakage

**WorkoutService Integration**:
- Creates event in completeWorkout() method
- Event includes:
  - Workout ID, user ID, workout date
  - Duration in minutes, calories burned
  - Workout type (determined from exercises)
  - Exercise count
  - Event ID and timestamp
- Analytics Service consumes event automatically

### Analytics Service - Event Consumption

**Existing EventConsumer** now fully utilized:

**handleMealCreatedEvent()**:
```java
analyticsService.updateMealData(
    userId, mealDate,
    totalCalories,
    totalProteinG.doubleValue(),
    totalCarbsG.doubleValue(),
    totalFatG.doubleValue()
);
```
- Updates DailyActivitySummary for the meal date
- Adds calories and macros to daily totals
- Increments meals logged count
- Recalculates net calories

**handleWorkoutCompletedEvent()**:
```java
analyticsService.updateWorkoutData(
    userId, workoutDate,
    caloriesBurned,
    durationMinutes
);
```
- Updates DailyActivitySummary for the workout date
- Adds calories burned to daily total
- Adds duration to total workout minutes
- Increments workouts completed count
- Recalculates net calories

## Complete Event Flow

### Meal Logging Flow:
```
1. User → POST /api/nutrition/meals
2. MealController validates request
3. MealService creates meal
4. Calculate nutrition (calories/macros × servings)
5. Save Meal + MealItems to PostgreSQL
6. Publish MealCreatedEvent → Kafka (meal.created topic)
7. Return 201 with meal data to user

   [Async in Kafka]
8. Analytics Service EventConsumer receives event
9. Update DailyActivitySummary (or create if not exists)
10. Add to totalCaloriesConsumed, totalProtein/Carbs/Fat
11. Increment mealsLogged count
12. Calculate netCalories = consumed - burned
13. Save to analytics database
```

### Workout Completion Flow:
```
1. User → POST /api/workouts (create, status=IN_PROGRESS)
2. User performs workout...
3. User → POST /api/workouts/{id}/complete
4. WorkoutController validates request
5. WorkoutService completes workout
6. Calculate total duration (end - start)
7. Calculate total calories (sum from exercises)
8. Set status=COMPLETED
9. Save Workout to PostgreSQL
10. Publish WorkoutCompletedEvent → Kafka (workout.completed topic)
11. Return 200 with workout data to user

   [Async in Kafka]
12. Analytics Service EventConsumer receives event
13. Update DailyActivitySummary (or create if not exists)
14. Add to totalCaloriesBurned, totalWorkoutDurationMinutes
15. Increment workoutsCompleted count
16. Calculate netCalories = consumed - burned
17. Save to analytics database
```

## Key Features

### Meal Tracking:
- ✅ Create meals with multiple food items
- ✅ Automatic nutrition calculation per item
- ✅ Automatic meal totals aggregation
- ✅ Query by date, date range, recent days
- ✅ Total calories calculation for any date
- ✅ Meal type categorization (4 types)
- ✅ Real-time analytics via Kafka events

### Workout Session Tracking:
- ✅ Create workout sessions with multiple exercises
- ✅ Track planned vs actual performance
- ✅ Weight tracking per exercise
- ✅ Automatic calorie burn calculation
- ✅ Duration tracking (start to completion)
- ✅ Workout status lifecycle (IN_PROGRESS → COMPLETED)
- ✅ Exercise ordering
- ✅ Real-time analytics via Kafka events

### Real-time Analytics:
- ✅ Automatic daily summary updates
- ✅ No manual aggregation needed
- ✅ Real-time calorie tracking (in vs out)
- ✅ Net calories calculation
- ✅ Activity counts (meals, workouts)
- ✅ Duration tracking (active time)
- ✅ Event-driven architecture

## Technical Implementation

### Data Consistency:
- All database operations wrapped in @Transactional
- Meal totals automatically recalculated on changes
- Workout totals calculated at completion
- Event publishing outside transaction scope

### Validation:
- Jakarta Validation on all request DTOs
- Food item existence validated before meal creation
- Exercise existence validated before workout creation
- Workout completion validates not already completed
- Min/max constraints on all numeric inputs

### Error Handling:
- ResourceNotFoundException for missing entities
- BadRequestException for invalid operations
- Event publishing failures logged but don't break flow
- Comprehensive error messages

### Performance Optimization:
- Read-only transactions for query methods
- Eager fetching only for small datasets (FoodItem, Exercise)
- Lazy fetching for large collections
- Indexed queries on user_id and dates
- Event publishing is async (non-blocking)

## API Examples

### Create Meal:
```bash
POST /api/nutrition/meals
{
  "userId": 1,
  "mealType": "BREAKFAST",
  "mealDate": "2024-01-15",
  "mealTime": "08:30:00",
  "items": [
    {"foodItemId": 5, "servings": 2.0},
    {"foodItemId": 12, "servings": 1.5}
  ],
  "notes": "Pre-workout meal"
}
```

Response:
```json
{
  "success": true,
  "message": "Meal created successfully",
  "data": {
    "id": 123,
    "userId": 1,
    "mealType": "BREAKFAST",
    "totalCalories": 450.5,
    "totalProteinG": 25.3,
    ...
  }
}
```

### Create and Complete Workout:
```bash
# 1. Create workout
POST /api/workouts
{
  "userId": 1,
  "workoutName": "Morning Strength Training",
  "workoutDate": "2024-01-15",
  "startTime": "2024-01-15T07:00:00",
  "exercises": [
    {
      "exerciseId": 3,
      "plannedSets": 3,
      "plannedReps": 10,
      "actualSets": 3,
      "actualReps": 10,
      "actualDurationSeconds": 300,
      "weightKg": 50.0
    }
  ]
}

# 2. Complete workout
POST /api/workouts/123/complete
{
  "endTime": "2024-01-15T08:00:00"
}
```

### Query Recent Meals:
```bash
GET /api/nutrition/meals/user/1/recent?days=7
```

### Query Workouts for Date Range:
```bash
GET /api/workouts/user/1/range?startDate=2024-01-01&endDate=2024-01-31
```

## Files Created (11 files)

**Nutrition Service**:
1. `nutrition-service/.../dto/CreateMealRequest.java`
2. `nutrition-service/.../dto/MealItemRequest.java`
3. `nutrition-service/.../service/MealService.java`
4. `nutrition-service/.../controller/MealController.java`
5. `nutrition-service/.../kafka/EventPublisher.java`

**Workout Service**:
6. `workout-service/.../dto/CreateWorkoutRequest.java`
7. `workout-service/.../dto/WorkoutExerciseRequest.java`
8. `workout-service/.../dto/CompleteWorkoutRequest.java`
9. `workout-service/.../service/WorkoutService.java`
10. `workout-service/.../kafka/EventPublisher.java`

**Documentation**:
11. `PR_PHASE_8_DESCRIPTION.md`

## Files Modified (3 files)

1. `nutrition-service/.../repository/MealRepository.java` - Added custom queries
2. `workout-service/.../controller/WorkoutController.java` - Added workout session endpoints
3. `README.md` - Added Phase 8 completion checklist

## Testing Performed

- All services compile successfully
- Meal creation with multiple items works
- Nutrition totals calculated correctly
- Workout creation and completion works
- Calorie burn calculated correctly
- Events published to Kafka successfully
- Analytics Service consumes events
- Daily summaries updated automatically
- All REST endpoints return correct responses
- Validation works as expected

## Verification Steps

1. Start all infrastructure: `docker-compose up -d`
2. Start all services (Eureka, Config, Gateway, User, Nutrition, Workout, Analytics)
3. Register user and login
4. Create meal: `POST /api/nutrition/meals`
5. Check Analytics: Meal count and calories should be in daily summary
6. Create workout: `POST /api/workouts`
7. Complete workout: `POST /api/workouts/{id}/complete`
8. Check Analytics: Workout count and calories burned in daily summary
9. Verify net calories = consumed - burned

## Dependencies

All dependencies already configured:
- Spring Boot Starter Data JPA
- Spring Boot Starter Web
- Spring Boot Starter Validation
- Spring Kafka
- PostgreSQL Driver
- Lombok

## Next Steps (Phase 9)

The next phase will implement:
- Advanced caching strategies
- Cache warming on application startup
- Multi-level caching (Caffeine + Redis)
- Cache invalidation strategies
- Cache metrics and monitoring

---

**Phase 8 Complete**: Full meal and workout tracking with real-time event-driven analytics is production-ready.
