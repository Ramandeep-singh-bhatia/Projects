-- Insert exercise categories
INSERT INTO exercise_categories (name, description) VALUES
('STRENGTH', 'Resistance and weight training exercises'),
('CARDIO', 'Cardiovascular and aerobic exercises'),
('FLEXIBILITY', 'Stretching and mobility exercises'),
('CORE', 'Abdominal and core strengthening exercises'),
('HIIT', 'High-intensity interval training exercises'),
('PLYOMETRICS', 'Explosive and jumping exercises'),
('BODYWEIGHT', 'No equipment required exercises');

-- STRENGTH EXERCISES
INSERT INTO exercises (name, category_id, description, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions, is_verified) VALUES
('Barbell Bench Press', 1, 'Classic chest exercise', 'Chest, Triceps, Shoulders', 'Barbell, Bench', 'INTERMEDIATE', 7.5, 'Lie on bench, lower bar to chest, press up', true),
('Barbell Squat', 1, 'Compound leg exercise', 'Quads, Glutes, Hamstrings', 'Barbell, Squat Rack', 'INTERMEDIATE', 8.0, 'Bar on shoulders, squat down, stand up', true),
('Deadlift', 1, 'Full body strength exercise', 'Back, Legs, Core', 'Barbell', 'ADVANCED', 9.0, 'Lift bar from ground to standing position', true),
('Dumbbell Shoulder Press', 1, 'Shoulder strength builder', 'Shoulders, Triceps', 'Dumbbells', 'BEGINNER', 6.5, 'Press dumbbells overhead from shoulder height', true),
('Barbell Row', 1, 'Back thickness builder', 'Back, Biceps', 'Barbell', 'INTERMEDIATE', 7.0, 'Bend over, pull bar to lower chest', true),
('Pull-ups', 1, 'Bodyweight back exercise', 'Back, Biceps', 'Pull-up Bar', 'INTERMEDIATE', 8.5, 'Hang from bar, pull chin over bar', true),
('Dips', 1, 'Triceps and chest exercise', 'Triceps, Chest', 'Dip Bars', 'INTERMEDIATE', 7.5, 'Support on bars, lower body, push back up', true),
('Lunges', 1, 'Single leg strength', 'Quads, Glutes', 'Dumbbells (optional)', 'BEGINNER', 6.0, 'Step forward, lower back knee, return', true),
('Leg Press', 1, 'Machine leg exercise', 'Quads, Glutes', 'Leg Press Machine', 'BEGINNER', 7.0, 'Push platform away with feet', true),
('Bicep Curls', 1, 'Arm isolation', 'Biceps', 'Dumbbells/Barbell', 'BEGINNER', 4.5, 'Curl weight from thigh to shoulder', true),
('Tricep Extensions', 1, 'Tricep isolation', 'Triceps', 'Dumbbell', 'BEGINNER', 4.5, 'Extend weight overhead', true),
('Lat Pulldown', 1, 'Back width builder', 'Back, Biceps', 'Cable Machine', 'BEGINNER', 6.0, 'Pull bar down to chest level', true);

-- CARDIO EXERCISES
INSERT INTO exercises (name, category_id, description, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions, is_verified) VALUES
('Running', 2, 'Outdoor or treadmill running', 'Legs, Cardio', 'None/Treadmill', 'BEGINNER', 10.0, 'Run at steady pace', true),
('Cycling', 2, 'Bike riding exercise', 'Legs, Cardio', 'Bike/Stationary Bike', 'BEGINNER', 8.0, 'Pedal at steady pace', true),
('Jump Rope', 2, 'High-intensity cardio', 'Full Body, Cardio', 'Jump Rope', 'BEGINNER', 12.0, 'Jump over rope continuously', true),
('Rowing', 2, 'Full body cardio', 'Back, Legs, Cardio', 'Rowing Machine', 'INTERMEDIATE', 9.5, 'Pull handle while extending legs', true),
('Elliptical', 2, 'Low-impact cardio', 'Full Body', 'Elliptical Machine', 'BEGINNER', 7.5, 'Pedal in elliptical motion', true),
('Swimming', 2, 'Full body water cardio', 'Full Body', 'Pool', 'INTERMEDIATE', 11.0, 'Swim laps using various strokes', true),
('Stair Climbing', 2, 'Lower body cardio', 'Legs, Glutes, Cardio', 'Stairs/Machine', 'BEGINNER', 9.0, 'Climb stairs at steady pace', true),
('Walking', 2, 'Low-intensity cardio', 'Legs', 'None', 'BEGINNER', 4.5, 'Walk at brisk pace', true);

-- FLEXIBILITY EXERCISES
INSERT INTO exercises (name, category_id, description, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions, is_verified) VALUES
('Hamstring Stretch', 3, 'Leg flexibility', 'Hamstrings', 'None', 'BEGINNER', 2.0, 'Reach toward toes while seated', true),
('Quad Stretch', 3, 'Front thigh stretch', 'Quadriceps', 'None', 'BEGINNER', 2.0, 'Pull foot toward glutes while standing', true),
('Shoulder Stretch', 3, 'Upper body mobility', 'Shoulders', 'None', 'BEGINNER', 2.0, 'Pull arm across body', true),
('Hip Flexor Stretch', 3, 'Hip mobility', 'Hip Flexors', 'None', 'BEGINNER', 2.0, 'Lunge position, push hips forward', true),
('Cat-Cow Stretch', 3, 'Spine mobility', 'Back, Core', 'None', 'BEGINNER', 2.5, 'Alternate arching and rounding spine', true),
('Downward Dog', 3, 'Full body stretch', 'Hamstrings, Shoulders, Back', 'None', 'BEGINNER', 3.0, 'Inverted V position', true),
('Childs Pose', 3, 'Relaxation stretch', 'Back, Hips', 'None', 'BEGINNER', 2.0, 'Sit back on heels, arms extended', true);

