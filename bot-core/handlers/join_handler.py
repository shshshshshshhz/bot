"""
Join Handler
Handles new member joins, SUDO gate authorization, and join tracking.

This is the CRITICAL security component that enforces the SUDO-gated installation rule.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import (
    get_groups_collection,
    get_group_users_collection,
    get_invite_links_collection
)
from config.settings import settings
from i18n.loader import _


async def handle_new_chat_members(client: Client, message: Message):
    """
    Handle new members joining the group.
    
    This includes:
    1. Bot being added to group (SUDO gate check)
    2. Regular users joining (track join data)
    """
    group_id = message.chat.id
    
    # Check if bot is among the new members
    bot_me = await client.get_me()
    for new_member in message.new_chat_members:
        if new_member.id == bot_me.id:
            # BOT WAS ADDED TO GROUP - CHECK SUDO AUTHORIZATION
            await handle_bot_added_to_group(client, message)
            return
    
    # Regular user joins - track join data
    await handle_user_join(client, message)


async def handle_bot_added_to_group(client: Client, message: Message):
    """
    CRITICAL SECURITY: Bot was added to a group.
    
    Flow:
    1. Check if group is approved
    2. If NOT approved AND AUTH_MODE is ON:
       - Send unauthorized message
       - Show "Contact Support" button
       - Leave group immediately
    3. If approved:
       - Send welcome message
       - Initialize group settings
    """
    group_id = message.chat.id
    groups_col = get_groups_collection()
    
    # Check if group exists and is approved
    group_doc = await groups_col.find_one({"group_id": group_id})
    
    if settings.AUTH_MODE and (not group_doc or not group_doc.get("approved", False)):
        # UNAUTHORIZED INSTALLATION - REJECT
        logger.warning(f"🚫 Unauthorized installation attempt in group {group_id}")
        
        # Get language (default to fa since group not approved yet)
        language = settings.DEFAULT_LANGUAGE
        
        # Create "Contact Support" button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=_(group_id, "auth.contact_support", language),
                url=f"t.me/{settings.SUPPORT_USERNAME}"
            )]
        ])
        
        # Send unauthorized message
        unauthorized_msg = _(group_id, "auth.unauthorized_install", language)
        
        try:
            await message.reply(
                unauthorized_msg,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Failed to send unauthorized message: {e}")
        
        # Leave the group immediately
        try:
            await client.leave_chat(group_id)
            logger.info(f"👋 Left unauthorized group {group_id}")
        except Exception as e:
            logger.error(f"Failed to leave group {group_id}: {e}")
        
        return
    
    # GROUP IS APPROVED OR AUTH_MODE IS OFF
    logger.success(f"✅ Bot added to approved group {group_id}")
    
    # Initialize group document if not exists
    if not group_doc:
        await groups_col.insert_one({
            "group_id": group_id,
            "approved": False if settings.AUTH_MODE else True,
            "language": settings.DEFAULT_LANGUAGE,
            "owner_user_id": None,
            "created_at": message.date,
            "settings": {}
        })
        logger.info(f"📝 Created new group document for {group_id}")
    
    # Send welcome message
    language = group_doc.get("language", settings.DEFAULT_LANGUAGE) if group_doc else settings.DEFAULT_LANGUAGE
    
    welcome_msg = (
        f"✅ {_(group_id, 'auth.group_approved', language)}\n\n"
        f"📖 {_(group_id, 'help.main', language)}"
    )
    
    try:
        await message.reply(welcome_msg)
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")


async def handle_user_join(client: Client, message: Message):
    """
    Handle regular user joining the group.
    
    Track join data:
    - join_method: invite_link / added_by_user / join_request / unknown
    - added_by: user_id (if added by someone)
    - invite_link_id: (if via invite link)
    - join_time: timestamp
    """
    group_id = message.chat.id
    groups_col = get_groups_collection()
    
    # Check if group is approved
    group_doc = await groups_col.find_one({"group_id": group_id})
    if not group_doc or not group_doc.get("approved", False):
        # Group not approved - don't track joins
        return
    
    # Check if join tracking is enabled
    settings_doc = group_doc.get("settings", {})
    if not settings_doc.get("track_join", False):
        return
    
    group_users_col = get_group_users_collection()
    
    # Determine join method
    join_method = "unknown"
    added_by = None
    invite_link_id = None
    invite_link_tag = None
    
    # Check if user was added by someone
    if message.from_user:
        added_by = message.from_user.id
        join_method = "added_by_user"
    
    # Check for invite link (if available in message metadata)
    # Note: Pyrogram doesn't always provide invite link info, but we try
    if hasattr(message, 'invite_link') and message.invite_link:
        join_method = "invite_link"
        invite_link_id = message.invite_link.invite_link
        
        # Try to get tag from database
        invite_links_col = get_invite_links_collection()
        link_doc = await invite_links_col.find_one({
            "group_id": group_id,
            "link_id": invite_link_id
        })
        if link_doc:
            invite_link_tag = link_doc.get("tag")
            # Increment join count
            await invite_links_col.update_one(
                {"_id": link_doc["_id"]},
                {"$inc": {"join_count": 1}}
            )
    
    # Store join data for each new member
    for new_member in message.new_chat_members:
        try:
            await group_users_col.update_one(
                {"group_id": group_id, "user_id": new_member.id},
                {
                    "$set": {
                        "join_method": join_method,
                        "added_by": added_by,
                        "invite_link_id": invite_link_id,
                        "invite_link_tag": invite_link_tag,
                        "join_time": message.date,
                        "last_seen": message.date
                    },
                    "$setOnInsert": {
                        "role": "member",
                        "is_vip": False,
                        "warns": 0
                    }
                },
                upsert=True
            )
            
            logger.info(
                f"📊 Tracked join: user={new_member.id}, "
                f"method={join_method}, group={group_id}"
            )
        except Exception as e:
            logger.error(f"Failed to track join for user {new_member.id}: {e}")


async def handle_chat_member_updated(client: Client, update: ChatMemberUpdated):
    """
    Handle chat member updates (alternative join tracking method).
    
    This catches join requests and other membership changes.
    """
    group_id = update.chat.id
    user_id = update.from_user.id if update.from_user else update.new_chat_member.user.id
    
    # Check if this is a new join (old=none/left, new=member/admin)
    old_status = update.old_chat_member.status if update.old_chat_member else "left"
    new_status = update.new_chat_member.status if update.new_chat_member else "left"
    
    if old_status in ["left", "kicked", "banned"] and new_status in ["member", "administrator", "creator"]:
        # User joined
        groups_col = get_groups_collection()
        group_doc = await groups_col.find_one({"group_id": group_id})
        
        if not group_doc or not group_doc.get("approved", False):
            return
        
        settings_doc = group_doc.get("settings", {})
        if not settings_doc.get("track_join", False):
            return
        
        # Determine join method
        join_method = "join_request" if hasattr(update, "invite_link") else "unknown"
        invite_link_id = update.invite_link.invite_link if hasattr(update, "invite_link") and update.invite_link else None
        
        group_users_col = get_group_users_collection()
        
        try:
            await group_users_col.update_one(
                {"group_id": group_id, "user_id": user_id},
                {
                    "$set": {
                        "join_method": join_method,
                        "invite_link_id": invite_link_id,
                        "join_time": update.date
                    },
                    "$setOnInsert": {
                        "role": "member",
                        "is_vip": False,
                        "warns": 0
                    }
                },
                upsert=True
            )
            
            logger.info(f"📊 Tracked join (member_updated): user={user_id}, group={group_id}")
        except Exception as e:
            logger.error(f"Failed to track join (member_updated): {e}")


def register_handlers(app: Client):
    """
    Register all join-related handlers.
    """
    # New chat members (when users join or bot is added)
    app.add_handler(
        filters.new_chat_members,
        handle_new_chat_members,
        group=1
    )
    
    # Chat member updates (join requests, etc.)
    app.add_handler(
        filters.chat_member_updated,
        handle_chat_member_updated,
        group=1
    )
    
    logger.info("✅ Join handlers registered")
