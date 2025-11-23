# FitTracker Pro - Production Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Java 17+ for local development
- Maven 3.8+ for building
- At least 8GB RAM for running all services

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database
POSTGRES_USER=fittracker
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<strong-password>

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Eureka
EUREKA_SERVER_URL=http://eureka-server:8761/eureka/

# JWT
JWT_SECRET=<your-256-bit-secret>
JWT_EXPIRATION=86400000

# Service Ports
EUREKA_PORT=8761
CONFIG_SERVER_PORT=8888
API_GATEWAY_PORT=8080
USER_SERVICE_PORT=8081
NUTRITION_SERVICE_PORT=8082
WORKOUT_SERVICE_PORT=8083
ANALYTICS_SERVICE_PORT=8084

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
JAEGER_PORT=16686
```

## Building for Production

### Build all services:

```bash
mvn clean package -DskipTests
```

### Build Docker images:

```bash
# Build Eureka Server
docker build -t fittracker/eureka-server:latest ./eureka-server

# Build Config Server
docker build -t fittracker/config-server:latest ./config-server

# Build API Gateway
docker build -t fittracker/api-gateway:latest ./api-gateway

# Build User Service
docker build -t fittracker/user-service:latest ./user-service

# Build Nutrition Service
docker build -t fittracker/nutrition-service:latest ./nutrition-service

# Build Workout Service
docker build -t fittracker/workout-service:latest ./workout-service

# Build Analytics Service
docker build -t fittracker/analytics-service:latest ./analytics-service
```

## Starting Services

### Development Mode:

```bash
docker-compose up -d
```

### Production Mode:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Service URLs

Once all services are running:

- **Eureka Dashboard**: http://localhost:8761
- **API Gateway**: http://localhost:8080
- **Swagger UI**:
  - User Service: http://localhost:8081/swagger-ui.html
  - Nutrition Service: http://localhost:8082/swagger-ui.html
  - Workout Service: http://localhost:8083/swagger-ui.html
  - Analytics Service: http://localhost:8084/swagger-ui.html
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Jaeger**: http://localhost:16686

## Monitoring and Health Checks

### Health Endpoints:

- User Service: http://localhost:8081/actuator/health
- Nutrition Service: http://localhost:8082/actuator/health
- Workout Service: http://localhost:8083/actuator/health
- Analytics Service: http://localhost:8084/actuator/health

### Metrics:

- Prometheus metrics: http://localhost:{port}/actuator/prometheus

## Database Migrations

Flyway migrations run automatically on service startup.

To manually run migrations:

```bash
# User Service
mvn flyway:migrate -pl user-service

# Nutrition Service
mvn flyway:migrate -pl nutrition-service

# Workout Service
mvn flyway:migrate -pl workout-service

# Analytics Service
mvn flyway:migrate -pl analytics-service
```

## Scaling Services

Scale individual services:

```bash
docker-compose up -d --scale user-service=3
docker-compose up -d --scale nutrition-service=2
docker-compose up -d --scale workout-service=2
docker-compose up -d --scale analytics-service=2
```

## Troubleshooting

### Check service logs:

```bash
docker-compose logs -f <service-name>
```

### Restart a service:

```bash
docker-compose restart <service-name>
```

### Database connection issues:

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Connect to PostgreSQL
docker exec -it fittracker-postgres psql -U fittracker -d fittracker_users
```

### Cache issues:

Clear Redis cache:

```bash
docker exec -it fittracker-redis redis-cli FLUSHALL
```

## Production Checklist

- [ ] Change default passwords in .env
- [ ] Generate strong JWT secret (256-bit)
- [ ] Configure SSL/TLS certificates
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Set up monitoring alerts
- [ ] Review security settings
- [ ] Configure firewall rules
- [ ] Set up CI/CD pipeline
- [ ] Load test the system
- [ ] Create disaster recovery plan

## Security Recommendations

1. **JWT Secret**: Use a strong, randomly generated 256-bit secret
2. **Database**: Use strong passwords, enable SSL connections
3. **Redis**: Enable password authentication, disable dangerous commands
4. **API Gateway**: Configure rate limiting, enable CORS properly
5. **Eureka**: Secure with authentication in production
6. **Monitoring**: Restrict access to Grafana and Prometheus

## Performance Tuning

### JVM Options:

Add to service startup:

```
JAVA_OPTS=-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200
```

### Database Connection Pool:

In application.yml:

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000
```

### Redis Configuration:

```yaml
spring:
  redis:
    lettuce:
      pool:
        max-active: 10
        max-idle: 5
        min-idle: 2
```

## Backup and Recovery

### Database Backup:

```bash
# Backup
docker exec fittracker-postgres pg_dump -U fittracker fittracker_users > backup_users.sql
docker exec fittracker-postgres pg_dump -U fittracker fittracker_nutrition > backup_nutrition.sql
docker exec fittracker-postgres pg_dump -U fittracker fittracker_workouts > backup_workouts.sql
docker exec fittracker-postgres pg_dump -U fittracker fittracker_analytics > backup_analytics.sql

# Restore
docker exec -i fittracker-postgres psql -U fittracker fittracker_users < backup_users.sql
```

### Redis Backup:

```bash
# Backup
docker exec fittracker-redis redis-cli SAVE
docker cp fittracker-redis:/data/dump.rdb ./redis-backup.rdb

# Restore
docker cp ./redis-backup.rdb fittracker-redis:/data/dump.rdb
docker-compose restart redis
```

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review Eureka dashboard for service health
- Check Grafana for metrics and alerts
- Open an issue on GitHub
