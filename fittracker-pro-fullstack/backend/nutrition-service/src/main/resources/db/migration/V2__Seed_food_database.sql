-- Seed food database with common foods
-- All values are per 100g serving unless otherwise noted

-- FRUITS
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, fiber_g, sugar_g, is_verified) VALUES
('Apple', 'FRUITS', '100', 'g', 52, 0.3, 14, 0.2, 2.4, 10.4, true),
('Banana', 'FRUITS', '100', 'g', 89, 1.1, 23, 0.3, 2.6, 12.2, true),
('Orange', 'FRUITS', '100', 'g', 47, 0.9, 12, 0.1, 2.4, 9.4, true),
('Strawberries', 'FRUITS', '100', 'g', 32, 0.7, 7.7, 0.3, 2.0, 4.9, true),
('Blueberries', 'FRUITS', '100', 'g', 57, 0.7, 14, 0.3, 2.4, 10, true),
('Grapes', 'FRUITS', '100', 'g', 69, 0.7, 18, 0.2, 0.9, 15, true),
('Watermelon', 'FRUITS', '100', 'g', 30, 0.6, 7.6, 0.2, 0.4, 6.2, true),
('Mango', 'FRUITS', '100', 'g', 60, 0.8, 15, 0.4, 1.6, 13.7, true),
('Pineapple', 'FRUITS', '100', 'g', 50, 0.5, 13, 0.1, 1.4, 9.9, true),
('Avocado', 'FRUITS', '100', 'g', 160, 2.0, 8.5, 14.7, 6.7, 0.7, true);

-- VEGETABLES
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, fiber_g, sugar_g, is_verified) VALUES
('Broccoli', 'VEGETABLES', '100', 'g', 34, 2.8, 7, 0.4, 2.6, 1.7, true),
('Carrots', 'VEGETABLES', '100', 'g', 41, 0.9, 10, 0.2, 2.8, 4.7, true),
('Spinach', 'VEGETABLES', '100', 'g', 23, 2.9, 3.6, 0.4, 2.2, 0.4, true),
('Tomato', 'VEGETABLES', '100', 'g', 18, 0.9, 3.9, 0.2, 1.2, 2.6, true),
('Cucumber', 'VEGETABLES', '100', 'g', 16, 0.7, 3.6, 0.1, 0.5, 1.7, true),
('Bell Pepper', 'VEGETABLES', '100', 'g', 31, 1.0, 6, 0.3, 2.1, 4.2, true),
('Lettuce', 'VEGETABLES', '100', 'g', 15, 1.4, 2.9, 0.2, 1.3, 0.8, true),
('Cauliflower', 'VEGETABLES', '100', 'g', 25, 1.9, 5, 0.3, 2.0, 1.9, true),
('Zucchini', 'VEGETABLES', '100', 'g', 17, 1.2, 3.1, 0.3, 1.0, 2.5, true),
('Sweet Potato', 'VEGETABLES', '100', 'g', 86, 1.6, 20, 0.1, 3.0, 4.2, true);

-- GRAINS
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, fiber_g, sugar_g, is_verified) VALUES
('Brown Rice (cooked)', 'GRAINS', '100', 'g', 111, 2.6, 23, 0.9, 1.8, 0.4, true),
('White Rice (cooked)', 'GRAINS', '100', 'g', 130, 2.7, 28, 0.3, 0.4, 0.1, true),
('Quinoa (cooked)', 'GRAINS', '100', 'g', 120, 4.4, 21, 1.9, 2.8, 0.9, true),
('Oatmeal (cooked)', 'GRAINS', '100', 'g', 71, 2.5, 12, 1.5, 1.7, 0.3, true),
('Whole Wheat Bread', 'GRAINS', '100', 'g', 247, 13, 41, 3.4, 6.0, 5.0, true),
('White Bread', 'GRAINS', '100', 'g', 265, 9.0, 49, 3.2, 2.7, 5.0, true),
('Pasta (cooked)', 'GRAINS', '100', 'g', 131, 5.0, 25, 1.1, 1.8, 0.6, true),
('Corn', 'GRAINS', '100', 'g', 86, 3.3, 19, 1.4, 2.0, 3.2, true);

-- PROTEIN
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, fiber_g, sodium_mg, is_verified) VALUES
('Chicken Breast (cooked)', 'PROTEIN', '100', 'g', 165, 31, 0, 3.6, 0, 74, true),
('Salmon (cooked)', 'PROTEIN', '100', 'g', 206, 22, 0, 13, 0, 59, true),
('Tuna (canned in water)', 'PROTEIN', '100', 'g', 116, 26, 0, 0.8, 0, 247, true),
('Eggs (whole)', 'PROTEIN', '100', 'g', 155, 13, 1.1, 11, 0, 124, true),
('Ground Beef (lean)', 'PROTEIN', '100', 'g', 217, 26, 0, 12, 0, 72, true),
('Turkey Breast (cooked)', 'PROTEIN', '100', 'g', 135, 30, 0, 0.7, 0, 98, true),
('Pork Chop (cooked)', 'PROTEIN', '100', 'g', 231, 26, 0, 14, 0, 62, true),
('Tofu', 'PROTEIN', '100', 'g', 76, 8.0, 1.9, 4.8, 0.3, 7, true),
('Chickpeas (cooked)', 'PROTEIN', '100', 'g', 164, 8.9, 27, 2.6, 7.6, 7, true),
('Black Beans (cooked)', 'PROTEIN', '100', 'g', 132, 8.9, 24, 0.5, 8.7, 2, true),
('Lentils (cooked)', 'PROTEIN', '100', 'g', 116, 9.0, 20, 0.4, 7.9, 2, true);

