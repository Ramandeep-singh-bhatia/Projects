package com.interviewtracker.service;

import com.interviewtracker.dto.AnalyticsSummaryDTO;
import com.interviewtracker.model.PracticeSession;
import com.interviewtracker.model.Topic;
import com.interviewtracker.model.TopicCategory;
import com.interviewtracker.repository.PracticeSessionRepository;
import com.interviewtracker.repository.TopicRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class AnalyticsService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private PracticeSessionRepository sessionRepository;

    public AnalyticsSummaryDTO getAnalyticsSummary() {
        AnalyticsSummaryDTO summary = new AnalyticsSummaryDTO();

        List<Topic> allTopics = topicRepository.findAll();
        List<PracticeSession> allSessions = sessionRepository.findAll();

        // Basic stats
        summary.setTotalTopics(allTopics.size());
        summary.setTotalSessions(allSessions.size());

        // Total time spent
        int totalTime = allSessions.stream()
                .mapToInt(PracticeSession::getDuration)
                .sum();
        summary.setTotalTimeSpent(totalTime);

        // Average confidence
        double avgConfidence = allTopics.stream()
                .mapToInt(Topic::getConfidence)
                .average()
                .orElse(0.0);
        summary.setAverageConfidence(Math.round(avgConfidence * 10.0) / 10.0);

        // Topics by category
        Map<String, Integer> topicsByCategory = new HashMap<>();
        topicsByCategory.put("DSA", (int) allTopics.stream().filter(t -> t.getCategory() == TopicCategory.DSA).count());
        topicsByCategory.put("HLD", (int) allTopics.stream().filter(t -> t.getCategory() == TopicCategory.HLD).count());
        topicsByCategory.put("LLD", (int) allTopics.stream().filter(t -> t.getCategory() == TopicCategory.LLD).count());
        topicsByCategory.put("BEHAVIORAL", (int) allTopics.stream().filter(t -> t.getCategory() == TopicCategory.BEHAVIORAL).count());
        summary.setTopicsByCategory(topicsByCategory);

        // Topics by confidence level
        Map<String, Integer> topicsByConfidence = new HashMap<>();
        topicsByConfidence.put("WEAK", (int) allTopics.stream().filter(t -> t.getConfidence() <= 4).count());
        topicsByConfidence.put("MEDIUM", (int) allTopics.stream().filter(t -> t.getConfidence() >= 5 && t.getConfidence() <= 7).count());
        topicsByConfidence.put("STRONG", (int) allTopics.stream().filter(t -> t.getConfidence() >= 8).count());
        summary.setTopicsByConfidenceLevel(topicsByConfidence);

        // Time by category
        Map<String, Integer> timeByCategory = calculateTimeByCategory(allTopics);
        summary.setTimeByCategory(timeByCategory);

        // Time this week vs last week
        LocalDateTime weekStart = LocalDateTime.now().minusWeeks(1).with(java.time.DayOfWeek.MONDAY)
                .withHour(0).withMinute(0).withSecond(0);
        LocalDateTime thisWeekStart = LocalDateTime.now().with(java.time.DayOfWeek.MONDAY)
                .withHour(0).withMinute(0).withSecond(0);

        int timeLastWeek = allSessions.stream()
                .filter(s -> s.getSessionDate().isAfter(weekStart) && s.getSessionDate().isBefore(thisWeekStart))
                .mapToInt(PracticeSession::getDuration)
                .sum();
        summary.setTimeLastWeek(timeLastWeek);

        int timeThisWeek = allSessions.stream()
                .filter(s -> s.getSessionDate().isAfter(thisWeekStart))
                .mapToInt(PracticeSession::getDuration)
                .sum();
        summary.setTimeThisWeek(timeThisWeek);

        // Average daily time (last 7 days)
        LocalDateTime sevenDaysAgo = LocalDateTime.now().minusDays(7);
        int timeLastSevenDays = allSessions.stream()
                .filter(s -> s.getSessionDate().isAfter(sevenDaysAgo))
                .mapToInt(PracticeSession::getDuration)
                .sum();
        summary.setAverageDailyTime(Math.round((timeLastSevenDays / 7.0) * 10.0) / 10.0);

        // Study streak
        int[] streaks = calculateStreaks(allSessions);
        summary.setCurrentStreak(streaks[0]);
        summary.setLongestStreak(streaks[1]);

        // Days studied this month
        LocalDateTime monthStart = LocalDateTime.now().withDayOfMonth(1).withHour(0).withMinute(0).withSecond(0);
        Set<LocalDate> daysStudied = allSessions.stream()
                .filter(s -> s.getSessionDate().isAfter(monthStart))
                .map(s -> s.getSessionDate().toLocalDate())
                .collect(Collectors.toSet());
        summary.setDaysStudiedThisMonth(daysStudied.size());

        return summary;
    }

    private Map<String, Integer> calculateTimeByCategory(List<Topic> topics) {
        Map<String, Integer> timeByCategory = new HashMap<>();
        timeByCategory.put("DSA", 0);
        timeByCategory.put("HLD", 0);
        timeByCategory.put("LLD", 0);
        timeByCategory.put("BEHAVIORAL", 0);

        for (Topic topic : topics) {
            String category = topic.getCategory().name();
            int currentTime = timeByCategory.getOrDefault(category, 0);
            timeByCategory.put(category, currentTime + topic.getTotalTimeSpent());
        }

        return timeByCategory;
    }

    private int[] calculateStreaks(List<PracticeSession> sessions) {
        if (sessions.isEmpty()) {
            return new int[]{0, 0};
        }

        // Get all unique study dates, sorted
        List<LocalDate> studyDates = sessions.stream()
                .map(s -> s.getSessionDate().toLocalDate())
                .distinct()
                .sorted()
                .collect(Collectors.toList());

        if (studyDates.isEmpty()) {
            return new int[]{0, 0};
        }

        int currentStreak = 0;
        int longestStreak = 0;
        int tempStreak = 1;

        LocalDate today = LocalDate.now();
        LocalDate yesterday = today.minusDays(1);

        // Calculate current streak
        if (studyDates.contains(today)) {
            currentStreak = 1;
            LocalDate checkDate = yesterday;
            while (studyDates.contains(checkDate)) {
                currentStreak++;
                checkDate = checkDate.minusDays(1);
            }
        } else if (studyDates.contains(yesterday)) {
            currentStreak = 1;
            LocalDate checkDate = yesterday.minusDays(1);
            while (studyDates.contains(checkDate)) {
                currentStreak++;
                checkDate = checkDate.minusDays(1);
            }
        }

        // Calculate longest streak
        for (int i = 1; i < studyDates.size(); i++) {
            long daysBetween = ChronoUnit.DAYS.between(studyDates.get(i - 1), studyDates.get(i));
            if (daysBetween == 1) {
                tempStreak++;
            } else {
                longestStreak = Math.max(longestStreak, tempStreak);
                tempStreak = 1;
            }
        }
        longestStreak = Math.max(longestStreak, tempStreak);

        return new int[]{currentStreak, longestStreak};
    }

    public List<PracticeSession> getRecentActivity(int limit) {
        return sessionRepository.findRecentSessions(limit);
    }
}
