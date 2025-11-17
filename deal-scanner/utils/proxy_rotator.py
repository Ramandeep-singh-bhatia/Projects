"""
User agent rotation and request header management.
Helps avoid detection when scraping websites.
"""
import random
from typing import Dict, List
from fake_useragent import UserAgent
from loguru import logger

from config.settings import SCRAPING_CONFIG


class UserAgentRotator:
    """Rotate user agents to avoid detection."""

    def __init__(self, custom_agents: List[str] = None):
        """
        Initialize user agent rotator.

        Args:
            custom_agents: Optional list of custom user agents
        """
        self.custom_agents = custom_agents or SCRAPING_CONFIG['user_agents']
        try:
            self.ua_generator = UserAgent()
        except Exception as e:
            logger.warning(f"Could not initialize UserAgent library: {e}")
            self.ua_generator = None

    def get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        # Prefer custom agents list
        if self.custom_agents:
            return random.choice(self.custom_agents)

        # Fallback to fake-useragent library
        if self.ua_generator:
            try:
                return self.ua_generator.random
            except Exception as e:
                logger.warning(f"Error getting random user agent: {e}")

        # Ultimate fallback
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    def get_chrome_user_agent(self) -> str:
        """Get a Chrome user agent."""
        chrome_agents = [ua for ua in self.custom_agents if 'Chrome' in ua]
        if chrome_agents:
            return random.choice(chrome_agents)

        if self.ua_generator:
            try:
                return self.ua_generator.chrome
            except Exception:
                pass

        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    def get_firefox_user_agent(self) -> str:
        """Get a Firefox user agent."""
        firefox_agents = [ua for ua in self.custom_agents if 'Firefox' in ua]
        if firefox_agents:
            return random.choice(firefox_agents)

        if self.ua_generator:
            try:
                return self.ua_generator.firefox
            except Exception:
                pass

        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'

    def get_headers(self, retailer: str = None, referer: str = None) -> Dict[str, str]:
        """
        Get realistic request headers.

        Args:
            retailer: Optional retailer name to customize headers
            referer: Optional referer URL

        Returns:
            Dictionary of HTTP headers
        """
        user_agent = self.get_random_user_agent()

        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

        if referer:
            headers['Referer'] = referer

        # Customize headers per retailer
        if retailer:
            retailer = retailer.lower()

            if retailer == 'amazon':
                headers.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Sec-Fetch-User': '?1',
                })

            elif retailer == 'bestbuy':
                headers.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                })

            elif retailer == 'walmart':
                headers.update({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                })

        return headers

    def get_selenium_options(self, headless: bool = True) -> List[str]:
        """
        Get Selenium Chrome options for anti-detection.

        Args:
            headless: Whether to run in headless mode

        Returns:
            List of Chrome options
        """
        options = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--window-size=1920,1080',
            f'--user-agent={self.get_random_user_agent()}',
            '--disable-infobars',
            '--disable-notifications',
            '--disable-popup-blocking',
            '--start-maximized',
        ]

        if headless:
            options.extend([
                '--headless=new',
                '--disable-extensions',
            ])

        return options

    def get_playwright_context_options(self) -> Dict:
        """Get Playwright context options for anti-detection."""
        return {
            'user_agent': self.get_random_user_agent(),
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
            'permissions': [],
            'geolocation': {'longitude': -74.0060, 'latitude': 40.7128},  # New York
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }


class ProxyRotator:
    """
    Proxy rotation manager (for future implementation).
    Currently a placeholder as we're using free tools only.
    """

    def __init__(self, proxies: List[str] = None):
        """
        Initialize proxy rotator.

        Args:
            proxies: List of proxy URLs
        """
        self.proxies = proxies or []
        self.current_index = 0

    def get_random_proxy(self) -> Dict[str, str]:
        """Get a random proxy configuration."""
        if not self.proxies:
            return {}

        proxy = random.choice(self.proxies)
        return {
            'http': proxy,
            'https': proxy,
        }

    def get_next_proxy(self) -> Dict[str, str]:
        """Get the next proxy in rotation."""
        if not self.proxies:
            return {}

        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)

        return {
            'http': proxy,
            'https': proxy,
        }

    def add_proxy(self, proxy: str):
        """Add a proxy to the rotation."""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logger.info(f"Added proxy: {proxy}")

    def remove_proxy(self, proxy: str):
        """Remove a proxy from rotation."""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            logger.info(f"Removed proxy: {proxy}")


# Singleton instances
ua_rotator = UserAgentRotator()
proxy_rotator = ProxyRotator()


def get_random_delay(min_delay: float = None, max_delay: float = None) -> float:
    """
    Get a random delay time for scraping.

    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Random delay time
    """
    min_delay = min_delay or SCRAPING_CONFIG['delays']['min']
    max_delay = max_delay or SCRAPING_CONFIG['delays']['max']
    return random.uniform(min_delay, max_delay)
