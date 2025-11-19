-- Create exercise_categories table
CREATE TABLE exercise_categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create exercises table
CREATE TABLE exercises (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id BIGINT NOT NULL,
    description TEXT,
    muscle_groups VARCHAR(255),
    equipment VARCHAR(100),
    difficulty_level VARCHAR(20) NOT NULL,
    calories_per_minute DECIMAL(5,2) NOT NULL DEFAULT 5.0,
    instructions TEXT,
    video_url VARCHAR(500),
    image_url VARCHAR(500),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_by_user_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES exercise_categories(id) ON DELETE RESTRICT,
    CONSTRAINT chk_difficulty CHECK (difficulty_level IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED'))
);

-- Create workout_templates table
CREATE TABLE workout_templates (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL,
    workout_type VARCHAR(50) NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,
    calories_estimate INT,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_template_difficulty CHECK (difficulty_level IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')),
    CONSTRAINT chk_workout_type CHECK (workout_type IN ('STRENGTH', 'CARDIO', 'HIIT', 'FLEXIBILITY', 'MIXED'))
);

-- Create workout_template_exercises table
CREATE TABLE workout_template_exercises (
    id BIGSERIAL PRIMARY KEY,
    template_id BIGINT NOT NULL,
    exercise_id BIGINT NOT NULL,
    exercise_order INT NOT NULL,
    sets INT,
    reps INT,
    duration_seconds INT,
    rest_seconds INT NOT NULL DEFAULT 60,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES workout_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE RESTRICT
);

-- Create workouts table
CREATE TABLE workouts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    template_id BIGINT,
    workout_name VARCHAR(255) NOT NULL,
    workout_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_duration_minutes INT,
    total_calories_burned INT,
    status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES workout_templates(id) ON DELETE SET NULL,
    CONSTRAINT chk_status CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
);

-- Create workout_exercises table
CREATE TABLE workout_exercises (
    id BIGSERIAL PRIMARY KEY,
    workout_id BIGINT NOT NULL,
    exercise_id BIGINT NOT NULL,
    exercise_order INT NOT NULL,
    planned_sets INT,
    planned_reps INT,
    planned_duration_seconds INT,
    actual_sets INT,
    actual_reps INT,
    actual_duration_seconds INT,
    weight_kg DECIMAL(6,2),
    calories_burned INT,
    notes TEXT,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE RESTRICT
);

-- Create workout_sets table (for detailed set tracking)
CREATE TABLE workout_sets (
    id BIGSERIAL PRIMARY KEY,
    workout_exercise_id BIGINT NOT NULL,
    set_number INT NOT NULL,
    reps INT,
    weight_kg DECIMAL(6,2),
    duration_seconds INT,
    rest_seconds INT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_exercises_category ON exercises(category_id);
CREATE INDEX idx_exercises_difficulty ON exercises(difficulty_level);
CREATE INDEX idx_exercises_name ON exercises(name);
CREATE INDEX idx_exercises_verified ON exercises(is_verified);

CREATE INDEX idx_templates_user ON workout_templates(user_id);
CREATE INDEX idx_templates_type ON workout_templates(workout_type);
CREATE INDEX idx_templates_public ON workout_templates(is_public);

CREATE INDEX idx_template_exercises_template ON workout_template_exercises(template_id);
CREATE INDEX idx_template_exercises_exercise ON workout_template_exercises(exercise_id);

CREATE INDEX idx_workouts_user ON workouts(user_id);
CREATE INDEX idx_workouts_date ON workouts(workout_date);
CREATE INDEX idx_workouts_status ON workouts(status);
CREATE INDEX idx_workouts_user_date ON workouts(user_id, workout_date);

CREATE INDEX idx_workout_exercises_workout ON workout_exercises(workout_id);
CREATE INDEX idx_workout_exercises_exercise ON workout_exercises(exercise_id);

CREATE INDEX idx_workout_sets_workout_exercise ON workout_sets(workout_exercise_id);

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_exercise_categories_updated_at BEFORE UPDATE ON exercise_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON exercises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workout_templates_updated_at BEFORE UPDATE ON workout_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workouts_updated_at BEFORE UPDATE ON workouts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
