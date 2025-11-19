package com.fittracker.analytics.controller;

import com.fittracker.common.dto.ApiResponse;
import com.fittracker.analytics.service.CacheWarmingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/analytics/cache")
@RequiredArgsConstructor
public class CacheController {

    private final CacheWarmingService cacheWarmingService;

    @PostMapping("/clear")
    public ResponseEntity<ApiResponse<Void>> clearAllCaches() {
        log.info("Manual cache clear requested");
        cacheWarmingService.clearAllCaches();
        return ResponseEntity.ok(ApiResponse.success("All caches cleared successfully", null));
    }

    @PostMapping("/clear/user/{userId}")
    public ResponseEntity<ApiResponse<Void>> clearUserCache(@PathVariable Long userId) {
        log.info("Manual cache clear requested for user {}", userId);
        cacheWarmingService.clearUserCache(userId);
        return ResponseEntity.ok(ApiResponse.success("User cache cleared successfully", null));
    }

    @PostMapping("/refresh")
    public ResponseEntity<ApiResponse<Void>> refreshCaches() {
        log.info("Manual cache refresh requested");
        cacheWarmingService.refreshCaches();
        return ResponseEntity.ok(ApiResponse.success("Caches refreshed successfully", null));
    }

    @PostMapping("/warm")
    public ResponseEntity<ApiResponse<Void>> warmCaches() {
        log.info("Manual cache warming requested");
        cacheWarmingService.warmUpCaches();
        return ResponseEntity.ok(ApiResponse.success("Caches warmed successfully", null));
    }
}
