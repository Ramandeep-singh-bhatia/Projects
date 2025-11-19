"""
Configuration settings for the Deal Scanner system.
All sensitive data should be stored in environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Keys (from environment variables)
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
RAINFOREST_API_KEY = os.getenv('RAINFOREST_API_KEY', '')

# Database Configuration
DATABASE_PATH = BASE_DIR / 'deal_scanner.db'

# Logging Configuration
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'scanner.log'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Rate Limits (requests per hour)
MAX_REQUESTS_PER_HOUR = {
    'amazon': 50,
    'bestbuy': 100,
    'walmart': 80,
    'target': 60,
    'rapidapi': 500,  # Monthly limit / 30 days / 24 hours ≈ 0.7/hour (conservative)
    'serpapi': 100,   # Monthly limit / 30 days / 24 hours ≈ 0.14/hour
    'rainforest': 100, # Monthly limit / 30 days / 24 hours ≈ 0.14/hour
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    ],
    'delays': {
        'min': 5,
        'max': 15,
        'between_products': 3,
    },
    'retry_logic': {
        'max_retries': 3,
        'backoff_factor': 2,
        'initial_wait': 1,
    },
    'timeout': 30,
    'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
}

# Deal Analysis Configuration
DEAL_ANALYSIS_CONFIG = {
    'min_deal_score': 70,  # Minimum score to send notification
    'price_drop_threshold': 0.15,  # 15% minimum price drop to consider
    'weights': {
        'price_vs_historical': 0.40,
        'product_quality': 0.30,
        'timing_seasonality': 0.15,
        'retailer_reputation': 0.15,
    }
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    'enabled': os.getenv('NOTIFICATIONS_ENABLED', 'true').lower() == 'true',
    'min_interval_minutes': 30,  # Don't spam notifications
    'include_image': True,
}

# Scheduler Configuration
SCHEDULER_CONFIG = {
    'high_priority_interval': 30,  # minutes
    'medium_priority_interval': 120,  # minutes (2 hours)
    'low_priority_interval': 1440,  # minutes (24 hours)
    'low_priority_time': '09:00',  # Time for daily low priority scan
}

# RSS Feed URLs
RSS_FEEDS = {
    'slickdeals': 'https://slickdeals.net/newsearch.php?rss=1&searchin=first&forumid%5B%5D=9',
    'reddit_buildapcsales': 'https://www.reddit.com/r/buildapcsales/.rss',
    'bestbuy_deals': 'https://www.bestbuy.com/rss/deals',
}

# API Endpoints
API_ENDPOINTS = {
    'rapidapi': {
        'base_url': 'https://real-time-amazon-data.p.rapidapi.com',
        'headers': {
            'X-RapidAPI-Key': RAPIDAPI_KEY,
            'X-RapidAPI-Host': 'real-time-amazon-data.p.rapidapi.com'
        }
    },
    'serpapi': {
        'base_url': 'https://serpapi.com/search',
    },
    'rainforest': {
        'base_url': 'https://api.rainforestapi.com/request',
    }
}

# Retailer Specific Configuration
RETAILERS = {
    'amazon': {
        'base_url': 'https://www.amazon.com',
        'search_url': 'https://www.amazon.com/s',
        'enabled': True,
    },
    'bestbuy': {
        'base_url': 'https://www.bestbuy.com',
        'top_deals_url': 'https://www.bestbuy.com/site/electronics/top-deals/pcmcat1563299784494.c',
        'deal_of_day_url': 'https://www.bestbuy.com/site/misc/deal-of-the-day/pcmcat248000050016.c',
        'enabled': True,
    },
    'walmart': {
        'base_url': 'https://www.walmart.com',
        'search_url': 'https://www.walmart.com/search',
        'enabled': True,
    },
    'target': {
        'base_url': 'https://www.target.com',
        'search_url': 'https://www.target.com/s',
        'enabled': True,
    }
}

# Product Categories
CATEGORIES = [
    'TV',
    'Baby Stroller',
    'Laptop',
    'Gaming Console',
    'Kitchen Appliance',
    'Smart Home',
    'Camera',
    'Headphones',
]

# OpenAI Configuration
OPENAI_CONFIG = {
    'model': 'gpt-3.5-turbo',  # Using cheaper model to conserve free credits
    'temperature': 0.3,
    'max_tokens': 500,
}
