package com.fittracker.analytics.controller;

import com.fittracker.analytics.entity.Achievement;
import com.fittracker.analytics.service.AchievementService;
import com.fittracker.common.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/analytics/achievements")
@RequiredArgsConstructor
public class AchievementController {

    private final AchievementService achievementService;

    @GetMapping("/user/{userId}")
    public ResponseEntity<ApiResponse<Page<Achievement>>> getUserAchievements(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        log.info("Get achievements for user {}", userId);
        Page<Achievement> achievements = achievementService.getUserAchievements(userId, PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(achievements));
    }

    @GetMapping("/user/{userId}/recent")
    public ResponseEntity<ApiResponse<List<Achievement>>> getRecentAchievements(@PathVariable Long userId) {
        log.info("Get recent achievements for user {}", userId);
        List<Achievement> achievements = achievementService.getRecentAchievements(userId);
        return ResponseEntity.ok(ApiResponse.success(achievements));
    }

    @GetMapping("/user/{userId}/type/{type}")
    public ResponseEntity<ApiResponse<List<Achievement>>> getAchievementsByType(
            @PathVariable Long userId,
            @PathVariable Achievement.AchievementType type) {
        log.info("Get {} achievements for user {}", type, userId);
        List<Achievement> achievements = achievementService.getAchievementsByType(userId, type);
        return ResponseEntity.ok(ApiResponse.success(achievements));
    }

    @GetMapping("/user/{userId}/period")
    public ResponseEntity<ApiResponse<List<Achievement>>> getAchievementsInPeriod(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        log.info("Get achievements for user {} from {} to {}", userId, startDate, endDate);
        List<Achievement> achievements = achievementService.getAchievementsInPeriod(userId, startDate, endDate);
        return ResponseEntity.ok(ApiResponse.success(achievements));
    }
}
