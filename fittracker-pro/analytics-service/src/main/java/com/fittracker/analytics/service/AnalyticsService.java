package com.fittracker.analytics.service;

import com.fittracker.analytics.entity.DailyActivitySummary;
import com.fittracker.analytics.repository.DailyActivitySummaryRepository;
import com.fittracker.common.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class AnalyticsService {

    private final DailyActivitySummaryRepository dailyActivitySummaryRepository;

    /**
     * Get or create daily activity summary for a specific date
     */
    @Transactional
    public DailyActivitySummary getOrCreateDailySummary(Long userId, LocalDate date) {
        return dailyActivitySummaryRepository.findByUserIdAndActivityDate(userId, date)
                .orElseGet(() -> {
                    DailyActivitySummary summary = DailyActivitySummary.builder()
                            .userId(userId)
                            .activityDate(date)
                            .build();
                    return dailyActivitySummaryRepository.save(summary);
                });
    }

    /**
     * Get daily activity summary for a specific date
     */
    @Transactional(readOnly = true)
    @Cacheable(value = "dailyActivity", key = "#userId + '-' + #date")
    public DailyActivitySummary getDailySummary(Long userId, LocalDate date) {
        return dailyActivitySummaryRepository.findByUserIdAndActivityDate(userId, date)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Daily activity summary not found for user " + userId + " on " + date));
    }

    /**
     * Get activity summaries for a date range
     */
    @Transactional(readOnly = true)
    public List<DailyActivitySummary> getActivityInRange(Long userId, LocalDate startDate, LocalDate endDate) {
        log.info("Fetching activity summaries for user {} from {} to {}", userId, startDate, endDate);
        return dailyActivitySummaryRepository.findByUserIdAndActivityDateBetweenOrderByActivityDateDesc(
                userId, startDate, endDate);
    }

    /**
     * Get recent activity summaries (last N days)
     */
    @Transactional(readOnly = true)
    public List<DailyActivitySummary> getRecentActivity(Long userId, int days) {
        LocalDate startDate = LocalDate.now().minusDays(days);
        log.info("Fetching last {} days of activity for user {}", days, userId);
        return dailyActivitySummaryRepository.findRecentActivity(userId, startDate);
    }

    /**
     * Update daily activity with meal data
     */
    @Transactional
    public DailyActivitySummary updateMealData(Long userId, LocalDate date,
                                               int calories, double protein, double carbs, double fat) {
        DailyActivitySummary summary = getOrCreateDailySummary(userId, date);

        summary.setTotalCaloriesConsumed(
                (summary.getTotalCaloriesConsumed() != null ? summary.getTotalCaloriesConsumed() : 0) + calories);
        summary.setTotalProteinG(summary.getTotalProteinG().add(java.math.BigDecimal.valueOf(protein)));
        summary.setTotalCarbsG(summary.getTotalCarbsG().add(java.math.BigDecimal.valueOf(carbs)));
        summary.setTotalFatG(summary.getTotalFatG().add(java.math.BigDecimal.valueOf(fat)));
        summary.setMealsLogged((summary.getMealsLogged() != null ? summary.getMealsLogged() : 0) + 1);

        summary.calculateNetCalories();

        log.info("Updated meal data for user {} on {}", userId, date);
        return dailyActivitySummaryRepository.save(summary);
    }

    /**
     * Update daily activity with workout data
     */
    @Transactional
    public DailyActivitySummary updateWorkoutData(Long userId, LocalDate date,
                                                  int caloriesBurned, int durationMinutes) {
        DailyActivitySummary summary = getOrCreateDailySummary(userId, date);

        summary.setTotalCaloriesBurned(
                (summary.getTotalCaloriesBurned() != null ? summary.getTotalCaloriesBurned() : 0) + caloriesBurned);
        summary.setTotalWorkoutDurationMinutes(
                (summary.getTotalWorkoutDurationMinutes() != null ? summary.getTotalWorkoutDurationMinutes() : 0) + durationMinutes);
        summary.setWorkoutsCompleted((summary.getWorkoutsCompleted() != null ? summary.getWorkoutsCompleted() : 0) + 1);
        summary.setActiveMinutes(
                (summary.getActiveMinutes() != null ? summary.getActiveMinutes() : 0) + durationMinutes);

        summary.calculateNetCalories();

        log.info("Updated workout data for user {} on {}", userId, date);
        return dailyActivitySummaryRepository.save(summary);
    }

    /**
     * Calculate average calories consumed over a period
     */
    @Transactional(readOnly = true)
    public Double calculateAverageCaloriesConsumed(Long userId, LocalDate startDate, LocalDate endDate) {
        Double avg = dailyActivitySummaryRepository.calculateAverageCaloriesConsumed(userId, startDate, endDate);
        return avg != null ? avg : 0.0;
    }

    /**
     * Calculate average calories burned over a period
     */
    @Transactional(readOnly = true)
    public Double calculateAverageCaloriesBurned(Long userId, LocalDate startDate, LocalDate endDate) {
        Double avg = dailyActivitySummaryRepository.calculateAverageCaloriesBurned(userId, startDate, endDate);
        return avg != null ? avg : 0.0;
    }

    /**
     * Count days with workouts in a period
     */
    @Transactional(readOnly = true)
    public Long countDaysWithWorkouts(Long userId, LocalDate startDate, LocalDate endDate) {
        return dailyActivitySummaryRepository.countDaysWithWorkouts(userId, startDate, endDate);
    }
}
