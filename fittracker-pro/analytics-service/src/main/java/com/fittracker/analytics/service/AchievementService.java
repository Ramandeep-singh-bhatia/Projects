package com.fittracker.analytics.service;

import com.fittracker.analytics.entity.Achievement;
import com.fittracker.analytics.repository.AchievementRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class AchievementService {

    private final AchievementRepository achievementRepository;

    /**
     * Create a new achievement for a user
     */
    @Transactional
    public Achievement createAchievement(Long userId, Achievement.AchievementType type,
                                        String name, String description, Map<String, Object> data) {
        Achievement achievement = Achievement.builder()
                .userId(userId)
                .achievementType(type)
                .achievementName(name)
                .description(description)
                .achievementDate(LocalDate.now())
                .achievementData(data != null ? data : new HashMap<>())
                .build();

        log.info("Creating achievement for user {}: {} - {}", userId, type, name);
        return achievementRepository.save(achievement);
    }

    /**
     * Create streak achievement
     */
    @Transactional
    public Achievement createStreakAchievement(Long userId, int streakDays, String activityType) {
        Map<String, Object> data = new HashMap<>();
        data.put("streakDays", streakDays);
        data.put("activityType", activityType);

        String name = String.format("%d Day %s Streak", streakDays, activityType);
        String description = String.format("Completed %s for %d consecutive days", activityType, streakDays);

        return createAchievement(userId, Achievement.AchievementType.STREAK, name, description, data);
    }

    /**
     * Create milestone achievement
     */
    @Transactional
    public Achievement createMilestoneAchievement(Long userId, String milestoneName,
                                                  String milestoneType, Object milestoneValue) {
        Map<String, Object> data = new HashMap<>();
        data.put("milestoneType", milestoneType);
        data.put("milestoneValue", milestoneValue);

        String description = String.format("Reached milestone: %s", milestoneName);

        return createAchievement(userId, Achievement.AchievementType.MILESTONE,
                milestoneName, description, data);
    }

    /**
     * Create goal completed achievement
     */
    @Transactional
    public Achievement createGoalCompletedAchievement(Long userId, Long goalId, String goalName) {
        Map<String, Object> data = new HashMap<>();
        data.put("goalId", goalId);
        data.put("goalName", goalName);

        String name = String.format("Goal Completed: %s", goalName);
        String description = "Successfully completed fitness goal";

        return createAchievement(userId, Achievement.AchievementType.GOAL_COMPLETED,
                name, description, data);
    }

    /**
     * Create personal record achievement
     */
    @Transactional
    public Achievement createPersonalRecordAchievement(Long userId, String exerciseName,
                                                      String recordType, Object recordValue) {
        Map<String, Object> data = new HashMap<>();
        data.put("exerciseName", exerciseName);
        data.put("recordType", recordType);
        data.put("recordValue", recordValue);

        String name = String.format("Personal Record: %s - %s", exerciseName, recordType);
        String description = String.format("New personal record for %s: %s", exerciseName, recordValue);

        return createAchievement(userId, Achievement.AchievementType.PERSONAL_RECORD,
                name, description, data);
    }

    /**
     * Get all achievements for a user with pagination
     */
    @Transactional(readOnly = true)
    public Page<Achievement> getUserAchievements(Long userId, Pageable pageable) {
        return achievementRepository.findByUserIdOrderByAchievementDateDesc(userId, pageable);
    }

    /**
     * Get achievements by type
     */
    @Transactional(readOnly = true)
    public List<Achievement> getAchievementsByType(Long userId, Achievement.AchievementType type) {
        return achievementRepository.findByUserIdAndAchievementType(userId, type);
    }

    /**
     * Get achievements in a date range
     */
    @Transactional(readOnly = true)
    public List<Achievement> getAchievementsInPeriod(Long userId, LocalDate startDate, LocalDate endDate) {
        return achievementRepository.findAchievementsInPeriod(userId, startDate, endDate);
    }

    /**
     * Get recent achievements (top 10)
     */
    @Transactional(readOnly = true)
    public List<Achievement> getRecentAchievements(Long userId) {
        return achievementRepository.findTop10ByUserIdOrderByAchievementDateDesc(userId);
    }

    /**
     * Count achievements in a period
     */
    @Transactional(readOnly = true)
    public Long countAchievementsInPeriod(Long userId, LocalDate startDate, LocalDate endDate) {
        return achievementRepository.countAchievementsInPeriod(userId, startDate, endDate);
    }
}
