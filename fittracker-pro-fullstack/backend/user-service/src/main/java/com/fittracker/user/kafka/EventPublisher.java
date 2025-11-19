package com.fittracker.user.kafka;

import com.fittracker.common.event.UserRegisteredEvent;
import com.fittracker.common.event.UserWeightUpdatedEvent;
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

    public void publishUserRegisteredEvent(UserRegisteredEvent event) {
        try {
            log.info("Publishing UserRegisteredEvent for user {}", event.getUserId());
            kafkaTemplate.send(KafkaTopics.USER_REGISTERED, event.getUserId().toString(), event);
            log.debug("UserRegisteredEvent published successfully: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to publish UserRegisteredEvent for user {}", event.getUserId(), e);
            // Don't throw exception - event publishing should not break the main flow
        }
    }

    public void publishUserWeightUpdatedEvent(UserWeightUpdatedEvent event) {
        try {
            log.info("Publishing UserWeightUpdatedEvent for user {}", event.getUserId());
            kafkaTemplate.send(KafkaTopics.USER_WEIGHT_UPDATED, event.getUserId().toString(), event);
            log.debug("UserWeightUpdatedEvent published successfully: {}", event.getEventId());
        } catch (Exception e) {
            log.error("Failed to publish UserWeightUpdatedEvent for user {}", event.getUserId(), e);
            // Don't throw exception - event publishing should not break the main flow
        }
    }
}
