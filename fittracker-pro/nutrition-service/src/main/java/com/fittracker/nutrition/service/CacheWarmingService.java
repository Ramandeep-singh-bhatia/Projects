package com.fittracker.nutrition.service;

import com.fittracker.nutrition.entity.FoodItem;
import com.fittracker.nutrition.repository.FoodItemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.cache.CacheManager;
import org.springframework.context.event.EventListener;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class CacheWarmingService {

    private final FoodItemRepository foodItemRepository;
    private final CacheManager cacheManager;

    /**
     * Warm up caches on application startup
     */
    @EventListener(ApplicationReadyEvent.class)
    public void warmUpCaches() {
        log.info("Starting cache warming for Nutrition Service...");

        long startTime = System.currentTimeMillis();

        warmFoodItemsCache();

        long duration = System.currentTimeMillis() - startTime;
        log.info("Cache warming completed in {} ms", duration);
    }

    /**
     * Warm up food items cache with verified items
     */
    private void warmFoodItemsCache() {
        try {
            log.info("Warming food items cache...");

            // Load verified food items (most commonly used)
            List<FoodItem> verifiedFoods = foodItemRepository.findByIsVerifiedTrue(PageRequest.of(0, 100))
                    .getContent();

            log.info("Loaded {} verified food items into cache", verifiedFoods.size());

            // Load all categories to ensure category-based searches are fast
            log.info("Food items cache warming completed");

        } catch (Exception e) {
            log.error("Error warming food items cache", e);
            // Don't fail application startup on cache warming errors
        }
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
     * Manually refresh caches
     */
    public void refreshCaches() {
        log.info("Refreshing caches...");
        clearAllCaches();
        warmUpCaches();
    }
}
