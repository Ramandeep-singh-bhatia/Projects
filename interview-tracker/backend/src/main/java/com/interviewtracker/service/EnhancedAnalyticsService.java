package com.interviewtracker.service;

import com.interviewtracker.dto.EnhancedAnalyticsDTO;
import com.interviewtracker.model.*;
import com.interviewtracker.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class EnhancedAnalyticsService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private PracticeSessionRepository sessionRepository;

    @Autowired
    private MockInterviewRepository mockInterviewRepository;

    @Autowired
    private ConfidenceHistoryRepository confidenceHistoryRepository;

    public EnhancedAnalyticsDTO getEnhancedAnalytics() {
        EnhancedAnalyticsDTO dto = new EnhancedAnalyticsDTO();

        // Study Efficiency
        Map<String, Double> efficiencyByCategory = calculateEfficiencyByCategory();
        dto.setEfficiencyByCategory(efficiencyByCategory);
        dto.setOverallEfficiency(efficiencyByCategory.values().stream()
                .mapToDouble(Double::doubleValue).average().orElse(0.0));

        dto.setMostEfficientTopics(getMostEfficientTopics(10));
        dto.setLeastEfficientTopics(getLeastEfficientTopics(10));

        // Optimal Duration
        Map<Integer, Double> performanceByDuration = calculatePerformanceByDuration();
        dto.setPerformanceByDuration(performanceByDuration);
        dto.setOptimalDuration(findOptimalDuration(performanceByDuration));

        // Best Time of Day
        Map<String, Double> performanceByHour = calculatePerformanceByHour();
        dto.setPerformanceByHour(performanceByHour);
        dto.setBestTimeOfDay(findBestTimeOfDay(performanceByHour));

        // Revision Effectiveness
        dto.setAverageLearningRating(calculateAverageRatingByType(SessionType.FIRST_LEARNING));
        dto.setAverageRevisionRating(calculateAverageRatingByType(SessionType.REVISION));
        dto.setRevisionEffectiveness(dto.getAverageRevisionRating() / Math.max(dto.getAverageLearningRating(), 1.0));

        // Interview Readiness
        Map<String, Object> readiness = calculateInterviewReadiness();
        dto.setReadinessScore((Double) readiness.get("score"));
        dto.setReadinessComponents((Map<String, Double>) readiness.get("components"));
        dto.setCategoryReadiness((Map<String, Double>) readiness.get("categoryReadiness"));
        dto.setActionableInsights((List<String>) readiness.get("insights"));

        // Progress Comparison
        dto.setThisMonthVsLast(calculateMonthComparison());

        // Milestones
        dto.setAchievements(calculateAchievements());
        dto.setNextMilestone(calculateNextMilestone());

        // Practice Patterns
        dto.setSessionSuccessRate(calculateSessionSuccessRate());
        dto.setSuccessRateByCategory(calculateSuccessRateByCategory());
        dto.setLearningVelocity(calculateLearningVelocity());

        return dto;
    }

    private Map<String, Double> calculateEfficiencyByCategory() {
        List<Topic> topics = topicRepository.findAll();
        Map<String, Double> efficiency = new HashMap<>();

        for (TopicCategory category : TopicCategory.values()) {
            List<Topic> categoryTopics = topics.stream()
                    .filter(t -> t.getCategory() == category)
                    .filter(t -> t.getTotalTimeSpent() > 0)
                    .collect(Collectors.toList());

            if (!categoryTopics.isEmpty()) {
                double avgEfficiency = categoryTopics.stream()
                        .mapToDouble(t -> (double) t.getConfidence() / (t.getTotalTimeSpent() / 60.0))
                        .average()
                        .orElse(0.0);
                efficiency.put(category.name(), avgEfficiency);
            }
        }

        return efficiency;
    }

    private List<Map<String, Object>> getMostEfficientTopics(int limit) {
        return topicRepository.findAll().stream()
                .filter(t -> t.getTotalTimeSpent() > 60) // At least 1 hour
                .map(t -> {
                    Map<String, Object> item = new HashMap<>();
                    item.put("topicName", t.getTopic());
                    item.put("category", t.getCategory());
                    item.put("efficiency", (double) t.getConfidence() / (t.getTotalTimeSpent() / 60.0));
                    return item;
                })
                .sorted(Comparator.comparingDouble((Map<String, Object> m) ->
                        (Double) m.get("efficiency")).reversed())
                .limit(limit)
                .collect(Collectors.toList());
    }

    private List<Map<String, Object>> getLeastEfficientTopics(int limit) {
        return topicRepository.findAll().stream()
                .filter(t -> t.getTotalTimeSpent() > 60)
                .map(t -> {
                    Map<String, Object> item = new HashMap<>();
                    item.put("topicName", t.getTopic());
                    item.put("category", t.getCategory());
                    item.put("efficiency", (double) t.getConfidence() / (t.getTotalTimeSpent() / 60.0));
                    return item;
                })
                .sorted(Comparator.comparingDouble(m -> (Double) m.get("efficiency")))
                .limit(limit)
                .collect(Collectors.toList());
    }

    private Map<Integer, Double> calculatePerformanceByDuration() {
        List<PracticeSession> sessions = sessionRepository.findAll();
        Map<Integer, List<Integer>> durationBuckets = new HashMap<>();

        for (PracticeSession session : sessions) {
            int bucket = (session.getDuration() / 15) * 15; // 15-min buckets
            durationBuckets.computeIfAbsent(bucket, k -> new ArrayList<>()).add(session.getPerformanceRating());
        }

        return durationBuckets.entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> e.getValue().stream().mapToInt(Integer::intValue).average().orElse(0.0)
                ));
    }

    private Integer findOptimalDuration(Map<Integer, Double> performanceByDuration) {
        return performanceByDuration.entrySet().stream()
                .max(Comparator.comparingDouble(Map.Entry::getValue))
                .map(Map.Entry::getKey)
                .orElse(45);
    }

    private Map<String, Double> calculatePerformanceByHour() {
        List<PracticeSession> sessions = sessionRepository.findAll();
        Map<Integer, List<Integer>> hourlyPerformance = new HashMap<>();

        for (PracticeSession session : sessions) {
            if (session.getSessionDate() != null) {
                int hour = session.getSessionDate().getHour();
                hourlyPerformance.computeIfAbsent(hour, k -> new ArrayList<>())
                        .add(session.getPerformanceRating());
            }
        }

        return hourlyPerformance.entrySet().stream()
                .collect(Collectors.toMap(
                        e -> e.getKey() + ":00",
                        e -> e.getValue().stream().mapToInt(Integer::intValue).average().orElse(0.0)
                ));
    }

    private String findBestTimeOfDay(Map<String, Double> performanceByHour) {
        return performanceByHour.entrySet().stream()
                .max(Comparator.comparingDouble(Map.Entry::getValue))
                .map(Map.Entry::getKey)
                .orElse("Not enough data");
    }

    private Double calculateAverageRatingByType(SessionType type) {
        return sessionRepository.findAll().stream()
                .filter(s -> s.getSessionType() == type)
                .mapToInt(PracticeSession::getPerformanceRating)
                .average()
                .orElse(0.0);
    }

    private Map<String, Object> calculateInterviewReadiness() {
        Map<String, Object> readiness = new HashMap<>();
        List<Topic> allTopics = topicRepository.findAll();

        // Component 1: Average Confidence (30%)
        double avgConfidence = allTopics.stream()
                .mapToInt(Topic::getConfidence)
                .average()
                .orElse(0.0);
        double confidenceScore = (avgConfidence / 10.0) * 100;

        // Component 2: Topic Coverage (25%)
        long masteredTopics = allTopics.stream().filter(t -> t.getConfidence() >= 7).count();
        double coverageScore = (masteredTopics / (double) Math.max(allTopics.size(), 1)) * 100;

        // Component 3: Practice Frequency (20%)
        LocalDateTime weekAgo = LocalDateTime.now().minusWeeks(1);
        long recentSessions = sessionRepository.findSessionsAfter(weekAgo).size();
        double frequencyScore = Math.min(recentSessions * 10, 100);

        // Component 4: Weak Areas (15%)
        long weakTopics = allTopics.stream().filter(t -> t.getConfidence() < 5).count();
        double weakAreaScore = Math.max(0, 100 - (weakTopics * 10));

        // Component 5: Mock Interviews (10%)
        LocalDateTime monthAgo = LocalDateTime.now().minusMonths(1);
        List<MockInterview> recentMocks = mockInterviewRepository.findCompletedAfter(monthAgo);
        double mockScore = Math.min(recentMocks.size() * 20, 100);

        // Calculate total
        double totalScore = (confidenceScore * 0.3) + (coverageScore * 0.25) +
                          (frequencyScore * 0.2) + (weakAreaScore * 0.15) + (mockScore * 0.1);

        readiness.put("score", totalScore);

        Map<String, Double> components = new HashMap<>();
        components.put("confidence", confidenceScore);
        components.put("coverage", coverageScore);
        components.put("frequency", frequencyScore);
        components.put("weakAreas", weakAreaScore);
        components.put("mockInterviews", mockScore);
        readiness.put("components", components);

        // Category readiness
        Map<String, Double> categoryReadiness = new HashMap<>();
        for (TopicCategory category : TopicCategory.values()) {
            double catReadiness = allTopics.stream()
                    .filter(t -> t.getCategory() == category)
                    .mapToInt(Topic::getConfidence)
                    .average()
                    .orElse(0.0) * 10;
            categoryReadiness.put(category.name(), catReadiness);
        }
        readiness.put("categoryReadiness", categoryReadiness);

        // Actionable insights
        List<String> insights = new ArrayList<>();
        if (totalScore < 60) insights.add("Major preparation gaps - focus on foundational topics");
        if (weakTopics > 5) insights.add("Address " + weakTopics + " weak areas to improve readiness");
        if (recentMocks.size() < 3) insights.add("Complete " + (3 - recentMocks.size()) + " more mock interviews");

        readiness.put("insights", insights);

        return readiness;
    }

    private Map<String, Object> calculateMonthComparison() {
        LocalDateTime thisMonthStart = LocalDateTime.now().withDayOfMonth(1).withHour(0).withMinute(0);
        LocalDateTime lastMonthStart = thisMonthStart.minusMonths(1);

        List<PracticeSession> thisMonth = sessionRepository.findSessionsAfter(thisMonthStart);
        List<PracticeSession> lastMonth = sessionRepository.findSessionsAfter(lastMonthStart).stream()
                .filter(s -> s.getSessionDate().isBefore(thisMonthStart))
                .collect(Collectors.toList());

        Map<String, Object> comparison = new HashMap<>();
        comparison.put("sessionsThisMonth", thisMonth.size());
        comparison.put("sessionsLastMonth", lastMonth.size());
        comparison.put("timeThisMonth", thisMonth.stream().mapToInt(PracticeSession::getDuration).sum());
        comparison.put("timeLastMonth", lastMonth.stream().mapToInt(PracticeSession::getDuration).sum());

        return comparison;
    }

    private List<Map<String, Object>> calculateAchievements() {
        List<Map<String, Object>> achievements = new ArrayList<>();
        List<Topic> topics = topicRepository.findAll();

        // Check various milestones
        long masteredTopics = topics.stream().filter(t -> t.getConfidence() >= 10).count();
        if (masteredTopics > 0) {
            Map<String, Object> achievement = new HashMap<>();
            achievement.put("name", "First Topic Mastered");
            achievement.put("description", "Achieved confidence level 10");
            achievement.put("unlocked", true);
            achievements.add(achievement);
        }

        return achievements;
    }

    private Map<String, Object> calculateNextMilestone() {
        Map<String, Object> milestone = new HashMap<>();
        milestone.put("name", "Week Warrior");
        milestone.put("description", "Meet weekly goals for 4 consecutive weeks");
        milestone.put("progress", 0);
        milestone.put("target", 4);
        return milestone;
    }

    private Double calculateSessionSuccessRate() {
        List<PracticeSession> sessions = sessionRepository.findAll();
        if (sessions.isEmpty()) return 0.0;

        long successful = sessions.stream()
                .filter(s -> s.getPerformanceRating() >= 7)
                .count();

        return (successful * 100.0) / sessions.size();
    }

    private Map<String, Double> calculateSuccessRateByCategory() {
        Map<String, Double> rates = new HashMap<>();
        List<PracticeSession> allSessions = sessionRepository.findAll();

        for (TopicCategory category : TopicCategory.values()) {
            List<PracticeSession> categorySessions = allSessions.stream()
                    .filter(s -> s.getTopic() != null && s.getTopic().getCategory() == category)
                    .collect(Collectors.toList());

            if (!categorySessions.isEmpty()) {
                long successful = categorySessions.stream()
                        .filter(s -> s.getPerformanceRating() >= 7)
                        .count();
                rates.put(category.name(), (successful * 100.0) / categorySessions.size());
            }
        }

        return rates;
    }

    private Double calculateLearningVelocity() {
        LocalDateTime weekAgo = LocalDateTime.now().minusWeeks(1);
        List<Topic> recentTopics = topicRepository.findAll().stream()
                .filter(t -> t.getCreatedDate().isAfter(weekAgo))
                .collect(Collectors.toList());

        return (double) recentTopics.size();
    }
}
