# FitTracker Pro - Deployment Guide

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployments](#cloud-deployments)
4. [Production Checklist](#production-checklist)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Scaling Strategies](#scaling-strategies)

## Deployment Overview

FitTracker Pro can be deployed in multiple ways:

- **Docker Compose** - Quick setup for small to medium deployments
- **Kubernetes** - Production-grade, scalable deployment
- **AWS** - Elastic Beanstalk, ECS, or EKS
- **Azure** - App Service, AKS
- **Google Cloud** - App Engine, GKE
- **Traditional VPS** - Manual deployment on VM

### Architecture Summary

```
┌────────────┐
│   Client   │
└──────┬─────┘
       │
┌──────▼─────────┐
│ Load Balancer  │
└──────┬─────────┘
       │
   ┌───┴───────────────┐
   │                   │
┌──▼──────┐    ┌──────▼────┐
│Frontend │    │   API     │
│ (Nginx) │    │  Gateway  │
└─────────┘    └─────┬─────┘
                     │
            ┌────────┴────────┐
            │   Microservices │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │   PostgreSQL    │
            └─────────────────┘
```

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Quick Deploy

1. **Clone and Configure**
   ```bash
   git clone <repository-url>
   cd fittracker-pro-fullstack
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

3. **Build and Start**
   ```bash
   docker-compose up -d
   ```

4. **Check Status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8080
   - Eureka: http://localhost:8761

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: fittracker-postgres
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/init-databases.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - fittracker-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: fittracker-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - fittracker-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  eureka:
    build:
      context: ./backend/eureka-server
      dockerfile: Dockerfile
    container_name: fittracker-eureka
    environment:
      SPRING_PROFILES_ACTIVE: prod
    ports:
      - "8761:8761"
    networks:
      - fittracker-network
    restart: unless-stopped

  user-service:
    build:
      context: ./backend/user-service
      dockerfile: Dockerfile
    container_name: fittracker-user-service
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/fittracker_user_db
      SPRING_DATASOURCE_USERNAME: ${DB_USER}
      SPRING_DATASOURCE_PASSWORD: ${DB_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      EUREKA_CLIENT_SERVICEURL_DEFAULTZONE: http://eureka:8761/eureka/
    depends_on:
      postgres:
        condition: service_healthy
      eureka:
        condition: service_started
    networks:
      - fittracker-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  nutrition-service:
    build:
      context: ./backend/nutrition-service
      dockerfile: Dockerfile
    container_name: fittracker-nutrition-service
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/fittracker_nutrition_db
      SPRING_DATASOURCE_USERNAME: ${DB_USER}
      SPRING_DATASOURCE_PASSWORD: ${DB_PASSWORD}
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PASSWORD: ${REDIS_PASSWORD}
      EUREKA_CLIENT_SERVICEURL_DEFAULTZONE: http://eureka:8761/eureka/
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      eureka:
        condition: service_started
    networks:
      - fittracker-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  api-gateway:
    build:
      context: ./backend/api-gateway
      dockerfile: Dockerfile
    container_name: fittracker-gateway
    environment:
      SPRING_PROFILES_ACTIVE: prod
      EUREKA_CLIENT_SERVICEURL_DEFAULTZONE: http://eureka:8761/eureka/
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8080:8080"
    depends_on:
      - eureka
      - user-service
      - nutrition-service
    networks:
      - fittracker-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_BASE_URL: ${API_BASE_URL}
    container_name: fittracker-frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api-gateway
    networks:
      - fittracker-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M

  prometheus:
    image: prom/prometheus:latest
    container_name: fittracker-prometheus
    volumes:
      - ./docker/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    networks:
      - fittracker-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: fittracker-grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana:/etc/grafana/provisioning
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
    networks:
      - fittracker-network
    restart: unless-stopped

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  fittracker-network:
    driver: bridge
```

### Environment Variables (.env)

```bash
# Database
DB_USER=fittracker_admin
DB_PASSWORD=<strong-password-here>

# JWT
JWT_SECRET=<your-super-secret-jwt-key-min-256-bits>

# Redis
REDIS_PASSWORD=<redis-password>

# API
API_BASE_URL=https://api.yourdomain.com

# Monitoring
GRAFANA_PASSWORD=<grafana-admin-password>

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=<smtp-password>
```

### Deploy Production

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale nutrition-service=3
```

## Cloud Deployments

### AWS Deployment

#### Option 1: AWS ECS (Elastic Container Service)

**Prerequisites:**
- AWS Account
- AWS CLI configured
- Docker images pushed to ECR

**Steps:**

1. **Create ECR Repositories**
   ```bash
   aws ecr create-repository --repository-name fittracker/frontend
   aws ecr create-repository --repository-name fittracker/backend
   aws ecr create-repository --repository-name fittracker/eureka
   ```

2. **Push Images to ECR**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Tag and push
   docker tag fittracker-frontend:latest \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com/fittracker/frontend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/fittracker/frontend:latest
   ```

3. **Create RDS Database**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier fittracker-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password <password> \
     --allocated-storage 20
   ```

4. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name fittracker-cluster
   ```

5. **Create Task Definitions**

   Create `task-definition.json`:
   ```json
   {
     "family": "fittracker-backend",
     "containerDefinitions": [
       {
         "name": "user-service",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/fittracker/backend:latest",
         "memory": 512,
         "portMappings": [
           {
             "containerPort": 8081,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "SPRING_DATASOURCE_URL",
             "value": "jdbc:postgresql://fittracker-db.xxx.rds.amazonaws.com:5432/user_db"
           }
         ]
       }
     ]
   }
   ```

6. **Register Task Definition**
   ```bash
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

7. **Create Service**
   ```bash
   aws ecs create-service \
     --cluster fittracker-cluster \
     --service-name user-service \
     --task-definition fittracker-backend \
     --desired-count 2
   ```

#### Option 2: AWS Elastic Beanstalk

**Prerequisites:**
- EB CLI installed

**Steps:**

1. **Initialize Application**
   ```bash
   cd backend
   eb init -p docker fittracker-backend
   ```

2. **Create Environment**
   ```bash
   eb create fittracker-prod
   ```

3. **Configure Environment Variables**
   ```bash
   eb setenv \
     SPRING_DATASOURCE_URL=jdbc:postgresql://xxx.rds.amazonaws.com:5432/db \
     JWT_SECRET=your-secret
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

### Google Cloud Platform (GCP)

#### Using Google Kubernetes Engine (GKE)

**Prerequisites:**
- `gcloud` CLI configured
- `kubectl` installed

**Steps:**

1. **Create GKE Cluster**
   ```bash
   gcloud container clusters create fittracker-cluster \
     --num-nodes=3 \
     --machine-type=n1-standard-2 \
     --region=us-central1
   ```

2. **Build and Push Images**
   ```bash
   # Build and tag
   docker build -t gcr.io/PROJECT_ID/fittracker-frontend:v1 frontend/

   # Push to Container Registry
   docker push gcr.io/PROJECT_ID/fittracker-frontend:v1
   ```

3. **Create Kubernetes Deployment**

   Create `k8s/deployment.yaml`:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: fittracker-frontend
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: fittracker-frontend
     template:
       metadata:
         labels:
           app: fittracker-frontend
       spec:
         containers:
         - name: frontend
           image: gcr.io/PROJECT_ID/fittracker-frontend:v1
           ports:
           - containerPort: 80
           resources:
             limits:
               memory: "256Mi"
               cpu: "500m"
             requests:
               memory: "128Mi"
               cpu: "250m"
   ```

4. **Apply Configuration**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

5. **Expose Service**
   ```bash
   kubectl expose deployment fittracker-frontend \
     --type=LoadBalancer \
     --port=80 \
     --target-port=80
   ```

### Azure Deployment

#### Using Azure App Service

**Steps:**

1. **Create App Service Plan**
   ```bash
   az appservice plan create \
     --name fittracker-plan \
     --resource-group fittracker-rg \
     --sku B1 \
     --is-linux
   ```

2. **Create Web App**
   ```bash
   az webapp create \
     --resource-group fittracker-rg \
     --plan fittracker-plan \
     --name fittracker-app \
     --deployment-container-image-name fittracker/backend:latest
   ```

3. **Configure Settings**
   ```bash
   az webapp config appsettings set \
     --resource-group fittracker-rg \
     --name fittracker-app \
     --settings \
       SPRING_DATASOURCE_URL="jdbc:postgresql://xxx.postgres.database.azure.com:5432/db" \
       JWT_SECRET="your-secret"
   ```

4. **Deploy**
   ```bash
   az webapp deployment source config \
     --name fittracker-app \
     --resource-group fittracker-rg \
     --repo-url https://github.com/your/repo \
     --branch main \
     --manual-integration
   ```

## Production Checklist

### Pre-Deployment

- [ ] **Security**
  - [ ] Change all default passwords
  - [ ] Generate strong JWT secret (min 256 bits)
  - [ ] Enable HTTPS/SSL
  - [ ] Configure CORS properly
  - [ ] Set up rate limiting
  - [ ] Enable firewall rules
  - [ ] Configure database encryption

- [ ] **Environment**
  - [ ] Set `SPRING_PROFILES_ACTIVE=prod`
  - [ ] Configure production database
  - [ ] Set proper logging levels
  - [ ] Configure email settings
  - [ ] Set up monitoring

- [ ] **Database**
  - [ ] Run migrations
  - [ ] Create database backups
  - [ ] Set up replication (if needed)
  - [ ] Configure connection pooling
  - [ ] Create indexes

- [ ] **Frontend**
  - [ ] Build production bundle
  - [ ] Enable minification
  - [ ] Configure CDN (optional)
  - [ ] Set correct API URL
  - [ ] Enable caching headers

- [ ] **Backend**
  - [ ] Optimize JVM settings
  - [ ] Configure health checks
  - [ ] Set up centralized logging
  - [ ] Enable metrics collection
  - [ ] Configure auto-scaling

### Post-Deployment

- [ ] **Verification**
  - [ ] Test user registration
  - [ ] Test login flow
  - [ ] Test all major features
  - [ ] Check health endpoints
  - [ ] Verify SSL certificate
  - [ ] Test error handling

- [ ] **Monitoring**
  - [ ] Set up alerts
  - [ ] Configure dashboards
  - [ ] Monitor error logs
  - [ ] Check performance metrics
  - [ ] Verify backup jobs

- [ ] **Documentation**
  - [ ] Update API documentation
  - [ ] Document deployment process
  - [ ] Create runbook
  - [ ] Update architecture diagrams

## Environment Configuration

### application-prod.yml

```yaml
server:
  port: 8080
  compression:
    enabled: true
  http2:
    enabled: true

spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  jpa:
    hibernate:
      ddl-auto: validate  # Never use 'update' or 'create' in production
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: false
        jdbc:
          batch_size: 20
        order_inserts: true
        order_updates: true

  redis:
    host: ${SPRING_REDIS_HOST}
    port: 6379
    password: ${SPRING_REDIS_PASSWORD}
    timeout: 60000
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0

logging:
  level:
    root: INFO
    com.ram.fittrackerpro: INFO
    org.springframework: WARN
    org.hibernate: WARN
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: /var/log/fittracker/application.log
    max-size: 10MB
    max-history: 30

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
  metrics:
    export:
      prometheus:
        enabled: true

jwt:
  secret: ${JWT_SECRET}
  expiration: 86400000
```

## SSL/TLS Configuration

### Using Let's Encrypt (Free SSL)

1. **Install Certbot**
   ```bash
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Get Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **Auto-Renewal**
   ```bash
   sudo certbot renew --dry-run

   # Add to crontab
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://api-gateway:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring & Logging

### Prometheus Configuration

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'spring-boot-apps'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets:
        - 'user-service:8081'
        - 'nutrition-service:8082'
        - 'workout-service:8083'
        - 'analytics-service:8084'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboards

Import these community dashboards:
- **Spring Boot 2.1 Statistics**: Dashboard ID 10280
- **PostgreSQL Database**: Dashboard ID 9628
- **Nginx**: Dashboard ID 12708

### Log Aggregation (ELK Stack)

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch
    ports:
      - "5000:5000"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    environment:
      ELASTICSEARCH_URL: http://elasticsearch:9200
    depends_on:
      - elasticsearch
    ports:
      - "5601:5601"
```

## Backup & Recovery

### Database Backup Strategy

**Automated Backup Script:**

```bash
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
RETENTION_DAYS=7

# Backup all databases
pg_dump -U postgres fittracker_user_db > $BACKUP_DIR/user_db_$DATE.sql
pg_dump -U postgres fittracker_nutrition_db > $BACKUP_DIR/nutrition_db_$DATE.sql
pg_dump -U postgres fittracker_workout_db > $BACKUP_DIR/workout_db_$DATE.sql
pg_dump -U postgres fittracker_analytics_db > $BACKUP_DIR/analytics_db_$DATE.sql

# Compress backups
gzip $BACKUP_DIR/*_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/ s3://fittracker-backups/$DATE/ --recursive

# Delete old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

**Cron Schedule:**

```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup-db.sh >> /var/log/backup.log 2>&1
```

### Restore Database

```bash
# Restore from backup
gunzip < backup_20241119.sql.gz | psql -U postgres -d fittracker_user_db
```

## Scaling Strategies

### Horizontal Scaling

**Docker Compose:**
```bash
docker-compose up -d --scale nutrition-service=3
```

**Kubernetes:**
```bash
kubectl scale deployment nutrition-service --replicas=5
```

### Load Balancing

**Nginx Load Balancer:**

```nginx
upstream backend {
    least_conn;
    server api-gateway-1:8080;
    server api-gateway-2:8080;
    server api-gateway-3:8080;
}

server {
    listen 80;
    location /api {
        proxy_pass http://backend;
        proxy_next_upstream error timeout invalid_header http_500;
    }
}
```

### Auto-Scaling (AWS)

```json
{
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 60
  }
}
```

---

**Last Updated:** November 2024
**Version:** 1.0.0
