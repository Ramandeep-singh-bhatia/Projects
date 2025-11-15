package com.interviewtracker.service;

import com.interviewtracker.dto.DashboardSuggestionDTO;
import com.interviewtracker.dto.WeeklyProgressDTO;
import com.interviewtracker.model.*;
import com.interviewtracker.repository.TopicRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class DashboardService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private SettingsService settingsService;

    @Autowired
    private TopicService topicService;

    public List<DashboardSuggestionDTO> getRevisionSuggestions(TopicCategory category, int limit) {
        List<Topic> topics;

        if (category != null) {
            topics = topicService.getAllTopicsByCategory(category);
        } else {
            topics = topicRepository.findAll();
        }

        List<DashboardSuggestionDTO> suggestions = new ArrayList<>();

        for (Topic topic : topics) {
            DashboardSuggestionDTO suggestion = createSuggestion(topic);
            suggestions.add(suggestion);
        }

        // Sort by priority score (highest first)
        suggestions.sort(Comparator.comparing(DashboardSuggestionDTO::getPriorityScore).reversed());

        // Return top N suggestions
        return suggestions.stream()
                .limit(limit > 0 ? limit : 15)
                .collect(Collectors.toList());
    }

    private DashboardSuggestionDTO createSuggestion(Topic topic) {
        DashboardSuggestionDTO suggestion = new DashboardSuggestionDTO();
        suggestion.setTopicId(topic.getId());
        suggestion.setTopic(topic.getTopic());
        suggestion.setSubtopic(topic.getSubtopic());
        suggestion.setCategory(topic.getCategory());
        suggestion.setConfidence(topic.getConfidence());

        // Calculate days since last studied
        long daysSinceLastStudied = 0;
        if (topic.getLastStudiedDate() != null) {
            daysSinceLastStudied = ChronoUnit.DAYS.between(
                    topic.getLastStudiedDate().toLocalDate(),
                    LocalDateTime.now().toLocalDate()
            );
        } else {
            // Never studied - treat as 90 days
            daysSinceLastStudied = 90;
        }
        suggestion.setDaysSinceLastStudied(daysSinceLastStudied);

        // Calculate estimated time (average of past sessions or default)
        int estimatedTime = 30; // default
        if (topic.getSessionCount() > 0) {
            estimatedTime = topic.getTotalTimeSpent() / topic.getSessionCount();
        }
        suggestion.setEstimatedTime(estimatedTime);

        // Set difficulty for DSA topics
        if (topic instanceof DSATopic) {
            suggestion.setDifficulty(((DSATopic) topic).getDifficulty());
        }

        // Calculate priority score
        double priorityScore = calculatePriorityScore(topic, daysSinceLastStudied);
        suggestion.setPriorityScore(priorityScore);

        return suggestion;
    }

    private double calculatePriorityScore(Topic topic, long daysSinceLastStudied) {
        // Difficulty weight (for DSA topics)
        double difficultyWeight = 1.0;
        if (topic instanceof DSATopic) {
            DifficultyLevel difficulty = ((DSATopic) topic).getDifficulty();
            difficultyWeight = switch (difficulty) {
                case EASY -> 1.0;
                case MEDIUM -> 1.5;
                case HARD -> 2.0;
            };
        }

        // Confidence weight (lower confidence = higher priority)
        double confidenceWeight = (11.0 - topic.getConfidence()) / 10.0;

        // Recency weight (more days = higher priority)
        double recencyWeight;
        if (daysSinceLastStudied <= 1) {
            recencyWeight = 0.3;
        } else if (daysSinceLastStudied <= 3) {
            recencyWeight = 0.6;
        } else if (daysSinceLastStudied <= 7) {
            recencyWeight = 1.0;
        } else if (daysSinceLastStudied <= 14) {
            recencyWeight = 1.5;
        } else if (daysSinceLastStudied <= 30) {
            recencyWeight = 2.0;
        } else {
            recencyWeight = 2.5;
        }

        return difficultyWeight * confidenceWeight * recencyWeight;
    }

    public WeeklyProgressDTO getCurrentWeekProgress() {
        Settings settings = settingsService.getSettings();
        LocalDateTime weekStart = getWeekStartDate(settings.getWeekStartDay());
        LocalDateTime weekEnd = weekStart.plusDays(7);

        WeeklyProgressDTO progress = new WeeklyProgressDTO();
        progress.setWeekStartDate(weekStart.toLocalDate());
        progress.setWeekEndDate(weekEnd.toLocalDate());

        // Set goals
        progress.setDsaGoal(settings.getWeeklyDsaGoal());
        progress.setHldGoal(settings.getWeeklyHldGoal());
        progress.setLldGoal(settings.getWeeklyLldGoal());
        progress.setBehavioralGoal(settings.getWeeklyBehavioralGoal());

        // Count actual topics studied this week (with at least one session)
        progress.setDsaActual(countTopicsStudiedThisWeek(TopicCategory.DSA, weekStart));
        progress.setHldActual(countTopicsStudiedThisWeek(TopicCategory.HLD, weekStart));
        progress.setLldActual(countTopicsStudiedThisWeek(TopicCategory.LLD, weekStart));
        progress.setBehavioralActual(countTopicsStudiedThisWeek(TopicCategory.BEHAVIORAL, weekStart));

        return progress;
    }

    public List<WeeklyProgressDTO> getWeeklyHistory(int weeks) {
        Settings settings = settingsService.getSettings();
        List<WeeklyProgressDTO> history = new ArrayList<>();

        for (int i = 1; i <= weeks; i++) {
            LocalDateTime weekStart = getWeekStartDate(settings.getWeekStartDay()).minusWeeks(i);
            LocalDateTime weekEnd = weekStart.plusDays(7);

            WeeklyProgressDTO progress = new WeeklyProgressDTO();
            progress.setWeekStartDate(weekStart.toLocalDate());
            progress.setWeekEndDate(weekEnd.toLocalDate());

            // Set goals
            progress.setDsaGoal(settings.getWeeklyDsaGoal());
            progress.setHldGoal(settings.getWeeklyHldGoal());
            progress.setLldGoal(settings.getWeeklyLldGoal());
            progress.setBehavioralGoal(settings.getWeeklyBehavioralGoal());

            // Count actual topics studied that week
            progress.setDsaActual(countTopicsStudiedInWeek(TopicCategory.DSA, weekStart, weekEnd));
            progress.setHldActual(countTopicsStudiedInWeek(TopicCategory.HLD, weekStart, weekEnd));
            progress.setLldActual(countTopicsStudiedInWeek(TopicCategory.LLD, weekStart, weekEnd));
            progress.setBehavioralActual(countTopicsStudiedInWeek(TopicCategory.BEHAVIORAL, weekStart, weekEnd));

            history.add(progress);
        }

        return history;
    }

    private LocalDateTime getWeekStartDate(WeekStartDay weekStartDay) {
        LocalDateTime now = LocalDateTime.now();
        int currentDayOfWeek = now.getDayOfWeek().getValue(); // Monday = 1, Sunday = 7

        if (weekStartDay == WeekStartDay.MONDAY) {
            // Go back to Monday of current week
            return now.minusDays(currentDayOfWeek - 1).withHour(0).withMinute(0).withSecond(0).withNano(0);
        } else {
            // WeekStartDay.SUNDAY
            int daysToSubtract = currentDayOfWeek == 7 ? 0 : currentDayOfWeek;
            return now.minusDays(daysToSubtract).withHour(0).withMinute(0).withSecond(0).withNano(0);
        }
    }

    private int countTopicsStudiedThisWeek(TopicCategory category, LocalDateTime weekStart) {
        List<Topic> topics = topicService.getTopicsByCategoryStudiedThisWeek(category, weekStart);
        return topics.size();
    }

    private int countTopicsStudiedInWeek(TopicCategory category, LocalDateTime weekStart, LocalDateTime weekEnd) {
        Class<? extends Topic> topicClass = switch (category) {
            case DSA -> DSATopic.class;
            case HLD -> HLDTopic.class;
            case LLD -> LLDTopic.class;
            case BEHAVIORAL -> BehavioralTopic.class;
        };

        List<Topic> allTopics = topicRepository.findByType(topicClass);
        return (int) allTopics.stream()
                .filter(t -> t.getLastStudiedDate() != null &&
                        !t.getLastStudiedDate().isBefore(weekStart) &&
                        t.getLastStudiedDate().isBefore(weekEnd))
                .count();
    }
}
