# FitTracker Pro - API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [User API](#user-api)
4. [Nutrition API](#nutrition-api)
5. [Workout API](#workout-api)
6. [Analytics API](#analytics-api)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples](#examples)

## Overview

### Base URL

```
Development: http://localhost:8080
Production:  https://api.fittrackerpro.com
```

### API Version

Current version: `v1`

All endpoints are prefixed with `/api`

### Response Format

All responses follow this structure:

```json
{
  "success": boolean,
  "message": string,
  "data": object | array,
  "timestamp": string
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Deletion successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Authentication

### Register User

Create a new user account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "fullName": "John Doe",
  "dateOfBirth": "1990-01-15",
  "gender": "MALE",
  "heightCm": 175.5,
  "currentWeightKg": 75.0,
  "targetWeightKg": 70.0,
  "activityLevel": "MODERATELY_ACTIVE",
  "fitnessGoal": "WEIGHT_LOSS"
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Valid email address |
| password | string | Yes | Min 8 chars, must contain uppercase, lowercase, number, special char |
| fullName | string | Yes | User's full name |
| dateOfBirth | date | Yes | Format: YYYY-MM-DD |
| gender | enum | Yes | MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY |
| heightCm | number | Yes | Height in centimeters |
| currentWeightKg | number | Yes | Current weight in kilograms |
| targetWeightKg | number | No | Target weight in kilograms |
| activityLevel | enum | Yes | SEDENTARY, LIGHTLY_ACTIVE, MODERATELY_ACTIVE, VERY_ACTIVE, EXTRA_ACTIVE |
| fitnessGoal | enum | Yes | WEIGHT_LOSS, WEIGHT_GAIN, MUSCLE_GAIN, MAINTENANCE |

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "fullName": "John Doe",
    "createdAt": "2024-11-19T10:30:00Z"
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Login

Authenticate and receive JWT token.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tokenType": "Bearer",
    "expiresIn": 86400,
    "user": {
      "id": 1,
      "email": "john.doe@example.com",
      "fullName": "John Doe"
    }
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Get User Profile

Get current user's profile information.

**Endpoint:** `GET /api/auth/profile`

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "fullName": "John Doe",
    "dateOfBirth": "1990-01-15",
    "gender": "MALE",
    "profile": {
      "heightCm": 175.5,
      "currentWeightKg": 75.0,
      "targetWeightKg": 70.0,
      "activityLevel": "MODERATELY_ACTIVE",
      "fitnessGoal": "WEIGHT_LOSS",
      "targetDailyCalories": 2000,
      "targetProteinG": 150,
      "targetCarbsG": 200,
      "targetFatG": 65
    }
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Update Profile

Update user profile information.

**Endpoint:** `PUT /api/auth/profile`

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "fullName": "John M. Doe",
  "currentWeightKg": 73.5,
  "targetWeightKg": 70.0,
  "activityLevel": "VERY_ACTIVE",
  "targetDailyCalories": 2200
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "fullName": "John M. Doe",
    "profile": {
      "currentWeightKg": 73.5,
      "targetWeightKg": 70.0,
      "activityLevel": "VERY_ACTIVE",
      "targetDailyCalories": 2200
    },
    "updatedAt": "2024-11-19T10:35:00Z"
  },
  "timestamp": "2024-11-19T10:35:00Z"
}
```

---

### Change Password

Change user password.

**Endpoint:** `PUT /api/auth/change-password`

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "currentPassword": "SecurePass123!",
  "newPassword": "NewSecurePass456!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": null,
  "timestamp": "2024-11-19T10:40:00Z"
}
```

---

## User API

### Get Weight History

Retrieve user's weight history.

**Endpoint:** `GET /api/users/weight-history`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| startDate | date | No | Start date (YYYY-MM-DD) |
| endDate | date | No | End date (YYYY-MM-DD) |
| limit | integer | No | Max records (default: 30) |

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Weight history retrieved",
  "data": [
    {
      "id": 1,
      "weightKg": 75.0,
      "recordedAt": "2024-11-01T08:00:00Z",
      "notes": "Starting weight"
    },
    {
      "id": 2,
      "weightKg": 74.5,
      "recordedAt": "2024-11-08T08:00:00Z",
      "notes": "Week 1 progress"
    }
  ],
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Add Weight Entry

Add a new weight measurement.

**Endpoint:** `POST /api/users/weight-history`

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "weightKg": 73.5,
  "notes": "Feeling great!"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Weight entry added",
  "data": {
    "id": 3,
    "weightKg": 73.5,
    "recordedAt": "2024-11-15T08:00:00Z",
    "notes": "Feeling great!"
  },
  "timestamp": "2024-11-15T08:00:00Z"
}
```

---

## Nutrition API

### Get Meals by Date

Retrieve all meals for a specific date.

**Endpoint:** `GET /api/meals/date/{date}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Date in YYYY-MM-DD format |

**Example:** `GET /api/meals/date/2024-11-19`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Meals retrieved successfully",
  "data": [
    {
      "id": 1,
      "userId": 1,
      "mealType": "BREAKFAST",
      "mealDate": "2024-11-19",
      "mealTime": "08:00:00",
      "notes": "Healthy breakfast",
      "totalCalories": 450,
      "totalProtein": 25.5,
      "totalCarbs": 60.0,
      "totalFat": 12.0,
      "totalFiber": 8.0,
      "totalSugar": 15.0,
      "items": [
        {
          "id": 1,
          "foodItemId": 101,
          "foodItemName": "Oatmeal",
          "servings": 1.0,
          "calories": 150,
          "protein": 5.0,
          "carbs": 27.0,
          "fat": 3.0
        },
        {
          "id": 2,
          "foodItemId": 102,
          "foodItemName": "Banana",
          "servings": 1.0,
          "calories": 105,
          "protein": 1.3,
          "carbs": 27.0,
          "fat": 0.4
        }
      ],
      "createdAt": "2024-11-19T08:15:00Z",
      "updatedAt": "2024-11-19T08:15:00Z"
    }
  ],
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Create Meal

Create a new meal entry.

**Endpoint:** `POST /api/meals`

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "mealType": "LUNCH",
  "mealDate": "2024-11-19",
  "mealTime": "12:30:00",
  "notes": "Office lunch",
  "items": [
    {
      "foodItemId": 201,
      "servings": 1.0
    },
    {
      "foodItemId": 202,
      "servings": 0.5
    }
  ]
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mealType | enum | Yes | BREAKFAST, LUNCH, DINNER, SNACK |
| mealDate | date | Yes | Date of meal (YYYY-MM-DD) |
| mealTime | time | No | Time of meal (HH:MM:SS) |
| notes | string | No | Additional notes |
| items | array | Yes | List of food items (min 1) |
| items[].foodItemId | integer | Yes | ID of food item |
| items[].servings | number | Yes | Number of servings |

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Meal created successfully",
  "data": {
    "id": 2,
    "userId": 1,
    "mealType": "LUNCH",
    "mealDate": "2024-11-19",
    "mealTime": "12:30:00",
    "notes": "Office lunch",
    "totalCalories": 650,
    "totalProtein": 45.0,
    "totalCarbs": 70.0,
    "totalFat": 20.0,
    "items": [...]
  },
  "timestamp": "2024-11-19T12:35:00Z"
}
```

---

### Update Meal

Update an existing meal.

**Endpoint:** `PUT /api/meals/{id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Meal ID |

**Request Body:**
```json
{
  "notes": "Updated notes",
  "items": [
    {
      "foodItemId": 201,
      "servings": 1.5
    }
  ]
}
```

**Response:** `200 OK`

---

### Delete Meal

Delete a meal entry.

**Endpoint:** `DELETE /api/meals/{id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Meal ID |

**Response:** `204 No Content`

---

### Search Food Items

Search for food items in the database.

**Endpoint:** `GET /api/food-items/search`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Search term |
| page | integer | No | Page number (default: 0) |
| size | integer | No | Page size (default: 20) |

**Example:** `GET /api/food-items/search?query=banana&page=0&size=10`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Food items found",
  "data": {
    "content": [
      {
        "id": 102,
        "name": "Banana",
        "brand": null,
        "servingSize": "1 medium",
        "servingUnit": "piece",
        "calories": 105,
        "proteinG": 1.3,
        "carbsG": 27.0,
        "fatG": 0.4,
        "fiberG": 3.1,
        "sugarG": 14.4,
        "isVerified": true
      }
    ],
    "page": 0,
    "size": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Get Daily Nutrition Summary

Get nutrition summary for a specific date.

**Endpoint:** `GET /api/nutrition/summary/daily/{date}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Date in YYYY-MM-DD format |

**Example:** `GET /api/nutrition/summary/daily/2024-11-19`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Daily summary retrieved",
  "data": {
    "date": "2024-11-19",
    "userId": 1,
    "dailyTotals": {
      "totalCalories": 1850,
      "totalProtein": 120.5,
      "totalCarbs": 220.0,
      "totalFat": 55.0,
      "totalFiber": 30.0,
      "totalSugar": 45.0,
      "mealCount": 4
    },
    "targets": {
      "targetCalories": 2000,
      "targetProtein": 150,
      "targetCarbs": 200,
      "targetFat": 65
    },
    "percentages": {
      "caloriesPercent": 92.5,
      "proteinPercent": 80.3,
      "carbsPercent": 110.0,
      "fatPercent": 84.6
    }
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Get Weekly Nutrition Summary

Get nutrition summary for a week.

**Endpoint:** `GET /api/nutrition/summary/weekly`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| startDate | string | Yes | Week start date (YYYY-MM-DD) |

**Example:** `GET /api/nutrition/summary/weekly?startDate=2024-11-13`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Weekly summary retrieved",
  "data": [
    {
      "date": "2024-11-13",
      "dailyTotals": {
        "totalCalories": 1950,
        "totalProtein": 130.0,
        "totalCarbs": 210.0,
        "totalFat": 60.0
      }
    },
    {
      "date": "2024-11-14",
      "dailyTotals": {
        "totalCalories": 2100,
        "totalProtein": 140.0,
        "totalCarbs": 230.0,
        "totalFat": 65.0
      }
    }
  ],
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

## Workout API

### Get Workouts by Date

Retrieve all workouts for a specific date.

**Endpoint:** `GET /api/workouts/date/{date}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Date in YYYY-MM-DD format |

**Example:** `GET /api/workouts/date/2024-11-19`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Workouts retrieved successfully",
  "data": [
    {
      "id": 1,
      "userId": 1,
      "workoutName": "Morning Strength Training",
      "workoutDate": "2024-11-19",
      "startTime": "2024-11-19T07:00:00Z",
      "endTime": "2024-11-19T08:00:00Z",
      "totalDurationMinutes": 60,
      "totalCaloriesBurned": 350,
      "status": "COMPLETED",
      "notes": "Great workout!",
      "exercises": [
        {
          "id": 1,
          "exercise": {
            "id": 101,
            "name": "Bench Press",
            "muscleGroup": "CHEST",
            "equipmentNeeded": "Barbell"
          },
          "plannedSets": 3,
          "plannedReps": 10,
          "actualSets": 3,
          "actualReps": 10,
          "weightKg": 60.0,
          "caloriesBurned": 100
        }
      ],
      "createdAt": "2024-11-19T07:00:00Z",
      "updatedAt": "2024-11-19T08:05:00Z"
    }
  ],
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Create Workout

Create a new workout.

**Endpoint:** `POST /api/workouts`

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "workoutName": "Evening Cardio",
  "workoutDate": "2024-11-19",
  "startTime": "2024-11-19T18:00:00",
  "notes": "Light cardio session",
  "exercises": [
    {
      "exerciseId": 201,
      "plannedSets": 1,
      "plannedDurationSeconds": 1200,
      "notes": "Treadmill running"
    },
    {
      "exerciseId": 202,
      "plannedSets": 3,
      "plannedReps": 15,
      "weightKg": 10.0
    }
  ]
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| workoutName | string | Yes | Name of the workout |
| workoutDate | date | Yes | Date of workout (YYYY-MM-DD) |
| startTime | datetime | Yes | Start time (ISO 8601) |
| notes | string | No | Additional notes |
| exercises | array | Yes | List of exercises (min 1) |
| exercises[].exerciseId | integer | Yes | ID of exercise |
| exercises[].plannedSets | integer | No | Planned sets |
| exercises[].plannedReps | integer | No | Planned reps |
| exercises[].plannedDurationSeconds | integer | No | Planned duration |
| exercises[].weightKg | number | No | Weight in kg |

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Workout created successfully",
  "data": {
    "id": 2,
    "userId": 1,
    "workoutName": "Evening Cardio",
    "workoutDate": "2024-11-19",
    "startTime": "2024-11-19T18:00:00Z",
    "status": "IN_PROGRESS",
    "exercises": [...]
  },
  "timestamp": "2024-11-19T18:05:00Z"
}
```

---

### Complete Workout

Mark a workout as completed.

**Endpoint:** `PUT /api/workouts/{id}/complete`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Workout ID |

**Request Body:**
```json
{
  "endTime": "2024-11-19T19:00:00"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Workout completed",
  "data": {
    "id": 2,
    "status": "COMPLETED",
    "endTime": "2024-11-19T19:00:00Z",
    "totalDurationMinutes": 60,
    "totalCaloriesBurned": 300
  },
  "timestamp": "2024-11-19T19:05:00Z"
}
```

---

### Delete Workout

Delete a workout entry.

**Endpoint:** `DELETE /api/workouts/{id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Workout ID |

**Response:** `204 No Content`

---

### Search Exercises

Search for exercises in the database.

**Endpoint:** `GET /api/exercises/search`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Search term |
| muscleGroup | string | No | Filter by muscle group |
| page | integer | No | Page number (default: 0) |
| size | integer | No | Page size (default: 20) |

**Example:** `GET /api/exercises/search?query=press&muscleGroup=CHEST`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Exercises found",
  "data": {
    "content": [
      {
        "id": 101,
        "name": "Bench Press",
        "description": "Classic chest exercise",
        "category": {
          "id": 1,
          "name": "Strength Training"
        },
        "muscleGroup": "CHEST",
        "difficultyLevel": "INTERMEDIATE",
        "equipmentNeeded": "Barbell, Bench",
        "caloriesPerMinute": 8.5,
        "isVerified": true
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 1,
    "totalPages": 1
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

## Analytics API

### Get Nutrition Analytics

Get nutrition analytics for a user.

**Endpoint:** `GET /api/analytics/nutrition/{userId}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| userId | integer | User ID |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| startDate | string | No | Start date (YYYY-MM-DD) |
| endDate | string | No | End date (YYYY-MM-DD) |
| period | string | No | DAILY, WEEKLY, MONTHLY |

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Analytics retrieved",
  "data": {
    "period": "WEEKLY",
    "averages": {
      "avgCalories": 1950,
      "avgProtein": 135.5,
      "avgCarbs": 215.0,
      "avgFat": 60.0
    },
    "trends": {
      "caloriesTrend": "STABLE",
      "macroBalance": "GOOD"
    },
    "insights": [
      "You've been consistent with your calorie intake",
      "Protein intake is below target by 10%"
    ]
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Get Workout Analytics

Get workout analytics for a user.

**Endpoint:** `GET /api/analytics/workout/{userId}`

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Analytics retrieved",
  "data": {
    "period": "MONTHLY",
    "totals": {
      "totalWorkouts": 16,
      "totalDurationMinutes": 960,
      "totalCaloriesBurned": 5600
    },
    "averages": {
      "avgWorkoutsPerWeek": 4,
      "avgDurationMinutes": 60,
      "avgCaloriesPerWorkout": 350
    },
    "breakdown": {
      "STRENGTH": 10,
      "CARDIO": 4,
      "FLEXIBILITY": 2
    }
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Get Goals

Get user's fitness goals.

**Endpoint:** `GET /api/goals`

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Goals retrieved",
  "data": [
    {
      "id": 1,
      "userId": 1,
      "goalType": "WEIGHT_LOSS",
      "targetValue": 70.0,
      "currentValue": 73.5,
      "startValue": 75.0,
      "targetDate": "2024-12-31",
      "status": "IN_PROGRESS",
      "progress": 68.2,
      "createdAt": "2024-11-01T00:00:00Z"
    }
  ],
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

### Create Goal

Create a new fitness goal.

**Endpoint:** `POST /api/goals`

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "goalType": "MUSCLE_GAIN",
  "targetValue": 80.0,
  "targetDate": "2025-06-30",
  "description": "Gain 5kg of muscle mass"
}
```

**Response:** `201 Created`

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "timestamp": "2024-11-19T10:30:00Z",
  "errors": [
    {
      "field": "email",
      "message": "Email is required"
    }
  ]
}
```

### Common Error Codes

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "timestamp": "2024-11-19T10:30:00Z",
  "errors": [
    {
      "field": "password",
      "message": "Password must be at least 8 characters"
    }
  ]
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "message": "Invalid or expired token",
  "data": null,
  "timestamp": "2024-11-19T10:30:00Z"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "message": "Resource not found",
  "data": null,
  "timestamp": "2024-11-19T10:30:00Z"
}
```

**409 Conflict:**
```json
{
  "success": false,
  "message": "Email already exists",
  "data": null,
  "timestamp": "2024-11-19T10:30:00Z"
}
```

**429 Too Many Requests:**
```json
{
  "success": false,
  "message": "Rate limit exceeded. Try again in 60 seconds",
  "data": null,
  "timestamp": "2024-11-19T10:30:00Z"
}
```

---

## Rate Limiting

**Limits:**
- **General API:** 100 requests per minute per user
- **Login:** 5 attempts per 15 minutes per IP
- **Registration:** 3 requests per hour per IP

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700000000
```

---

## Examples

### Complete Workflow Example

**1. Register a new user:**
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "fullName": "Test User",
    "dateOfBirth": "1995-05-15",
    "gender": "MALE",
    "heightCm": 180,
    "currentWeightKg": 80,
    "targetWeightKg": 75,
    "activityLevel": "MODERATELY_ACTIVE",
    "fitnessGoal": "WEIGHT_LOSS"
  }'
```

**2. Login:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }' | jq -r '.data.token')
```

**3. Create a meal:**
```bash
curl -X POST http://localhost:8080/api/meals \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mealType": "BREAKFAST",
    "mealDate": "2024-11-19",
    "items": [
      {"foodItemId": 1, "servings": 1.0},
      {"foodItemId": 2, "servings": 1.0}
    ]
  }'
```

**4. Get daily summary:**
```bash
curl http://localhost:8080/api/nutrition/summary/daily/2024-11-19 \
  -H "Authorization: Bearer $TOKEN"
```

**5. Create a workout:**
```bash
curl -X POST http://localhost:8080/api/workouts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workoutName": "Upper Body",
    "workoutDate": "2024-11-19",
    "startTime": "2024-11-19T10:00:00",
    "exercises": [
      {
        "exerciseId": 1,
        "plannedSets": 3,
        "plannedReps": 10,
        "weightKg": 50
      }
    ]
  }'
```

---

**Last Updated:** November 2024
**Version:** 1.0.0
**Support:** support@fittrackerpro.com
