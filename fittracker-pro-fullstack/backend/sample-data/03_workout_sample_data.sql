-- FitTracker Pro - Sample Workout Data
-- Insert sample exercises and workouts for testing and demonstration

-- Insert sample exercise categories (if they don't exist)
INSERT INTO exercise_categories (name, description, created_at)
VALUES
    ('Strength', 'Resistance and weight training exercises', CURRENT_TIMESTAMP),
    ('Cardio', 'Cardiovascular and aerobic exercises', CURRENT_TIMESTAMP),
    ('Flexibility', 'Stretching and flexibility exercises', CURRENT_TIMESTAMP),
    ('Core', 'Abdominal and core strengthening exercises', CURRENT_TIMESTAMP),
    ('Functional', 'Functional and compound movement exercises', CURRENT_TIMESTAMP)
ON CONFLICT (name) DO NOTHING;

-- Insert sample exercises
INSERT INTO exercises (name, description, category_id, muscle_group, difficulty_level, equipment_needed, is_verified, instructions, calories_per_minute, created_at, updated_at)
VALUES
    -- Strength Exercises
    ('Bench Press', 'Horizontal chest press with barbell', (SELECT id FROM exercise_categories WHERE name = 'Strength'), 'CHEST', 'INTERMEDIATE', 'Barbell, Bench', true,
     'Lie on bench, grip barbell slightly wider than shoulders, lower to chest, press up', 8.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Barbell Squat', 'Compound lower body exercise with barbell', (SELECT id FROM exercise_categories WHERE name = 'Strength'), 'LEGS', 'INTERMEDIATE', 'Barbell, Squat Rack', true,
     'Place bar on upper back, feet shoulder-width, squat down keeping knees over toes, stand up', 10.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Deadlift', 'Hip hinge movement lifting barbell from floor', (SELECT id FROM exercise_categories WHERE name = 'Strength'), 'BACK', 'ADVANCED', 'Barbell', true,
     'Stand with feet hip-width, grip bar, keep back straight, lift by extending hips and knees', 9.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Dumbbell Shoulder Press', 'Overhead pressing movement with dumbbells', (SELECT id FROM exercise_categories WHERE name = 'Strength'), 'SHOULDERS', 'BEGINNER', 'Dumbbells', true,
     'Sit or stand, hold dumbbells at shoulder height, press overhead until arms extended, lower back down', 7.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Bicep Curls', 'Isolated bicep exercise with dumbbells', (SELECT id FROM exercise_categories WHERE name = 'Strength'), 'ARMS', 'BEGINNER', 'Dumbbells', true,
     'Stand with dumbbells at sides, curl weights up by bending elbows, lower back down', 4.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Tricep Dips', 'Bodyweight tricep exercise', (SELECT id FROM exercise_categories WHERE name = 'Strength'), 'ARMS', 'INTERMEDIATE', 'Dip Bars or Bench', true,
     'Support yourself on bars, lower body by bending elbows, press back up', 6.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Pull-ups', 'Upper body pulling exercise', (SELECT id FROM exercise_categories WHERE name = 'Strength'), 'BACK', 'INTERMEDIATE', 'Pull-up Bar', true,
     'Hang from bar with overhand grip, pull body up until chin over bar, lower back down', 8.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Cardio Exercises
    ('Running', 'Outdoor or treadmill running', (SELECT id FROM exercise_categories WHERE name = 'Cardio'), 'FULL_BODY', 'BEGINNER', 'None or Treadmill', true,
     'Maintain steady pace with proper running form, land mid-foot, keep shoulders relaxed', 12.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Cycling', 'Stationary or outdoor cycling', (SELECT id FROM exercise_categories WHERE name = 'Cardio'), 'LEGS', 'BEGINNER', 'Bicycle or Stationary Bike', true,
     'Maintain steady cadence, adjust resistance as needed, keep core engaged', 9.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Jump Rope', 'Cardiovascular jump rope exercise', (SELECT id FROM exercise_categories WHERE name = 'Cardio'), 'FULL_BODY', 'BEGINNER', 'Jump Rope', true,
     'Jump with feet together, rotate rope with wrists, maintain rhythm', 13.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Burpees', 'Full body conditioning exercise', (SELECT id FROM exercise_categories WHERE name = 'Cardio'), 'FULL_BODY', 'INTERMEDIATE', 'None', true,
     'From standing, drop to push-up, perform push-up, jump feet to hands, jump up with arms overhead', 11.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Core Exercises
    ('Plank', 'Isometric core strengthening exercise', (SELECT id FROM exercise_categories WHERE name = 'Core'), 'CORE', 'BEGINNER', 'None', true,
     'Hold push-up position on forearms, keep body straight from head to heels', 5.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Crunches', 'Abdominal flexion exercise', (SELECT id FROM exercise_categories WHERE name = 'Core'), 'CORE', 'BEGINNER', 'None', true,
     'Lie on back, knees bent, hands behind head, curl shoulders off ground', 4.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    ('Russian Twists', 'Rotational core exercise', (SELECT id FROM exercise_categories WHERE name = 'Core'), 'CORE', 'INTERMEDIATE', 'Medicine Ball (optional)', true,
     'Sit with knees bent, lean back slightly, rotate torso side to side', 6.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Flexibility
    ('Yoga Flow', 'Dynamic yoga sequence', (SELECT id FROM exercise_categories WHERE name = 'Flexibility'), 'FULL_BODY', 'BEGINNER', 'Yoga Mat', true,
     'Flow through various poses maintaining breath awareness', 3.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert sample workouts for user 1 (John Doe) for the past 7 days
DO $$
DECLARE
    current_date_val DATE;
    workout_id_val BIGINT;
    start_time_val TIME;
    end_time_val TIME;
BEGIN
    -- Workout Day 1 (6 days ago) - Upper Body
    current_date_val := CURRENT_DATE - 6;
    start_time_val := '08:00:00';
    end_time_val := '09:15:00';

    INSERT INTO workouts (user_id, workout_name, workout_date, start_time, end_time, total_duration_minutes, total_calories_burned, status, notes, created_at, updated_at)
    VALUES (1, 'Upper Body Strength', current_date_val, start_time_val, end_time_val, 75, 450, 'COMPLETED', 'Great workout session', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    RETURNING id INTO workout_id_val;

    INSERT INTO workout_exercises (workout_id, exercise_id, exercise_order, planned_sets, planned_reps, actual_sets, actual_reps, weight_kg, calories_burned, created_at)
    VALUES
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Bench Press'), 1, 4, 10, 4, 10, 80.0, 96, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Pull-ups'), 2, 3, 8, 3, 8, 0.0, 72, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Dumbbell Shoulder Press'), 3, 3, 12, 3, 12, 25.0, 84, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Bicep Curls'), 4, 3, 12, 3, 12, 15.0, 48, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Tricep Dips'), 5, 3, 12, 3, 12, 0.0, 72, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Plank'), 6, 3, NULL, 3, NULL, 0.0, 78, CURRENT_TIMESTAMP);

    -- Workout Day 2 (5 days ago) - Cardio
    current_date_val := CURRENT_DATE - 5;
    start_time_val := '07:00:00';
    end_time_val := '07:45:00';

    INSERT INTO workouts (user_id, workout_name, workout_date, start_time, end_time, total_duration_minutes, total_calories_burned, status, notes, created_at, updated_at)
    VALUES (1, 'Morning Cardio', current_date_val, start_time_val, end_time_val, 45, 480, 'COMPLETED', 'Morning run', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    RETURNING id INTO workout_id_val;

    INSERT INTO workout_exercises (workout_id, exercise_id, exercise_order, planned_duration_seconds, actual_duration_seconds, calories_burned, created_at)
    VALUES
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Running'), 1, 1800, 1800, 360, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Jump Rope'), 2, 600, 600, 120, CURRENT_TIMESTAMP);

    -- Workout Day 3 (4 days ago) - Lower Body
    current_date_val := CURRENT_DATE - 4;
    start_time_val := '18:00:00';
    end_time_val := '19:20:00';

    INSERT INTO workouts (user_id, workout_name, workout_date, start_time, end_time, total_duration_minutes, total_calories_burned, status, notes, created_at, updated_at)
    VALUES (1, 'Lower Body Power', current_date_val, start_time_val, end_time_val, 80, 550, 'COMPLETED', 'Leg day!', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    RETURNING id INTO workout_id_val;

    INSERT INTO workout_exercises (workout_id, exercise_id, exercise_order, planned_sets, planned_reps, actual_sets, actual_reps, weight_kg, calories_burned, created_at)
    VALUES
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Barbell Squat'), 1, 4, 8, 4, 8, 100.0, 160, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Deadlift'), 2, 4, 6, 4, 6, 120.0, 144, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Cycling'), 3, NULL, NULL, NULL, NULL, 0.0, 180, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Russian Twists'), 4, 3, 20, 3, 20, 10.0, 66, CURRENT_TIMESTAMP);

    -- Workout Day 4 (2 days ago) - Full Body HIIT
    current_date_val := CURRENT_DATE - 2;
    start_time_val := '06:30:00';
    end_time_val := '07:15:00';

    INSERT INTO workouts (user_id, workout_name, workout_date, start_time, end_time, total_duration_minutes, total_calories_burned, status, notes, created_at, updated_at)
    VALUES (1, 'HIIT Training', current_date_val, start_time_val, end_time_val, 45, 420, 'COMPLETED', 'Intense session', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    RETURNING id INTO workout_id_val;

    INSERT INTO workout_exercises (workout_id, exercise_id, exercise_order, planned_sets, planned_reps, actual_sets, actual_reps, calories_burned, created_at)
    VALUES
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Burpees'), 1, 4, 15, 4, 15, 176, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Jump Rope'), 2, 4, NULL, 4, NULL, 156, CURRENT_TIMESTAMP),
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Plank'), 3, 4, NULL, 4, NULL, 88, CURRENT_TIMESTAMP);

    -- Workout Day 5 (Today) - Active Recovery
    current_date_val := CURRENT_DATE;
    start_time_val := '17:00:00';
    end_time_val := '18:00:00';

    INSERT INTO workouts (user_id, workout_name, workout_date, start_time, end_time, total_duration_minutes, total_calories_burned, status, notes, created_at, updated_at)
    VALUES (1, 'Active Recovery', current_date_val, start_time_val, end_time_val, 60, 180, 'COMPLETED', 'Recovery and stretching', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    RETURNING id INTO workout_id_val;

    INSERT INTO workout_exercises (workout_id, exercise_id, exercise_order, planned_duration_seconds, actual_duration_seconds, calories_burned, created_at)
    VALUES
        (workout_id_val, (SELECT id FROM exercises WHERE name = 'Yoga Flow'), 1, 3600, 3600, 180, CURRENT_TIMESTAMP);
END $$;
