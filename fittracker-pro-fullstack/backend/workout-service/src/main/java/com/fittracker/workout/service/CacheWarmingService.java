package com.fittracker.workout.service;

import com.fittracker.workout.entity.Exercise;
import com.fittracker.workout.repository.ExerciseRepository;
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

    private final ExerciseRepository exerciseRepository;
    private final CacheManager cacheManager;

    /**
     * Warm up caches on application startup
     */
    @EventListener(ApplicationReadyEvent.class)
    public void warmUpCaches() {
        log.info("Starting cache warming for Workout Service...");

        long startTime = System.currentTimeMillis();

        warmExercisesCache();

        long duration = System.currentTimeMillis() - startTime;
        log.info("Cache warming completed in {} ms", duration);
    }

    /**
     * Warm up exercises cache with verified exercises
     */
    private void warmExercisesCache() {
        try {
            log.info("Warming exercises cache...");

            // Load all verified exercises (exercise library)
            List<Exercise> verifiedExercises = exerciseRepository.findByIsVerifiedTrue(PageRequest.of(0, 100))
                    .getContent();

            log.info("Loaded {} verified exercises into cache", verifiedExercises.size());

            // Pre-load common exercises by difficulty
            exerciseRepository.findByDifficultyLevel(Exercise.DifficultyLevel.BEGINNER, PageRequest.of(0, 20));
            exerciseRepository.findByDifficultyLevel(Exercise.DifficultyLevel.INTERMEDIATE, PageRequest.of(0, 20));

            log.info("Exercises cache warming completed");

        } catch (Exception e) {
            log.error("Error warming exercises cache", e);
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
