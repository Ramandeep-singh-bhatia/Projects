-- Create databases for each microservice
CREATE DATABASE fittracker_user;
CREATE DATABASE fittracker_nutrition;
CREATE DATABASE fittracker_workout;
CREATE DATABASE fittracker_analytics;

-- Grant all privileges to fittracker user
GRANT ALL PRIVILEGES ON DATABASE fittracker_user TO fittracker;
GRANT ALL PRIVILEGES ON DATABASE fittracker_nutrition TO fittracker;
GRANT ALL PRIVILEGES ON DATABASE fittracker_workout TO fittracker;
GRANT ALL PRIVILEGES ON DATABASE fittracker_analytics TO fittracker;
