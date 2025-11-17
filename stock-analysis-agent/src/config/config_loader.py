"""
Configuration loader for Stock Analysis Agent
Loads settings from .env and settings.yaml files
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
ENV_FILE = CONFIG_DIR / ".env"
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"


class APIConfig(BaseModel):
    """API configuration"""
    alpha_vantage_key: Optional[str] = None
    news_api_key: Optional[str] = None
    fmp_api_key: Optional[str] = None
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: Optional[str] = None


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = "sqlite:///data/stock_analysis.db"


class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True


class NotificationConfig(BaseModel):
    """Notification configuration"""
    enable_email: bool = False
    enable_desktop: bool = True
    enable_file_alerts: bool = True
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    alert_email_to: Optional[str] = None


class EnvironmentSettings(BaseSettings):
    """Settings from .env file"""
    alpha_vantage_api_key: Optional[str] = Field(None, alias="ALPHA_VANTAGE_API_KEY")
    news_api_key: Optional[str] = Field(None, alias="NEWS_API_KEY")
    fmp_api_key: Optional[str] = Field(None, alias="FMP_API_KEY")
    reddit_client_id: Optional[str] = Field(None, alias="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(None, alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: Optional[str] = Field(None, alias="REDDIT_USER_AGENT")

    database_url: str = Field("sqlite:///data/stock_analysis.db", alias="DATABASE_URL")

    news_scan_interval: int = Field(30, alias="NEWS_SCAN_INTERVAL")
    portfolio_monitor_interval: int = Field(60, alias="PORTFOLIO_MONITOR_INTERVAL")

    min_signal_confidence: float = Field(60.0, alias="MIN_SIGNAL_CONFIDENCE")
    min_sentiment_strength: float = Field(0.3, alias="MIN_SENTIMENT_STRENGTH")

    dashboard_host: str = Field("0.0.0.0", alias="DASHBOARD_HOST")
    dashboard_port: int = Field(8000, alias="DASHBOARD_PORT")
    debug_mode: bool = Field(True, alias="DEBUG_MODE")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_to_file: bool = Field(True, alias="LOG_TO_FILE")
    log_dir: str = Field("logs", alias="LOG_DIR")

    enable_email_alerts: bool = Field(False, alias="ENABLE_EMAIL_ALERTS")
    smtp_server: Optional[str] = Field(None, alias="SMTP_SERVER")
    smtp_port: Optional[int] = Field(None, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, alias="SMTP_PASSWORD")
    alert_email_to: Optional[str] = Field(None, alias="ALERT_EMAIL_TO")

    enable_desktop_notifications: bool = Field(True, alias="ENABLE_DESKTOP_NOTIFICATIONS")
    enable_file_alerts: bool = Field(True, alias="ENABLE_FILE_ALERTS")
    alert_file_path: str = Field("logs/alerts.json", alias="ALERT_FILE_PATH")

    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = False


class Config:
    """Main configuration class combining all settings"""

    def __init__(self):
        self._env_settings: Optional[EnvironmentSettings] = None
        self._yaml_settings: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load all configuration"""
        # Load environment variables
        if ENV_FILE.exists():
            load_dotenv(ENV_FILE)
            self._env_settings = EnvironmentSettings()
        else:
            print(f"⚠ Warning: .env file not found at {ENV_FILE}")
            print(f"  Creating from .env.example...")
            example_file = CONFIG_DIR / ".env.example"
            if example_file.exists():
                import shutil
                shutil.copy(example_file, ENV_FILE)
                print(f"  ✓ Created {ENV_FILE}")
                print(f"  Please edit it with your API keys")
            self._env_settings = EnvironmentSettings()

        # Load YAML settings
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                self._yaml_settings = yaml.safe_load(f)
        else:
            print(f"⚠ Warning: settings.yaml not found at {SETTINGS_FILE}")
            self._yaml_settings = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key (dot notation supported)"""
        # Try environment settings first
        if hasattr(self._env_settings, key):
            return getattr(self._env_settings, key)

        # Try YAML settings with dot notation
        keys = key.split('.')
        value = self._yaml_settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @property
    def api(self) -> APIConfig:
        """Get API configuration"""
        return APIConfig(
            alpha_vantage_key=self._env_settings.alpha_vantage_api_key,
            news_api_key=self._env_settings.news_api_key,
            fmp_api_key=self._env_settings.fmp_api_key,
            reddit_client_id=self._env_settings.reddit_client_id,
            reddit_client_secret=self._env_settings.reddit_client_secret,
            reddit_user_agent=self._env_settings.reddit_user_agent,
        )

    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration"""
        # Convert relative path to absolute
        db_url = self._env_settings.database_url
        if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"):
            # Relative path - make it absolute
            db_path = db_url.replace("sqlite:///", "")
            absolute_path = PROJECT_ROOT / db_path
            db_url = f"sqlite:///{absolute_path}"

        return DatabaseConfig(url=db_url)

    @property
    def dashboard(self) -> DashboardConfig:
        """Get dashboard configuration"""
        return DashboardConfig(
            host=self._env_settings.dashboard_host,
            port=self._env_settings.dashboard_port,
            debug=self._env_settings.debug_mode,
        )

    @property
    def notifications(self) -> NotificationConfig:
        """Get notification configuration"""
        return NotificationConfig(
            enable_email=self._env_settings.enable_email_alerts,
            enable_desktop=self._env_settings.enable_desktop_notifications,
            enable_file_alerts=self._env_settings.enable_file_alerts,
            smtp_server=self._env_settings.smtp_server,
            smtp_port=self._env_settings.smtp_port,
            smtp_username=self._env_settings.smtp_username,
            smtp_password=self._env_settings.smtp_password,
            alert_email_to=self._env_settings.alert_email_to,
        )

    @property
    def log_level(self) -> str:
        """Get log level"""
        return self._env_settings.log_level

    @property
    def log_dir(self) -> Path:
        """Get log directory path"""
        log_dir = PROJECT_ROOT / self._env_settings.log_dir
        log_dir.mkdir(exist_ok=True)
        return log_dir

    def validate_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return {
            "alpha_vantage": bool(self.api.alpha_vantage_key),
            "newsapi": bool(self.api.news_api_key),
            "fmp": bool(self.api.fmp_api_key),
            "reddit": bool(self.api.reddit_client_id and self.api.reddit_client_secret),
        }

    def print_status(self):
        """Print configuration status"""
        print("\n" + "=" * 60)
        print("Configuration Status")
        print("=" * 60)

        # API Keys
        print("\n🔑 API Keys:")
        api_status = self.validate_api_keys()
        for api_name, configured in api_status.items():
            status = "✓ Configured" if configured else "✗ Not configured (using free alternatives)"
            print(f"  {api_name:20s}: {status}")

        # Database
        print(f"\n💾 Database:")
        print(f"  URL: {self.database.url}")

        # Dashboard
        print(f"\n🌐 Dashboard:")
        print(f"  Host: {self.dashboard.host}")
        print(f"  Port: {self.dashboard.port}")
        print(f"  Debug: {self.dashboard.debug}")

        # Notifications
        print(f"\n🔔 Notifications:")
        print(f"  Email: {'✓ Enabled' if self.notifications.enable_email else '✗ Disabled'}")
        print(f"  Desktop: {'✓ Enabled' if self.notifications.enable_desktop else '✗ Disabled'}")
        print(f"  File Alerts: {'✓ Enabled' if self.notifications.enable_file_alerts else '✗ Disabled'}")

        # Scanning
        print(f"\n⏱ Scanning Intervals:")
        print(f"  News: Every {self._env_settings.news_scan_interval} minutes")
        print(f"  Portfolio: Every {self._env_settings.portfolio_monitor_interval} minutes")

        print("\n" + "=" * 60)


# Singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config() -> Config:
    """Reload configuration from files"""
    global _config_instance
    _config_instance = Config()
    return _config_instance


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    config.print_status()
