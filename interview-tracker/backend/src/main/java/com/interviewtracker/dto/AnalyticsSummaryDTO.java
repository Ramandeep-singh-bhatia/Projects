package com.interviewtracker.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AnalyticsSummaryDTO {
    private Integer totalTopics;
    private Integer totalSessions;
    private Integer totalTimeSpent; // in minutes
    private Double averageConfidence;
    private Integer currentStreak; // consecutive days
    private Integer longestStreak;
    private Integer daysStudiedThisMonth;
    private Map<String, Integer> topicsByCategory;
    private Map<String, Integer> topicsByConfidenceLevel; // weak, medium, strong
    private Map<String, Integer> timeByCategory; // in minutes
    private Integer timeThisWeek;
    private Integer timeLastWeek;
    private Double averageDailyTime; // last 7 days
}
