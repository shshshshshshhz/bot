# Bot-Core

**Main Telegram bot service** - Event handlers, command routing, authentication, and role enforcement.

## Overview

This module is the **heart of the bot** and handles:
- Telegram event handling (messages, callbacks, joins/leaves)
- Command routing and execution
- Panel (inline keyboard) routing
- Authentication and authorization (SUDO gate, role system)
- i18n (bilingual Persian/English support)
- Rate limiting and flood control
- Job scheduling (daily reports, cleanup tasks)
- Error tracking and logging

## Directory Structure

```
bot-core/
├── handlers/          # Telegram event handlers
│   ├── message_handler.py
│   ├── callback_handler.py
│   ├── join_handler.py
│   ├── leave_handler.py
│   └── member_update_handler.py
├── middlewares/       # Request/response middlewares
│   ├── auth_middleware.py
│   ├── rate_limiter.py
│   ├── logger_middleware.py
│   └── i18n_middleware.py
├── routers/           # Command and panel routing
│   ├── command_router.py
│   ├── panel_router.py
│   └── module_loader.py
├── services/          # Business logic services
│   ├── auth_service.py       # Role & permission checks
│   ├── group_service.py      # Group activation gate
│   ├── user_service.py       # User management
│   ├── permission_service.py # Permission templates (apanel/upanel)
│   └── tracking_service.py   # Join tracking
├── i18n/              # Translations
│   ├── fa.json        # Persian
│   ├── en.json        # English
│   └── loader.py      # i18n loader
├── utils/             # Helper utilities
│   ├── decorators.py  # @sudo_only, @owner_only, etc.
│   ├── keyboards.py   # Inline keyboard builders
│   ├── filters.py     # Custom Pyrogram filters
│   └── helpers.py     # General helpers
├── models/            # Data models (Pydantic)
│   ├── user.py
│   ├── group.py
│   ├── permission.py
│   └── log.py
├── config/            # Configuration management
│   ├── settings.py    # Environment variables
│   └── database.py    # MongoDB connection
├── tests/             # Unit & integration tests
│   ├── test_auth.py
│   ├── test_commands.py
│   └── test_panels.py
├── main.py            # Bot entry point
└── README.md          # This file
```

## Key Components

### 1. Authentication Flow (SUDO Gate)

```python
# When bot is added to group
1. join_handler.py triggers
2. Check if group is approved (auth_service.py)
3. If NOT approved:
   - Send unauthorized message (i18n aware)
   - Show "Contact Support" button (links to SUDO)
   - Leave group immediately
4. If approved:
   - Load group settings
   - Initialize modules
   - Send welcome message
```

### 2. Role Enforcement

All commands pass through role checks:

```python
@sudo_only  # Only SUDO users
@owner_only  # Only GROUP_OWNER
@admin_only(permission="bot_ban")  # BOT_ADMIN with specific permission
@respect_vip  # Check VIP immunity
```

### 3. Permission Templates (apanel/upanel)

```python
# APANEL: Default permissions for all new admins
permission_service.get_default_permissions(group_id)

# UPANEL: Per-admin overrides
permission_service.get_user_permissions(group_id, user_id)
# Falls back to APANEL if no override exists
```

### 4. i18n System

```python
# Automatic language detection per group
from utils.i18n import _

# Usage in handlers
await message.reply(_(group_id, "unauthorized_install"))

# i18n/fa.json
{
  "unauthorized_install": "این ربات بدون مجوز اضافه شده است."
}

# i18n/en.json
{
  "unauthorized_install": "Unauthorized installation."
}
```

## Running the Bot

### Development

```bash
cd bot-core
python main.py
```

### Production (with systemd)

```bash
sudo cp telegram-bot.service /etc/systemd/system/
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### Docker

```bash
docker build -t telegram-bot-core .
docker run -d --name bot-core \
  --env-file ../.env \
  -v $(pwd)/logs:/app/logs \
  telegram-bot-core
```

## Environment Variables

See `../.env.example` for full configuration options.

**Required:**
- `API_ID`
- `API_HASH`
- `BOT_TOKEN`
- `MONGODB_URI`
- `SUDO_USERS`

## Testing

```bash
pytest tests/ -v
pytest tests/test_auth.py -v  # Specific test
pytest --cov=handlers tests/  # With coverage
```

## Logging

Logs are written to:
- Console (stdout)
- File: `logs/bot.log` (rotated)
- Sentry (if configured)

Log levels:
- `DEBUG` - Detailed debugging
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical failures

## Performance

- **Rate Limiting:** 20 commands/min per user
- **Panel Interactions:** 30 callbacks/min per user
- **Join Events:** No limit (tracked and logged)
- **Database Queries:** Indexed on group_id, user_id

## Security Features

1. **SUDO Gate:** Prevents unauthorized installations
2. **Role-Based Access:** Strict command permissions
3. **VIP Protection:** Cannot ban VIP without demvip
4. **Rate Limiting:** Prevents spam/flood
5. **Input Validation:** All inputs sanitized
6. **Audit Logs:** Every action logged

## API Integration

Bot-core can communicate with admin-api:

```python
# services/api_client.py
async def notify_api(event_type, payload):
    # Send event to admin-api for webhooks, analytics, etc.
    pass
```

## Module Integration

Bot-core loads modules from `bot-modules/`:

```python
# routers/module_loader.py
def load_modules():
    modules = [
        "moderation",
        "anti_spam",
        "join_tracking",
        # ... all 10+ modules
    ]
    for module in modules:
        import_module(f"bot_modules.{module}")
```

Each module registers:
- Commands → `command_router.py`
- Panels → `panel_router.py`
- i18n keys → `i18n/loader.py`

## Troubleshooting

**Bot doesn't respond:**
1. Check if bot token is valid
2. Verify MongoDB connection
3. Check logs: `tail -f logs/bot.log`
4. Ensure group is approved (`approve_group` command)

**Unauthorized install not working:**
1. Verify `AUTH_MODE=on` in `.env`
2. Check `SUPPORT_USERNAME` is set
3. Test in new group

**Language not switching:**
1. Verify `lang fa` or `lang en` command executed
2. Check `i18n/fa.json` and `i18n/en.json` exist
3. Restart bot if needed

## Contributing

When adding new features:
1. Add handler in `handlers/`
2. Add routing in `routers/`
3. Add i18n keys in `i18n/fa.json` and `i18n/en.json`
4. Add tests in `tests/`
5. Update this README

---

**Part of Enterprise Telegram Group Management Bot**
