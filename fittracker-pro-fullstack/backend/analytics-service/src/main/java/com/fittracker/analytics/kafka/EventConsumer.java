package com.fittracker.analytics.kafka;

import com.fittracker.analytics.service.AnalyticsService;
import com.fittracker.common.event.MealCreatedEvent;
import com.fittracker.common.event.UserRegisteredEvent;
import com.fittracker.common.event.UserWeightUpdatedEvent;
import com.fittracker.common.event.WorkoutCompletedEvent;
import com.fittracker.common.kafka.KafkaTopics;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class EventConsumer {

    private final AnalyticsService analyticsService;

    @KafkaListener(topics = KafkaTopics.USER_REGISTERED, groupId = "analytics-service-group")
    public void handleUserRegisteredEvent(UserRegisteredEvent event) {
        try {
            log.info("Received UserRegisteredEvent for user {}", event.getUserId());

            // Create initial daily activity summary for the user
            analyticsService.getOrCreateDailySummary(event.getUserId(), event.getRegisteredAt().toLocalDate());

            log.debug("Processed UserRegisteredEvent: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to process UserRegisteredEvent for user {}", event.getUserId(), e);
            // Consider implementing dead letter queue or retry logic
        }
    }

    @KafkaListener(topics = KafkaTopics.USER_WEIGHT_UPDATED, groupId = "analytics-service-group")
    public void handleUserWeightUpdatedEvent(UserWeightUpdatedEvent event) {
        try {
            log.info("Received UserWeightUpdatedEvent for user {}: {} kg",
                    event.getUserId(), event.getWeightKg());

            // Weight updates are tracked in the User Service
            // This event is logged for potential future analytics

            log.debug("Processed UserWeightUpdatedEvent: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to process UserWeightUpdatedEvent for user {}", event.getUserId(), e);
        }
    }

    @KafkaListener(topics = KafkaTopics.MEAL_CREATED, groupId = "analytics-service-group")
    public void handleMealCreatedEvent(MealCreatedEvent event) {
        try {
            log.info("Received MealCreatedEvent for user {}: {} calories",
                    event.getUserId(), event.getTotalCalories());

            // Update daily activity summary with meal data
            analyticsService.updateMealData(
                    event.getUserId(),
                    event.getMealDate(),
                    event.getTotalCalories(),
                    event.getTotalProteinG().doubleValue(),
                    event.getTotalCarbsG().doubleValue(),
                    event.getTotalFatG().doubleValue()
            );

            log.debug("Processed MealCreatedEvent: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to process MealCreatedEvent for user {}", event.getUserId(), e);
        }
    }

    @KafkaListener(topics = KafkaTopics.WORKOUT_COMPLETED, groupId = "analytics-service-group")
    public void handleWorkoutCompletedEvent(WorkoutCompletedEvent event) {
        try {
            log.info("Received WorkoutCompletedEvent for user {}: {} minutes, {} calories",
                    event.getUserId(), event.getDurationMinutes(), event.getCaloriesBurned());

            // Update daily activity summary with workout data
            analyticsService.updateWorkoutData(
                    event.getUserId(),
                    event.getWorkoutDate(),
                    event.getCaloriesBurned(),
                    event.getDurationMinutes()
            );

            log.debug("Processed WorkoutCompletedEvent: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to process WorkoutCompletedEvent for user {}", event.getUserId(), e);
        }
    }
}
