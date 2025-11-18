# FitTracker Pro - Operations Guide

## Table of Contents

1. [Production Deployment](#production-deployment)
2. [Monitoring and Alerts](#monitoring-and-alerts)
3. [Backup and Recovery](#backup-and-recovery)
4. [Scaling](#scaling)
5. [Performance Tuning](#performance-tuning)
6. [Security Operations](#security-operations)
7. [Incident Response](#incident-response)
8. [Maintenance](#maintenance)

---

## Production Deployment

### Pre-Deployment Checklist

✅ **Infrastructure:**
- [ ] PostgreSQL 14+ installed and configured
- [ ] Redis 7+ installed and configured
- [ ] Kafka cluster ready
- [ ] Docker and Docker Compose installed
- [ ] Sufficient disk space (50GB+ recommended)
- [ ] Network ports open (8080-8084, 5432, 6379, 9092, etc.)

✅ **Security:**
- [ ] Strong passwords generated for all services
- [ ] JWT secret generated (256-bit)
- [ ] SSL/TLS certificates obtained
- [ ] Firewall rules configured
- [ ] Database credentials secured
- [ ] Redis password authentication enabled

✅ **Configuration:**
- [ ] .env file created from .env.example
- [ ] All environment variables set
- [ ] Service profiles set to 'prod'
- [ ] Log levels configured appropriately
- [ ] Backup strategy in place

✅ **Testing:**
- [ ] All tests passing
- [ ] Integration tests run successfully
- [ ] Load testing completed
- [ ] Security scan performed
- [ ] API documentation reviewed

### Deployment Steps

**Step 1: Prepare Environment**

```bash
# Create .env file
cp .env.example .env

# Edit with production values
vi .env
```

**Critical environment variables:**

```env
# Database
POSTGRES_PASSWORD=<strong-password-here>
REDIS_PASSWORD=<strong-password-here>

# JWT Security
JWT_SECRET=<256-bit-secret-generated-with-openssl-rand-base64-32>
JWT_EXPIRATION=86400000

# Monitoring
GRAFANA_ADMIN_PASSWORD=<strong-password-here>
```

**Step 2: Build Services**

```bash
# Build all JAR files
mvn clean package -DskipTests

# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Verify images
docker images | grep fittracker
```

**Step 3: Start Infrastructure**

```bash
# Start infrastructure services first
docker-compose up -d postgres redis kafka zookeeper

# Wait for health checks (60 seconds)
watch docker-compose ps

# Verify
docker-compose logs postgres | grep "ready to accept connections"
docker-compose logs kafka | grep "started"
```

**Step 4: Start Microservices**

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Watch logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify all services registered with Eureka
curl http://localhost:8761
```

**Step 5: Verify Deployment**

```bash
# Check health endpoints
curl http://localhost:8081/actuator/health  # User Service
curl http://localhost:8082/actuator/health  # Nutrition Service
curl http://localhost:8083/actuator/health  # Workout Service
curl http://localhost:8084/actuator/health  # Analytics Service

# Test API Gateway
curl http://localhost:8080/actuator/health

# Check service registration
curl http://localhost:8761/eureka/apps
```

**Step 6: Load Sample Data (Optional)**

```bash
cd sample-data
./load-all-data.sh
```

**Step 7: Configure Monitoring**

```bash
# Access Grafana
open http://localhost:3000

# Login: admin / <GRAFANA_ADMIN_PASSWORD>
# Import dashboards from docker/grafana/dashboards/
```

---

## Monitoring and Alerts

### Health Checks

**Service Health Endpoints:**

```bash
# All services expose /actuator/health
curl http://localhost:8081/actuator/health

# Response:
{
  "status": "UP",
  "components": {
    "db": {"status": "UP"},
    "diskSpace": {"status": "UP"},
    "ping": {"status": "UP"}
  }
}
```

**Automated Health Monitoring Script:**

```bash
#!/bin/bash
# health-check.sh

SERVICES=(
    "http://localhost:8081/actuator/health"
    "http://localhost:8082/actuator/health"
    "http://localhost:8083/actuator/health"
    "http://localhost:8084/actuator/health"
)

for service in "${SERVICES[@]}"; do
    status=$(curl -s $service | jq -r '.status')
    if [ "$status" != "UP" ]; then
        echo "ALERT: Service $service is DOWN"
        # Send alert (email, Slack, PagerDuty, etc.)
    fi
done
```

**Run as cron job:**

```bash
# Check every 5 minutes
*/5 * * * * /path/to/health-check.sh
```

### Prometheus Metrics

**Access Prometheus:**
```
http://localhost:9090
```

**Key Metrics to Monitor:**

**1. Request Rate:**
```promql
rate(http_server_requests_seconds_count[5m])
```

**2. Error Rate:**
```promql
rate(http_server_requests_seconds_count{status=~"5.."}[5m])
```

**3. Response Time (95th percentile):**
```promql
histogram_quantile(0.95, rate(http_server_requests_seconds_bucket[5m]))
```

**4. JVM Memory:**
```promql
jvm_memory_used_bytes{area="heap"}
```

**5. Database Connections:**
```promql
hikaricp_connections_active
```

**6. Cache Hit Rate:**
```promql
rate(cache_gets_total{result="hit"}[5m]) /
rate(cache_gets_total[5m])
```

### Grafana Dashboards

**Access Grafana:**
```
http://localhost:3000
Username: admin
Password: <GRAFANA_ADMIN_PASSWORD>
```

**Pre-configured Dashboards:**

1. **System Overview**
   - CPU, Memory, Disk usage
   - Network I/O
   - Container stats

2. **Application Metrics**
   - Request rates per service
   - Response times
   - Error rates
   - Throughput

3. **JVM Metrics**
   - Heap usage
   - GC activity
   - Thread count
   - Class loading

4. **Database Metrics**
   - Connection pool utilization
   - Query performance
   - Slow queries
   - Deadlocks

5. **Cache Metrics**
   - Hit/miss rates
   - Eviction rates
   - Cache size

### Alerting Rules

**Configure in Prometheus** (docker/prometheus.yml):

```yaml
rule_files:
  - 'alert.rules'

alerting:
  alertmanagers:
    - static_configs:
      - targets: ['alertmanager:9093']
```

**Sample Alert Rules** (docker/prometheus/alert.rules):

```yaml
groups:
  - name: fittracker_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_server_requests_seconds_count{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Service {{ $labels.service }} has error rate > 5%"

      - alert: HighMemoryUsage
        expr: jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Service {{ $labels.service }} using > 90% heap"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.job }} is not responding"
```

### Jaeger Distributed Tracing

**Access Jaeger UI:**
```
http://localhost:16686
```

**Common Tracing Queries:**

1. **Find slow requests:**
   - Service: user-service
   - Min Duration: 500ms
   - Limit Results: 100

2. **Track request across services:**
   - Service: api-gateway
   - Operation: POST /api/nutrition/meals
   - View trace to see flow through all services

3. **Identify bottlenecks:**
   - Look for spans with long durations
   - Check database queries
   - Identify external API calls

---

## Backup and Recovery

### Database Backup

**Automated Daily Backup:**

```bash
#!/bin/bash
# backup-databases.sh

BACKUP_DIR="/var/backups/fittracker"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup each database
databases=("fittracker_users" "fittracker_nutrition" "fittracker_workouts" "fittracker_analytics")

for db in "${databases[@]}"; do
    docker exec fittracker-postgres pg_dump -U fittracker $db | \
        gzip > "$BACKUP_DIR/${db}_${DATE}.sql.gz"

    echo "Backed up $db to ${db}_${DATE}.sql.gz"
done

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed at $(date)"
```

**Schedule with cron:**

```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup-databases.sh >> /var/log/fittracker-backup.log 2>&1
```

**Manual Backup:**

```bash
# Backup single database
docker exec fittracker-postgres pg_dump -U fittracker fittracker_users > users_backup.sql

# Backup all databases
docker exec fittracker-postgres pg_dumpall -U fittracker > full_backup.sql
```

### Database Restore

**Restore from backup:**

```bash
# Restore single database
gunzip < backup_file.sql.gz | \
    docker exec -i fittracker-postgres psql -U fittracker -d fittracker_users

# Or uncompressed backup
docker exec -i fittracker-postgres psql -U fittracker -d fittracker_users < backup_file.sql
```

**Full Restore Process:**

```bash
# 1. Stop all microservices
docker-compose -f docker-compose.prod.yml stop user-service nutrition-service workout-service analytics-service

# 2. Drop and recreate databases
docker exec -it fittracker-postgres psql -U fittracker <<EOF
DROP DATABASE fittracker_users;
DROP DATABASE fittracker_nutrition;
DROP DATABASE fittracker_workouts;
DROP DATABASE fittracker_analytics;

CREATE DATABASE fittracker_users;
CREATE DATABASE fittracker_nutrition;
CREATE DATABASE fittracker_workouts;
CREATE DATABASE fittracker_analytics;
EOF

# 3. Restore from backups
gunzip < users_backup.sql.gz | docker exec -i fittracker-postgres psql -U fittracker -d fittracker_users
gunzip < nutrition_backup.sql.gz | docker exec -i fittracker-postgres psql -U fittracker -d fittracker_nutrition
gunzip < workouts_backup.sql.gz | docker exec -i fittracker-postgres psql -U fittracker -d fittracker_workouts
gunzip < analytics_backup.sql.gz | docker exec -i fittracker-postgres psql -U fittracker -d fittracker_analytics

# 4. Restart services
docker-compose -f docker-compose.prod.yml start
```

### Redis Backup

**Enable RDB snapshots** (docker-compose.prod.yml):

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --save 60 1000 --appendonly yes
  volumes:
    - redis_data:/data
```

**Manual snapshot:**

```bash
docker exec fittracker-redis redis-cli BGSAVE
```

**Backup Redis data:**

```bash
# Copy RDB file
docker cp fittracker-redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

### Kafka Backup

**Kafka data is in Docker volumes:**

```bash
# Backup Kafka volume
docker run --rm \
    -v fittracker-pro_kafka_data:/data \
    -v $(pwd):/backup \
    alpine tar czf /backup/kafka_backup_$(date +%Y%m%d).tar.gz -C /data .
```

---

## Scaling

### Horizontal Scaling

**Scale microservices:**

```bash
# Scale nutrition service to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale nutrition-service=3

# Scale workout service to 2 instances
docker-compose -f docker-compose.prod.yml up -d --scale workout-service=2

# Check instances
docker-compose ps
```

**Verify in Eureka:**
```bash
# Check Eureka dashboard
open http://localhost:8761

# Should show multiple instances:
# NUTRITION-SERVICE: 3 instances
# WORKOUT-SERVICE: 2 instances
```

**Load balancing is automatic** through API Gateway and Eureka.

### Vertical Scaling

**Increase JVM memory:**

Edit docker-compose.prod.yml:

```yaml
user-service:
  environment:
    JAVA_OPTS: -Xms1g -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200
```

**Increase database connections:**

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 10
```

### Database Scaling

**Read Replicas:**

For read-heavy workloads, configure PostgreSQL replication:

1. Set up primary-replica replication
2. Configure services to use read replicas for queries
3. Use primary for writes

**Connection Pooling:**

Adjust pool sizes based on load:

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10  # Per service instance
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

**Rule of thumb:**
- Total connections = (instances × pool size) × services
- PostgreSQL max_connections should be 2-3× total expected connections

---

## Performance Tuning

### JVM Tuning

**Recommended settings for production:**

```bash
JAVA_OPTS=" \
  -Xms512m \
  -Xmx1024m \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/logs/heap-dump.hprof \
  -XX:+PrintGCDetails \
  -XX:+PrintGCDateStamps \
  -Xloggc:/logs/gc.log \
  -XX:+UseGCLogFileRotation \
  -XX:NumberOfGCLogFiles=10 \
  -XX:GCLogFileSize=10M"
```

### Database Optimization

**1. Add Indexes:**

```sql
-- Index frequently queried columns
CREATE INDEX idx_meals_user_date ON meals(user_id, meal_date);
CREATE INDEX idx_workouts_user_date ON workouts(user_id, workout_date);
CREATE INDEX idx_daily_summary_user_date ON daily_summaries(user_id, date);
```

**2. Analyze Query Performance:**

```sql
EXPLAIN ANALYZE
SELECT * FROM meals
WHERE user_id = 1 AND meal_date BETWEEN '2024-01-01' AND '2024-01-31';
```

**3. Vacuum and Analyze:**

```bash
# Run weekly
docker exec fittracker-postgres psql -U fittracker -d fittracker_users -c "VACUUM ANALYZE;"
```

**4. Connection Pool Tuning:**

Monitor active connections:

```sql
SELECT count(*) FROM pg_stat_activity;
```

Adjust pool sizes if seeing connection waits.

### Cache Tuning

**1. Increase Redis Memory:**

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

**2. Adjust Cache TTL:**

```java
@Cacheable(value = "foodItems", key = "#id")
@CacheEvict(value = "foodItems", allEntries = true, condition = "#result.size() > 1000")
public FoodItem getFoodItem(Long id) {
    // ...
}
```

**3. Monitor Cache Performance:**

```bash
# Redis stats
docker exec fittracker-redis redis-cli INFO stats

# Cache hit rate
docker exec fittracker-redis redis-cli INFO stats | grep keyspace
```

### Kafka Tuning

**1. Increase Partitions:**

```bash
docker exec fittracker-kafka kafka-topics \
    --bootstrap-server localhost:9092 \
    --alter \
    --topic meal-events \
    --partitions 10
```

**2. Consumer Group Tuning:**

```yaml
spring:
  kafka:
    consumer:
      max-poll-records: 500
      fetch-min-size: 1
      fetch-max-wait: 500
```

---

## Security Operations

### SSL/TLS Configuration

**1. Obtain Certificates:**

```bash
# Using Let's Encrypt
certbot certonly --standalone -d api.fittrackerpro.com
```

**2. Configure API Gateway:**

```yaml
server:
  port: 8443
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: ${SSL_KEYSTORE_PASSWORD}
    key-store-type: PKCS12
```

### Rotate JWT Secrets

**1. Generate new secret:**

```bash
openssl rand -base64 32
```

**2. Update .env:**

```env
JWT_SECRET=<new-secret>
```

**3. Restart services:**

```bash
docker-compose -f docker-compose.prod.yml restart user-service api-gateway
```

**Note:** This will invalidate all existing tokens.

### Database Security

**1. Restrict Access:**

```sql
-- Revoke public access
REVOKE ALL ON DATABASE fittracker_users FROM PUBLIC;

-- Grant specific permissions
GRANT CONNECT ON DATABASE fittracker_users TO fittracker;
```

**2. Enable SSL:**

Edit postgresql.conf:
```
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

**3. Audit Logging:**

```sql
ALTER SYSTEM SET log_statement = 'mod';  -- Log all modifications
ALTER SYSTEM SET log_duration = on;
```

### Security Audits

**Run weekly security scans:**

```bash
# Dependency check
mvn dependency-check:check

# Container vulnerability scan
docker scan fittracker/user-service:latest

# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8080
```

---

## Incident Response

### Service Down

**1. Identify affected service:**

```bash
docker-compose ps
curl http://localhost:8761  # Check Eureka
```

**2. Check logs:**

```bash
docker-compose logs -f user-service --tail=100
```

**3. Restart service:**

```bash
docker-compose restart user-service
```

**4. If restart fails, rebuild:**

```bash
docker-compose up -d --build user-service
```

### High CPU/Memory

**1. Identify container:**

```bash
docker stats
```

**2. Get thread dump (if JVM):**

```bash
docker exec user-service jstack 1 > thread-dump.txt
```

**3. Get heap dump:**

```bash
docker exec user-service jmap -dump:format=b,file=/tmp/heap.hprof 1
docker cp user-service:/tmp/heap.hprof ./
```

**4. Analyze with tools:**
- Thread dump: jstack, VisualVM
- Heap dump: jhat, Eclipse MAT

### Database Issues

**1. Check connections:**

```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```

**2. Kill idle connections:**

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '1 hour';
```

**3. Check locks:**

```sql
SELECT * FROM pg_locks WHERE NOT granted;
```

### Kafka Issues

**1. Check consumer lag:**

```bash
docker exec fittracker-kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --describe \
    --group analytics-service
```

**2. Reset consumer offset (if needed):**

```bash
docker exec fittracker-kafka kafka-consumer-groups \
    --bootstrap-server localhost:9092 \
    --group analytics-service \
    --reset-offsets \
    --to-earliest \
    --topic meal-events \
    --execute
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backups completed

**Weekly:**
- [ ] Review Grafana dashboards
- [ ] Analyze slow queries
- [ ] Check Kafka consumer lag
- [ ] Review security alerts
- [ ] Vacuum database

**Monthly:**
- [ ] Review and archive logs
- [ ] Update dependencies
- [ ] Review and rotate secrets
- [ ] Capacity planning review
- [ ] Disaster recovery drill

### Log Management

**View logs:**

```bash
# Service logs
docker-compose logs -f --tail=100 user-service

# All services
docker-compose logs -f

# Infrastructure
docker-compose logs postgres redis kafka
```

**Log rotation:**

Configure in docker-compose.prod.yml:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

**Archive old logs:**

```bash
#!/bin/bash
# archive-logs.sh

# Archive logs older than 30 days
find /var/lib/docker/containers -name "*.log" -mtime +30 -exec gzip {} \;

# Move to archive
mv /var/lib/docker/containers/*.log.gz /var/log/fittracker/archive/

# Delete archives older than 90 days
find /var/log/fittracker/archive -name "*.log.gz" -mtime +90 -delete
```

### Updates and Patches

**Update application:**

```bash
# 1. Pull latest code
git pull origin main

# 2. Build
mvn clean package -DskipTests

# 3. Rebuild Docker images
docker-compose -f docker-compose.prod.yml build

# 4. Rolling update (one service at a time)
docker-compose -f docker-compose.prod.yml up -d --no-deps user-service
# Wait and verify
docker-compose -f docker-compose.prod.yml up -d --no-deps nutrition-service
# Repeat for other services
```

**Update infrastructure:**

```bash
# Update PostgreSQL
docker-compose pull postgres
docker-compose up -d postgres

# Update Redis
docker-compose pull redis
docker-compose up -d redis

# Update Kafka (carefully!)
# Read Kafka upgrade guide first
docker-compose pull kafka zookeeper
docker-compose up -d zookeeper
# Wait 1 minute
docker-compose up -d kafka
```

---

For troubleshooting common issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
For architectural details, see [ARCHITECTURE.md](ARCHITECTURE.md).
For API documentation, see [API_REFERENCE.md](API_REFERENCE.md).
