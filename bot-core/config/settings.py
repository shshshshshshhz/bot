"""
Configuration Settings
Loads environment variables and provides type-safe configuration access.
"""

import os
from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic for validation and type checking.
    """
    
    # ==================== Telegram Configuration ====================
    API_ID: int = Field(..., description="Telegram API ID from my.telegram.org")
    API_HASH: str = Field(..., description="Telegram API Hash")
    BOT_TOKEN: str = Field(..., description="Bot token from @BotFather")
    BOT_USERNAME: str = Field(..., description="Bot username (without @)")
    BOT_NAME: str = Field(default="Group Manager Bot", description="Bot display name")
    
    # ==================== SUDO Configuration ====================
    SUDO_USERS: List[int] = Field(default_factory=list, description="List of SUDO user IDs")
    SUPPORT_USERNAME: str = Field(..., description="Support username for contact button")
    
    @field_validator('SUDO_USERS', mode='before')
    def parse_sudo_users(cls, v):
        """Parse SUDO_USERS from comma-separated string or list."""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(',') if x.strip()]
        return v
    
    # ==================== Database Configuration ====================
    MONGODB_URI: str = Field(default="mongodb://localhost:27017/", description="MongoDB connection URI")
    DATABASE_NAME: str = Field(default="telegram_group_bot", description="Database name")
    
    # ==================== Language & i18n ====================
    DEFAULT_LANGUAGE: str = Field(default="fa", description="Default language (fa or en)")
    SUPPORTED_LANGUAGES: List[str] = Field(default=["fa", "en"], description="Supported languages")
    
    @field_validator('SUPPORTED_LANGUAGES', mode='before')
    def parse_languages(cls, v):
        """Parse SUPPORTED_LANGUAGES from comma-separated string or list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split(',') if x.strip()]
        return v
    
    # ==================== Security Settings ====================
    AUTH_MODE: bool = Field(default=True, description="Enable strict installation gate")
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_COMMANDS_PER_MINUTE: int = Field(default=20, description="Commands per minute limit")
    RATE_LIMIT_PANELS_PER_MINUTE: int = Field(default=30, description="Panel interactions per minute limit")
    
    @field_validator('AUTH_MODE', mode='before')
    def parse_auth_mode(cls, v):
        """Parse AUTH_MODE from string."""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)
    
    # ==================== API Configuration ====================
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_SECRET_KEY: str = Field(..., description="Secret key for JWT")
    API_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiration in minutes")
    
    # ==================== Logging Configuration ====================
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    LOG_FILE_PATH: str = Field(default="logs/bot.log", description="Log file path")
    LOG_ROTATION: str = Field(default="10 MB", description="Log rotation size")
    LOG_RETENTION: str = Field(default="30 days", description="Log retention period")
    
    # Sentry (optional)
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # ==================== Feature Flags ====================
    ENABLE_WEB_DASHBOARD: bool = Field(default=True, description="Enable web dashboard")
    ENABLE_ADMIN_API: bool = Field(default=True, description="Enable admin API")
    ENABLE_DAILY_REPORTS: bool = Field(default=True, description="Enable daily reports")
    ENABLE_VERIFICATION: bool = Field(default=True, description="Enable verification gate")
    ENABLE_ANTIBETRA: bool = Field(default=True, description="Enable anti-betrayal module")
    
    # ==================== Scheduler Configuration ====================
    DAILY_REPORT_TIME: str = Field(default="00:00", description="Daily report time (HH:MM UTC)")
    CLEANUP_SCHEDULE: str = Field(default="0 2 * * *", description="Cleanup cron schedule")
    
    # ==================== File Storage ====================
    TEMP_DIR: str = Field(default="/tmp/telegram_bot", description="Temporary directory")
    UPLOAD_MAX_SIZE_MB: int = Field(default=50, description="Max upload size in MB")
    
    # ==================== External Services ====================
    REDIS_URL: Optional[str] = Field(default=None, description="Redis URL for caching")
    
    # Webhook (if not using polling)
    WEBHOOK_ENABLED: bool = Field(default=False, description="Enable webhook mode")
    WEBHOOK_URL: Optional[str] = Field(default=None, description="Webhook URL")
    WEBHOOK_PATH: str = Field(default="/webhook", description="Webhook path")
    WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Webhook secret")
    
    # ==================== Development Settings ====================
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENV: str = Field(default="production", description="Environment (development/production)")
    TEST_MODE: bool = Field(default=False, description="Test mode")
    TEST_GROUP_ID: Optional[int] = Field(default=None, description="Test group ID")
    
    # ==================== Dashboard Configuration ====================
    DASHBOARD_URL: str = Field(default="http://localhost:3000", description="Dashboard URL")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="CORS allowed origins"
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split(',') if x.strip()]
        return v
    
    # ==================== Backup Configuration ====================
    BACKUP_ENABLED: bool = Field(default=True, description="Enable backups")
    BACKUP_SCHEDULE: str = Field(default="0 3 * * *", description="Backup cron schedule")
    BACKUP_RETENTION_DAYS: int = Field(default=30, description="Backup retention in days")
    BACKUP_PATH: str = Field(default="/backups", description="Backup directory")
    
    # ==================== Command Settings ====================
    COMMAND_PREFIX: str = Field(default="", description="Command prefix (empty for no prefix, '/' for slash, '!' for exclamation)")
    ALLOW_SLASH_COMMANDS: bool = Field(default=True, description="Allow commands with /")
    ALLOW_NO_PREFIX_COMMANDS: bool = Field(default=True, description="Allow commands without prefix")
    
    # ==================== Pyrogram Settings ====================
    WORKERS: int = Field(default=8, description="Number of worker threads")
    
    # ==================== Paths ====================
    @property
    def BASE_DIR(self) -> Path:
        """Get base directory (bot-core)."""
        return Path(__file__).parent.parent
    
    @property
    def I18N_DIR(self) -> Path:
        """Get i18n directory."""
        return self.BASE_DIR / "i18n"
    
    @property
    def LOGS_DIR(self) -> Path:
        """Get logs directory."""
        path = Path(self.LOG_FILE_PATH).parent
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def SESSION_DIR(self) -> Path:
        """Get session directory."""
        path = self.BASE_DIR / "session"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    # ==================== Validation ====================
    def validate_config(self) -> bool:
        """
        Validate critical configuration.
        Returns True if valid, raises ValueError if invalid.
        """
        # Check Telegram credentials
        if not self.API_ID or not self.API_HASH or not self.BOT_TOKEN:
            raise ValueError("Missing Telegram credentials (API_ID, API_HASH, BOT_TOKEN)")
        
        # Check SUDO users
        if not self.SUDO_USERS:
            raise ValueError("At least one SUDO user must be configured")
        
        # Check database
        if not self.MONGODB_URI:
            raise ValueError("MONGODB_URI is required")
        
        # Check API secret
        if self.ENABLE_ADMIN_API and not self.API_SECRET_KEY:
            raise ValueError("API_SECRET_KEY is required when admin API is enabled")
        
        # Check language
        if self.DEFAULT_LANGUAGE not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"DEFAULT_LANGUAGE must be one of {self.SUPPORTED_LANGUAGES}")
        
        return True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# ==================== Create Settings Instance ====================
settings = Settings()

# Validate on load
try:
    settings.validate_config()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and ensure all required variables are set.")
    exit(1)


# ==================== Export ====================
__all__ = ["settings"]
