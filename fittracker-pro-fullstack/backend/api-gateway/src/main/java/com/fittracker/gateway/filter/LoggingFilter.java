package com.fittracker.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.UUID;

@Slf4j
@Component
public class LoggingFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String correlationId = UUID.randomUUID().toString();

        log.info("Request [{}] - Method: {}, URI: {}, Remote Address: {}",
                correlationId,
                request.getMethod(),
                request.getURI(),
                request.getRemoteAddress());

        // Add correlation ID to request headers
        ServerHttpRequest modifiedRequest = request.mutate()
                .header("X-Correlation-ID", correlationId)
                .build();

        long startTime = System.currentTimeMillis();

        return chain.filter(exchange.mutate().request(modifiedRequest).build())
                .then(Mono.fromRunnable(() -> {
                    ServerHttpResponse response = exchange.getResponse();
                    long endTime = System.currentTimeMillis();
                    long duration = endTime - startTime;

                    log.info("Response [{}] - Status: {}, Duration: {}ms",
                            correlationId,
                            response.getStatusCode(),
                            duration);

                    // Add correlation ID to response headers
                    response.getHeaders().add("X-Correlation-ID", correlationId);
                }));
    }

    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;
    }
}
