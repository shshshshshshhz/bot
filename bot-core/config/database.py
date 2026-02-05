"""
Database Configuration and Connection Management
MongoDB connection using Motor (async) with connection pooling.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from loguru import logger
from typing import Optional

from config.settings import settings


# ==================== Global Database Instance ====================
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance.
    Must call init_database() first.
    """
    if _database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _database


async def init_database() -> AsyncIOMotorDatabase:
    """
    Initialize MongoDB connection.
    Creates indexes for optimal query performance.
    """
    global _client, _database
    
    try:
        # Create client with connection pooling
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Get database
        _database = _client[settings.DATABASE_NAME]
        
        # Test connection
        await _client.admin.command('ping')
        logger.info(f"📊 Connected to MongoDB: {settings.DATABASE_NAME}")
        
        # Create indexes for performance
        await _create_indexes()
        
        return _database
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.exception(f"❌ Database initialization error: {e}")
        raise


async def close_database():
    """
    Close database connection gracefully.
    """
    global _client, _database
    
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("📊 MongoDB connection closed")


async def _create_indexes():
    """
    Create database indexes for optimal query performance.
    This is called during initialization.
    """
    db = get_database()
    
    logger.info("📇 Creating database indexes...")
    
    # ==================== users collection ====================
    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("username")
    await db.users.create_index("is_sudo")
    
    # ==================== groups collection ====================
    await db.groups.create_index("group_id", unique=True)
    await db.groups.create_index("approved")
    await db.groups.create_index("owner_user_id")
    await db.groups.create_index([("approved", 1), ("created_at", -1)])
    
    # ==================== group_users collection ====================
    await db.group_users.create_index([("group_id", 1), ("user_id", 1)], unique=True)
    await db.group_users.create_index([("group_id", 1), ("role", 1)])
    await db.group_users.create_index([("group_id", 1), ("is_vip", 1)])
    await db.group_users.create_index([("group_id", 1), ("last_seen", -1)])
    await db.group_users.create_index([("group_id", 1), ("join_time", -1)])
    await db.group_users.create_index("added_by")
    await db.group_users.create_index("invite_link_id")
    
    # ==================== admin_defaults collection ====================
    await db.admin_defaults.create_index("group_id", unique=True)
    
    # ==================== admin_overrides collection ====================
    await db.admin_overrides.create_index([("group_id", 1), ("admin_user_id", 1)], unique=True)
    await db.admin_overrides.create_index("group_id")
    
    # ==================== invite_links collection ====================
    await db.invite_links.create_index([("group_id", 1), ("link_id", 1)], unique=True)
    await db.invite_links.create_index("group_id")
    await db.invite_links.create_index("created_by")
    await db.invite_links.create_index([("group_id", 1), ("created_at", -1)])
    
    # ==================== logs collection ====================
    await db.logs.create_index([("group_id", 1), ("timestamp", -1)])
    await db.logs.create_index([("group_id", 1), ("type", 1), ("timestamp", -1)])
    await db.logs.create_index("actor_id")
    await db.logs.create_index("target_id")
    await db.logs.create_index("timestamp", expireAfterSeconds=60*60*24*90)  # 90 days TTL
    
    # ==================== settings collection ====================
    await db.settings.create_index([("group_id", 1), ("module_key", 1)], unique=True)
    await db.settings.create_index("group_id")
    
    # ==================== antibetra collection ====================
    await db.antibetra.create_index("group_id", unique=True)
    
    logger.success("✅ Database indexes created")


# ==================== Collection Helpers ====================

def get_users_collection():
    """Get users collection."""
    return get_database().users


def get_groups_collection():
    """Get groups collection."""
    return get_database().groups


def get_group_users_collection():
    """Get group_users collection."""
    return get_database().group_users


def get_admin_defaults_collection():
    """Get admin_defaults collection."""
    return get_database().admin_defaults


def get_admin_overrides_collection():
    """Get admin_overrides collection."""
    return get_database().admin_overrides


def get_invite_links_collection():
    """Get invite_links collection."""
    return get_database().invite_links


def get_logs_collection():
    """Get logs collection."""
    return get_database().logs


def get_settings_collection():
    """Get settings collection."""
    return get_database().settings


def get_antibetra_collection():
    """Get antibetra collection."""
    return get_database().antibetra


# ==================== Export ====================
__all__ = [
    "init_database",
    "close_database",
    "get_database",
    "get_users_collection",
    "get_groups_collection",
    "get_group_users_collection",
    "get_admin_defaults_collection",
    "get_admin_overrides_collection",
    "get_invite_links_collection",
    "get_logs_collection",
    "get_settings_collection",
    "get_antibetra_collection",
]
