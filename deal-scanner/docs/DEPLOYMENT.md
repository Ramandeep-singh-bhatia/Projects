# Deployment Guide - Multi-Retail Deal Scanner

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [Local Deployment](#local-deployment)
3. [Linux Server (Systemd)](#linux-server-systemd)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Platforms](#cloud-platforms)
6. [Raspberry Pi](#raspberry-pi)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Security Hardening](#security-hardening)
9. [Backup & Recovery](#backup--recovery)
10. [Scaling](#scaling)

## Deployment Options

### Comparison Table

| Option | Cost | Complexity | Uptime | Best For |
|--------|------|------------|--------|----------|
| Local (PC/Mac) | Free | Low | When PC is on | Testing |
| Raspberry Pi | $35 one-time | Medium | 99%+ | Home users |
| Linux VPS | $3-5/month | Medium | 99.9% | Power users |
| AWS EC2 Free Tier | Free (12 months) | High | 99.99% | Developers |
| Google Cloud Run | Pay-per-use | Medium | 99.95% | Scalability |
| Docker (Local) | Free | Medium | When host is on | Development |

### Requirements by Deployment Type

**Minimum Requirements:**
- 1 CPU core
- 1GB RAM
- 2GB disk space
- Internet connection

**Recommended:**
- 2 CPU cores
- 2GB RAM
- 5GB disk space
- 10Mbps internet

## Local Deployment

### Quick Start (Development)

**1. Run in Terminal:**
```bash
cd deal-scanner
python main.py
```

**2. Run in Background (macOS/Linux):**
```bash
# Start
nohup python main.py > logs/output.log 2>&1 &

# Save PID
echo $! > scanner.pid

# Check status
ps -p $(cat scanner.pid)

# View logs
tail -f logs/scanner.log

# Stop
kill $(cat scanner.pid)
```

**3. Run in Background (Windows):**

Create `start.bat`:
```batch
@echo off
start /B pythonw main.py
```

Create `stop.bat`:
```batch
@echo off
taskkill /F /IM pythonw.exe
```

### Using Screen (Linux/macOS)

**Install Screen:**
```bash
# Ubuntu/Debian
sudo apt install screen

# macOS
brew install screen
```

**Usage:**
```bash
# Start new session
screen -S deal-scanner

# Run app
python main.py

# Detach: Press Ctrl+A, then D

# List sessions
screen -ls

# Reattach
screen -r deal-scanner

# Kill session
screen -X -S deal-scanner quit
```

### Using Tmux (Linux/macOS)

**Install Tmux:**
```bash
# Ubuntu/Debian
sudo apt install tmux

# macOS
brew install tmux
```

**Usage:**
```bash
# Start new session
tmux new -s deal-scanner

# Run app
python main.py

# Detach: Press Ctrl+B, then D

# List sessions
tmux ls

# Reattach
tmux attach -t deal-scanner

# Kill session
tmux kill-session -t deal-scanner
```

## Linux Server (Systemd)

### Prerequisites

- Linux server (Ubuntu, Debian, CentOS, etc.)
- SSH access
- Python 3.11+ installed
- Chrome/Chromium installed

### Setup Steps

**1. Transfer Files:**
```bash
# From your local machine
scp -r deal-scanner user@server:/home/user/
```

**2. Install Dependencies:**
```bash
ssh user@server

cd /home/user/deal-scanner

# Install Python packages
pip3 install -r requirements.txt

# Install Chrome
sudo apt update
sudo apt install chromium-browser
```

**3. Configure Environment:**
```bash
# Copy and edit .env
cp .env.example .env
nano .env

# Add your API keys
```

**4. Test Run:**
```bash
python3 main.py
# Press Ctrl+C after verifying it works
```

### Create Systemd Service

**1. Create Service File:**
```bash
sudo nano /etc/systemd/system/deal-scanner.service
```

**2. Add Configuration:**
```ini
[Unit]
Description=Multi-Retail Deal Scanner
After=network.target

[Service]
Type=simple
User=yourusername
Group=yourusername
WorkingDirectory=/home/yourusername/deal-scanner
Environment="PATH=/home/yourusername/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /home/yourusername/deal-scanner/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/yourusername/deal-scanner/logs/systemd.log
StandardError=append:/home/yourusername/deal-scanner/logs/systemd-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/yourusername/deal-scanner/logs /home/yourusername/deal-scanner

[Install]
WantedBy=multi-user.target
```

**3. Enable and Start:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable (start on boot)
sudo systemctl enable deal-scanner

# Start now
sudo systemctl start deal-scanner

# Check status
sudo systemctl status deal-scanner
```

### Systemd Management Commands

```bash
# Start service
sudo systemctl start deal-scanner

# Stop service
sudo systemctl stop deal-scanner

# Restart service
sudo systemctl restart deal-scanner

# View status
sudo systemctl status deal-scanner

# View logs
sudo journalctl -u deal-scanner -f

# View last 100 lines
sudo journalctl -u deal-scanner -n 100

# Disable (don't start on boot)
sudo systemctl disable deal-scanner
```

## Docker Deployment

### Create Dockerfile

**1. Create** `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Run as non-root user
RUN useradd -m -u 1000 scanner && \
    chown -R scanner:scanner /app
USER scanner

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=true

# Run the application
CMD ["python", "main.py"]
```

### Create docker-compose.yml

**2. Create** `docker-compose.yml`:
```yaml
version: '3.8'

services:
  deal-scanner:
    build: .
    container_name: deal-scanner
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./deal_scanner.db:/app/deal_scanner.db
      - ./config/products.json:/app/config/products.json
    environment:
      - HEADLESS=true
      - LOG_LEVEL=INFO
    networks:
      - deal-scanner-network

networks:
  deal-scanner-network:
    driver: bridge
```

### Build and Run

```bash
# Build image
docker-compose build

# Start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down

# Restart
docker-compose restart

# View running containers
docker ps

# Execute commands in container
docker-compose exec deal-scanner python -c "from utils.database import db; print(db.get_statistics())"
```

### Docker Management

```bash
# View container logs
docker logs -f deal-scanner

# Enter container shell
docker exec -it deal-scanner /bin/bash

# View resource usage
docker stats deal-scanner

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d

# Remove all containers and volumes
docker-compose down -v
```

### Docker with Cron (Scheduled Runs)

Instead of 24/7, run at specific times:

**Dockerfile for cron:**
```dockerfile
FROM python:3.11-slim

# Install cron and dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Create cron job
RUN echo "0 */2 * * * cd /app && python main.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/deal-scanner
RUN chmod 0644 /etc/cron.d/deal-scanner
RUN crontab /etc/cron.d/deal-scanner

CMD ["cron", "-f"]
```

## Cloud Platforms

### AWS EC2 (Free Tier)

**Free Tier:**
- t2.micro instance (1 vCPU, 1GB RAM)
- 750 hours/month (24/7 for 1 instance)
- 12 months free for new accounts

**Setup:**

1. **Launch Instance:**
   - Go to AWS Console → EC2
   - Click "Launch Instance"
   - Choose Ubuntu Server 22.04 LTS
   - Select t2.micro (free tier)
   - Configure security group (allow SSH)
   - Create/download key pair

2. **Connect:**
   ```bash
   ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com
   ```

3. **Install:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python 3.11
   sudo apt install python3.11 python3.11-pip -y

   # Install Chrome
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo apt install ./google-chrome-stable_current_amd64.deb -y

   # Clone/upload your code
   git clone <your-repo>
   cd deal-scanner

   # Install dependencies
   pip3 install -r requirements.txt

   # Configure
   cp .env.example .env
   nano .env
   ```

4. **Deploy with Systemd:**
   - Follow [Systemd instructions](#create-systemd-service) above

### Google Cloud Platform (Free Tier)

**Free Tier:**
- f1-micro instance (0.6GB RAM)
- 30GB storage
- Always free (no 12-month limit)

**Setup:**

1. **Create VM:**
   - Go to GCP Console → Compute Engine
   - Create instance
   - Machine type: f1-micro
   - Boot disk: Ubuntu 22.04
   - Allow HTTP/HTTPS traffic

2. **Connect (SSH):**
   - Click SSH button in console
   - Or use gcloud CLI:
     ```bash
     gcloud compute ssh instance-name
     ```

3. **Install (same as AWS above)**

### DigitalOcean Droplet

**Cost:** $4-6/month (no free tier)

**Setup:**

1. **Create Droplet:**
   - Choose Ubuntu 22.04
   - Basic plan: $4/month (1GB RAM)
   - Choose datacenter region
   - Add SSH key

2. **Connect:**
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Install (same as above)**

### Oracle Cloud (Always Free)

**Free Tier:**
- 2 AMD VMs (1/8 OCPU, 1GB RAM each)
- OR 1 ARM VM (4 cores, 24GB RAM)
- Always free (no time limit)

**Best free option for this project!**

**Setup:**

1. **Create Account:**
   - Sign up at oracle.com/cloud/free
   - Requires credit card (not charged)

2. **Create Instance:**
   - Compute → Instances → Create Instance
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.E2.1.Micro (always free)
   - Add SSH key

3. **Connect & Install** (same as above)

### Heroku (Container)

**Not recommended** - Heroku's free tier was discontinued. Alternative: Railway.app

### Railway.app

**Free Tier:** $5 credit/month

1. **Create Account:** railway.app
2. **New Project → Deploy from GitHub**
3. **Add environment variables**
4. **Deploy**

## Raspberry Pi

### Best for Home Users

**Hardware:**
- Raspberry Pi 4 (2GB+ RAM): $35-55
- MicroSD card (32GB+): $10
- Power supply: $8
- Case: $5

**Total:** ~$60 for 24/7 operation

### Setup

**1. Install Raspberry Pi OS:**
- Download Raspberry Pi Imager
- Install Raspberry Pi OS Lite (64-bit)
- Enable SSH in imager settings

**2. First Boot:**
```bash
# Find Pi on network
ping raspberrypi.local

# Connect
ssh pi@raspberrypi.local
# Default password: raspberry

# Change password
passwd

# Update system
sudo apt update && sudo apt upgrade -y
```

**3. Install Dependencies:**
```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-pip -y

# Install Chromium
sudo apt install chromium-browser chromium-chromedriver -y

# Install git
sudo apt install git -y
```

**4. Clone and Setup:**
```bash
# Clone repository
git clone <your-repo>
cd deal-scanner

# Install Python packages
pip3 install -r requirements.txt

# Configure
cp .env.example .env
nano .env
```

**5. Test Run:**
```bash
python3 main.py
```

**6. Setup Systemd Service:**
- Follow [Systemd instructions](#create-systemd-service)
- Use `pi` as username

### Pi-Specific Optimizations

**Reduce Memory Usage:**

Edit `config/settings.py`:
```python
SCRAPING_CONFIG = {
    'headless': True,  # Essential on Pi
    # Reduce concurrent operations
}
```

**Reduce Chrome Memory:**

```python
# In scrapers, add these options
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--single-process')
```

**Monitor Resources:**
```bash
# CPU/Memory usage
top

# Temperature
vcgencmd measure_temp
```

## Monitoring & Maintenance

### Health Checks

**Create health check script:** `health_check.sh`

```bash
#!/bin/bash

LOG_FILE="logs/scanner.log"
PID_FILE="scanner.pid"

# Check if process is running
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null; then
        echo "✓ Scanner is running (PID: $PID)"
    else
        echo "✗ Scanner is not running"
        exit 1
    fi
else
    echo "✗ PID file not found"
    exit 1
fi

# Check log for recent activity
RECENT_LOGS=$(tail -n 50 $LOG_FILE | grep -c "$(date +%Y-%m-%d)")
if [ $RECENT_LOGS -gt 0 ]; then
    echo "✓ Recent activity found ($RECENT_LOGS log entries today)"
else
    echo "⚠ No recent activity in logs"
fi

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠ Disk usage high: ${DISK_USAGE}%"
else
    echo "✓ Disk usage OK: ${DISK_USAGE}%"
fi

# Check database size
DB_SIZE=$(du -h deal_scanner.db | awk '{print $1}')
echo "✓ Database size: $DB_SIZE"

echo "Health check completed"
```

**Run periodically:**
```bash
chmod +x health_check.sh

# Manual
./health_check.sh

# Cron (every hour)
crontab -e
# Add: 0 * * * * /path/to/health_check.sh >> /path/to/health.log 2>&1
```

### Log Rotation

**Create logrotate config:** `/etc/logrotate.d/deal-scanner`

```
/home/user/deal-scanner/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 user user
}
```

**Test:**
```bash
sudo logrotate -f /etc/logrotate.d/deal-scanner
```

### Automated Restarts

**Cron job to restart daily:**

```bash
crontab -e

# Add:
0 3 * * * sudo systemctl restart deal-scanner
```

**Or use systemd timer:**

Create `/etc/systemd/system/deal-scanner-restart.timer`:
```ini
[Unit]
Description=Restart Deal Scanner Daily

[Timer]
OnCalendar=daily
OnCalendar=03:00
Persistent=true

[Install]
WantedBy=timers.target
```

Create `/etc/systemd/system/deal-scanner-restart.service`:
```ini
[Unit]
Description=Restart Deal Scanner

[Service]
Type=oneshot
ExecStart=/bin/systemctl restart deal-scanner
```

Enable:
```bash
sudo systemctl enable deal-scanner-restart.timer
sudo systemctl start deal-scanner-restart.timer
```

### Monitoring Tools

**1. Uptimerobot (Free):**
- Monitor HTTP endpoint
- Email alerts if down
- Setup: uptimerobot.com

**2. Healthchecks.io (Free):**
```python
# Add to main.py
import requests

HEALTHCHECK_URL = "https://hc-ping.com/your-uuid"

def ping_healthcheck():
    try:
        requests.get(HEALTHCHECK_URL, timeout=5)
    except:
        pass

# Call periodically
schedule.every(5).minutes.do(ping_healthcheck)
```

**3. Prometheus + Grafana (Advanced):**

Expose metrics endpoint:
```python
from prometheus_client import start_http_server, Counter, Gauge

# Metrics
deals_found = Counter('deals_found_total', 'Total deals found')
products_scanned = Counter('products_scanned_total', 'Products scanned')
current_deals = Gauge('current_deals', 'Current active deals')

# Start metrics server
start_http_server(8000)

# Track metrics
deals_found.inc()
products_scanned.inc()
current_deals.set(len(active_deals))
```

## Security Hardening

### Environment Variables

**Never commit .env:**
```bash
# .gitignore
.env
*.db
logs/
```

**Use environment variable encryption (production):**
```bash
# Install
pip install python-dotenv[encryption]

# Encrypt
python -c "from dotenv import load_dotenv; load_dotenv('.env', override=True, encrypt=True)"
```

### File Permissions

```bash
# Restrict .env
chmod 600 .env

# Restrict database
chmod 600 deal_scanner.db

# Restrict logs
chmod 700 logs/
chmod 600 logs/*.log
```

### Firewall

**Ubuntu/Debian (UFW):**
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status
```

**CentOS/RHEL (firewalld):**
```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### Updates

**Automated security updates (Ubuntu):**
```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

**Manual updates:**
```bash
# System
sudo apt update && sudo apt upgrade -y

# Python packages
pip install -r requirements.txt --upgrade
```

## Backup & Recovery

### Database Backup

**Manual backup:**
```bash
# Backup database
cp deal_scanner.db backups/deal_scanner_$(date +%Y%m%d).db

# Or with SQLite
sqlite3 deal_scanner.db ".backup backups/deal_scanner_$(date +%Y%m%d).db"
```

**Automated backup script:** `backup.sh`

```bash
#!/bin/bash

BACKUP_DIR="/home/user/deal-scanner/backups"
DB_FILE="/home/user/deal-scanner/deal_scanner.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/deal_scanner_$DATE.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
sqlite3 $DB_FILE ".backup $BACKUP_FILE"

# Compress
gzip $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

**Schedule backup (cron):**
```bash
crontab -e

# Daily at 2 AM
0 2 * * * /home/user/deal-scanner/backup.sh >> /home/user/deal-scanner/logs/backup.log 2>&1
```

### Remote Backup (Cloud)

**AWS S3:**
```bash
# Install AWS CLI
pip install awscli

# Configure
aws configure

# Backup script
aws s3 cp backups/ s3://your-bucket/deal-scanner-backups/ --recursive
```

**Rclone (Multiple clouds):**
```bash
# Install
sudo apt install rclone

# Configure
rclone config

# Backup
rclone sync backups/ remote:deal-scanner-backups/
```

### Restore

```bash
# Stop scanner
sudo systemctl stop deal-scanner

# Restore database
gunzip -c backups/deal_scanner_20250117.db.gz > deal_scanner.db

# Restart scanner
sudo systemctl start deal-scanner
```

## Scaling

### Vertical Scaling (More Resources)

**Increase server resources:**
- More RAM → More concurrent scrapers
- More CPU → Faster processing
- More disk → More history storage

### Horizontal Scaling (Multiple Instances)

**Partition watchlist by hash:**

**Instance 1:**
```bash
export INSTANCE_ID=0
export TOTAL_INSTANCES=2
python main.py
```

**Instance 2:**
```bash
export INSTANCE_ID=1
export TOTAL_INSTANCES=2
python main.py
```

**In main.py:**
```python
import os

instance_id = int(os.getenv('INSTANCE_ID', 0))
total_instances = int(os.getenv('TOTAL_INSTANCES', 1))

# Partition watchlist
watchlist_partition = [
    item for i, item in enumerate(watchlist)
    if i % total_instances == instance_id
]
```

### Load Balancing

**Use PostgreSQL instead of SQLite:**

```python
# Install
pip install psycopg2-binary

# Connect
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="dealdb",
    user="postgres",
    password="password"
)
```

**Use Redis for caching:**

```python
import redis
cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Cache product data
cache.setex(f'product:{product_id}', 3600, json.dumps(product))

# Retrieve
cached = cache.get(f'product:{product_id}')
```

### Queue-Based Architecture (Advanced)

Use Celery + Redis:

```python
from celery import Celery

app = Celery('deal-scanner', broker='redis://localhost:6379')

@app.task
def scan_product(watchlist_item):
    # Scan logic
    pass

# Schedule tasks
for item in watchlist:
    scan_product.delay(item)
```

---

## Deployment Checklist

Before going live:

- [ ] Environment variables configured
- [ ] Telegram bot tested
- [ ] Watchlist configured
- [ ] Initial scan completed successfully
- [ ] Logs rotating properly
- [ ] Backups scheduled
- [ ] Monitoring setup
- [ ] Firewall configured
- [ ] SSL/HTTPS if exposing API
- [ ] Documentation reviewed

## Troubleshooting Deployment Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed troubleshooting guide.

Quick checks:
1. Check logs: `tail -f logs/scanner.log`
2. Check service status: `systemctl status deal-scanner`
3. Check disk space: `df -h`
4. Check memory: `free -h`
5. Test notification: Run test script

---

Your Deal Scanner is now deployed and running 24/7! 🚀
