package com.fittracker.analytics.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.cache.CacheManager;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class CacheWarmingService {

    private final CacheManager cacheManager;
    private final ReportService reportService;

    /**
     * Warm up caches on application startup
     */
    @EventListener(ApplicationReadyEvent.class)
    public void warmUpCaches() {
        log.info("Starting cache warming for Analytics Service...");

        long startTime = System.currentTimeMillis();

        // Analytics cache warming is minimal since data is user-specific
        // Most caching happens on-demand for daily summaries
        log.info("Analytics Service uses on-demand caching for user-specific data");

        long duration = System.currentTimeMillis() - startTime;
        log.info("Cache warming completed in {} ms", duration);
    }

    /**
     * Manually clear all caches
     */
    public void clearAllCaches() {
        log.info("Clearing all caches...");
        cacheManager.getCacheNames().forEach(cacheName -> {
            var cache = cacheManager.getCache(cacheName);
            if (cache != null) {
                cache.clear();
                log.info("Cleared cache: {}", cacheName);
            }
        });
    }

    /**
     * Clear cache for specific user
     */
    public void clearUserCache(Long userId) {
        log.info("Clearing cache for user {}", userId);

        // Clear daily activity cache
        var dailyActivityCache = cacheManager.getCache("dailyActivity");
        if (dailyActivityCache != null) {
            // Cache keys are userId + '-' + date, so we can't easily clear just one user
            // For now, clear all - in production, would use a more sophisticated approach
            dailyActivityCache.clear();
        }

        // Clear other user-specific caches
        cacheManager.getCacheNames().forEach(cacheName -> {
            var cache = cacheManager.getCache(cacheName);
            if (cache != null && (cacheName.startsWith("goals") ||
                                 cacheName.startsWith("achievements") ||
                                 cacheName.startsWith("weeklyReports") ||
                                 cacheName.startsWith("monthlyReports"))) {
                cache.clear();
            }
        });
    }

    /**
     * Manually refresh caches
     */
    public void refreshCaches() {
        log.info("Refreshing caches...");
        clearAllCaches();
        warmUpCaches();
    }
}
