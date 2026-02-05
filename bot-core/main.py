#!/usr/bin/env python3
"""
Enterprise Telegram Group Management Bot
Main Entry Point - bot-core

This is the main entry point for the Telegram bot service.
Initializes all handlers, middlewares, schedulers, and starts the bot.
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from config.database import init_database, close_database
from handlers import (
    message_handler,
    callback_handler,
    join_handler,
    leave_handler,
    member_update_handler
)
from middlewares import (
    auth_middleware,
    rate_limiter,
    logger_middleware,
    i18n_middleware
)
from routers.module_loader import load_modules
from services.scheduler import init_scheduler, shutdown_scheduler
from i18n.loader import load_translations


# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)
logger.add(
    settings.LOG_FILE_PATH,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
)


# Initialize Pyrogram Client
app = Client(
    name="group_manager_bot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    workers=settings.WORKERS,
    workdir=str(Path(__file__).parent / "session")
)


async def startup():
    """
    Startup sequence:
    1. Initialize database connection
    2. Load translations (i18n)
    3. Load modules from bot-modules
    4. Register middlewares
    5. Register handlers
    6. Start scheduler
    7. Log SUDO users and bot info
    """
    logger.info("🚀 Starting Enterprise Telegram Group Management Bot...")
    
    # 1. Initialize database
    logger.info("📊 Connecting to MongoDB...")
    await init_database()
    logger.success("✅ Database connected")
    
    # 2. Load translations
    logger.info("🌐 Loading translations (fa/en)...")
    load_translations()
    logger.success(f"✅ Loaded translations: {settings.SUPPORTED_LANGUAGES}")
    
    # 3. Load modules
    logger.info("📦 Loading feature modules...")
    loaded_modules = load_modules(app)
    logger.success(f"✅ Loaded {len(loaded_modules)} modules: {', '.join(loaded_modules)}")
    
    # 4. Register middlewares (order matters!)
    logger.info("🔧 Registering middlewares...")
    app.add_handler(logger_middleware.LoggerMiddleware(), group=-1)
    app.add_handler(i18n_middleware.I18nMiddleware(), group=-1)
    app.add_handler(auth_middleware.AuthMiddleware(), group=-1)
    app.add_handler(rate_limiter.RateLimiterMiddleware(), group=-1)
    logger.success("✅ Middlewares registered")
    
    # 5. Register core handlers
    logger.info("🎯 Registering event handlers...")
    message_handler.register_handlers(app)
    callback_handler.register_handlers(app)
    join_handler.register_handlers(app)
    leave_handler.register_handlers(app)
    member_update_handler.register_handlers(app)
    logger.success("✅ Event handlers registered")
    
    # 6. Start scheduler (for daily reports, cleanup, etc.)
    logger.info("⏰ Starting job scheduler...")
    await init_scheduler(app)
    logger.success("✅ Scheduler started")
    
    # 7. Log bot information
    me = await app.get_me()
    logger.info(f"🤖 Bot Name: {me.first_name}")
    logger.info(f"🆔 Bot ID: {me.id}")
    logger.info(f"👤 Bot Username: @{me.username}")
    logger.info(f"🔐 SUDO Users: {len(settings.SUDO_USERS)}")
    logger.info(f"🌍 Default Language: {settings.DEFAULT_LANGUAGE}")
    logger.info(f"🛡️  Auth Mode: {'ON' if settings.AUTH_MODE else 'OFF'}")
    
    if settings.DEBUG:
        logger.warning("⚠️  DEBUG mode is enabled!")
    
    logger.success("✅ Bot started successfully and is now running!")
    logger.info("Press Ctrl+C to stop the bot.")


async def shutdown():
    """
    Shutdown sequence:
    1. Stop scheduler
    2. Close database connection
    3. Log shutdown message
    """
    logger.info("🛑 Shutting down bot...")
    
    # 1. Stop scheduler
    await shutdown_scheduler()
    logger.info("⏰ Scheduler stopped")
    
    # 2. Close database
    await close_database()
    logger.info("📊 Database connection closed")
    
    logger.success("✅ Bot shut down gracefully. Goodbye! 👋")


async def main():
    """
    Main entry point:
    - Start the bot
    - Keep it running
    - Handle graceful shutdown
    """
    try:
        # Start bot
        await app.start()
        
        # Run startup tasks
        await startup()
        
        # Keep bot running
        await idle()
        
    except KeyboardInterrupt:
        logger.info("⚠️  Keyboard interrupt received (Ctrl+C)")
    except Exception as e:
        logger.exception(f"❌ Fatal error: {e}")
        raise
    finally:
        # Graceful shutdown
        await shutdown()
        await app.stop()


if __name__ == "__main__":
    """
    Entry point when running the script directly.
    """
    try:
        # Check Python version
        if sys.version_info < (3, 10):
            logger.error("❌ Python 3.10+ is required!")
            sys.exit(1)
        
        # Run the bot
        asyncio.run(main())
        
    except Exception as e:
        logger.exception(f"❌ Failed to start bot: {e}")
        sys.exit(1)
