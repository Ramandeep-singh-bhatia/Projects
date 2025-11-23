# FitTracker Pro - API Reference

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [User Service APIs](#user-service-apis)
4. [Nutrition Service APIs](#nutrition-service-apis)
5. [Workout Service APIs](#workout-service-apis)
6. [Analytics Service APIs](#analytics-service-apis)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Pagination](#pagination)
10. [API Versioning](#api-versioning)

---

## Introduction

FitTracker Pro provides a comprehensive REST API for all health and fitness tracking functionality. All APIs are accessed through the **API Gateway** at `http://localhost:8080`.

### Base URL

```
Development: http://localhost:8080
Production: https://api.fittrackerpro.com
```

### API Style

- **REST**: Resource-oriented URLs
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Request Format**: JSON
- **Response Format**: JSON (wrapped in ApiResponse)
- **Authentication**: JWT Bearer Token

### Common Headers

```http
Content-Type: application/json
Authorization: Bearer {jwt-token}
Accept: application/json
```

### Response Wrapper

All responses are wrapped in a standard `ApiResponse` object:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": 1,
    "email": "user@example.com"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Invalid credentials",
  "data": null,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Authentication

### Register New User

Create a new user account.

**Endpoint:** `POST /api/users/register`
**Authentication:** Not required
**Rate Limit:** 5 requests per hour per IP

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "firstName": "John",
  "lastName": "Doe",
  "dateOfBirth": "1990-05-15",
  "gender": "MALE",
  "heightCm": 180.0,
  "weightKg": 85.5
}
```

**Validations:**
- `email`: Valid email format, unique
- `password`: Minimum 8 characters, at least one uppercase, one lowercase, one number, one special character
- `firstName`, `lastName`: 2-100 characters
- `dateOfBirth`: Must be at least 13 years old
- `gender`: MALE, FEMALE, or OTHER
- `heightCm`: 50-300 cm
- `weightKg`: 20-500 kg

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "dateOfBirth": "1990-05-15",
    "gender": "MALE",
    "heightCm": 180.0,
    "weightKg": 85.5,
    "createdAt": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `400 Bad Request`: Validation error
- `409 Conflict`: Email already exists

---

### Login

Authenticate and receive JWT token.

**Endpoint:** `POST /api/users/login`
**Authentication:** Not required
**Rate Limit:** 10 requests per minute per IP

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
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
    },
    "expiresIn": 86400
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

**Token Expiration:**
- Default: 24 hours (86400 seconds)
- After expiration, request new token via `/login`

---

## User Service APIs

Base Path: `/api/users`

### Get Current User Profile

Retrieve the authenticated user's profile.

**Endpoint:** `GET /api/users/profile`
**Authentication:** Required
**Rate Limit:** 100 requests per minute

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
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
    },
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `404 Not Found`: User not found

---

### Update User Profile

Update the authenticated user's profile settings.

**Endpoint:** `PUT /api/users/profile`
**Authentication:** Required

**Request Body:**
```json
{
  "activityLevel": "VERY_ACTIVE",
  "fitnessGoal": "MUSCLE_GAIN",
  "targetWeightKg": 88.0,
  "targetCaloriesPerDay": 3000,
  "targetProteinGrams": 200,
  "targetCarbsGrams": 350,
  "targetFatGrams": 90
}
```

**Field Definitions:**

**activityLevel** (enum):
- `SEDENTARY`: Little or no exercise
- `LIGHTLY_ACTIVE`: Light exercise 1-3 days/week
- `MODERATELY_ACTIVE`: Moderate exercise 3-5 days/week
- `VERY_ACTIVE`: Hard exercise 6-7 days/week
- `EXTRA_ACTIVE`: Very hard exercise, physical job

**fitnessGoal** (enum):
- `WEIGHT_LOSS`: Lose weight
- `WEIGHT_GAIN`: Gain weight
- `MUSCLE_GAIN`: Build muscle
- `MAINTENANCE`: Maintain current weight

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "activityLevel": "VERY_ACTIVE",
    "fitnessGoal": "MUSCLE_GAIN",
    "targetWeightKg": 88.0,
    "targetCaloriesPerDay": 3000,
    "targetProteinGrams": 200,
    "targetCarbsGrams": 350,
    "targetFatGrams": 90,
    "updatedAt": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Update User Weight

Update user's current weight (for progress tracking).

**Endpoint:** `PUT /api/users/weight`
**Authentication:** Required

**Request Body:**
```json
{
  "weightKg": 83.5
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Weight updated successfully",
  "data": {
    "weightKg": 83.5,
    "previousWeight": 85.5,
    "changeKg": -2.0,
    "updatedAt": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Change Password

Change the authenticated user's password.

**Endpoint:** `PUT /api/users/password`
**Authentication:** Required

**Request Body:**
```json
{
  "currentPassword": "OldPassword123!",
  "newPassword": "NewSecurePassword456!"
}
```

**Validations:**
- Current password must be correct
- New password: 8+ characters, uppercase, lowercase, number, special char
- New password must be different from current password

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": null,
  "timestamp": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `400 Bad Request`: Current password incorrect
- `400 Bad Request`: New password doesn't meet requirements

---

## Nutrition Service APIs

Base Path: `/api/nutrition`

### List Food Items

Browse the food database with filtering and pagination.

**Endpoint:** `GET /api/nutrition/food-items`
**Authentication:** Required
**Rate Limit:** 100 requests per minute

**Query Parameters:**
- `category` (optional): Filter by category ID
- `verified` (optional): true/false - Show only verified items
- `page` (optional): Page number (0-indexed, default: 0)
- `size` (optional): Page size (default: 20, max: 100)
- `sort` (optional): Sort field (name, calories, protein, etc.)
- `direction` (optional): asc/desc (default: asc)

**Example Request:**
```
GET /api/nutrition/food-items?verified=true&page=0&size=10&sort=name&direction=asc
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Food items retrieved successfully",
  "data": {
    "content": [
      {
        "id": 1,
        "name": "Chicken Breast",
        "brand": "Generic",
        "category": {
          "id": 1,
          "name": "Proteins"
        },
        "servingSize": 100,
        "servingUnit": "grams",
        "caloriesPerServing": 165,
        "proteinGrams": 31.0,
        "carbsGrams": 0.0,
        "fatGrams": 3.6,
        "fiberGrams": 0.0,
        "sugarGrams": 0.0,
        "sodiumMg": 74,
        "isVerified": true,
        "barcode": null
      }
    ],
    "page": 0,
    "size": 10,
    "totalElements": 17,
    "totalPages": 2,
    "isFirst": true,
    "isLast": false
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Search Food Items

Search for food items by name.

**Endpoint:** `GET /api/nutrition/food-items/search`
**Authentication:** Required

**Query Parameters:**
- `query` (required): Search term (minimum 2 characters)
- `verified` (optional): true/false
- `page`, `size`: Pagination parameters

**Example Request:**
```
GET /api/nutrition/food-items/search?query=chicken&verified=true
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Search results",
  "data": {
    "content": [
      {
        "id": 1,
        "name": "Chicken Breast",
        "brand": "Generic",
        "caloriesPerServing": 165,
        "proteinGrams": 31.0,
        "isVerified": true
      }
    ],
    "totalElements": 1
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Get Food Item Details

Get detailed information about a specific food item.

**Endpoint:** `GET /api/nutrition/food-items/{id}`
**Authentication:** Required

**Path Parameters:**
- `id`: Food item ID

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Food item retrieved successfully",
  "data": {
    "id": 1,
    "name": "Chicken Breast",
    "brand": "Generic",
    "category": {
      "id": 1,
      "name": "Proteins",
      "description": "High protein foods"
    },
    "servingSize": 100,
    "servingUnit": "grams",
    "caloriesPerServing": 165,
    "proteinGrams": 31.0,
    "carbsGrams": 0.0,
    "fatGrams": 3.6,
    "fiberGrams": 0.0,
    "sugarGrams": 0.0,
    "sodiumMg": 74,
    "isVerified": true,
    "barcode": null,
    "createdAt": "2024-01-01T00:00:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `404 Not Found`: Food item not found

---

### Create Meal

Log a new meal with food items.

**Endpoint:** `POST /api/nutrition/meals`
**Authentication:** Required

**Request Body:**
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
    },
    {
      "foodItemId": 16,
      "servings": 1.0
    }
  ]
}
```

**Field Definitions:**

**mealType** (enum):
- `BREAKFAST`
- `LUNCH`
- `DINNER`
- `SNACK`

**servings**: Number of servings (e.g., 1.5 = 1.5 servings)

**Validations:**
- `userId`: Must match authenticated user
- `mealDate`: Cannot be in the future
- `items`: At least one item required
- `servings`: Minimum 0.1, maximum 50

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Meal created successfully",
  "data": {
    "id": 123,
    "userId": 1,
    "mealType": "BREAKFAST",
    "mealDate": "2024-01-15",
    "mealTime": "08:30:00",
    "notes": "Healthy breakfast",
    "totalCalories": 478,
    "totalProtein": 32.6,
    "totalCarbs": 69.3,
    "totalFat": 18.8,
    "totalFiber": 7.5,
    "totalSugar": 13.4,
    "items": [
      {
        "id": 1,
        "foodItem": {
          "id": 7,
          "name": "Oatmeal"
        },
        "servings": 1.5,
        "calories": 225,
        "proteinGrams": 7.5,
        "carbsGrams": 40.5,
        "fatGrams": 4.5
      },
      {
        "id": 2,
        "foodItem": {
          "id": 11,
          "name": "Banana"
        },
        "servings": 1.0,
        "calories": 89,
        "proteinGrams": 1.1,
        "carbsGrams": 22.8,
        "fatGrams": 0.3
      },
      {
        "id": 3,
        "foodItem": {
          "id": 16,
          "name": "Almonds"
        },
        "servings": 1.0,
        "calories": 164,
        "proteinGrams": 6.0,
        "carbsGrams": 6.0,
        "fatGrams": 14.0
      }
    ],
    "createdAt": "2024-01-15T08:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Side Effects:**
- Publishes `MealCreatedEvent` to Kafka
- Analytics Service updates daily summary

---

### Get Meals by Date

Retrieve all meals for a specific date.

**Endpoint:** `GET /api/nutrition/meals/date/{date}`
**Authentication:** Required

**Path Parameters:**
- `date`: Date in YYYY-MM-DD format

**Example Request:**
```
GET /api/nutrition/meals/date/2024-01-15
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Meals retrieved successfully",
  "data": {
    "date": "2024-01-15",
    "meals": [
      {
        "id": 123,
        "mealType": "BREAKFAST",
        "mealTime": "08:30:00",
        "totalCalories": 478,
        "totalProtein": 32.6,
        "itemCount": 3
      },
      {
        "id": 124,
        "mealType": "LUNCH",
        "mealTime": "12:30:00",
        "totalCalories": 532,
        "totalProtein": 68.9,
        "itemCount": 3
      }
    ],
    "dailyTotals": {
      "totalCalories": 2143,
      "totalProtein": 152.4,
      "totalCarbs": 218.5,
      "totalFat": 68.2,
      "mealCount": 4
    }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Get Meal Details

Get full details of a specific meal.

**Endpoint:** `GET /api/nutrition/meals/{id}`
**Authentication:** Required

**Path Parameters:**
- `id`: Meal ID

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Meal retrieved successfully",
  "data": {
    "id": 123,
    "userId": 1,
    "mealType": "BREAKFAST",
    "mealDate": "2024-01-15",
    "mealTime": "08:30:00",
    "notes": "Healthy breakfast",
    "totalCalories": 478,
    "totalProtein": 32.6,
    "totalCarbs": 69.3,
    "totalFat": 18.8,
    "items": [...]
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `403 Forbidden`: Meal belongs to different user
- `404 Not Found`: Meal not found

---

### Delete Meal

Delete a meal.

**Endpoint:** `DELETE /api/nutrition/meals/{id}`
**Authentication:** Required

**Path Parameters:**
- `id`: Meal ID

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Meal deleted successfully",
  "data": null,
  "timestamp": "2024-01-15T10:30:00"
}
```

**Side Effects:**
- Publishes `MealDeletedEvent` to Kafka
- Analytics Service updates daily summary

---

### Get Nutrition Summary

Get nutrition summary for a date range.

**Endpoint:** `GET /api/nutrition/meals/summary`
**Authentication:** Required

**Query Parameters:**
- `startDate`: Start date (YYYY-MM-DD)
- `endDate`: End date (YYYY-MM-DD)

**Example Request:**
```
GET /api/nutrition/meals/summary?startDate=2024-01-08&endDate=2024-01-15
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Nutrition summary retrieved",
  "data": {
    "startDate": "2024-01-08",
    "endDate": "2024-01-15",
    "dayCount": 7,
    "averageCaloriesPerDay": 2187,
    "averageProteinPerDay": 148.3,
    "averageCarbsPerDay": 215.7,
    "averageFatPerDay": 70.2,
    "totalMeals": 28,
    "dailyBreakdown": [
      {
        "date": "2024-01-15",
        "calories": 2143,
        "protein": 152.4,
        "carbs": 218.5,
        "fat": 68.2
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Workout Service APIs

Base Path: `/api/workouts`

### List Exercises

Browse the exercise library.

**Endpoint:** `GET /api/workouts/exercises`
**Authentication:** Required

**Query Parameters:**
- `category` (optional): Exercise category ID
- `muscleGroup` (optional): CHEST, BACK, LEGS, ARMS, SHOULDERS, CORE, FULL_BODY
- `difficulty` (optional): BEGINNER, INTERMEDIATE, ADVANCED
- `verified` (optional): true/false
- `page`, `size`: Pagination parameters

**Example Request:**
```
GET /api/workouts/exercises?muscleGroup=CHEST&difficulty=INTERMEDIATE&verified=true
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Exercises retrieved successfully",
  "data": {
    "content": [
      {
        "id": 1,
        "name": "Bench Press",
        "description": "Horizontal chest press with barbell",
        "category": {
          "id": 1,
          "name": "Strength"
        },
        "muscleGroup": "CHEST",
        "difficultyLevel": "INTERMEDIATE",
        "equipmentNeeded": "Barbell, Bench",
        "isVerified": true,
        "caloriesPerMinute": 8.0,
        "instructions": "Lie on bench, grip barbell slightly wider than shoulders..."
      }
    ],
    "totalElements": 1
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Search Exercises

Search exercises by name.

**Endpoint:** `GET /api/workouts/exercises/search`
**Authentication:** Required

**Query Parameters:**
- `query` (required): Search term
- `verified` (optional): true/false
- `page`, `size`: Pagination

**Example Request:**
```
GET /api/workouts/exercises/search?query=bench
```

**Response:** Similar to List Exercises

---

### Get Exercise Details

Get detailed information about an exercise.

**Endpoint:** `GET /api/workouts/exercises/{id}`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Exercise retrieved successfully",
  "data": {
    "id": 1,
    "name": "Bench Press",
    "description": "Horizontal chest press with barbell",
    "category": {
      "id": 1,
      "name": "Strength",
      "description": "Resistance training exercises"
    },
    "muscleGroup": "CHEST",
    "difficultyLevel": "INTERMEDIATE",
    "equipmentNeeded": "Barbell, Bench",
    "isVerified": true,
    "instructions": "1. Lie on bench\n2. Grip barbell...",
    "caloriesPerMinute": 8.0,
    "createdAt": "2024-01-01T00:00:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Create Workout

Start a new workout session.

**Endpoint:** `POST /api/workouts`
**Authentication:** Required

**Request Body:**
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

**Field Definitions:**

For strength exercises:
- `plannedSets`, `actualSets`: Number of sets
- `plannedReps`, `actualReps`: Repetitions per set
- `weightKg`: Weight used (0 for bodyweight)

For cardio exercises:
- `plannedDurationSeconds`: Planned duration
- `actualDurationSeconds`: Actual duration

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Workout created successfully",
  "data": {
    "id": 456,
    "userId": 1,
    "workoutName": "Upper Body Strength",
    "workoutDate": "2024-01-15",
    "startTime": "18:00:00",
    "status": "IN_PROGRESS",
    "exercises": [
      {
        "id": 1,
        "exercise": {
          "id": 1,
          "name": "Bench Press"
        },
        "exerciseOrder": 1,
        "plannedSets": 4,
        "plannedReps": 10,
        "actualSets": 4,
        "actualReps": 10,
        "weightKg": 80.0,
        "caloriesBurned": 96
      }
    ],
    "createdAt": "2024-01-15T18:00:00"
  },
  "timestamp": "2024-01-15T18:00:00"
}
```

---

### Complete Workout

Mark a workout as completed.

**Endpoint:** `POST /api/workouts/{id}/complete`
**Authentication:** Required

**Path Parameters:**
- `id`: Workout ID

**Request Body:**
```json
{
  "endTime": "19:15:00"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Workout completed successfully",
  "data": {
    "id": 456,
    "userId": 1,
    "workoutName": "Upper Body Strength",
    "workoutDate": "2024-01-15",
    "startTime": "18:00:00",
    "endTime": "19:15:00",
    "totalDurationMinutes": 75,
    "totalCaloriesBurned": 450,
    "status": "COMPLETED",
    "exerciseCount": 6,
    "completedAt": "2024-01-15T19:15:00"
  },
  "timestamp": "2024-01-15T19:15:00"
}
```

**Side Effects:**
- Publishes `WorkoutCompletedEvent` to Kafka
- Analytics Service updates daily summary

---

### Get Workout History

Retrieve workout history for a date range.

**Endpoint:** `GET /api/workouts/history`
**Authentication:** Required

**Query Parameters:**
- `startDate` (optional): Start date (default: 30 days ago)
- `endDate` (optional): End date (default: today)
- `status` (optional): IN_PROGRESS, COMPLETED, CANCELLED
- `page`, `size`: Pagination

**Example Request:**
```
GET /api/workouts/history?startDate=2024-01-08&endDate=2024-01-15&status=COMPLETED
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Workout history retrieved",
  "data": {
    "content": [
      {
        "id": 456,
        "workoutName": "Upper Body Strength",
        "workoutDate": "2024-01-15",
        "durationMinutes": 75,
        "caloriesBurned": 450,
        "status": "COMPLETED",
        "exerciseCount": 6
      },
      {
        "id": 455,
        "workoutName": "HIIT Training",
        "workoutDate": "2024-01-13",
        "durationMinutes": 45,
        "caloriesBurned": 420,
        "status": "COMPLETED",
        "exerciseCount": 3
      }
    ],
    "totalElements": 5,
    "summary": {
      "totalWorkouts": 5,
      "totalDurationMinutes": 305,
      "totalCaloriesBurned": 2080,
      "averageDuration": 61
    }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Get Workout Details

Get full details of a specific workout.

**Endpoint:** `GET /api/workouts/{id}`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Workout retrieved successfully",
  "data": {
    "id": 456,
    "userId": 1,
    "workoutName": "Upper Body Strength",
    "workoutDate": "2024-01-15",
    "startTime": "18:00:00",
    "endTime": "19:15:00",
    "totalDurationMinutes": 75,
    "totalCaloriesBurned": 450,
    "status": "COMPLETED",
    "notes": "Evening workout",
    "exercises": [...]
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Delete Workout

Delete a workout.

**Endpoint:** `DELETE /api/workouts/{id}`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Workout deleted successfully",
  "data": null,
  "timestamp": "2024-01-15T10:30:00"
}
```

**Side Effects:**
- Publishes `WorkoutDeletedEvent` to Kafka
- Analytics Service updates daily summary

---

## Analytics Service APIs

Base Path: `/api/analytics`

### Get Daily Summary

Get analytics summary for a specific date.

**Endpoint:** `GET /api/analytics/daily/{date}`
**Authentication:** Required

**Path Parameters:**
- `date`: Date in YYYY-MM-DD format

**Example Request:**
```
GET /api/analytics/daily/2024-01-15
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Daily summary retrieved",
  "data": {
    "userId": 1,
    "date": "2024-01-15",
    "totalCaloriesConsumed": 2143,
    "totalCaloriesBurned": 450,
    "netCalories": 1693,
    "totalProteinGrams": 152,
    "totalCarbsGrams": 218,
    "totalFatGrams": 68,
    "totalFiberGrams": 35,
    "workoutDurationMinutes": 75,
    "workoutCount": 1,
    "mealCount": 4,
    "targetCalories": 2200,
    "targetProtein": 150,
    "targetCarbs": 220,
    "targetFat": 70,
    "calorieProgress": 97.4,
    "proteinProgress": 101.3,
    "carbsProgress": 99.1,
    "fatProgress": 97.1
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**Calculation:**
- `netCalories` = `totalCaloriesConsumed` - `totalCaloriesBurned`
- `calorieProgress` = (`totalCaloriesConsumed` / `targetCalories`) * 100

---

### Get Weekly Summary

Get aggregated analytics for a week.

**Endpoint:** `GET /api/analytics/weekly`
**Authentication:** Required

**Query Parameters:**
- `startDate`: Week start date (default: 7 days ago)

**Example Request:**
```
GET /api/analytics/weekly?startDate=2024-01-08
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Weekly summary retrieved",
  "data": {
    "userId": 1,
    "weekStartDate": "2024-01-08",
    "weekEndDate": "2024-01-14",
    "averageCaloriesPerDay": 2187,
    "averageProteinPerDay": 148,
    "averageCarbsPerDay": 216,
    "averageFatPerDay": 70,
    "totalWorkoutMinutes": 305,
    "totalWorkouts": 5,
    "averageWorkoutDuration": 61,
    "totalCaloriesBurned": 2080,
    "dailySummaries": [
      {
        "date": "2024-01-08",
        "calories": 2156,
        "workouts": 1
      }
    ],
    "weeklyGoalProgress": {
      "calorieProgress": 99.4,
      "workoutProgress": 100
    }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Get Date Range Summary

Get analytics for a custom date range.

**Endpoint:** `GET /api/analytics/range`
**Authentication:** Required

**Query Parameters:**
- `startDate`: Start date (YYYY-MM-DD)
- `endDate`: End date (YYYY-MM-DD)

**Example Request:**
```
GET /api/analytics/range?startDate=2024-01-01&endDate=2024-01-31
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Range summary retrieved",
  "data": {
    "userId": 1,
    "startDate": "2024-01-01",
    "endDate": "2024-01-31",
    "dayCount": 31,
    "totalCaloriesConsumed": 67797,
    "totalCaloriesBurned": 8960,
    "averageCaloriesPerDay": 2187,
    "totalWorkouts": 20,
    "totalWorkoutMinutes": 1220,
    "trends": {
      "caloriesTrend": "stable",
      "weightTrend": "decreasing",
      "workoutFrequency": "consistent"
    }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Get Goal Progress

Track progress towards fitness goals.

**Endpoint:** `GET /api/analytics/goals/progress`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Goal progress retrieved",
  "data": {
    "userId": 1,
    "currentWeight": 83.5,
    "targetWeight": 80.0,
    "startWeight": 85.5,
    "weightProgress": 57.1,
    "remainingKg": 3.5,
    "calorieGoal": {
      "target": 2200,
      "averageActual": 2187,
      "progress": 99.4
    },
    "workoutGoal": {
      "targetWorkoutsPerWeek": 5,
      "actualWorkoutsThisWeek": 4,
      "progress": 80
    },
    "macroGoals": {
      "protein": {
        "target": 150,
        "averageActual": 148,
        "progress": 98.7
      },
      "carbs": {
        "target": 220,
        "averageActual": 216,
        "progress": 98.2
      },
      "fat": {
        "target": 70,
        "averageActual": 70,
        "progress": 100
      }
    },
    "estimatedDaysToGoal": 35
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "timestamp": "2024-01-15T10:30:00",
  "errors": [
    {
      "field": "email",
      "message": "Email is already in use"
    }
  ]
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Validation error, invalid input |
| 401 | Unauthorized | Authentication failed or token invalid |
| 403 | Forbidden | User doesn't have permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (e.g., duplicate email) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (should be rare) |
| 503 | Service Unavailable | Service temporarily unavailable |

### Validation Errors

**Example:**
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "timestamp": "2024-01-15T10:30:00",
  "errors": [
    {
      "field": "email",
      "message": "Email must be valid"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters"
    }
  ]
}
```

---

## Rate Limiting

Rate limits protect the API from abuse:

| Endpoint | Limit |
|----------|-------|
| POST /api/users/register | 5 per hour per IP |
| POST /api/users/login | 10 per minute per IP |
| GET /api/nutrition/* | 100 per minute per user |
| POST /api/nutrition/meals | 50 per hour per user |
| GET /api/workouts/* | 100 per minute per user |
| POST /api/workouts | 50 per hour per user |
| GET /api/analytics/* | 100 per minute per user |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000400
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (0-indexed, default: 0)
- `size`: Page size (default: 20, max: 100)
- `sort`: Sort field (default varies by endpoint)
- `direction`: asc or desc (default: asc)

**Example:**
```
GET /api/nutrition/food-items?page=1&size=50&sort=name&direction=asc
```

**Response:**
```json
{
  "content": [...],
  "page": 1,
  "size": 50,
  "totalElements": 234,
  "totalPages": 5,
  "isFirst": false,
  "isLast": false,
  "hasNext": true,
  "hasPrevious": true
}
```

---

## API Versioning

Current version: **v1**

All endpoints are prefixed with `/api/`

Future versions will use URL versioning:
- v1: `/api/...` (current)
- v2: `/api/v2/...` (future)

**Version Header:**
```http
API-Version: 1
```

---

## Swagger/OpenAPI Documentation

Interactive API documentation available at:

- **User Service**: http://localhost:8081/swagger-ui.html
- **Nutrition Service**: http://localhost:8082/swagger-ui.html
- **Workout Service**: http://localhost:8083/swagger-ui.html
- **Analytics Service**: http://localhost:8084/swagger-ui.html

**OpenAPI JSON:**
- http://localhost:8081/v3/api-docs
- http://localhost:8082/v3/api-docs
- http://localhost:8083/v3/api-docs
- http://localhost:8084/v3/api-docs

---

## Quick Reference

### Base URLs
- Development: `http://localhost:8080`
- Production: `https://api.fittrackerpro.com`

### Authentication
```http
Authorization: Bearer {jwt-token}
```

### Common Endpoints
```
POST /api/users/login
GET  /api/users/profile
GET  /api/nutrition/food-items
POST /api/nutrition/meals
GET  /api/workouts/exercises
POST /api/workouts
GET  /api/analytics/daily/{date}
```

---

For architectural details, see [ARCHITECTURE.md](ARCHITECTURE.md).
For deployment guide, see [DEPLOYMENT.md](DEPLOYMENT.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
