package com.fittracker.nutrition.kafka;

import com.fittracker.common.event.MealCreatedEvent;
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

    public void publishMealCreatedEvent(MealCreatedEvent event) {
        try {
            log.info("Publishing MealCreatedEvent for user {}: {} calories",
                    event.getUserId(), event.getTotalCalories());
            kafkaTemplate.send(KafkaTopics.MEAL_CREATED, event.getUserId().toString(), event);
            log.debug("MealCreatedEvent published successfully: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to publish MealCreatedEvent for user {}", event.getUserId(), e);
            // Don't throw exception - event publishing should not break the main flow
        }
    }
}
