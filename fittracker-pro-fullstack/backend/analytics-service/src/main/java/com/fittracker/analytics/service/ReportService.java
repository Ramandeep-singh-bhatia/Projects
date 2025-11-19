package com.fittracker.analytics.service;

import com.fittracker.analytics.entity.DailyActivitySummary;
import com.fittracker.analytics.entity.MonthlyReport;
import com.fittracker.analytics.entity.WeeklyReport;
import com.fittracker.analytics.repository.DailyActivitySummaryRepository;
import com.fittracker.analytics.repository.MonthlyReportRepository;
import com.fittracker.analytics.repository.UserGoalRepository;
import com.fittracker.analytics.repository.WeeklyReportRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.TemporalAdjusters;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ReportService {

    private final DailyActivitySummaryRepository dailyActivitySummaryRepository;
    private final WeeklyReportRepository weeklyReportRepository;
    private final MonthlyReportRepository monthlyReportRepository;
    private final UserGoalRepository userGoalRepository;

    /**
     * Generate weekly report for a user
     */
    @Transactional
    public WeeklyReport generateWeeklyReport(Long userId, LocalDate weekStartDate) {
        LocalDate weekStart = weekStartDate.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
        LocalDate weekEnd = weekStart.plusDays(6);

        log.info("Generating weekly report for user {} - week starting {}", userId, weekStart);

        // Check if report already exists
        return weeklyReportRepository.findByUserIdAndWeekStartDate(userId, weekStart)
                .orElseGet(() -> {
                    // Fetch daily summaries for the week
                    List<DailyActivitySummary> dailySummaries =
                            dailyActivitySummaryRepository.findByUserIdAndActivityDateBetweenOrderByActivityDateDesc(
                                    userId, weekStart, weekEnd);

                    // Calculate totals and averages
                    int totalCaloriesConsumed = dailySummaries.stream()
                            .mapToInt(s -> s.getTotalCaloriesConsumed() != null ? s.getTotalCaloriesConsumed() : 0)
                            .sum();

                    int totalCaloriesBurned = dailySummaries.stream()
                            .mapToInt(s -> s.getTotalCaloriesBurned() != null ? s.getTotalCaloriesBurned() : 0)
                            .sum();

                    int totalWorkouts = dailySummaries.stream()
                            .mapToInt(s -> s.getWorkoutsCompleted() != null ? s.getWorkoutsCompleted() : 0)
                            .sum();

                    int totalWorkoutMinutes = dailySummaries.stream()
                            .mapToInt(s -> s.getTotalWorkoutDurationMinutes() != null ? s.getTotalWorkoutDurationMinutes() : 0)
                            .sum();

                    BigDecimal avgDailyCalories = dailySummaries.isEmpty() ? BigDecimal.ZERO :
                            BigDecimal.valueOf(totalCaloriesConsumed)
                                    .divide(BigDecimal.valueOf(dailySummaries.size()), 2, RoundingMode.HALF_UP);

                    // Calculate consistency score (0-100)
                    long daysWithActivity = dailySummaries.stream()
                            .filter(s -> s.getWorkoutsCompleted() != null && s.getWorkoutsCompleted() > 0)
                            .count();
                    BigDecimal consistencyScore = BigDecimal.valueOf(daysWithActivity * 100.0 / 7.0)
                            .setScale(2, RoundingMode.HALF_UP);

                    // Count goals achieved in this week
                    Long goalsAchieved = userGoalRepository.countGoalsCompletedInPeriod(userId, weekStart, weekEnd);

                    // Create additional report data
                    Map<String, Object> reportData = new HashMap<>();
                    reportData.put("daysWithActivity", daysWithActivity);
                    reportData.put("daysLogged", dailySummaries.size());

                    WeeklyReport report = WeeklyReport.builder()
                            .userId(userId)
                            .weekStartDate(weekStart)
                            .weekEndDate(weekEnd)
                            .totalCaloriesConsumed(totalCaloriesConsumed)
                            .totalCaloriesBurned(totalCaloriesBurned)
                            .totalWorkouts(totalWorkouts)
                            .totalWorkoutMinutes(totalWorkoutMinutes)
                            .avgDailyCalories(avgDailyCalories)
                            .goalsAchieved(goalsAchieved.intValue())
                            .consistencyScore(consistencyScore)
                            .reportData(reportData)
                            .build();

                    return weeklyReportRepository.save(report);
                });
    }

    /**
     * Generate monthly report for a user
     */
    @Transactional
    public MonthlyReport generateMonthlyReport(Long userId, int year, int month) {
        log.info("Generating monthly report for user {} - {}/{}", userId, year, month);

        // Check if report already exists
        return monthlyReportRepository.findByUserIdAndYearAndMonth(userId, year, month)
                .orElseGet(() -> {
                    LocalDate monthStart = LocalDate.of(year, month, 1);
                    LocalDate monthEnd = monthStart.with(TemporalAdjusters.lastDayOfMonth());

                    // Fetch daily summaries for the month
                    List<DailyActivitySummary> dailySummaries =
                            dailyActivitySummaryRepository.findByUserIdAndActivityDateBetweenOrderByActivityDateDesc(
                                    userId, monthStart, monthEnd);

                    // Calculate totals and averages
                    int totalCaloriesConsumed = dailySummaries.stream()
                            .mapToInt(s -> s.getTotalCaloriesConsumed() != null ? s.getTotalCaloriesConsumed() : 0)
                            .sum();

                    int totalCaloriesBurned = dailySummaries.stream()
                            .mapToInt(s -> s.getTotalCaloriesBurned() != null ? s.getTotalCaloriesBurned() : 0)
                            .sum();

                    int totalWorkouts = dailySummaries.stream()
                            .mapToInt(s -> s.getWorkoutsCompleted() != null ? s.getWorkoutsCompleted() : 0)
                            .sum();

                    int totalWorkoutMinutes = dailySummaries.stream()
                            .mapToInt(s -> s.getTotalWorkoutDurationMinutes() != null ? s.getTotalWorkoutDurationMinutes() : 0)
                            .sum();

                    BigDecimal avgDailyCalories = dailySummaries.isEmpty() ? BigDecimal.ZERO :
                            BigDecimal.valueOf(totalCaloriesConsumed)
                                    .divide(BigDecimal.valueOf(dailySummaries.size()), 2, RoundingMode.HALF_UP);

                    // Calculate consistency score
                    long daysWithActivity = dailySummaries.stream()
                            .filter(s -> s.getWorkoutsCompleted() != null && s.getWorkoutsCompleted() > 0)
                            .count();
                    int totalDaysInMonth = monthEnd.getDayOfMonth();
                    BigDecimal consistencyScore = BigDecimal.valueOf(daysWithActivity * 100.0 / totalDaysInMonth)
                            .setScale(2, RoundingMode.HALF_UP);

                    // Count goals achieved in this month
                    Long goalsAchieved = userGoalRepository.countGoalsCompletedInPeriod(userId, monthStart, monthEnd);

                    // Create additional report data
                    Map<String, Object> reportData = new HashMap<>();
                    reportData.put("daysWithActivity", daysWithActivity);
                    reportData.put("daysLogged", dailySummaries.size());
                    reportData.put("totalDaysInMonth", totalDaysInMonth);

                    MonthlyReport report = MonthlyReport.builder()
                            .userId(userId)
                            .month(month)
                            .year(year)
                            .totalCaloriesConsumed(totalCaloriesConsumed)
                            .totalCaloriesBurned(totalCaloriesBurned)
                            .totalWorkouts(totalWorkouts)
                            .totalWorkoutMinutes(totalWorkoutMinutes)
                            .avgDailyCalories(avgDailyCalories)
                            .goalsAchieved(goalsAchieved.intValue())
                            .consistencyScore(consistencyScore)
                            .reportData(reportData)
                            .build();

                    return monthlyReportRepository.save(report);
                });
    }

    /**
     * Get weekly report for a specific week
     */
    @Transactional(readOnly = true)
    public WeeklyReport getWeeklyReport(Long userId, LocalDate weekStartDate) {
        LocalDate weekStart = weekStartDate.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
        return weeklyReportRepository.findByUserIdAndWeekStartDate(userId, weekStart)
                .orElse(null);
    }

    /**
     * Get monthly report for a specific month
     */
    @Transactional(readOnly = true)
    public MonthlyReport getMonthlyReport(Long userId, int year, int month) {
        return monthlyReportRepository.findByUserIdAndYearAndMonth(userId, year, month)
                .orElse(null);
    }

    /**
     * Get all weekly reports for a user
     */
    @Transactional(readOnly = true)
    public List<WeeklyReport> getAllWeeklyReports(Long userId) {
        return weeklyReportRepository.findByUserIdOrderByWeekStartDateDesc(userId);
    }

    /**
     * Get all monthly reports for a user
     */
    @Transactional(readOnly = true)
    public List<MonthlyReport> getAllMonthlyReports(Long userId) {
        return monthlyReportRepository.findByUserIdOrderByYearDescMonthDesc(userId);
    }

    /**
     * Get recent weekly reports
     */
    @Transactional(readOnly = true)
    public List<WeeklyReport> getRecentWeeklyReports(Long userId, int weeks) {
        LocalDate startDate = LocalDate.now().minusWeeks(weeks);
        return weeklyReportRepository.findRecentReports(userId, startDate);
    }
}
