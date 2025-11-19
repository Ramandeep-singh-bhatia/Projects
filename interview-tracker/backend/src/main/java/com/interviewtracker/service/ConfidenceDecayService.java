package com.interviewtracker.service;

import com.interviewtracker.model.*;
import com.interviewtracker.repository.ConfidenceHistoryRepository;
import com.interviewtracker.repository.TopicRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ConfidenceDecayService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private ConfidenceHistoryRepository confidenceHistoryRepository;

    @Autowired
    private SettingsService settingsService;

    /**
     * Scheduled task that runs daily at midnight to apply confidence decay
     */
    @Scheduled(cron = "0 0 0 * * *") // Run at midnight daily
    @Transactional
    public void applyConfidenceDecay() {
        Settings settings = settingsService.getSettings();

        if (!settings.getConfidenceDecayEnabled()) {
            return;
        }

        List<Topic> allTopics = topicRepository.findAll();
        int decayedCount = 0;

        for (Topic topic : allTopics) {
            if (topic.getDecayDisabled() != null && topic.getDecayDisabled()) {
                continue; // Skip topics with decay disabled
            }

            if (topic.getLastStudiedDate() == null) {
                continue; // Skip topics that have never been studied
            }

            long daysSinceLastStudied = ChronoUnit.DAYS.between(
                    topic.getLastStudiedDate().toLocalDate(),
                    LocalDateTime.now().toLocalDate()
            );

            if (daysSinceLastStudied <= settings.getDecayThresholdDays()) {
                continue; // No decay yet
            }

            // Calculate decay
            double decayRate = getDecayRateForTopic(topic, settings);
            long decayIntervals = (daysSinceLastStudied - settings.getDecayThresholdDays()) / settings.getDecayIntervalDays();

            if (decayIntervals > 0) {
                double totalDecay = decayRate * decayIntervals;
                int newConfidence = Math.max(1, topic.getConfidence() - (int) Math.ceil(totalDecay));

                if (newConfidence < topic.getConfidence()) {
                    // Apply decay
                    int oldConfidence = topic.getConfidence();
                    topic.setConfidence(newConfidence);
                    topicRepository.save(topic);

                    // Record in history
                    ConfidenceHistory history = new ConfidenceHistory();
                    history.setTopic(topic);
                    history.setOldConfidence(oldConfidence);
                    history.setNewConfidence(newConfidence);
                    history.setChangeReason(ChangeReason.DECAY);
                    history.setNotes("Automatic decay after " + daysSinceLastStudied + " days");
                    confidenceHistoryRepository.save(history);

                    decayedCount++;
                }
            }
        }

        System.out.println("Confidence decay applied to " + decayedCount + " topics");
    }

    private double getDecayRateForTopic(Topic topic, Settings settings) {
        if (topic instanceof DSATopic) {
            DifficultyLevel difficulty = ((DSATopic) topic).getDifficulty();
            return switch (difficulty) {
                case EASY -> settings.getDecayRateEasy();
                case MEDIUM -> settings.getDecayRateMedium();
                case HARD -> settings.getDecayRateHard();
            };
        }
        return settings.getDecayRate(); // Default rate for non-DSA topics
    }

    /**
     * Manually trigger decay (for admin/testing)
     */
    @Transactional
    public int applyDecayManually() {
        applyConfidenceDecay();
        return Math.toIntExact(confidenceHistoryRepository.countByTopicIdAndChangeReason(null, ChangeReason.DECAY));
    }

    /**
     * Preview upcoming decay for all topics
     */
    public List<Map<String, Object>> previewDecay() {
        Settings settings = settingsService.getSettings();
        List<Topic> allTopics = topicRepository.findAll();
        List<Map<String, Object>> previews = new ArrayList<>();

        for (Topic topic : allTopics) {
            if (topic.getDecayDisabled() != null && topic.getDecayDisabled()) {
                continue;
            }

            if (topic.getLastStudiedDate() == null) {
                continue;
            }

            long daysSinceLastStudied = ChronoUnit.DAYS.between(
                    topic.getLastStudiedDate().toLocalDate(),
                    LocalDateTime.now().toLocalDate()
            );

            if (daysSinceLastStudied <= settings.getDecayThresholdDays()) {
                continue;
            }

            double decayRate = getDecayRateForTopic(topic, settings);
            long decayIntervals = (daysSinceLastStudied - settings.getDecayThresholdDays()) / settings.getDecayIntervalDays();

            if (decayIntervals > 0) {
                double totalDecay = decayRate * decayIntervals;
                int projectedConfidence = Math.max(1, topic.getConfidence() - (int) Math.ceil(totalDecay));

                Map<String, Object> preview = new HashMap<>();
                preview.put("topicId", topic.getId());
                preview.put("topicName", topic.getTopic());
                preview.put("category", topic.getCategory());
                preview.put("currentConfidence", topic.getConfidence());
                preview.put("daysSinceStudied", daysSinceLastStudied);
                preview.put("projectedConfidence", projectedConfidence);
                preview.put("decayAmount", topic.getConfidence() - projectedConfidence);

                // Calculate days until next decay
                long daysUntilNextDecay = settings.getDecayIntervalDays() -
                    ((daysSinceLastStudied - settings.getDecayThresholdDays()) % settings.getDecayIntervalDays());
                preview.put("daysUntilNextDecay", daysUntilNextDecay);

                previews.add(preview);
            }
        }

        return previews;
    }

    /**
     * Get confidence history for a topic
     */
    public List<ConfidenceHistory> getConfidenceHistory(Long topicId) {
        return confidenceHistoryRepository.findByTopicIdOrderByChangeDateDesc(topicId);
    }

    /**
     * Record confidence change
     */
    @Transactional
    public void recordConfidenceChange(Topic topic, Integer oldConfidence, Integer newConfidence,
                                      ChangeReason reason, String notes) {
        ConfidenceHistory history = new ConfidenceHistory();
        history.setTopic(topic);
        history.setOldConfidence(oldConfidence);
        history.setNewConfidence(newConfidence);
        history.setChangeReason(reason);
        history.setNotes(notes);
        confidenceHistoryRepository.save(history);
    }
}
