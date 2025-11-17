-- Analytics Service Database Schema
-- This schema tracks user activity, nutrition trends, workout analytics, and goal progress

-- Table: daily_activity_summary
-- Stores aggregated daily activity data for each user
CREATE TABLE daily_activity_summary (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    activity_date DATE NOT NULL,
    total_calories_consumed INT DEFAULT 0,
    total_calories_burned INT DEFAULT 0,
    net_calories INT DEFAULT 0,
    total_protein_g DECIMAL(8,2) DEFAULT 0,
    total_carbs_g DECIMAL(8,2) DEFAULT 0,
    total_fat_g DECIMAL(8,2) DEFAULT 0,
    meals_logged INT DEFAULT 0,
    workouts_completed INT DEFAULT 0,
    total_workout_duration_minutes INT DEFAULT 0,
    active_minutes INT DEFAULT 0,
    steps_count INT DEFAULT 0,
    water_intake_ml INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_activity_date UNIQUE (user_id, activity_date)
);

CREATE INDEX idx_daily_activity_user_date ON daily_activity_summary(user_id, activity_date DESC);
CREATE INDEX idx_daily_activity_date ON daily_activity_summary(activity_date);

-- Table: nutrition_analytics
-- Stores nutrition trends and analysis
CREATE TABLE nutrition_analytics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- DAILY, WEEKLY, MONTHLY
    avg_daily_calories DECIMAL(8,2) DEFAULT 0,
    avg_protein_g DECIMAL(8,2) DEFAULT 0,
    avg_carbs_g DECIMAL(8,2) DEFAULT 0,
    avg_fat_g DECIMAL(8,2) DEFAULT 0,
    total_meals_logged INT DEFAULT 0,
    days_logged INT DEFAULT 0,
    adherence_percentage DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_period_type CHECK (period_type IN ('DAILY', 'WEEKLY', 'MONTHLY'))
);

CREATE INDEX idx_nutrition_analytics_user ON nutrition_analytics(user_id, start_date DESC);
CREATE INDEX idx_nutrition_analytics_period ON nutrition_analytics(period_type, end_date DESC);

-- Table: workout_analytics
-- Stores workout trends and progress tracking
CREATE TABLE workout_analytics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- DAILY, WEEKLY, MONTHLY
    total_workouts INT DEFAULT 0,
    total_duration_minutes INT DEFAULT 0,
    total_calories_burned INT DEFAULT 0,
    avg_workout_duration_minutes DECIMAL(8,2) DEFAULT 0,
    workout_frequency DECIMAL(5,2) DEFAULT 0, -- workouts per week
    most_common_workout_type VARCHAR(50),
    strength_workouts INT DEFAULT 0,
    cardio_workouts INT DEFAULT 0,
    flexibility_workouts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_workout_period_type CHECK (period_type IN ('DAILY', 'WEEKLY', 'MONTHLY'))
);

CREATE INDEX idx_workout_analytics_user ON workout_analytics(user_id, start_date DESC);
CREATE INDEX idx_workout_analytics_period ON workout_analytics(period_type, end_date DESC);

-- Table: user_goals
-- Tracks user fitness goals
CREATE TABLE user_goals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    goal_type VARCHAR(50) NOT NULL, -- WEIGHT_LOSS, WEIGHT_GAIN, MUSCLE_GAIN, ENDURANCE, GENERAL_FITNESS
    target_value DECIMAL(10,2) NOT NULL,
    current_value DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(20) NOT NULL, -- kg, lbs, minutes, calories
    start_date DATE NOT NULL,
    target_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, COMPLETED, ABANDONED, PAUSED
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT chk_goal_type CHECK (goal_type IN ('WEIGHT_LOSS', 'WEIGHT_GAIN', 'MUSCLE_GAIN', 'ENDURANCE', 'GENERAL_FITNESS', 'NUTRITION', 'STRENGTH')),
    CONSTRAINT chk_goal_status CHECK (status IN ('ACTIVE', 'COMPLETED', 'ABANDONED', 'PAUSED'))
);

CREATE INDEX idx_user_goals_user_status ON user_goals(user_id, status);
CREATE INDEX idx_user_goals_target_date ON user_goals(target_date);

