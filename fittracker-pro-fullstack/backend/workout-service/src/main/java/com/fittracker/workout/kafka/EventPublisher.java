package com.fittracker.workout.kafka;

import com.fittracker.common.event.WorkoutCompletedEvent;
import com.fittracker.common.kafka.KafkaTopics;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class EventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publishWorkoutCompletedEvent(WorkoutCompletedEvent event) {
        try {
            log.info("Publishing WorkoutCompletedEvent for user {}: {} minutes, {} calories",
                    event.getUserId(), event.getDurationMinutes(), event.getCaloriesBurned());
            kafkaTemplate.send(KafkaTopics.WORKOUT_COMPLETED, event.getUserId().toString(), event);
            log.debug("WorkoutCompletedEvent published successfully: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to publish WorkoutCompletedEvent for user {}", event.getUserId(), e);
            // Don't throw exception - event publishing should not break the main flow
        }
    }
}
