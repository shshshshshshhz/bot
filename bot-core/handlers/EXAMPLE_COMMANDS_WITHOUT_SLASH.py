"""
Example: Command Handler WITHOUT SLASH
نمونه: دستورات بدون اسلش

This shows how commands work with the custom filter.
"""

from pyrogram import Client
from pyrogram.types import Message

# استفاده از فیلتر سفارشی
from utils.filters import command, admin_command, owner_command, sudo_command


# ================== مثال 1: دستور ساده ==================

@Client.on_message(command("ban"))
async def ban_user(client: Client, message: Message):
    """
    این کار میکنه با:
    - /ban
    - ban
    - !ban (اگه تو تنظیمات فعال کنی)
    """
    await message.reply("کاربر بن شد!")


# ================== مثال 2: چند دستور ==================

@Client.on_message(command(["setvip", "vip"]))
async def set_vip(client: Client, message: Message):
    """
    این کار میکنه با:
    - /setvip یا setvip
    - /vip یا vip
    """
    await message.reply("💎 کاربر VIP شد!")


# ================== مثال 3: دستور ادمین ==================

@Client.on_message(admin_command("kick"))
async def kick_user(client: Client, message: Message):
    """
    فقط برای ادمین‌ها
    کار میکنه با: /kick یا kick
    """
    await message.reply("👢 کاربر اخراج شد!")


# ================== مثال 4: دستور Owner ==================

@Client.on_message(owner_command("promoteadmin"))
async def promote_admin(client: Client, message: Message):
    """
    فقط برای Owner
    کار میکنه با: /promoteadmin یا promoteadmin
    """
    await message.reply("⬆️ پنل ارتقا باز شد!")


# ================== مثال 5: دستور SUDO ==================

@Client.on_message(sudo_command("approve_group"))
async def approve_group(client: Client, message: Message):
    """
    فقط برای SUDO
    کار میکنه با: /approve_group یا approve_group
    """
    await message.reply("✅ گروه تایید شد!")


# ================== مثال 6: دستور با آرگومنت ==================

@Client.on_message(command("mute"))
async def mute_user(client: Client, message: Message):
    """
    استخراج آرگومنت‌ها
    
    استفاده:
    - mute 60
    - /mute 30
    """
    # حذف command از text
    text = message.text
    
    # حذف اسلش و command name
    import re
    # پیدا کردن اولین فضای خالی بعد از command
    match = re.match(r'^[/!]?\w+\s+(.+)', text)
    
    if match:
        args = match.group(1)  # "60" یا "30"
        duration = int(args)
        await message.reply(f"🔇 کاربر برای {duration} دقیقه ساکت شد!")
    else:
        await message.reply("⚠️ لطفاً مدت زمان را مشخص کنید.\n\nمثال: mute 60")


# ================== مثال 7: دستور با reply ==================

@Client.on_message(command("warn"))
async def warn_user(client: Client, message: Message):
    """
    دستوری که نیاز به reply داره
    
    استفاده:
    - روی پیام کاربر reply کن و بزن: warn
    - یا: /warn
    """
    if not message.reply_to_message:
        await message.reply("❌ لطفاً روی پیام کاربر reply کنید.")
        return
    
    target = message.reply_to_message.from_user
    await message.reply(f"⚠️ اخطار به {target.first_name}!")


# ================== مثال 8: دستور با username ==================

@Client.on_message(command("setvip"))
async def setvip_user(client: Client, message: Message):
    """
    دستور با username یا reply
    
    استفاده:
    - setvip @username
    - /setvip @username
    - روی پیام reply: setvip
    """
    target = None
    
    # روش 1: چک reply
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    
    # روش 2: چک username در text
    elif len(message.command) > 1:
        username = message.command[1].replace("@", "")
        # اینجا باید از دیتابیس یا API بگیری
        # target = await get_user_by_username(username)
        await message.reply(f"💎 @{username} به VIP تبدیل شد!")
        return
    
    if target:
        await message.reply(f"💎 {target.first_name} به VIP تبدیل شد!")
    else:
        await message.reply("❌ لطفاً روی پیام reply کنید یا @username بنویسید.")


# ================== نکته مهم: استخراج command name ==================

def get_command_name(message: Message) -> str:
    """
    استخراج اسم command از پیام
    
    مثال:
    - "/ban test" → "ban"
    - "kick @user" → "kick"
    - "!setvip" → "setvip"
    """
    text = message.text or ""
    import re
    
    # پیدا کردن اولین کلمه (با یا بدون prefix)
    match = re.match(r'^[/!]?(\w+)', text)
    if match:
        return match.group(1).lower()
    return ""


def get_command_args(message: Message) -> str:
    """
    استخراج آرگومنت‌های command
    
    مثال:
    - "/ban test reason" → "test reason"
    - "mute 60" → "60"
    """
    text = message.text or ""
    import re
    
    # پیدا کردن همه چیز بعد از اولین فضا
    match = re.match(r'^[/!]?\w+\s+(.+)', text)
    if match:
        return match.group(1)
    return ""


"""
================== تنظیمات در .env ==================

# گزینه 1: فقط بدون اسلش
ALLOW_SLASH_COMMANDS=false
ALLOW_NO_PREFIX_COMMANDS=true

# گزینه 2: فقط با اسلش (مثل قبل)
ALLOW_SLASH_COMMANDS=true
ALLOW_NO_PREFIX_COMMANDS=false

# گزینه 3: هر دو (توصیه میشه)
ALLOW_SLASH_COMMANDS=true
ALLOW_NO_PREFIX_COMMANDS=true

# گزینه 4: prefix سفارشی (مثل !)
COMMAND_PREFIX=!
ALLOW_SLASH_COMMANDS=true
ALLOW_NO_PREFIX_COMMANDS=true

================== مثال‌های استفاده ==================

با تنظیم پیش‌فرض (هر دو فعال):

✅ ban              → کار میکنه
✅ /ban             → کار میکنه
✅ setvip @user     → کار میکنه
✅ /setvip @user    → کار میکنه
✅ mute 60          → کار میکنه
✅ /mute 60         → کار میکنه

اگه فقط بدون اسلش فعال کنی:

✅ ban              → کار میکنه
❌ /ban             → کار نمیکنه
✅ setvip @user     → کار میکنه
❌ /setvip @user    → کار نمیکنه

================== نکته امنیتی ==================

وقتی بدون اسلش فعاله، مراقب باش که دستورات با کلمات معمولی
conflict نداشته باشن!

مثلاً اگه دستور "test" داری، هر وقت کسی بگه "test" اجرا میشه!

راه حل:
1. فقط دستورات مخصوص انگلیسی باشن (ban, kick, mute, ...)
2. از پیشوند استفاده کن (! یا .)
3. فقط در گروه کار کنه (با filters.group)

"""
