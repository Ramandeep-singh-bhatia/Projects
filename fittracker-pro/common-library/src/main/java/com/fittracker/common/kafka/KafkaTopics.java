package com.fittracker.common.kafka;

public final class KafkaTopics {

    private KafkaTopics() {
        // Utility class
    }

    public static final String USER_REGISTERED = "user.registered";
    public static final String USER_WEIGHT_UPDATED = "user.weight.updated";
    public static final String MEAL_CREATED = "meal.created";
    public static final String WORKOUT_COMPLETED = "workout.completed";
}
