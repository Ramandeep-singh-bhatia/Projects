package com.interviewtracker.service;

import com.interviewtracker.model.CalibrationCheck;
import com.interviewtracker.model.CalibrationType;
import com.interviewtracker.model.Topic;
import com.interviewtracker.repository.CalibrationCheckRepository;
import com.interviewtracker.repository.TopicRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

@Service
@RequiredArgsConstructor
public class CalibrationService {

    private final CalibrationCheckRepository calibrationCheckRepository;
    private final TopicRepository topicRepository;
    private final TopicService topicService;

    // Identify topics that need calibration
    public List<Topic> getTopicsNeedingCalibration() {
        List<Topic> allTopics = topicRepository.findAll();
        List<Topic> needsCalibration = new ArrayList<>();

        for (Topic topic : allTopics) {
            // Trigger conditions:
            // 1. High confidence (8+) and not verified in 14+ days
            // 2. Large confidence jump recently

            if (topic.getConfidence() >= 8) {
                List<CalibrationCheck> history = calibrationCheckRepository.findByTopicOrderByCheckDateDesc(topic);
                if (history.isEmpty()) {
                    needsCalibration.add(topic);
                } else {
                    CalibrationCheck last = history.get(0);
                    long daysSinceLastCheck = ChronoUnit.DAYS.between(last.getCheckDate(), LocalDateTime.now());
                    if (daysSinceLastCheck >= 14) {
                        needsCalibration.add(topic);
                    }
                }
            }
        }

        return needsCalibration;
    }

    // Create calibration check
    @Transactional
    public CalibrationCheck triggerCalibration(Long topicId, CalibrationType type) {
        Topic topic = topicRepository.findById(topicId)
                .orElseThrow(() -> new RuntimeException("Topic not found with id: " + topicId));

        CalibrationCheck check = new CalibrationCheck();
        check.setTopic(topic);
        check.setType(type);
        check.setConfidenceBefore(topic.getConfidence());
        check.setCheckDate(LocalDateTime.now());
        check.setPassed(null); // To be filled when completed

        return calibrationCheckRepository.save(check);
    }

    // Complete calibration check
    @Transactional
    public CalibrationCheck completeCalibration(Long checkId, boolean passed, String userResponse, String notes) {
        CalibrationCheck check = calibrationCheckRepository.findById(checkId)
                .orElseThrow(() -> new RuntimeException("Calibration check not found with id: " + checkId));

        check.setPassed(passed);
        check.setUserResponse(userResponse);
        check.setNotes(notes);

        // Adjust confidence based on result
        Topic topic = check.getTopic();
        int newConfidence = topic.getConfidence();

        if (!passed) {
            // Failed calibration - reduce confidence
            if (check.getType() == CalibrationType.QUIZ) {
                newConfidence = Math.max(1, newConfidence - 2); // Reduce by 2 for quiz failure
            } else {
                newConfidence = Math.max(1, newConfidence - 1); // Reduce by 1 for other failures
            }
        }
        // If passed, maintain confidence (no increase for calibration pass)

        check.setConfidenceAfter(newConfidence);
        topic.setConfidence(newConfidence);
        topicService.updateTopic(topic.getId(), topic);

        return calibrationCheckRepository.save(check);
    }

    // Get calibration history for topic
    public List<CalibrationCheck> getCalibrationHistory(Long topicId) {
        Topic topic = topicRepository.findById(topicId)
                .orElseThrow(() -> new RuntimeException("Topic not found with id: " + topicId));
        return calibrationCheckRepository.findByTopicOrderByCheckDateDesc(topic);
    }

    // Get pending calibrations
    public List<CalibrationCheck> getPendingCalibrations() {
        return calibrationCheckRepository.findAll().stream()
                .filter(c -> c.getPassed() == null)
                .toList();
    }

    // Get calibration accuracy metrics
    public Map<String, Object> getCalibrationAccuracy() {
        Map<String, Object> metrics = new HashMap<>();
        List<CalibrationCheck> allChecks = calibrationCheckRepository.findAll().stream()
                .filter(c -> c.getPassed() != null)
                .toList();

        if (allChecks.isEmpty()) {
            metrics.put("totalCalibrations", 0);
            metrics.put("passRate", 0.0);
            metrics.put("averageConfidenceChange", 0.0);
            return metrics;
        }

        long passed = allChecks.stream().filter(CalibrationCheck::getPassed).count();
        double passRate = (double) passed / allChecks.size() * 100;

        double avgConfidenceChange = allChecks.stream()
                .mapToInt(c -> c.getConfidenceAfter() - c.getConfidenceBefore())
                .average()
                .orElse(0.0);

        metrics.put("totalCalibrations", allChecks.size());
        metrics.put("passRate", Math.round(passRate * 10) / 10.0);
        metrics.put("averageConfidenceChange", Math.round(avgConfidenceChange * 10) / 10.0);

        return metrics;
    }
}