-- DAIRY
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, sugar_g, is_verified) VALUES
('Whole Milk', 'DAIRY', '100', 'ml', 61, 3.2, 4.8, 3.3, 5.1, true),
('Skim Milk', 'DAIRY', '100', 'ml', 34, 3.4, 5.0, 0.1, 5.0, true),
('Greek Yogurt (plain)', 'DAIRY', '100', 'g', 59, 10, 3.6, 0.4, 3.2, true),
('Regular Yogurt (plain)', 'DAIRY', '100', 'g', 61, 3.5, 4.7, 3.3, 4.7, true),
('Cheddar Cheese', 'DAIRY', '100', 'g', 403, 25, 1.3, 33, 0.5, true),
('Mozzarella Cheese', 'DAIRY', '100', 'g', 280, 28, 2.2, 17, 1.0, true),
('Cottage Cheese (low-fat)', 'DAIRY', '100', 'g', 72, 12, 3.4, 1.0, 2.7, true),
('Butter', 'DAIRY', '100', 'g', 717, 0.9, 0.1, 81, 0.1, true);

-- NUTS AND SEEDS
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, fiber_g, is_verified) VALUES
('Almonds', 'PROTEIN', '100', 'g', 579, 21, 22, 50, 12.5, true),
('Walnuts', 'PROTEIN', '100', 'g', 654, 15, 14, 65, 6.7, true),
('Peanuts', 'PROTEIN', '100', 'g', 567, 26, 16, 49, 8.5, true),
('Cashews', 'PROTEIN', '100', 'g', 553, 18, 30, 44, 3.3, true),
('Peanut Butter', 'PROTEIN', '100', 'g', 588, 25, 20, 50, 6.0, true),
('Chia Seeds', 'PROTEIN', '100', 'g', 486, 17, 42, 31, 34.4, true),
('Flax Seeds', 'PROTEIN', '100', 'g', 534, 18, 29, 42, 27.3, true);

-- BEVERAGES
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, sugar_g, is_verified) VALUES
('Water', 'BEVERAGES', '100', 'ml', 0, 0, 0, 0, 0, true),
('Coffee (black)', 'BEVERAGES', '100', 'ml', 1, 0.1, 0, 0, 0, true),
('Green Tea', 'BEVERAGES', '100', 'ml', 1, 0, 0.3, 0, 0, true),
('Orange Juice', 'BEVERAGES', '100', 'ml', 45, 0.7, 10, 0.2, 8.4, true),
('Apple Juice', 'BEVERAGES', '100', 'ml', 46, 0.1, 11, 0.1, 10, true),
('Almond Milk (unsweetened)', 'BEVERAGES', '100', 'ml', 13, 0.4, 0.2, 1.0, 0, true),
('Soda (cola)', 'BEVERAGES', '100', 'ml', 41, 0, 10.6, 0, 10.6, true);

-- FATS AND OILS
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, is_verified) VALUES
('Olive Oil', 'FATS_OILS', '100', 'ml', 884, 0, 0, 100, true),
('Coconut Oil', 'FATS_OILS', '100', 'g', 862, 0, 0, 100, true),
('Avocado Oil', 'FATS_OILS', '100', 'ml', 884, 0, 0, 100, true);

-- SNACKS
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, fiber_g, sugar_g, is_verified) VALUES
('Potato Chips', 'SNACKS', '100', 'g', 536, 6.6, 53, 34, 4.2, 0.4, true),
('Pretzels', 'SNACKS', '100', 'g', 380, 10, 80, 2.6, 2.9, 5.0, true),
('Popcorn (air-popped)', 'SNACKS', '100', 'g', 382, 12, 78, 4.5, 14.5, 0.9, true),
('Granola Bar', 'SNACKS', '100', 'g', 471, 9.7, 64, 20, 6.9, 28, true),
('Trail Mix', 'SNACKS', '100', 'g', 462, 13, 45, 29, 7.0, 30, true);

-- SWEETS
INSERT INTO food_items (name, category, serving_size, serving_unit, calories_per_serving, protein_g, carbs_g, fat_g, sugar_g, is_verified) VALUES
('Chocolate (dark 70%)', 'SWEETS', '100', 'g', 598, 7.9, 46, 43, 24, true),
('Chocolate (milk)', 'SWEETS', '100', 'g', 535, 7.7, 59, 30, 52, true),
('Ice Cream (vanilla)', 'SWEETS', '100', 'g', 207, 3.5, 24, 11, 21, true),
('Cookies (chocolate chip)', 'SWEETS', '100', 'g', 488, 5.4, 68, 22, 39, true),
('Cake (chocolate)', 'SWEETS', '100', 'g', 371, 4.9, 50, 17, 32, true),
('Honey', 'SWEETS', '100', 'g', 304, 0.3, 82, 0, 82, true);

-- Update sequence to current value
SELECT setval('food_items_id_seq', (SELECT MAX(id) FROM food_items));
