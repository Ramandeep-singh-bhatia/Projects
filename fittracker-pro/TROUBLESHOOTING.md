# FitTracker Pro - Troubleshooting Guide

## Table of Contents

1. [Build and Compilation Issues](#build-and-compilation-issues)
2. [Service Startup Problems](#service-startup-problems)
3. [Database Issues](#database-issues)
4. [Network and Connectivity](#network-and-connectivity)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Kafka and Messaging](#kafka-and-messaging)
7. [Caching Issues](#caching-issues)
8. [Performance Problems](#performance-problems)
9. [Docker and Container Issues](#docker-and-container-issues)
10. [Common Error Messages](#common-error-messages)

---

## Build and Compilation Issues

### Problem: Maven Build Fails with "Java version mismatch"

**Symptom:**
```
[ERROR] Failed to execute goal ... compiler:compile ... Source option 17 is no longer supported
```

**Solution:**
```bash
# Verify Java version
java -version  # Must show 17 or higher

# Set JAVA_HOME
export JAVA_HOME=/path/to/jdk-17

# On macOS with Homebrew:
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# On Linux:
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk

# Verify
echo $JAVA_HOME
mvn -version  # Should show Java 17
```

**In IntelliJ IDEA:**
```
File → Project Structure → Project SDK → Select JDK 17
File → Settings → Build, Execution, Deployment → Build Tools → Maven → JDK for importer → Select JDK 17
```

---

### Problem: "Cannot resolve symbol" or "Package does not exist"

**Symptom:**
```
[ERROR] cannot find symbol: class Lombok
[ERROR] package com.fittracker.common does not exist
```

**Solution:**

**1. Ensure Lombok is installed (IntelliJ):**
```
File → Settings → Plugins → Search "Lombok" → Install
File → Settings → Build, Execution, Deployment → Compiler → Annotation Processors → Enable annotation processing ✓
```

**2. Rebuild common module:**
```bash
cd common
mvn clean install
cd ..
```

**3. Reimport Maven project:**
```
Right-click pom.xml → Maven → Reload Project
```

**4. Invalidate caches (IntelliJ):**
```
File → Invalidate Caches / Restart → Invalidate and Restart
```

---

### Problem: Build fails with "dependency not found"

**Symptom:**
```
[ERROR] Failed to read artifact descriptor for org.springframework.boot:spring-boot-starter-web:jar:3.2.0
```

**Solution:**

**1. Clear Maven cache:**
```bash
# Delete .m2 cache
rm -rf ~/.m2/repository

# Rebuild
mvn clean install
```

**2. Check Maven settings:**
```bash
# Verify Maven installation
mvn --version

# Check settings.xml
cat ~/.m2/settings.xml
```

**3. Check internet connection:**
```bash
# Test connectivity to Maven Central
ping repo.maven.apache.org

# Try alternate mirror in settings.xml
```

---

## Service Startup Problems

### Problem: Service fails to start - "Port already in use"

**Symptom:**
```
Web server failed to start. Port 8081 was already in use.
```

**Solution:**

**1. Find process using the port:**
```bash
# On Linux/Mac:
lsof -i :8081

# On Windows:
netstat -ano | findstr :8081
```

**2. Kill the process:**
```bash
# Linux/Mac:
kill -9 <PID>

# Windows:
taskkill /PID <PID> /F
```

**3. Or change the port:**
```yaml
# application.yml
server:
  port: 8091  # Use different port
```

---

### Problem: Service starts but doesn't register with Eureka

**Symptom:**
```
Service running but not visible in Eureka dashboard (http://localhost:8761)
```

**Solution:**

**1. Check Eureka Server is running:**
```bash
curl http://localhost:8761
```

**2. Verify Eureka configuration:**
```yaml
# application.yml
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
    register-with-eureka: true
    fetch-registry: true
```

**3. Check logs for connection errors:**
```bash
mvn spring-boot:run | grep -i eureka
```

**4. Check network connectivity:**
```bash
ping localhost
curl http://localhost:8761/eureka/apps
```

**5. Wait 30-60 seconds** - Registration can take time

**6. Restart in this order:**
```bash
# 1. Eureka
cd eureka-server && mvn spring-boot:run

# 2. Wait 30 seconds

# 3. Other services
cd user-service && mvn spring-boot:run
```

---

### Problem: Application fails to connect to database

**Symptom:**
```
com.zaxxer.hikari.pool.HikariPool$PoolInitializationException: Failed to initialize pool
org.postgresql.util.PSQLException: Connection refused
```

**Solution:**

**1. Verify PostgreSQL is running:**
```bash
docker-compose ps postgres

# Should show "Up (healthy)"
```

**2. Check database exists:**
```bash
docker exec -it fittracker-postgres psql -U fittracker -l

# Should list: fittracker_users, fittracker_nutrition, etc.
```

**3. Verify connection details:**
```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/fittracker_users
    username: fittracker
    password: fittracker123  # Match docker-compose.yml
```

**4. Test connection manually:**
```bash
docker exec -it fittracker-postgres psql -U fittracker -d fittracker_users

# If successful, database is accessible
```

**5. Check firewall:**
```bash
# Ensure port 5432 is open
sudo ufw status
sudo ufw allow 5432
```

**6. Recreate database if needed:**
```bash
docker-compose down -v  # WARNING: Deletes data!
docker-compose up -d
```

---

## Database Issues

### Problem: Flyway migration fails

**Symptom:**
```
FlywayException: Validate failed: Migration checksum mismatch
```

**Solution:**

**1. Check which migration failed:**
```bash
docker exec -it fittracker-postgres psql -U fittracker -d fittracker_users -c "SELECT * FROM flyway_schema_history ORDER BY installed_rank DESC LIMIT 5;"
```

**2. If development environment, reset database:**
```bash
# Drop and recreate database
docker exec -it fittracker-postgres psql -U fittracker <<EOF
DROP DATABASE fittracker_users;
CREATE DATABASE fittracker_users;
EOF

# Restart service to run migrations
mvn spring-boot:run
```

**3. If production, repair Flyway:**
```bash
mvn flyway:repair -pl user-service
```

**4. Never modify existing migrations!** Create new ones instead.

---

### Problem: "too many connections" error

**Symptom:**
```
PSQLException: FATAL: sorry, too many clients already
```

**Solution:**

**1. Check current connections:**
```sql
SELECT count(*) FROM pg_stat_activity;
```

**2. Check max connections:**
```sql
SHOW max_connections;
```

**3. Reduce connection pool size:**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 5  # Reduce from 10
```

**4. Increase PostgreSQL max_connections:**

Edit docker-compose.yml:
```yaml
postgres:
  command: postgres -c max_connections=200
```

**5. Kill idle connections:**
```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '10 minutes';
```

---

### Problem: Slow queries

**Symptom:**
```
Queries taking seconds instead of milliseconds
```

**Solution:**

**1. Enable query logging:**
```yaml
spring:
  jpa:
    show-sql: true
logging:
  level:
    org.hibernate.SQL: DEBUG
```

**2. Analyze slow query:**
```sql
EXPLAIN ANALYZE
SELECT * FROM meals WHERE user_id = 1 AND meal_date BETWEEN '2024-01-01' AND '2024-01-31';
```

**3. Add indexes:**
```sql
CREATE INDEX idx_meals_user_date ON meals(user_id, meal_date);
```

**4. Check statistics:**
```sql
ANALYZE meals;
```

**5. Vacuum if needed:**
```sql
VACUUM ANALYZE meals;
```

---

## Network and Connectivity

### Problem: API Gateway returns 503 Service Unavailable

**Symptom:**
```
HTTP 503: Service Unavailable
No instances available for user-service
```

**Solution:**

**1. Check Eureka for registered services:**
```bash
curl http://localhost:8761/eureka/apps
```

**2. Verify service is running:**
```bash
curl http://localhost:8081/actuator/health
```

**3. Check service logs:**
```bash
docker-compose logs user-service | grep -i "registered with eureka"
```

**4. Restart in order:**
```bash
docker-compose restart eureka-server
# Wait 30 seconds
docker-compose restart user-service
# Wait 30 seconds
docker-compose restart api-gateway
```

---

### Problem: CORS errors in browser

**Symptom:**
```
Access to XMLHttpRequest at 'http://localhost:8080/api/users/login' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**

**Add CORS configuration to API Gateway:**

```java
@Bean
public CorsWebFilter corsWebFilter() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(Arrays.asList("http://localhost:3000", "https://app.fittrackerpro.com"));
    config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(Arrays.asList("*"));
    config.setAllowCredentials(true);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);

    return new CorsWebFilter(source);
}
```

---

## Authentication and Authorization

### Problem: JWT token invalid or expired

**Symptom:**
```
HTTP 401: Unauthorized
JWT token is expired or invalid
```

**Solution:**

**1. Check token expiration:**
```bash
# Default expiration is 24 hours
# Get new token by logging in again
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

**2. Verify JWT secret matches across services:**
```bash
# Check .env file
grep JWT_SECRET .env

# Should be same in all services
```

**3. Check token format:**
```bash
# Token should be: Authorization: Bearer eyJhbGci...
# NOT: Authorization: eyJhbGci... (missing "Bearer ")
```

**4. Decode token to check expiration:**
```bash
# Use https://jwt.io or:
echo "eyJhbGci..." | cut -d. -f2 | base64 -d
```

---

### Problem: "Access Denied" or 403 Forbidden

**Symptom:**
```
HTTP 403: Forbidden
Access Denied
```

**Solution:**

**1. Check user has correct role:**
```sql
SELECT * FROM users WHERE email = 'user@example.com';
```

**2. Verify endpoint security configuration:**
```java
.authorizeExchange()
    .pathMatchers("/api/users/register", "/api/users/login").permitAll()
    .anyExchange().authenticated()
```

**3. Check token includes user ID:**
```bash
# Decode JWT payload
```

**4. Verify resource ownership:**
```java
// Ensure user can only access their own data
if (!meal.getUserId().equals(currentUserId)) {
    throw new AccessDeniedException();
}
```

---

## Kafka and Messaging

### Problem: Events not being consumed

**Symptom:**
```
Meals created but Analytics not updating
Events published but no consumer logs
```

**Solution:**

**1. Check Kafka is running:**
```bash
docker-compose ps kafka

# Should show "Up (healthy)"
```

**2. List topics:**
```bash
docker exec fittracker-kafka kafka-topics --list --bootstrap-server localhost:9092

# Should show: meal-events, workout-events, user-events
```

**3. Check consumer group:**
```bash
docker exec fittracker-kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe \
    --group analytics-service
```

**4. Check consumer lag:**
```bash
docker exec fittracker-kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe \
    --group analytics-service

# LAG column should be 0 or low
```

**5. Check consumer logs:**
```bash
docker-compose logs analytics-service | grep -i "received.*event"
```

**6. Manually consume messages:**
```bash
docker exec -it fittracker-kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic meal-events \
    --from-beginning

# Should show recent events
```

**7. Reset consumer offset if needed:**
```bash
# WARNING: Will reprocess all events
docker exec fittracker-kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group analytics-service \
    --reset-offsets \
    --to-earliest \
    --topic meal-events \
    --execute
```

---

### Problem: Kafka consumer lag increasing

**Symptom:**
```
Consumer lag growing over time
Events piling up
```

**Solution:**

**1. Check consumer is running:**
```bash
docker-compose ps analytics-service
```

**2. Check for errors in consumer:**
```bash
docker-compose logs analytics-service | grep -i error
```

**3. Scale consumers (if using multiple partitions):**
```bash
docker-compose up -d --scale analytics-service=2
```

**4. Increase consumer resources:**
```yaml
analytics-service:
  environment:
    JAVA_OPTS: -Xms1g -Xmx2g
```

**5. Optimize consumer:**
```yaml
spring:
  kafka:
    consumer:
      max-poll-records: 500  # Process more messages per poll
      fetch-min-size: 1024
```

---

## Caching Issues

### Problem: Stale data from cache

**Symptom:**
```
Updated food item but still seeing old values
```

**Solution:**

**1. Clear cache manually:**
```bash
curl -X POST http://localhost:8082/cache/clear \
  -H "Authorization: Bearer $TOKEN"
```

**2. Clear Redis directly:**
```bash
docker exec fittracker-redis redis-cli FLUSHALL
```

**3. Check cache eviction:**
```java
@CacheEvict(value = "foodItems", key = "#id")
public void updateFoodItem(Long id, FoodItem item) {
    // Should evict cache on update
}
```

**4. Reduce TTL for testing:**
```java
@Cacheable(value = "foodItems", key = "#id")
// TTL configured in CacheConfig (default 1 hour)
```

**5. Disable cache for debugging:**
```yaml
spring:
  cache:
    type: none
```

---

### Problem: Redis connection refused

**Symptom:**
```
io.lettuce.core.RedisConnectionException: Unable to connect to localhost:6379
```

**Solution:**

**1. Check Redis is running:**
```bash
docker-compose ps redis
```

**2. Test connection:**
```bash
docker exec fittracker-redis redis-cli ping
# Should return: PONG
```

**3. Verify configuration:**
```yaml
spring:
  redis:
    host: localhost
    port: 6379
    password: ${REDIS_PASSWORD}  # If set
```

**4. Check Redis password:**
```bash
# If Redis has password
docker exec fittracker-redis redis-cli -a ${REDIS_PASSWORD} ping
```

**5. Restart Redis:**
```bash
docker-compose restart redis
```

---

## Performance Problems

### Problem: High memory usage / OutOfMemoryError

**Symptom:**
```
java.lang.OutOfMemoryError: Java heap space
```

**Solution:**

**1. Increase heap size:**
```bash
# Run with more memory
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xmx2g"

# Or in Docker:
JAVA_OPTS: "-Xms512m -Xmx2g"
```

**2. Generate heap dump:**
```bash
# Add to JVM args:
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heap.hprof
```

**3. Analyze with MAT (Memory Analyzer Tool):**
```bash
# Download Eclipse MAT
# Open heap dump file
# Look for memory leaks
```

**4. Check for leaks:**
- Unclosed database connections
- Large collections in memory
- Cache growing unbounded

**5. Enable GC logging:**
```bash
-Xloggc:gc.log -XX:+PrintGCDetails -XX:+PrintGCDateStamps
```

---

### Problem: Slow API responses

**Symptom:**
```
API calls taking seconds instead of milliseconds
```

**Solution:**

**1. Enable request timing logs:**
```yaml
logging:
  level:
    org.springframework.web: DEBUG
```

**2. Check database query performance:**
```sql
-- Enable slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s

-- Check slow queries
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**3. Add database indexes:**
```sql
-- Find missing indexes
SELECT * FROM pg_stat_user_tables WHERE idx_scan = 0;
```

**4. Enable caching:**
```java
@Cacheable("foodItems")
public FoodItem getFoodItem(Long id) { ... }
```

**5. Use Jaeger to find bottlenecks:**
```bash
# Access Jaeger UI
open http://localhost:16686

# Find slow traces
# Analyze span durations
```

**6. Check connection pool:**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10  # Increase if needed
```

---

## Docker and Container Issues

### Problem: Docker containers won't start

**Symptom:**
```
docker-compose up fails
Container exits immediately
```

**Solution:**

**1. Check Docker is running:**
```bash
docker ps
```

**2. Check logs:**
```bash
docker-compose logs <service-name>
```

**3. Remove old containers:**
```bash
docker-compose down
docker-compose up -d
```

**4. Rebuild images:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

**5. Check disk space:**
```bash
df -h

# Clean up Docker
docker system prune -a
```

**6. Check Docker resources:**
```
Docker Desktop → Settings → Resources
- Increase CPU
- Increase Memory (8GB+ recommended)
```

---

### Problem: "No space left on device"

**Symptom:**
```
Error: failed to start containers: no space left on device
```

**Solution:**

**1. Check disk usage:**
```bash
df -h
docker system df
```

**2. Clean up Docker:**
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

**3. Check logs:**
```bash
# Log files can get large
find /var/lib/docker/containers -name "*.log" -exec ls -lh {} \;

# Configure log rotation in docker-compose.yml
```

---

## Common Error Messages

### "Connection pool exhausted"

**Cause:** Too many simultaneous database connections

**Solution:**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20  # Increase
```

---

### "Unable to acquire JDBC Connection"

**Cause:** Database not accessible

**Solution:**
1. Check PostgreSQL is running
2. Verify connection string
3. Check firewall rules
4. Test manual connection

---

### "Failed to register with Eureka"

**Cause:** Eureka Server not reachable

**Solution:**
1. Start Eureka Server first
2. Check network connectivity
3. Verify eureka.client.service-url.defaultZone

---

### "Message not received by Kafka"

**Cause:** Kafka not running or consumer not configured

**Solution:**
1. Check Kafka is running
2. Verify topic exists
3. Check consumer group
4. Review consumer logs

---

### "Cache miss rate too high"

**Cause:** Cache not warming properly or TTL too short

**Solution:**
1. Check cache warming logs
2. Increase TTL
3. Preload more data

---

### "401 Unauthorized"

**Cause:** Missing or invalid JWT token

**Solution:**
1. Login to get new token
2. Check Authorization header format
3. Verify token not expired

---

### "415 Unsupported Media Type"

**Cause:** Missing or wrong Content-Type header

**Solution:**
```bash
# Add Content-Type header
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

---

## Getting More Help

### Enable Debug Logging

```yaml
logging:
  level:
    root: INFO
    com.fittracker: DEBUG
    org.springframework: DEBUG
    org.hibernate.SQL: DEBUG
```

### Check Health Endpoints

```bash
curl http://localhost:8081/actuator/health
curl http://localhost:8081/actuator/metrics
curl http://localhost:8081/actuator/env
```

### Collect Diagnostic Information

```bash
#!/bin/bash
# collect-diagnostics.sh

echo "=== Docker Status ===" > diagnostics.txt
docker-compose ps >> diagnostics.txt

echo "\n=== Service Logs ===" >> diagnostics.txt
docker-compose logs --tail=100 >> diagnostics.txt

echo "\n=== Database Status ===" >> diagnostics.txt
docker exec fittracker-postgres psql -U fittracker -c "\l" >> diagnostics.txt

echo "\n=== Redis Status ===" >> diagnostics.txt
docker exec fittracker-redis redis-cli INFO >> diagnostics.txt

echo "\n=== Kafka Topics ===" >> diagnostics.txt
docker exec fittracker-kafka kafka-topics --list --bootstrap-server localhost:9092 >> diagnostics.txt

echo "Diagnostics saved to diagnostics.txt"
```

---

## Still Having Issues?

1. **Check Documentation:**
   - [README.md](README.md)
   - [GETTING_STARTED.md](GETTING_STARTED.md)
   - [ARCHITECTURE.md](ARCHITECTURE.md)
   - [API_REFERENCE.md](API_REFERENCE.md)
   - [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
   - [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)

2. **Review Logs Carefully:**
   - Stack traces contain valuable information
   - Look for "Caused by:" messages
   - Check all related service logs

3. **Search Issues:**
   - GitHub Issues
   - Stack Overflow
   - Spring Boot documentation

4. **Create an Issue:**
   - Provide error messages
   - Include steps to reproduce
   - Share relevant logs
   - Specify environment (OS, Java version, etc.)

---

**Remember:** Most issues are configuration-related. Double-check your environment variables, connection strings, and service startup order!
