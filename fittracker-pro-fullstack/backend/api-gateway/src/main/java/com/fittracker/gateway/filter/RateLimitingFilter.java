package com.fittracker.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.Objects;

@Slf4j
@Component
public class RateLimitingFilter implements GlobalFilter, Ordered {

    @Autowired
    private ReactiveRedisTemplate<String, String> redisTemplate;

    private static final int MAX_REQUESTS_PER_MINUTE = 100;
    private static final Duration WINDOW_DURATION = Duration.ofMinutes(1);

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String clientIp = Objects.requireNonNull(exchange.getRequest().getRemoteAddress()).getAddress().getHostAddress();
        String key = "rate_limit:" + clientIp;

        return redisTemplate.opsForValue()
                .increment(key)
                .flatMap(count -> {
                    if (count == 1) {
                        // Set expiration for the first request
                        return redisTemplate.expire(key, WINDOW_DURATION)
                                .flatMap(expired -> processRequest(exchange, chain, count));
                    } else {
                        return processRequest(exchange, chain, count);
                    }
                })
                .onErrorResume(e -> {
                    log.error("Rate limiting error: {}", e.getMessage());
                    // On Redis error, allow the request
                    return chain.filter(exchange);
                });
    }

    private Mono<Void> processRequest(ServerWebExchange exchange, GatewayFilterChain chain, Long count) {
        if (count > MAX_REQUESTS_PER_MINUTE) {
            log.warn("Rate limit exceeded for IP: {}",
                    Objects.requireNonNull(exchange.getRequest().getRemoteAddress()).getAddress().getHostAddress());
            exchange.getResponse().setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
            exchange.getResponse().getHeaders().add("X-Rate-Limit-Retry-After-Seconds",
                    String.valueOf(WINDOW_DURATION.getSeconds()));
            return exchange.getResponse().setComplete();
        }

        // Add rate limit headers
        exchange.getResponse().getHeaders().add("X-Rate-Limit-Limit", String.valueOf(MAX_REQUESTS_PER_MINUTE));
        exchange.getResponse().getHeaders().add("X-Rate-Limit-Remaining",
                String.valueOf(MAX_REQUESTS_PER_MINUTE - count));

        return chain.filter(exchange);
    }

    @Override
    public int getOrder() {
        return -1; // Execute before other filters
    }
}
