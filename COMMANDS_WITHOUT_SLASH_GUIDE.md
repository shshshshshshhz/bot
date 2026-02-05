# 🎯 راهنمای دستورات بدون اسلش (/)

## چطور کار میکنه؟

با تنظیمات جدید، میتونی دستورات رو به **3 روش** بزنی:

### ✅ روش 1: بدون اسلش (بدون /)
```
ban
setvip @user
mute 60
who_added @user
```

### ✅ روش 2: با اسلش (/)
```
/ban
/setvip @user
/mute 60
/who_added @user
```

### ✅ روش 3: با پیشوند سفارشی (! یا .)
```
!ban
!setvip @user
.mute 60
.who_added @user
```

---

## 🔧 تنظیمات

### فایل `.env`:

```env
# گزینه 1: فقط بدون اسلش ✅ (پیشنهادی شما)
ALLOW_SLASH_COMMANDS=false
ALLOW_NO_PREFIX_COMMANDS=true
COMMAND_PREFIX=

# گزینه 2: فقط با اسلش (مثل قبل)
ALLOW_SLASH_COMMANDS=true
ALLOW_NO_PREFIX_COMMANDS=false
COMMAND_PREFIX=

# گزینه 3: هر دو روش (انعطاف بیشتر)
ALLOW_SLASH_COMMANDS=true
ALLOW_NO_PREFIX_COMMANDS=true
COMMAND_PREFIX=

# گزینه 4: فقط ! (Discord style)
ALLOW_SLASH_COMMANDS=false
ALLOW_NO_PREFIX_COMMANDS=false
COMMAND_PREFIX=!
```

---

## 📝 مثال‌های کاربردی

### مثال 1: بن کردن
```
کاربر: ban
بات: 🔨 کاربر بن شد!

کاربر: /ban
بات: 🔨 کاربر بن شد!
```

### مثال 2: VIP کردن
```
# با reply
کاربر: [روی پیام کاربر reply میکنه] setvip
بات: 💎 کاربر به VIP تبدیل شد!

# با username
کاربر: setvip @john
بات: 💎 @john به VIP تبدیل شد!
```

### مثال 3: میوت با زمان
```
کاربر: mute 60
بات: 🔇 کاربر برای 60 دقیقه ساکت شد!

کاربر: mute 30
بات: 🔇 کاربر برای 30 دقیقه ساکت شد!
```

### مثال 4: ردیابی ورود
```
کاربر: who_added @user
بات: 📊 اطلاعات ورود کاربر:
     روش ورود: لینک دعوت
     اضافه شده توسط: @admin
     زمان: 2026-02-03 10:30
```

### مثال 5: لیست VIP
```
کاربر: viplist
بات: 💎 لیست کاربران VIP:
     1. @user1
     2. @user2
     3. @user3
```

---

## ⚙️ همه دستورات (264 عدد)

### 🔐 SUDO
```
sudo_add 123456
sudo_remove 123456
sudo_list
approve_group
revoke_group
```

### 👑 Owner
```
setowner @user
ownerinfo
promoteadmin @user
demoteadmin @user
apanel
upanel @admin
```

### 💎 VIP
```
setvip @user
demvip @user
viplist
```

### 🔨 Moderation
```
ban
unban @user
kick
mute 60
unmute
warn
unwarn
warns @user
del
purge 50
pin
unpin
lockdown on
slowmode 30
```

### 🔒 Locks
```
lock photo on
lock video on
lock gif on
lock sticker on
lock forward on
antilink on
antiforward on
```

### 🛡 Filters
```
blacklist add spam
blacklist remove spam
whitelist add telegram
punish blacklist warn
```

### 📊 Join Tracking
```
track_join on
who_added @user
invite_tree @user
added_list @user
link_list
link_tag <link> "Campaign Name"
```

### ✅ Verification
```
rverify on
verify_type code
verify_timeout 120
verify_attempts 3
```

### 🔍 Bio/Account
```
bioscan on
bioscan_action report
accage on
accage_min_days 30
```

### 🛡 Anti-Betrayal
```
rantibetra on
setmaxban 5
setmaxbantime 30
```

### 🗑 Cleanup
```
clean fakes
clean inactive
inactive_days 60
clean_preview
clean_execute
```

### 📊 Reports
```
gpstatus on
gpstatus_visibility admins
```

### 📜 Logs
```
log on
setlogchat -1001234567890
logs
```

### 🏷 Tagging
```
tag admins
tag active
tag vip
tag new
```

### ⚙️ Settings
```
panel
panel_lock on
lang fa
lang en
```

---

## 💡 نکات مهم

### ✅ مزایا
1. **راحت‌تر** - نیاز نیست / بزنی
2. **سریع‌تر** - یک کاراکتر کمتر
3. **طبیعی‌تر** - مثل Discord

