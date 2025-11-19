-- Create food_items table
CREATE TABLE food_items (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    barcode VARCHAR(50),
    category VARCHAR(50) NOT NULL,
    serving_size VARCHAR(100) NOT NULL,
    serving_unit VARCHAR(20) NOT NULL,
    calories_per_serving DECIMAL(8,2) NOT NULL,
    protein_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    carbs_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    fat_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    fiber_g DECIMAL(6,2) DEFAULT 0,
    sugar_g DECIMAL(6,2) DEFAULT 0,
    sodium_mg DECIMAL(8,2) DEFAULT 0,
    cholesterol_mg DECIMAL(6,2) DEFAULT 0,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_by_user_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_category CHECK (category IN ('FRUITS', 'VEGETABLES', 'GRAINS', 'PROTEIN', 'DAIRY', 'FATS_OILS', 'BEVERAGES', 'SNACKS', 'SWEETS', 'OTHER'))
);

-- Create meals table
CREATE TABLE meals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    meal_date DATE NOT NULL,
    meal_time TIME,
    total_calories DECIMAL(8,2) NOT NULL DEFAULT 0,
    total_protein_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_carbs_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_fat_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_fiber_g DECIMAL(6,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_meal_type CHECK (meal_type IN ('BREAKFAST', 'LUNCH', 'DINNER', 'SNACK'))
);

-- Create meal_items table
CREATE TABLE meal_items (
    id BIGSERIAL PRIMARY KEY,
    meal_id BIGINT NOT NULL,
    food_item_id BIGINT NOT NULL,
    servings DECIMAL(6,2) NOT NULL,
    calories DECIMAL(8,2) NOT NULL,
    protein_g DECIMAL(6,2) NOT NULL,
    carbs_g DECIMAL(6,2) NOT NULL,
    fat_g DECIMAL(6,2) NOT NULL,
    fiber_g DECIMAL(6,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    FOREIGN KEY (food_item_id) REFERENCES food_items(id) ON DELETE RESTRICT
);

-- Create meal_plans table
CREATE TABLE meal_plans (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    target_calories_per_day INT,
    target_protein_g INT,
    target_carbs_g INT,
    target_fat_g INT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create daily_nutrition_summary table for caching daily totals
CREATE TABLE daily_nutrition_summary (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    summary_date DATE NOT NULL,
    total_calories DECIMAL(8,2) NOT NULL DEFAULT 0,
    total_protein_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_carbs_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_fat_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_fiber_g DECIMAL(6,2) DEFAULT 0,
    meals_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, summary_date)
);

-- Create indexes for better query performance
CREATE INDEX idx_food_items_name ON food_items(name);
CREATE INDEX idx_food_items_category ON food_items(category);
CREATE INDEX idx_food_items_barcode ON food_items(barcode);
CREATE INDEX idx_food_items_verified ON food_items(is_verified);

CREATE INDEX idx_meals_user_id ON meals(user_id);
CREATE INDEX idx_meals_date ON meals(meal_date);
CREATE INDEX idx_meals_user_date ON meals(user_id, meal_date);
CREATE INDEX idx_meals_type ON meals(meal_type);

CREATE INDEX idx_meal_items_meal_id ON meal_items(meal_id);
CREATE INDEX idx_meal_items_food_id ON meal_items(food_item_id);

CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_meal_plans_active ON meal_plans(is_active);
CREATE INDEX idx_meal_plans_dates ON meal_plans(start_date, end_date);

CREATE INDEX idx_daily_summary_user_id ON daily_nutrition_summary(user_id);
CREATE INDEX idx_daily_summary_date ON daily_nutrition_summary(summary_date);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_food_items_updated_at BEFORE UPDATE ON food_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meals_updated_at BEFORE UPDATE ON meals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meal_plans_updated_at BEFORE UPDATE ON meal_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_summary_updated_at BEFORE UPDATE ON daily_nutrition_summary
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