-- CORE EXERCISES
INSERT INTO exercises (name, category_id, description, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions, is_verified) VALUES
('Plank', 4, 'Isometric core exercise', 'Core, Shoulders', 'None', 'BEGINNER', 5.0, 'Hold straight body position on forearms', true),
('Crunches', 4, 'Ab isolation', 'Abs', 'None', 'BEGINNER', 4.0, 'Lift shoulders off ground', true),
('Russian Twists', 4, 'Oblique exercise', 'Obliques, Core', 'Weight (optional)', 'INTERMEDIATE', 5.5, 'Twist torso side to side while seated', true),
('Leg Raises', 4, 'Lower ab exercise', 'Lower Abs', 'None', 'INTERMEDIATE', 5.0, 'Raise legs from lying position', true),
('Mountain Climbers', 4, 'Dynamic core cardio', 'Core, Full Body', 'None', 'INTERMEDIATE', 8.0, 'Alternate bringing knees to chest in plank', true),
('Bicycle Crunches', 4, 'Oblique and ab exercise', 'Abs, Obliques', 'None', 'BEGINNER', 5.5, 'Alternate elbow to opposite knee', true),
('Dead Bug', 4, 'Core stability', 'Core', 'None', 'BEGINNER', 4.0, 'Alternate extending opposite arm and leg', true);

-- HIIT EXERCISES
INSERT INTO exercises (name, category_id, description, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions, is_verified) VALUES
('Burpees', 5, 'Full body explosive exercise', 'Full Body', 'None', 'INTERMEDIATE', 12.0, 'Drop to plank, jump up', true),
('High Knees', 5, 'Cardio intensity', 'Legs, Cardio', 'None', 'BEGINNER', 10.0, 'Run in place with high knee lift', true),
('Jump Squats', 5, 'Explosive leg exercise', 'Legs, Glutes', 'None', 'INTERMEDIATE', 11.0, 'Squat then jump explosively', true),
('Box Jumps', 5, 'Plyometric leg exercise', 'Legs, Glutes', 'Box/Platform', 'INTERMEDIATE', 10.5, 'Jump onto elevated platform', true),
('Battle Ropes', 5, 'Upper body cardio', 'Arms, Shoulders, Core', 'Battle Ropes', 'INTERMEDIATE', 11.0, 'Create waves with heavy ropes', true),
('Kettlebell Swings', 5, 'Explosive hip exercise', 'Glutes, Hamstrings, Core', 'Kettlebell', 'INTERMEDIATE', 10.0, 'Swing kettlebell from hips to eye level', true);

-- PLYOMETRIC EXERCISES
INSERT INTO exercises (name, category_id, description, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions, is_verified) VALUES
('Jumping Jacks', 6, 'Full body warm-up', 'Full Body', 'None', 'BEGINNER', 8.0, 'Jump while spreading legs and raising arms', true),
('Tuck Jumps', 6, 'Explosive jumping', 'Legs, Core', 'None', 'ADVANCED', 12.0, 'Jump and bring knees to chest', true),
('Broad Jumps', 6, 'Forward jumping', 'Legs, Glutes', 'None', 'INTERMEDIATE', 9.0, 'Jump forward for maximum distance', true),
('Depth Jumps', 6, 'Advanced plyometric', 'Legs, Core', 'Box/Platform', 'ADVANCED', 11.0, 'Step off box and immediately jump', true);

-- BODYWEIGHT EXERCISES
INSERT INTO exercises (name, category_id, description, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions, is_verified) VALUES
('Push-ups', 7, 'Upper body bodyweight', 'Chest, Triceps, Shoulders', 'None', 'BEGINNER', 7.0, 'Lower chest to ground, push up', true),
('Squats', 7, 'Leg bodyweight', 'Quads, Glutes', 'None', 'BEGINNER', 6.0, 'Lower hips to knee level, stand up', true),
('Sit-ups', 7, 'Ab exercise', 'Abs', 'None', 'BEGINNER', 4.5, 'Raise torso to seated position', true),
('Wall Sits', 7, 'Isometric leg exercise', 'Quads, Glutes', 'None', 'BEGINNER', 5.5, 'Hold seated position against wall', true),
('Glute Bridges', 7, 'Hip extension', 'Glutes, Hamstrings', 'None', 'BEGINNER', 4.5, 'Lift hips from lying position', true),
('Superman', 7, 'Lower back exercise', 'Lower Back, Glutes', 'None', 'BEGINNER', 3.5, 'Lift arms and legs while lying on stomach', true);

-- Update sequences
SELECT setval('exercise_categories_id_seq', (SELECT MAX(id) FROM exercise_categories));
SELECT setval('exercises_id_seq', (SELECT MAX(id) FROM exercises));
