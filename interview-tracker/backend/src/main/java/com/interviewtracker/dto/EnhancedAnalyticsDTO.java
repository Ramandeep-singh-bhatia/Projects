package com.interviewtracker.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class EnhancedAnalyticsDTO {
    // Study Efficiency
    private Double overallEfficiency;
    private Map<String, Double> efficiencyByCategory;
    private List<Map<String, Object>> mostEfficientTopics;
    private List<Map<String, Object>> leastEfficientTopics;

    // Optimal Duration
    private Integer optimalDuration;
    private Map<Integer, Double> performanceByDuration;

    // Best Time of Day
    private String bestTimeOfDay;
    private Map<String, Double> performanceByHour;

    // Revision Effectiveness
    private Double revisionEffectiveness;
    private Double averageLearningRating;
    private Double averageRevisionRating;

    // Interview Readiness
    private Double readinessScore;
    private Map<String, Double> readinessComponents;
    private Map<String, Double> categoryReadiness;
    private List<String> actionableInsights;

    // Progress Comparison
    private Map<String, Object> thisMonthVsLast;

    // Milestones
    private List<Map<String, Object>> achievements;
    private Map<String, Object> nextMilestone;

    // Practice Patterns
    private Double sessionSuccessRate;
    private Map<String, Double> successRateByCategory;
    private Double learningVelocity; // topics per week
}
