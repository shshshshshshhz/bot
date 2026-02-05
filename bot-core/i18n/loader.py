"""
i18n Loader
Translation system for bilingual (Persian/English) support.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from config.settings import settings
from config.database import get_groups_collection


# Global translations cache
_translations: Dict[str, Dict] = {}


def load_translations():
    """
    Load all translation files from i18n directory.
    Called during bot startup.
    """
    global _translations
    
    i18n_dir = settings.I18N_DIR
    
    for lang in settings.SUPPORTED_LANGUAGES:
        lang_file = i18n_dir / f"{lang}.json"
        
        if not lang_file.exists():
            logger.error(f"❌ Translation file not found: {lang_file}")
            continue
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                _translations[lang] = json.load(f)
            
            logger.success(f"✅ Loaded {lang} translations")
        except Exception as e:
            logger.error(f"❌ Failed to load {lang} translations: {e}")
    
    if not _translations:
        logger.error("❌ No translations loaded! Bot will not work properly.")
        raise RuntimeError("No translations loaded")


def get_translation(key: str, language: str = None) -> str:
    """
    Get translation for a key in specified language.
    
    Args:
        key: Translation key (dot-separated path, e.g., "auth.unauthorized_install")
        language: Language code (fa/en). If None, uses default language.
    
    Returns:
        Translated string or key if not found.
    """
    if language is None:
        language = settings.DEFAULT_LANGUAGE
    
    if language not in _translations:
        logger.warning(f"⚠️  Language '{language}' not loaded, falling back to {settings.DEFAULT_LANGUAGE}")
        language = settings.DEFAULT_LANGUAGE
    
    # Navigate through nested dict using dot-separated key
    keys = key.split('.')
    value = _translations.get(language, {})
    
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            break
    
    if value is None or not isinstance(value, str):
        logger.warning(f"⚠️  Translation key not found: {key} (lang: {language})")
        return key  # Return key itself as fallback
    
    return value


async def get_group_language(group_id: int) -> str:
    """
    Get language setting for a specific group.
    
    Args:
        group_id: Telegram group ID
    
    Returns:
        Language code (fa/en)
    """
    try:
        groups_col = get_groups_collection()
        group_doc = await groups_col.find_one({"group_id": group_id})
        
        if group_doc and "language" in group_doc:
            return group_doc["language"]
    except Exception as e:
        logger.error(f"Failed to get group language for {group_id}: {e}")
    
    # Fallback to default
    return settings.DEFAULT_LANGUAGE


def _(group_id: Optional[int], key: str, language: Optional[str] = None, **kwargs) -> str:
    """
    Shorthand translation function with formatting support.
    
    Usage:
        # Simple translation
        await message.reply(_(group_id, "auth.unauthorized_install"))
        
        # With language override
        await message.reply(_(group_id, "auth.unauthorized_install", language="en"))
        
        # With formatting
        await message.reply(_(
            group_id,
            "moderation.banned",
            user="John",
            by="Admin",
            reason="Spam"
        ))
    
    Args:
        group_id: Group ID (used to determine language if language param not provided)
        key: Translation key
        language: Override language (optional)
        **kwargs: Format variables for string formatting
    
    Returns:
        Translated and formatted string
    """
    # If language not specified, use group language or default
    if language is None:
        if group_id:
            # This is sync function, so we can't await
            # In handlers, use get_group_language() async function instead
            # Here we just use default
            language = settings.DEFAULT_LANGUAGE
        else:
            language = settings.DEFAULT_LANGUAGE
    
    # Get translation
    text = get_translation(key, language)
    
    # Format if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            logger.warning(f"⚠️  Missing format variable {e} for key: {key}")
    
    return text


# Export shorthand function as main interface
translate = _


__all__ = [
    "load_translations",
    "get_translation",
    "get_group_language",
    "_",
    "translate"
]
