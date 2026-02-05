"""
Custom Filters
Custom Pyrogram filters for flexible command handling.
"""

from pyrogram import filters
from pyrogram.types import Message
from typing import List, Union
import re

from config.settings import settings


def command(
    commands: Union[str, List[str]],
    prefixes: Union[str, List[str]] = None,
    case_sensitive: bool = False
):
    """
    Custom command filter that supports:
    - Commands WITH slash: /ban, /setvip
    - Commands WITHOUT slash: ban, setvip
    - Both at the same time
    
    Args:
        commands: Command name(s) - e.g., "ban" or ["ban", "kick"]
        prefixes: Custom prefixes (None = use settings)
        case_sensitive: Case sensitivity
    
    Usage:
        @app.on_message(command("ban"))  # Works for: /ban OR ban
        @app.on_message(command(["ban", "kick"]))
    """
    # Convert to list
    if isinstance(commands, str):
        commands = [commands]
    
    # Determine prefixes
    if prefixes is None:
        prefixes = []
        if settings.ALLOW_SLASH_COMMANDS:
            prefixes.append("/")
        if settings.ALLOW_NO_PREFIX_COMMANDS:
            prefixes.append("")  # No prefix
        if settings.COMMAND_PREFIX:
            prefixes.append(settings.COMMAND_PREFIX)
    elif isinstance(prefixes, str):
        prefixes = [prefixes]
    
    async def func(flt, client, message: Message):
        if not message.text:
            return False
        
        text = message.text
        if not case_sensitive:
            text = text.lower()
            commands_lower = [cmd.lower() for cmd in commands]
        else:
            commands_lower = commands
        
        # Check each command with each prefix
        for prefix in prefixes:
            for cmd in commands_lower:
                # Pattern: ^prefix+command(\s|$)
                # Matches: "ban ", "ban@botname ", "/ban ", etc.
                pattern = rf"^{re.escape(prefix)}{re.escape(cmd)}(\s|@|$)"
                if re.match(pattern, text):
                    return True
        
        return False
    
    return filters.create(func, "CustomCommandFilter")


def admin_command(commands: Union[str, List[str]], **kwargs):
    """
    Command filter for admin-only commands.
    Only works in groups.
    """
    return command(commands, **kwargs) & filters.group


def owner_command(commands: Union[str, List[str]], **kwargs):
    """
    Command filter for owner-only commands.
    """
    return command(commands, **kwargs) & filters.group


def sudo_command(commands: Union[str, List[str]], **kwargs):
    """
    Command filter for SUDO-only commands.
    """
    return command(commands, **kwargs)


__all__ = [
    "command",
    "admin_command", 
    "owner_command",
    "sudo_command"
]