-- Table: goal_progress_tracking
-- Tracks progress snapshots for goals over time
CREATE TABLE goal_progress_tracking (
    id BIGSERIAL PRIMARY KEY,
    goal_id BIGINT NOT NULL,
    recorded_date DATE NOT NULL,
    current_value DECIMAL(10,2) NOT NULL,
    progress_percentage DECIMAL(5,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES user_goals(id) ON DELETE CASCADE
);

CREATE INDEX idx_goal_progress_goal_date ON goal_progress_tracking(goal_id, recorded_date DESC);

-- Table: achievements
-- Tracks user achievements and milestones
CREATE TABLE achievements (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    achievement_type VARCHAR(50) NOT NULL, -- STREAK, MILESTONE, GOAL_COMPLETED, PERSONAL_RECORD
    achievement_name VARCHAR(255) NOT NULL,
    description TEXT,
    achievement_date DATE NOT NULL,
    achievement_data JSONB, -- Flexible field for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_achievement_type CHECK (achievement_type IN ('STREAK', 'MILESTONE', 'GOAL_COMPLETED', 'PERSONAL_RECORD', 'CONSISTENCY', 'IMPROVEMENT'))
);

CREATE INDEX idx_achievements_user ON achievements(user_id, achievement_date DESC);
CREATE INDEX idx_achievements_type ON achievements(achievement_type);
CREATE INDEX idx_achievements_data ON achievements USING GIN(achievement_data);

-- Table: weekly_reports
-- Stores generated weekly summary reports
CREATE TABLE weekly_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    total_calories_consumed INT DEFAULT 0,
    total_calories_burned INT DEFAULT 0,
    total_workouts INT DEFAULT 0,
    total_workout_minutes INT DEFAULT 0,
    avg_daily_calories DECIMAL(8,2) DEFAULT 0,
    weight_change_kg DECIMAL(5,2) DEFAULT 0,
    goals_achieved INT DEFAULT 0,
    consistency_score DECIMAL(5,2) DEFAULT 0, -- 0-100 score
    report_data JSONB, -- Additional report metrics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_week_report UNIQUE (user_id, week_start_date)
);

CREATE INDEX idx_weekly_reports_user ON weekly_reports(user_id, week_start_date DESC);

-- Table: monthly_reports
-- Stores generated monthly summary reports
CREATE TABLE monthly_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    total_calories_consumed INT DEFAULT 0,
    total_calories_burned INT DEFAULT 0,
    total_workouts INT DEFAULT 0,
    total_workout_minutes INT DEFAULT 0,
    avg_daily_calories DECIMAL(8,2) DEFAULT 0,
    weight_change_kg DECIMAL(5,2) DEFAULT 0,
    goals_achieved INT DEFAULT 0,
    consistency_score DECIMAL(5,2) DEFAULT 0,
    best_week_start_date DATE,
    report_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_month_report UNIQUE (user_id, year, month),
    CONSTRAINT chk_month CHECK (month >= 1 AND month <= 12)
);

CREATE INDEX idx_monthly_reports_user ON monthly_reports(user_id, year DESC, month DESC);

-- Table: exercise_progress
-- Tracks progress on individual exercises over time
CREATE TABLE exercise_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    exercise_id BIGINT NOT NULL,
    exercise_name VARCHAR(255) NOT NULL,
    recorded_date DATE NOT NULL,
    max_weight_kg DECIMAL(6,2),
    max_reps INT,
    max_duration_seconds INT,
    total_volume DECIMAL(10,2), -- weight * reps * sets
    personal_record BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exercise_progress_user_exercise ON exercise_progress(user_id, exercise_id, recorded_date DESC);
CREATE INDEX idx_exercise_progress_pr ON exercise_progress(user_id, personal_record) WHERE personal_record = TRUE;

-- Table: nutrition_trends
-- Stores calculated nutrition trends and patterns
CREATE TABLE nutrition_trends (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    trend_date DATE NOT NULL,
    trend_type VARCHAR(50) NOT NULL, -- CALORIES, PROTEIN, CARBS, FATS, MACROS_BALANCE
    trend_direction VARCHAR(20), -- INCREASING, DECREASING, STABLE
    trend_value DECIMAL(8,2),
    moving_average DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_trend_type CHECK (trend_type IN ('CALORIES', 'PROTEIN', 'CARBS', 'FATS', 'MACROS_BALANCE', 'MEAL_FREQUENCY')),
    CONSTRAINT chk_trend_direction CHECK (trend_direction IN ('INCREASING', 'DECREASING', 'STABLE'))
);

CREATE INDEX idx_nutrition_trends_user ON nutrition_trends(user_id, trend_date DESC);

-- Triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_daily_activity_summary_updated_at BEFORE UPDATE ON daily_activity_summary FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_nutrition_analytics_updated_at BEFORE UPDATE ON nutrition_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workout_analytics_updated_at BEFORE UPDATE ON workout_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_goals_updated_at BEFORE UPDATE ON user_goals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE daily_activity_summary IS 'Aggregated daily activity metrics for each user';
COMMENT ON TABLE nutrition_analytics IS 'Nutrition trends and analysis over different time periods';
COMMENT ON TABLE workout_analytics IS 'Workout trends and progress tracking over different time periods';
COMMENT ON TABLE user_goals IS 'User fitness goals and targets';
COMMENT ON TABLE goal_progress_tracking IS 'Historical progress snapshots for goals';
COMMENT ON TABLE achievements IS 'User achievements and milestones';
COMMENT ON TABLE weekly_reports IS 'Auto-generated weekly summary reports';
COMMENT ON TABLE monthly_reports IS 'Auto-generated monthly summary reports';
COMMENT ON TABLE exercise_progress IS 'Individual exercise performance tracking';
COMMENT ON TABLE nutrition_trends IS 'Calculated nutrition trends and patterns';
