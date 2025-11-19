# Deployment Guide

Production deployment instructions for the Interview Preparation Tracker application.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Prerequisites](#prerequisites)
- [Production Build](#production-build)
- [Deployment Methods](#deployment-methods)
  - [Docker Deployment](#docker-deployment)
  - [Traditional Server Deployment](#traditional-server-deployment)
  - [Cloud Platform Deployment](#cloud-platform-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Migration](#database-migration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup Strategy](#backup-strategy)
- [Security Hardening](#security-hardening)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

## Deployment Options

### Recommended for Personal Use
- **Docker Compose** - Easiest, containerized
- **VPS (DigitalOcean, Linode)** - Full control
- **Heroku** - Simple, managed platform

### Recommended for Production
- **AWS (Elastic Beanstalk or ECS)** - Scalable
- **Google Cloud Run** - Serverless containers
- **Azure App Service** - Managed platform
- **Kubernetes** - For large-scale deployments

## Prerequisites

### For All Deployments
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- SMTP server for notifications (optional)

### For Cloud Deployments
- Cloud provider account
- CLI tools installed (AWS CLI, gcloud, az)
- Payment method configured

### Build Tools
- Java 17+
- Maven 3.9+
- Node.js 18+
- npm

## Production Build

### Backend Build

```bash
cd backend

# Run tests
mvn test

# Create production JAR
mvn clean package -DskipTests

# JAR file created at: target/interview-tracker-backend-1.0.0.jar
```

**Production application.properties:**

```properties
# Create: src/main/resources/application-prod.properties

# Server
server.port=8080

# Database (PostgreSQL recommended for production)
spring.datasource.url=${DATABASE_URL}
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect

# File Storage
app.file-storage.upload-dir=${UPLOAD_DIR:/app/uploads}
app.file-storage.backup-dir=${BACKUP_DIR:/app/backups}

# CORS (set to your frontend domain)
app.cors.allowed-origins=${ALLOWED_ORIGINS:https://yourdomain.com}

# Logging
logging.level.root=INFO
logging.level.com.interviewtracker=INFO
logging.file.name=/var/log/interview-tracker/application.log

# Security (HTTPS only in production)
server.ssl.enabled=true
server.ssl.key-store=${SSL_KEYSTORE_PATH}
server.ssl.key-store-password=${SSL_KEYSTORE_PASSWORD}
```

### Frontend Build

```bash
cd frontend

# Install dependencies
npm install

# Create production build
npm run build

# Output in: dist/ directory (optimized, minified)
```

**Production environment variables:**

Create `.env.production`:
```bash
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=Interview Tracker
VITE_ENABLE_ANALYTICS=true
```

## Deployment Methods

### Docker Deployment

#### Step 1: Create Dockerfiles

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

# Create directories for data persistence
RUN mkdir -p /app/database /app/uploads /app/backups

EXPOSE 8080

ENV SPRING_PROFILES_ACTIVE=prod

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Nginx Configuration** (`frontend/nginx.conf`):
```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Caching for static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Step 2: Create Docker Compose

**`docker-compose.yml`**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: interview-tracker-db
    environment:
      POSTGRES_DB: interview_tracker
      POSTGRES_USER: ${DB_USERNAME:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: interview-tracker-backend
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DATABASE_URL: jdbc:postgresql://postgres:5432/interview_tracker
      DB_USERNAME: ${DB_USERNAME:-postgres}
      DB_PASSWORD: ${DB_PASSWORD:-changeme}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS:-http://localhost}
    volumes:
      - app_uploads:/app/uploads
      - app_backups:/app/backups
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: interview-tracker-frontend
    depends_on:
      - backend
    ports:
      - "80:80"
      - "443:443"
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:
  app_uploads:
  app_backups:

networks:
  app-network:
    driver: bridge
```

#### Step 3: Deploy with Docker Compose

```bash
# Create .env file with secrets
cat > .env <<EOF
DB_USERNAME=postgres
DB_PASSWORD=your_secure_password
ALLOWED_ORIGINS=https://yourdomain.com
EOF

# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Stop and remove all data
docker-compose down -v
```

#### Step 4: Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (certbot sets up cron job automatically)
sudo certbot renew --dry-run
```

### Traditional Server Deployment

#### Ubuntu/Debian Server Setup

**Step 1: Install Prerequisites**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Java 17
sudo apt install openjdk-17-jdk -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Step 2: Setup PostgreSQL**

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE interview_tracker;
CREATE USER tracker_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE interview_tracker TO tracker_user;
\q
```

**Step 3: Deploy Backend**

```bash
# Create application user
sudo useradd -r -s /bin/false tracker

# Create directories
sudo mkdir -p /opt/interview-tracker/backend
sudo mkdir -p /var/log/interview-tracker
sudo mkdir -p /opt/interview-tracker/uploads
sudo chown -R tracker:tracker /opt/interview-tracker
sudo chown -R tracker:tracker /var/log/interview-tracker

# Copy JAR file
sudo cp target/interview-tracker-backend-1.0.0.jar /opt/interview-tracker/backend/app.jar

# Create application.properties
sudo nano /opt/interview-tracker/backend/application-prod.properties
# (paste production configuration)

# Create systemd service
sudo nano /etc/systemd/system/interview-tracker.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Interview Tracker Backend
After=syslog.target network.target postgresql.service

[Service]
User=tracker
ExecStart=/usr/bin/java -jar /opt/interview-tracker/backend/app.jar --spring.config.location=/opt/interview-tracker/backend/application-prod.properties
SuccessExitStatus=143
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=interview-tracker

# Resource limits
LimitNOFILE=65536
MemoryLimit=1G

[Install]
WantedBy=multi-user.target
```

**Start Backend Service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable interview-tracker

# Start service
sudo systemctl start interview-tracker

# Check status
sudo systemctl status interview-tracker

# View logs
sudo journalctl -u interview-tracker -f
```

**Step 4: Deploy Frontend**

```bash
# Build frontend (on local machine)
cd frontend
npm run build

# Copy dist/ to server
scp -r dist/* user@server:/var/www/interview-tracker/

# On server, set permissions
sudo chown -R www-data:www-data /var/www/interview-tracker
```

**Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/interview-tracker
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/interview-tracker;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' 'https://yourdomain.com' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }

    # Static file caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

**Enable Nginx Site:**
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/interview-tracker /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Cloud Platform Deployment

#### AWS Elastic Beanstalk

**Step 1: Prepare Application**

Create `Procfile`:
```
web: java -jar target/interview-tracker-backend-1.0.0.jar
```

Create `.ebextensions/options.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    SPRING_PROFILES_ACTIVE: prod
    SERVER_PORT: 5000
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
```

**Step 2: Deploy**

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init interview-tracker --platform java-17 --region us-east-1

# Create environment
eb create interview-tracker-prod --database.engine postgres

# Deploy
eb deploy

# Open in browser
eb open
```

#### Heroku

**Step 1: Prepare Application**

Create `Procfile`:
```
web: java -Dserver.port=$PORT -jar target/interview-tracker-backend-1.0.0.jar
```

Create `system.properties`:
```
java.runtime.version=17
```

**Step 2: Deploy**

```bash
# Install Heroku CLI
# (download from heroku.com)

# Login
heroku login

# Create app
heroku create interview-tracker-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SPRING_PROFILES_ACTIVE=prod
heroku config:set ALLOWED_ORIGINS=https://interview-tracker-app.herokuapp.com

# Deploy
git push heroku main

# Open app
heroku open

# View logs
heroku logs --tail
```

#### Google Cloud Run

**Step 1: Build and Push Container**

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/interview-tracker

# Or use Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

**cloudbuild.yaml:**
```yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/interview-tracker-backend', './backend']

  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/interview-tracker-frontend', './frontend']

images:
  - 'gcr.io/$PROJECT_ID/interview-tracker-backend'
  - 'gcr.io/$PROJECT_ID/interview-tracker-frontend'
```

**Step 2: Deploy to Cloud Run**

```bash
# Deploy backend
gcloud run deploy interview-tracker-backend \
  --image gcr.io/YOUR_PROJECT_ID/interview-tracker-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SPRING_PROFILES_ACTIVE=prod

# Deploy frontend
gcloud run deploy interview-tracker-frontend \
  --image gcr.io/YOUR_PROJECT_ID/interview-tracker-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Configuration

### Environment Variables

**Backend:**
```bash
# Database
DATABASE_URL=jdbc:postgresql://localhost:5432/interview_tracker
DB_USERNAME=postgres
DB_PASSWORD=secure_password

# File Storage
UPLOAD_DIR=/app/uploads
BACKUP_DIR=/app/backups

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL
SSL_KEYSTORE_PATH=/path/to/keystore.p12
SSL_KEYSTORE_PASSWORD=keystore_password

# Logging
LOG_LEVEL=INFO

# Email (if implementing notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=app-specific-password
```

**Frontend:**
```bash
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=Interview Tracker
VITE_ENABLE_ANALYTICS=true
```

### Configuration Management

**Use Secret Managers:**

**AWS Secrets Manager:**
```java
@Configuration
public class SecretsConfig {
    @Value("${aws.secretsmanager.secret-name}")
    private String secretName;

    @Bean
    public DataSource dataSource() {
        // Retrieve secret from AWS Secrets Manager
    }
}
```

**HashiCorp Vault:**
```properties
spring.cloud.vault.uri=https://vault.example.com
spring.cloud.vault.token=${VAULT_TOKEN}
spring.cloud.vault.kv.backend=secret
```

## Database Migration

### From H2 to PostgreSQL

**Step 1: Export Data**

```bash
# In application, use "Export Data" feature
# Or use H2 console to export SQL
```

**Step 2: Setup PostgreSQL**

```sql
CREATE DATABASE interview_tracker;
CREATE USER tracker_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE interview_tracker TO tracker_user;
```

**Step 3: Update Configuration**

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/interview_tracker
spring.datasource.driver-class-name=org.postgresql.Driver
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
```

**Step 4: Run Application**

```bash
# Tables auto-created by Hibernate
java -jar app.jar
```

**Step 5: Import Data**

```bash
# Use "Import Data" feature
# Or run SQL import scripts
```

### Database Backup

**PostgreSQL Backup:**
```bash
# Manual backup
pg_dump -U tracker_user interview_tracker > backup_$(date +%Y%m%d).sql

# Automated backup (cron)
0 2 * * * pg_dump -U tracker_user interview_tracker > /backups/db_$(date +\%Y\%m\%d).sql
```

**Restore:**
```bash
psql -U tracker_user interview_tracker < backup_20240115.sql
```

## Monitoring & Logging

### Application Monitoring

**Spring Boot Actuator:**

Add to `pom.xml`:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

Configure endpoints:
```properties
management.endpoints.web.exposure.include=health,info,metrics,prometheus
management.endpoint.health.show-details=when-authorized
```

Access metrics:
```bash
curl http://localhost:8080/actuator/health
curl http://localhost:8080/actuator/metrics
```

### Logging

**Logback Configuration** (`logback-spring.xml`):
```xml
<configuration>
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>/var/log/interview-tracker/application.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>/var/log/interview-tracker/application-%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="FILE" />
    </root>
</configuration>
```

### External Monitoring Tools

**Prometheus + Grafana:**
```yaml
# docker-compose.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

**ELK Stack (Elasticsearch, Logstash, Kibana):**
```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
```

## Backup Strategy

### Automated Backups

**Script:** `backup.sh`
```bash
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
pg_dump -U tracker_user interview_tracker | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Files backup
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" /app/uploads

# Application data export (via API)
curl -X GET http://localhost:8080/api/data/export > "$BACKUP_DIR/data_$DATE.json"

# Upload to cloud storage (optional)
aws s3 cp "$BACKUP_DIR/" s3://my-backups/ --recursive

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Cron Job:**
```bash
# Run daily at 2 AM
0 2 * * * /opt/interview-tracker/backup.sh >> /var/log/backup.log 2>&1
```

### Disaster Recovery

1. Keep backups in multiple locations (local + cloud)
2. Test restore procedure monthly
3. Document recovery steps
4. Maintain off-site backup copy
5. Set backup retention policy (e.g., 30 days)

## Security Hardening

### Checklist

- [ ] Enable HTTPS (SSL/TLS)
- [ ] Implement authentication
- [ ] Enable CSRF protection
- [ ] Set secure HTTP headers
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Scan dependencies for vulnerabilities
- [ ] Use secrets management
- [ ] Enable firewall rules
- [ ] Restrict database access
- [ ] Implement audit logging
- [ ] Regular security audits

### Security Headers

**Add to Nginx config:**
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Dependency Scanning

```bash
# Check for vulnerable dependencies
mvn dependency-check:check

# Update dependencies
mvn versions:display-dependency-updates
```

## Performance Tuning

### JVM Options

```bash
java -Xms512m -Xmx1024m \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:ParallelGCThreads=8 \
     -XX:ConcGCThreads=2 \
     -Djava.security.egd=file:/dev/./urandom \
     -jar app.jar
```

### Database Connection Pool

```properties
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.idle-timeout=600000
spring.datasource.hikari.max-lifetime=1800000
```

### Nginx Performance

```nginx
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 10M;
```

## Troubleshooting

### Common Issues

**Issue:** Application won't start
```bash
# Check logs
sudo journalctl -u interview-tracker -n 100

# Check port availability
sudo netstat -tlnp | grep 8080

# Check Java version
java -version
```

**Issue:** Database connection failed
```bash
# Test PostgreSQL connection
psql -U tracker_user -d interview_tracker -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

**Issue:** High memory usage
```bash
# Check Java heap usage
jmap -heap <PID>

# Generate heap dump
jmap -dump:live,format=b,file=heap.bin <PID>

# Analyze with VisualVM or Eclipse MAT
```

**Issue:** Slow API responses
```bash
# Enable SQL logging
logging.level.org.hibernate.SQL=DEBUG

# Check database query performance
EXPLAIN ANALYZE SELECT * FROM topic WHERE ...;

# Add indexes if needed
CREATE INDEX idx_topic_category ON topic(category);
```

---

**Deployment Checklist:**

- [ ] Production build tested locally
- [ ] Environment variables configured
- [ ] Database migrated and tested
- [ ] SSL certificate installed
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Security hardening applied
- [ ] Documentation updated
- [ ] Rollback plan prepared
- [ ] Team notified of deployment

---

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)

For API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

For development guide, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
