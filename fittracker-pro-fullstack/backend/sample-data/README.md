# FitTracker Pro - Sample Data

This directory contains sample data scripts for populating the FitTracker Pro databases with test data for demonstration and testing purposes.

## Sample Data Files

1. **01_users_sample_data.sql** - Sample user accounts and profiles
2. **02_nutrition_sample_data.sql** - Food items, categories, and meal history
3. **03_workout_sample_data.sql** - Exercises, categories, and workout history

## Sample User Accounts

All sample users have the password: `Password123!`

| Email | Name | Gender | Goal | Activity Level |
|-------|------|--------|------|----------------|
| john.doe@example.com | John Doe | Male | Weight Loss | Moderately Active |
| jane.smith@example.com | Jane Smith | Female | Maintenance | Active |
| mike.johnson@example.com | Mike Johnson | Male | Weight Loss | Lightly Active |
| sarah.williams@example.com | Sarah Williams | Female | Muscle Gain | Very Active |
| alex.brown@example.com | Alex Brown | Male | Muscle Gain | Moderately Active |

## How to Load Sample Data

### Option 1: Using Docker Exec

If services are running in Docker containers:

```bash
# Load Users data
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_users < sample-data/01_users_sample_data.sql

# Load Nutrition data
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_nutrition < sample-data/02_nutrition_sample_data.sql

# Load Workout data
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_workouts < sample-data/03_workout_sample_data.sql
```

### Option 2: Using psql Directly

If PostgreSQL is accessible locally:

```bash
# Load Users data
psql -U fittracker -d fittracker_users -h localhost -p 5432 -f sample-data/01_users_sample_data.sql

# Load Nutrition data
psql -U fittracker -d fittracker_nutrition -h localhost -p 5432 -f sample-data/02_nutrition_sample_data.sql

# Load Workout data
psql -U fittracker -d fittracker_workouts -h localhost -p 5432 -f sample-data/03_workout_sample_data.sql
```

### Option 3: Load All at Once

```bash
# Create a script to load all sample data
./sample-data/load-all-data.sh
```

## Sample Data Contents

### Users Service
- 5 user accounts with different profiles
- User profiles with varied fitness goals (weight loss, maintenance, muscle gain)
- Different activity levels (lightly active, moderately active, active, very active)

### Nutrition Service
- 17+ food items across 7 categories
- Realistic nutritional information
- 7 days of meal history for user "John Doe"
- 4 meals per day (breakfast, lunch, dinner, snack)
- Approximately 2000-2400 calories per day

### Workout Service
- 15+ exercises across 5 categories (strength, cardio, flexibility, core, functional)
- Varied difficulty levels (beginner, intermediate, advanced)
- 5 completed workouts for user "John Doe" over the past 7 days
- Mix of strength training, cardio, and flexibility work
- Realistic calorie burn and duration data

## Testing Recommendations

1. **Login as John Doe** (`john.doe@example.com` / `Password123!`) to see complete data:
   - 7 days of meal history
   - 5 completed workouts
   - Populated analytics dashboard

2. **Login as other users** to test with minimal data

3. **Create new data** using the API endpoints to test event publishing and analytics updates

## Notes

- Sample data is designed for testing and demonstration purposes only
- All bcrypt password hashes use the same password: `Password123!`
- Data includes realistic nutrition and exercise information
- John Doe's profile has the most complete data for demonstration purposes
- Analytics data will be automatically calculated from events when services are running

## Security Warning

⚠️ **DO NOT use these sample credentials or data in production environments!**

These are test accounts with weak, known passwords intended only for development and demonstration purposes.
