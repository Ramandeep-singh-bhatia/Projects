package com.fittracker.analytics.controller;

import com.fittracker.analytics.entity.DailyActivitySummary;
import com.fittracker.analytics.service.AnalyticsService;
import com.fittracker.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/analytics")
@RequiredArgsConstructor
public class AnalyticsController {

    private final AnalyticsService analyticsService;

    @GetMapping("/daily/{userId}")
    public ResponseEntity<ApiResponse<DailyActivitySummary>> getDailySummary(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        log.info("Get daily summary for user {} on {}", userId, date);
        DailyActivitySummary summary = analyticsService.getDailySummary(userId, date);
        return ResponseEntity.ok(ApiResponse.success(summary));
    }

    @GetMapping("/daily/{userId}/range")
    public ResponseEntity<ApiResponse<List<DailyActivitySummary>>> getActivityInRange(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        log.info("Get activity range for user {} from {} to {}", userId, startDate, endDate);
        List<DailyActivitySummary> summaries = analyticsService.getActivityInRange(userId, startDate, endDate);
        return ResponseEntity.ok(ApiResponse.success(summaries));
    }

    @GetMapping("/daily/{userId}/recent")
    public ResponseEntity<ApiResponse<List<DailyActivitySummary>>> getRecentActivity(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "7") int days) {
        log.info("Get last {} days of activity for user {}", days, userId);
        List<DailyActivitySummary> summaries = analyticsService.getRecentActivity(userId, days);
        return ResponseEntity.ok(ApiResponse.success(summaries));
    }

    @GetMapping("/daily/{userId}/averages")
    public ResponseEntity<ApiResponse<Object>> getAverages(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        log.info("Get averages for user {} from {} to {}", userId, startDate, endDate);

        Double avgCaloriesConsumed = analyticsService.calculateAverageCaloriesConsumed(userId, startDate, endDate);
        Double avgCaloriesBurned = analyticsService.calculateAverageCaloriesBurned(userId, startDate, endDate);
        Long daysWithWorkouts = analyticsService.countDaysWithWorkouts(userId, startDate, endDate);

        java.util.Map<String, Object> averages = new java.util.HashMap<>();
        averages.put("avgCaloriesConsumed", avgCaloriesConsumed);
        averages.put("avgCaloriesBurned", avgCaloriesBurned);
        averages.put("daysWithWorkouts", daysWithWorkouts);

        return ResponseEntity.ok(ApiResponse.success(averages));
    }

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<Object>> health() {
        java.util.Map<String, String> health = new java.util.HashMap<>();
        health.put("status", "UP");
        health.put("service", "analytics-service");
        return ResponseEntity.ok(ApiResponse.success(health));
    }
}
