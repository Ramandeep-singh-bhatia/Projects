package com.fittracker.analytics.config;

import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        // Default cache configuration - 1 hour TTL
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofHours(1))
                .disableCachingNullValues();

        // Custom cache configurations
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();

        // Daily activity summaries - cache for 30 minutes (frequently updated)
        cacheConfigurations.put("dailyActivity",
                RedisCacheConfiguration.defaultCacheConfig()
                        .entryTtl(Duration.ofMinutes(30))
                        .disableCachingNullValues());

        // Weekly reports - cache for 6 hours (less frequently updated)
        cacheConfigurations.put("weeklyReports",
                RedisCacheConfiguration.defaultCacheConfig()
                        .entryTtl(Duration.ofHours(6))
                        .disableCachingNullValues());

        // Monthly reports - cache for 12 hours (rarely updated)
        cacheConfigurations.put("monthlyReports",
                RedisCacheConfiguration.defaultCacheConfig()
                        .entryTtl(Duration.ofHours(12))
                        .disableCachingNullValues());

        // Goals - cache for 1 hour
        cacheConfigurations.put("goals",
                RedisCacheConfiguration.defaultCacheConfig()
                        .entryTtl(Duration.ofHours(1))
                        .disableCachingNullValues());

        // Achievements - cache for 2 hours (rarely change)
        cacheConfigurations.put("achievements",
                RedisCacheConfiguration.defaultCacheConfig()
                        .entryTtl(Duration.ofHours(2))
                        .disableCachingNullValues());

        return RedisCacheManager.builder(connectionFactory)
                .cacheDefaults(defaultConfig)
                .withInitialCacheConfigurations(cacheConfigurations)
                .build();
    }
}
