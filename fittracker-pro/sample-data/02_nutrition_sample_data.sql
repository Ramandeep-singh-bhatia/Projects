-- FitTracker Pro - Sample Nutrition Data
-- Insert sample food items and meals for testing and demonstration

-- Insert sample food categories (if they don't exist)
INSERT INTO food_categories (name, description, created_at)
VALUES
    ('Proteins', 'High protein foods including meats, eggs, and dairy', CURRENT_TIMESTAMP),
    ('Grains', 'Whole grains, rice, pasta, and bread', CURRENT_TIMESTAMP),
    ('Vegetables', 'Fresh and cooked vegetables', CURRENT_TIMESTAMP),
    ('Fruits', 'Fresh and dried fruits', CURRENT_TIMESTAMP),
    ('Dairy', 'Milk, cheese, yogurt and other dairy products', CURRENT_TIMESTAMP),
    ('Beverages', 'Drinks and liquid nutrition', CURRENT_TIMESTAMP),
    ('Snacks', 'Healthy snacks and treats', CURRENT_TIMESTAMP)
ON CONFLICT (name) DO NOTHING;

-- Insert sample food items
INSERT INTO food_items (name, brand, category_id, serving_size, serving_unit, calories_per_serving, protein_grams, carbs_grams, fat_grams, fiber_grams, sugar_grams, sodium_mg, is_verified, barcode, created_at, updated_at)
VALUES
    -- Proteins
    ('Chicken Breast', 'Generic', (SELECT id FROM food_categories WHERE name = 'Proteins'), 100, 'grams', 165, 31.0, 0.0, 3.6, 0.0, 0.0, 74, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Salmon Fillet', 'Fresh', (SELECT id FROM food_categories WHERE name = 'Proteins'), 100, 'grams', 208, 20.0, 0.0, 13.0, 0.0, 0.0, 59, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Eggs', 'Generic', (SELECT id FROM food_categories WHERE name = 'Proteins'), 50, 'grams', 72, 6.3, 0.4, 4.8, 0.0, 0.2, 71, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Greek Yogurt', 'Chobani', (SELECT id FROM food_categories WHERE name = 'Dairy'), 150, 'grams', 100, 17.0, 6.0, 0.0, 0.0, 4.0, 60, true, '051500255025', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Grains
    ('Brown Rice', 'Generic', (SELECT id FROM food_categories WHERE name = 'Grains'), 100, 'grams', 112, 2.6, 23.5, 0.9, 1.8, 0.4, 5, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Whole Wheat Bread', 'Generic', (SELECT id FROM food_categories WHERE name = 'Grains'), 30, 'grams', 80, 4.0, 14.0, 1.0, 2.0, 2.0, 150, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Oatmeal', 'Quaker', (SELECT id FROM food_categories WHERE name = 'Grains'), 40, 'grams', 150, 5.0, 27.0, 3.0, 4.0, 1.0, 0, true, '030000010303', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Vegetables
    ('Broccoli', 'Fresh', (SELECT id FROM food_categories WHERE name = 'Vegetables'), 100, 'grams', 34, 2.8, 6.6, 0.4, 2.6, 1.7, 33, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Sweet Potato', 'Fresh', (SELECT id FROM food_categories WHERE name = 'Vegetables'), 100, 'grams', 86, 1.6, 20.1, 0.1, 3.0, 4.2, 55, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Spinach', 'Fresh', (SELECT id FROM food_categories WHERE name = 'Vegetables'), 100, 'grams', 23, 2.9, 3.6, 0.4, 2.2, 0.4, 79, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Fruits
    ('Banana', 'Fresh', (SELECT id FROM food_categories WHERE name = 'Fruits'), 100, 'grams', 89, 1.1, 22.8, 0.3, 2.6, 12.2, 1, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Apple', 'Fresh', (SELECT id FROM food_categories WHERE name = 'Fruits'), 100, 'grams', 52, 0.3, 13.8, 0.2, 2.4, 10.4, 1, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Blueberries', 'Fresh', (SELECT id FROM food_categories WHERE name = 'Fruits'), 100, 'grams', 57, 0.7, 14.5, 0.3, 2.4, 10.0, 1, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Beverages
    ('Almond Milk', 'Silk', (SELECT id FROM food_categories WHERE name = 'Beverages'), 240, 'ml', 30, 1.0, 1.0, 2.5, 0.5, 0.0, 170, true, '025293600409', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Protein Shake', 'Optimum Nutrition', (SELECT id FROM food_categories WHERE name = 'Beverages'), 30, 'grams', 120, 24.0, 3.0, 1.0, 1.0, 1.0, 130, true, '748927022657', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

    -- Snacks
    ('Almonds', 'Generic', (SELECT id FROM food_categories WHERE name = 'Snacks'), 28, 'grams', 164, 6.0, 6.0, 14.0, 3.5, 1.2, 0, true, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Peanut Butter', 'Jif', (SELECT id FROM food_categories WHERE name = 'Snacks'), 32, 'grams', 190, 8.0, 7.0, 16.0, 2.0, 3.0, 150, true, '051500255698', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert sample meals for user 1 (John Doe) for the past 7 days
DO $$
DECLARE
    current_date_val DATE;
    meal_id_breakfast BIGINT;
    meal_id_lunch BIGINT;
    meal_id_dinner BIGINT;
    meal_id_snack BIGINT;
BEGIN
    FOR i IN 0..6 LOOP
        current_date_val := CURRENT_DATE - i;

        -- Breakfast
        INSERT INTO meals (user_id, meal_type, meal_date, meal_time, notes, created_at, updated_at)
        VALUES (1, 'BREAKFAST', current_date_val, '08:00:00', 'Morning breakfast', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id INTO meal_id_breakfast;

        INSERT INTO meal_items (meal_id, food_item_id, servings, calories, protein_grams, carbs_grams, fat_grams, created_at)
        VALUES
            (meal_id_breakfast, (SELECT id FROM food_items WHERE name = 'Oatmeal'), 1.5, 225, 7.5, 40.5, 4.5, CURRENT_TIMESTAMP),
            (meal_id_breakfast, (SELECT id FROM food_items WHERE name = 'Banana'), 1.0, 89, 1.1, 22.8, 0.3, CURRENT_TIMESTAMP),
            (meal_id_breakfast, (SELECT id FROM food_items WHERE name = 'Almonds'), 1.0, 164, 6.0, 6.0, 14.0, CURRENT_TIMESTAMP);

        -- Lunch
        INSERT INTO meals (user_id, meal_type, meal_date, meal_time, notes, created_at, updated_at)
        VALUES (1, 'LUNCH', current_date_val, '12:30:00', 'Lunch meal', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id INTO meal_id_lunch;

        INSERT INTO meal_items (meal_id, food_item_id, servings, calories, protein_grams, carbs_grams, fat_grams, created_at)
        VALUES
            (meal_id_lunch, (SELECT id FROM food_items WHERE name = 'Chicken Breast'), 2.0, 330, 62.0, 0.0, 7.2, CURRENT_TIMESTAMP),
            (meal_id_lunch, (SELECT id FROM food_items WHERE name = 'Brown Rice'), 1.5, 168, 3.9, 35.3, 1.4, CURRENT_TIMESTAMP),
            (meal_id_lunch, (SELECT id FROM food_items WHERE name = 'Broccoli'), 1.0, 34, 2.8, 6.6, 0.4, CURRENT_TIMESTAMP);

        -- Dinner
        INSERT INTO meals (user_id, meal_type, meal_date, meal_time, notes, created_at, updated_at)
        VALUES (1, 'DINNER', current_date_val, '19:00:00', 'Evening dinner', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id INTO meal_id_dinner;

        INSERT INTO meal_items (meal_id, food_item_id, servings, calories, protein_grams, carbs_grams, fat_grams, created_at)
        VALUES
            (meal_id_dinner, (SELECT id FROM food_items WHERE name = 'Salmon Fillet'), 1.5, 312, 30.0, 0.0, 19.5, CURRENT_TIMESTAMP),
            (meal_id_dinner, (SELECT id FROM food_items WHERE name = 'Sweet Potato'), 2.0, 172, 3.2, 40.2, 0.2, CURRENT_TIMESTAMP),
            (meal_id_dinner, (SELECT id FROM food_items WHERE name = 'Spinach'), 1.0, 23, 2.9, 3.6, 0.4, CURRENT_TIMESTAMP);

        -- Snack
        INSERT INTO meals (user_id, meal_type, meal_date, meal_time, notes, created_at, updated_at)
        VALUES (1, 'SNACK', current_date_val, '15:00:00', 'Afternoon snack', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id INTO meal_id_snack;

        INSERT INTO meal_items (meal_id, food_item_id, servings, calories, protein_grams, carbs_grams, fat_grams, created_at)
        VALUES
            (meal_id_snack, (SELECT id FROM food_items WHERE name = 'Greek Yogurt'), 1.0, 100, 17.0, 6.0, 0.0, CURRENT_TIMESTAMP),
            (meal_id_snack, (SELECT id FROM food_items WHERE name = 'Blueberries'), 1.0, 57, 0.7, 14.5, 0.3, CURRENT_TIMESTAMP);
    END LOOP;
END $$;
