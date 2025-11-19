# Troubleshooting Guide

## Table of Contents
1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Installation Problems](#installation-problems)
4. [Runtime Errors](#runtime-errors)
5. [Notification Issues](#notification-issues)
6. [Scraping Problems](#scraping-problems)
7. [Database Issues](#database-issues)
8. [Performance Problems](#performance-problems)
9. [API Issues](#api-issues)
10. [Getting Help](#getting-help)

## Quick Diagnostics

### Step 1: Check System Status

```bash
# Is the scanner running?
ps aux | grep main.py

# Or if using systemd:
sudo systemctl status deal-scanner

# Check recent logs
tail -n 100 logs/scanner.log
```

### Step 2: Verify Configuration

```bash
# Check environment file exists
ls -la .env

# Verify it's not empty
cat .env | grep -v '^#' | grep -v '^$'

# Check database exists
ls -lh deal_scanner.db
```

### Step 3: Test Components

```python
# Test database
python -c "from utils.database import db; print(db.get_statistics())"

# Test Telegram
python -c "from utils.notifier import notifier; import asyncio; asyncio.run(notifier.send_message('Test'))"

# Test scraper
python -c "from scrapers.amazon_scraper import AmazonScraper; s=AmazonScraper(); print('OK')"
```

## Common Issues

### Issue: No Notifications Received

**Symptoms:**
- Scanner running but no Telegram messages
- Logs show deals found

**Diagnosis:**
```bash
# Check Telegram settings
grep TELEGRAM .env

# Test notification
python << EOF
from utils.notifier import notifier
import asyncio

async def test():
    result = await notifier.send_message("Test notification")
    print(f"Result: {result}")

asyncio.run(test())
EOF
```

**Solutions:**

1. **Verify bot token:**
   ```bash
   # Token should be like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   # Check it starts with numbers, has colon, then letters
   echo $TELEGRAM_BOT_TOKEN
   ```

2. **Verify chat ID:**
   ```bash
   # Should be a number (positive or negative)
   echo $TELEGRAM_CHAT_ID
   ```

3. **Start bot conversation:**
   - Open Telegram
   - Search for your bot (username you created)
   - Send `/start`

4. **Check bot permissions:**
   - Bot can't message you until you start conversation
   - Check bot isn't blocked

5. **Test with curl:**
   ```bash
   BOT_TOKEN="your_token"
   CHAT_ID="your_chat_id"

   curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=Test message"
   ```

### Issue: Scanner Crashes on Start

**Symptoms:**
- Process exits immediately
- Error in logs

**Common Causes:**

1. **Missing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Wrong Python version:**
   ```bash
   python --version  # Should be 3.11+
   python3.11 main.py  # Use specific version
   ```

3. **Database locked:**
   ```bash
   # Check if another instance is running
   ps aux | grep main.py

   # Remove lock if stuck
   rm -f deal_scanner.db-journal
   ```

4. **Permission issues:**
   ```bash
   # Check permissions
   ls -la deal_scanner.db logs/

   # Fix if needed
   chmod 644 deal_scanner.db
   chmod 755 logs/
   ```

5. **Chromium not found:**
   ```bash
   # Install Chrome/Chromium
   # Ubuntu:
   sudo apt install chromium-browser

   # Mac:
   brew install chromium

   # Verify:
   which chromium-browser
   which google-chrome
   ```

### Issue: High CPU/Memory Usage

**Symptoms:**
- System slow
- Scanner consuming lots of resources

**Diagnosis:**
```bash
# Check resource usage
top -p $(pgrep -f main.py)

# Or
htop | grep python
```

**Solutions:**

1. **Too many browsers open:**
   ```bash
   # Check Chrome processes
   ps aux | grep chrome | wc -l

   # Kill orphaned browsers
   pkill -f chromium
   pkill -f chrome
   ```

2. **Reduce scan frequency:**
   Edit `config/products.json` - change high priority to medium

3. **Enable headless mode:**
   ```bash
   # In .env
   HEADLESS=true
   ```

4. **Limit concurrent operations:**
   Edit `config/settings.py`:
   ```python
   # Reduce max results
   max_results = 5  # Instead of 20
   ```

5. **Add memory limits (systemd):**
   ```ini
   [Service]
   MemoryLimit=500M
   ```

### Issue: "Rate Limit Exceeded" Errors

**Symptoms:**
- Logs show: "Rate limit exceeded for rapidapi"
- API calls failing

**Solutions:**

1. **Check API usage:**
   ```python
   from utils.database import db
   print(db.get_api_usage_count('rapidapi', hours=24))
   print("Limit:", 500/30/24, "per hour")  # Monthly limit
   ```

2. **Wait for reset:**
   - RapidAPI: Monthly reset
   - Other APIs: Check their docs

3. **System falls back to scraping:**
   - This is automatic
   - Check logs for "falling back to scraping"

4. **Reduce API usage:**
   - Use high priority sparingly
   - Rely more on web scraping
   - Disable optional API integrations

### Issue: Scraper Returns Empty Results

**Symptoms:**
- Logs show: "Found 0 products"
- Search should return results

**Diagnosis:**

1. **Test URL manually:**
   - Copy search URL from logs
   - Open in browser
   - Check if products visible

2. **Check for CAPTCHA:**
   ```bash
   # Run without headless to see browser
   export HEADLESS=false
   python main.py
   ```

3. **Verify selectors still work:**
   Website may have changed HTML structure

**Solutions:**

1. **Website changed structure:**
   - Update selectors in scraper
   - Check developer guide

2. **CAPTCHA/anti-bot:**
   - Increase delays
   - Change user agents
   - Use VPN

3. **Timeout issues:**
   ```python
   # Increase timeout in config/settings.py
   SCRAPING_CONFIG = {
       'timeout': 60,  # Increase from 30
   }
   ```

4. **JavaScript not loading:**
   ```python
   # Add more wait time in scraper
   WebDriverWait(driver, 30).until(...)  # Increase from 15
   time.sleep(5)  # Add explicit wait
   ```

### Issue: Notifications Too Frequent

**Symptoms:**
- Too many Telegram messages
- Overwhelmed with notifications

**Solutions:**

1. **Increase minimum interval:**
   Edit `config/settings.py`:
   ```python
   NOTIFICATION_CONFIG = {
       'min_interval_minutes': 60,  # Increase from 30
   }
   ```

2. **Increase deal score threshold:**
   ```python
   DEAL_ANALYSIS_CONFIG = {
       'min_deal_score': 80,  # Increase from 70
   }
   ```

3. **Reduce watchlist items:**
   - Remove low-value items
   - Be more specific with keywords

4. **Change priorities:**
   - Move items from high to medium/low
   - Reduce scan frequency

## Installation Problems

### Python Not Found

**Error:** `python: command not found`

**Solutions:**
```bash
# Linux: Install Python 3.11
sudo apt update
sudo apt install python3.11

# Mac: Use Homebrew
brew install python@3.11

# Verify
python3.11 --version
```

### pip Not Found

**Error:** `pip: command not found`

**Solutions:**
```bash
# Linux
sudo apt install python3-pip

# Mac
python3.11 -m ensurepip

# Use python -m pip instead
python3.11 -m pip install -r requirements.txt
```

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'selenium'`

**Solutions:**
```bash
# Install dependencies
pip install -r requirements.txt

# If using virtual environment, activate it first
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install in virtual environment
pip install -r requirements.txt
```

### Chrome/Chromium Issues

**Error:** `selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH`

**Solutions:**
```bash
# Linux
sudo apt install chromium-browser chromium-chromedriver

# Mac
brew install chromedriver

# Or use webdriver-manager (automatic)
pip install webdriver-manager
# (Already in requirements.txt)
```

### Permission Errors

**Error:** `PermissionError: [Errno 13] Permission denied`

**Solutions:**
```bash
# Install without sudo (user install)
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Runtime Errors

### Database Locked Error

**Error:** `sqlite3.OperationalError: database is locked`

**Causes:**
- Multiple instances running
- Unfinished transaction
- System crash during write

**Solutions:**
```bash
# 1. Check for multiple instances
ps aux | grep main.py
kill <process_id>

# 2. Remove lock file
rm deal_scanner.db-journal

# 3. Backup and recreate
cp deal_scanner.db deal_scanner.db.backup
sqlite3 deal_scanner.db "VACUUM;"

# 4. If corrupted, rebuild
# (You'll lose data)
rm deal_scanner.db
python main.py  # Will recreate
```

### Selenium Timeout Error

**Error:** `TimeoutException: Message:`

**Solutions:**

1. **Increase timeout:**
   ```python
   # In scraper
   WebDriverWait(driver, 30).until(...)  # Increase from 15
   ```

2. **Check internet connection:**
   ```bash
   ping google.com
   ```

3. **Slow website:**
   - Add explicit waits
   - Check website status

4. **Wrong selector:**
   - Website HTML changed
   - Update selector in scraper

### OpenAI API Error

**Error:** `openai.error.AuthenticationError`

**Solutions:**

1. **Check API key:**
   ```bash
   echo $OPENAI_API_KEY
   # Should start with sk-
   ```

2. **Verify account has credits:**
   - Visit https://platform.openai.com/account/billing

3. **Disable AI analysis (fallback):**
   ```bash
   # Remove OpenAI key from .env
   # System will use rule-based analysis
   ```

### JSON Decode Error

**Error:** `json.decoder.JSONDecodeError: Expecting value`

**Causes:**
- Malformed products.json
- Invalid JSON from API

**Solutions:**

1. **Validate products.json:**
   ```bash
   python -m json.tool config/products.json
   ```

2. **Fix JSON errors:**
   - Missing commas
   - Extra commas
   - Unquoted strings
   - Use JSON validator online

3. **Reset to example:**
   ```bash
   cp config/products.json.backup config/products.json
   ```

## Notification Issues

### Telegram Flood Control

**Error:** `telegram.error.RetryAfter: Flood control exceeded`

**Cause:** Sending too many messages too quickly

**Solutions:**

1. **Wait specified time:**
   Error message tells you how long to wait

2. **Reduce notification frequency:**
   Increase `min_interval_minutes` in settings

3. **Batch notifications:**
   Combine multiple deals into one message

### Bot Can't Send Messages

**Error:** `telegram.error.Unauthorized: Forbidden: bot was blocked by the user`

**Solutions:**

1. **Unblock bot in Telegram:**
   - Find bot in Telegram
   - Unblock if blocked
   - Send `/start`

2. **Verify chat ID:**
   ```bash
   # Get your chat ID
   # Message @userinfobot in Telegram
   ```

### Message Too Long

**Error:** `telegram.error.BadRequest: Message is too long`

**Solution:**

Edit `utils/notifier.py` to truncate long messages:
```python
def format_deal_alert(self, product_data):
    message = f"..."
    # Truncate title
    title = product_data['title'][:100]
    message += f"<b>{title}</b>\n"
    # ...
    return message[:4096]  # Telegram limit
```

## Scraping Problems

### CAPTCHA Detected

**Symptoms:**
- Scraper hangs
- Empty results
- CAPTCHA visible in browser (when HEADLESS=false)

**Solutions:**

1. **Increase delays:**
   ```python
   SCRAPING_CONFIG = {
       'delays': {
           'min': 10,  # Increase from 5
           'max': 20,  # Increase from 15
       }
   }
   ```

2. **Change user agent:**
   - Rotate more frequently
   - Use less common user agents

3. **Use VPN:**
   - Change IP address
   - Avoid detection

4. **Reduce frequency:**
   - Lower priority items
   - Spread out scans

5. **Use API instead:**
   - APIs don't get CAPTCHAs
   - Set up RapidAPI account

### Stale Element Error

**Error:** `selenium.common.exceptions.StaleElementReferenceException`

**Cause:** Page changed after element was found

**Solution:**
```python
from selenium.common.exceptions import StaleElementReferenceException

max_retries = 3
for i in range(max_retries):
    try:
        element = driver.find_element(...)
        text = element.text
        break
    except StaleElementReferenceException:
        if i == max_retries - 1:
            raise
        time.sleep(1)
```

### JavaScript Not Executing

**Symptoms:**
- Elements not found
- Page looks different than expected

**Solutions:**

1. **Wait for JavaScript:**
   ```python
   # Wait for specific element
   WebDriverWait(driver, 15).until(
       EC.presence_of_element_located((By.ID, "element-id"))
   )

   # Or wait for page load
   driver.implicitly_wait(10)
   ```

2. **Execute JavaScript directly:**
   ```python
   driver.execute_script("return document.readyState") == "complete"
   ```

3. **Scroll to trigger lazy loading:**
   ```python
   driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
   time.sleep(2)
   ```

## Database Issues

### Database Corrupted

**Error:** `sqlite3.DatabaseError: database disk image is malformed`

**Solutions:**

1. **Try to recover:**
   ```bash
   # Dump to SQL
   sqlite3 deal_scanner.db ".dump" > dump.sql

   # Create new database
   mv deal_scanner.db deal_scanner.db.corrupted
   sqlite3 deal_scanner.db < dump.sql
   ```

2. **Restore from backup:**
   ```bash
   cp backups/deal_scanner_latest.db deal_scanner.db
   ```

3. **Start fresh:**
   ```bash
   # Backup old database
   mv deal_scanner.db deal_scanner.db.old

   # Run scanner (will create new DB)
   python main.py
   ```

### Disk Full

**Error:** `sqlite3.OperationalError: disk I/O error`

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h
   ```

2. **Clean old logs:**
   ```bash
   find logs/ -name "*.log" -mtime +7 -delete
   ```

3. **Clean price history:**
   ```python
   from utils.database import db

   with db.get_connection() as conn:
       conn.execute("""
           DELETE FROM price_history
           WHERE timestamp < datetime('now', '-90 days')
       """)
   ```

4. **Vacuum database:**
   ```bash
   sqlite3 deal_scanner.db "VACUUM;"
   ```

## Performance Problems

### Slow Scraping

**Symptoms:**
- Each product takes minutes
- Scanner times out

**Solutions:**

1. **Reduce max_results:**
   ```python
   # In agent
   products = scraper.search_products(keywords, max_results=5)
   ```

2. **Parallel processing:**
   ```python
   from concurrent.futures import ThreadPoolExecutor

   with ThreadPoolExecutor(max_workers=3) as executor:
       futures = [executor.submit(process_product, p) for p in products]
       results = [f.result() for f in futures]
   ```

3. **Cache results:**
   ```python
   import functools

   @functools.lru_cache(maxsize=100)
   def get_product_data(product_id):
       # Expensive operation
       pass
   ```

### Memory Leak

**Symptoms:**
- Memory usage grows over time
- Eventually crashes

**Solutions:**

1. **Close browsers:**
   ```python
   # In scraper
   def __del__(self):
       self.close()

   def close(self):
       if self.driver:
           self.driver.quit()
   ```

2. **Restart periodically:**
   ```bash
   # Cron job to restart daily
   0 3 * * * systemctl restart deal-scanner
   ```

3. **Clear caches:**
   ```python
   import gc

   # After processing batch
   gc.collect()
   ```

### Database Growing Too Large

**Symptoms:**
- deal_scanner.db is multiple GB
- Queries slow

**Solutions:**

1. **Clean old data:**
   ```python
   # Keep only last 90 days of price history
   DELETE FROM price_history
   WHERE timestamp < datetime('now', '-90 days')
   ```

2. **Archive old data:**
   ```bash
   # Export to CSV
   sqlite3 -header -csv deal_scanner.db \
       "SELECT * FROM price_history WHERE timestamp < datetime('now', '-90 days')" \
       > archive.csv

   # Delete from database
   sqlite3 deal_scanner.db \
       "DELETE FROM price_history WHERE timestamp < datetime('now', '-90 days')"
   ```

3. **Vacuum database:**
   ```bash
   sqlite3 deal_scanner.db "VACUUM;"
   ```

## API Issues

### API Key Invalid

**Error:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**

1. **Verify API key:**
   ```bash
   # Check format
   echo $RAPIDAPI_KEY
   # Should be long alphanumeric string
   ```

2. **Regenerate key:**
   - Visit API provider dashboard
   - Generate new key
   - Update .env

3. **Check subscription:**
   - Free tier may have expired
   - Need to resubscribe

### API Quota Exceeded

**Error:** `429 Too Many Requests`

**Solutions:**

1. **Wait for reset:**
   - Check API dashboard for reset time
   - Usually monthly or daily

2. **Upgrade plan:**
   - Consider paid tier if needed

3. **Use fallback:**
   - System automatically uses web scraping

4. **Optimize usage:**
   - Reduce high-priority items
   - Use APIs only for important searches

### API Response Changed

**Error:** `KeyError` when parsing API response

**Solutions:**

1. **Check API documentation:**
   - API may have updated
   - Response format changed

2. **Add error handling:**
   ```python
   title = data.get('title') or data.get('name') or 'Unknown'
   ```

3. **Log raw response:**
   ```python
   logger.debug(f"API response: {response.json()}")
   ```

4. **Update parser:**
   - Adjust code to new format
   - See developer guide

## Getting Help

### Before Asking for Help

Gather this information:

1. **System info:**
   ```bash
   python --version
   pip list | grep -E "selenium|beautifulsoup|requests"
   uname -a  # Linux
   sw_vers   # Mac
   ```

2. **Error logs:**
   ```bash
   tail -n 100 logs/scanner.log > error_log.txt
   ```

3. **Configuration (sanitized):**
   ```bash
   # Remove sensitive data
   cat .env | grep -v TOKEN | grep -v KEY
   ```

4. **Steps to reproduce**

### Where to Get Help

1. **GitHub Issues:**
   - Check existing issues
   - Create new issue with details above

2. **Logs Analysis:**
   - Read logs carefully
   - Error messages are usually clear

3. **Documentation:**
   - Re-read relevant sections
   - Check example code

4. **Community:**
   - Stack Overflow (tag: web-scraping)
   - Reddit r/webscraping

### Debug Mode

Enable maximum logging:

```bash
# .env
LOG_LEVEL=DEBUG
HEADLESS=false

# Run
python main.py 2>&1 | tee debug.log
```

### Create Minimal Reproduction

If asking for help, create minimal example:

```python
# minimal_example.py
from scrapers.amazon_scraper import AmazonScraper

scraper = AmazonScraper()
try:
    products = scraper.search_products_api("laptop", max_results=1)
    print(f"Success: {len(products)} products")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    scraper.close()
```

---

## Quick Reference: Common Commands

```bash
# Check status
systemctl status deal-scanner

# View logs
tail -f logs/scanner.log

# Restart
systemctl restart deal-scanner

# Test notification
python -c "from utils.notifier import notifier; import asyncio; asyncio.run(notifier.send_message('Test'))"

# Check database
sqlite3 deal_scanner.db "SELECT COUNT(*) FROM products;"

# Clear old data
sqlite3 deal_scanner.db "DELETE FROM price_history WHERE timestamp < datetime('now', '-90 days');"

# Backup database
cp deal_scanner.db backups/deal_scanner_$(date +%Y%m%d).db
```

---

Most issues can be resolved by:
1. Reading error messages carefully
2. Checking logs
3. Verifying configuration
4. Restarting the service

If stuck, don't hesitate to open a GitHub issue! 🆘
