-- FitTracker Pro - Sample Users Data
-- Insert sample user profiles for testing and demonstration

-- Note: These passwords are bcrypt hashed for "Password123!"
-- In production, users should create their own secure passwords

-- Insert sample users
INSERT INTO users (email, password_hash, first_name, last_name, date_of_birth, gender, height_cm, weight_kg, created_at, updated_at)
VALUES
    ('john.doe@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'John', 'Doe', '1990-05-15', 'MALE', 180.0, 85.5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('jane.smith@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Jane', 'Smith', '1992-08-22', 'FEMALE', 165.0, 62.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('mike.johnson@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Mike', 'Johnson', '1988-03-10', 'MALE', 175.0, 90.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('sarah.williams@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Sarah', 'Williams', '1995-11-30', 'FEMALE', 170.0, 58.5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('alex.brown@example.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Alex', 'Brown', '1993-07-18', 'MALE', 182.0, 78.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert user profiles with goals
INSERT INTO user_profiles (user_id, activity_level, fitness_goal, target_weight_kg, target_calories_per_day, target_protein_grams, target_carbs_grams, target_fat_grams, created_at, updated_at)
VALUES
    (1, 'MODERATELY_ACTIVE', 'WEIGHT_LOSS', 80.0, 2200, 150, 220, 70, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 'ACTIVE', 'MAINTENANCE', 62.0, 1800, 100, 200, 60, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (3, 'LIGHTLY_ACTIVE', 'WEIGHT_LOSS', 82.0, 2000, 140, 200, 65, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (4, 'VERY_ACTIVE', 'MUSCLE_GAIN', 62.0, 2400, 140, 280, 75, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (5, 'MODERATELY_ACTIVE', 'MUSCLE_GAIN', 82.0, 2800, 180, 320, 85, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Note: All users have password "Password123!"
-- Recommended test credentials:
-- Email: john.doe@example.com, Password: Password123!
-- Email: jane.smith@example.com, Password: Password123!