### ⚠️ نکات امنیتی

#### مشکل: تداخل با کلمات معمولی
```
❌ مشکل: اگه دستور "test" داشته باشی
کاربر: "test"
بات: [اجرای دستور test!]

✅ راه حل 1: دستورات انگلیسی خاص
ban, kick, mute, setvip, ... (کسی اینجوری صحبت نمیکنه)

✅ راه حل 2: فقط در گروه کار کنه
(پیام‌های شخصی ignore بشن)

✅ راه حل 3: استفاده از prefix
!ban, .ban, ...
```

#### مشکل: اسپم دستورات
```
❌ کاربران ممکنه اشتباهی دستور رو بزنن

✅ راه حل: Rate Limiting
فقط 20 دستور در دقیقه (تو تنظیمات هست)
```

---

## 🎨 سفارشی‌سازی

### حالت 1: فقط بدون اسلش (Discord-like)
```env
ALLOW_SLASH_COMMANDS=false
ALLOW_NO_PREFIX_COMMANDS=true
COMMAND_PREFIX=
```
**نتیجه:**
- ✅ `ban` کار میکنه
- ❌ `/ban` کار نمیکنه

### حالت 2: با پیشوند ! (Discord style)
```env
ALLOW_SLASH_COMMANDS=false
ALLOW_NO_PREFIX_COMMANDS=false
COMMAND_PREFIX=!
```
**نتیجه:**
- ✅ `!ban` کار میکنه
- ❌ `/ban` کار نمیکنه
- ❌ `ban` کار نمیکنه

### حالت 3: ترکیبی (Maximum Flexibility)
```env
ALLOW_SLASH_COMMANDS=true
ALLOW_NO_PREFIX_COMMANDS=true
COMMAND_PREFIX=!
```
**نتیجه:**
- ✅ `ban` کار میکنه
- ✅ `/ban` کار میکنه
- ✅ `!ban` کار میکنه

---

## 🧪 تست کردن

### 1. بدون اسلش
```
شما: ban
بات: 🔨 کاربر بن شد!
```

### 2. با اسلش
```
شما: /ban
بات: [اگه ALLOW_SLASH_COMMANDS=true باشه] 🔨 کاربر بن شد!
بات: [اگه ALLOW_SLASH_COMMANDS=false باشه] هیچ اتفاقی نمی‌افته
```

### 3. با آرگومنت
```
شما: mute 60
بات: 🔇 کاربر برای 60 دقیقه ساکت شد!
```

### 4. با reply
```
شما: [reply به پیام کاربر] warn
بات: ⚠️ اخطار به کاربر!
```

### 5. با username
```
شما: setvip @john
بات: 💎 @john به VIP تبدیل شد!
```

---

## 📚 کد پیاده‌سازی

کدها در این فایل‌ها هستن:

1. **`bot-core/utils/filters.py`** - فیلتر سفارشی
2. **`bot-core/config/settings.py`** - تنظیمات
3. **`bot-core/handlers/EXAMPLE_COMMANDS_WITHOUT_SLASH.py`** - مثال‌ها
4. **`.env.example`** - تنظیمات محیطی

---

## 🚀 استفاده در کد

### روش استفاده:

```python
from pyrogram import Client
from pyrogram.types import Message
from utils.filters import command

# دستور ساده
@Client.on_message(command("ban"))
async def ban_user(client: Client, message: Message):
    await message.reply("🔨 کاربر بن شد!")

# چند دستور
@Client.on_message(command(["setvip", "vip"]))
async def set_vip(client: Client, message: Message):
    await message.reply("💎 کاربر VIP شد!")

# با آرگومنت
@Client.on_message(command("mute"))
async def mute_user(client: Client, message: Message):
    # استخراج زمان از message.text
    import re
    match = re.match(r'^[/!]?mute\s+(\d+)', message.text)
    if match:
        duration = int(match.group(1))
        await message.reply(f"🔇 میوت برای {duration} دقیقه!")
```

---

## ✅ پیشنهاد نهایی

برای بهترین تجربه، این تنظیمات رو توصیه می‌کنم:

```env
# هر دو روش فعال (بیشترین انعطاف)
ALLOW_SLASH_COMMANDS=true
ALLOW_NO_PREFIX_COMMANDS=true
COMMAND_PREFIX=
```

**چرا؟**
- کاربران تازه‌کار میتونن با / بزنن
- کاربران حرفه‌ای میتونن بدون / بزنن
- هیچ محدودیتی نداره

---

**همه چیز آماده است!** 🎉

فقط کافیه `.env` رو تنظیم کنی و بات رو اجرا کنی.
