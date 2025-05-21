from fastapi import FastAPI
from pydantic import BaseModel
from keyauth.api import Keyauth, KeyauthError
import platform, hashlib, requests
from datetime import datetime, timezone

app = FastAPI()

# إعدادات KeyAuth
name = "123"
owner_id = "hKsGVXgQWd"
secret = "caf9850754119109448034765052eae71bac6d7f791e60e3b1c3aeb487ce1fb3"
version = "1.0"
BOT_TOKEN = "7599892515:AAFx6GXQJKL9pZDYXttyCFszxFFbUkNE5TA"
CHAT_ID = "7946491186"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/xxxxxxxxx/xxxxxxxxx"

# دالة للحصول على hash وهمي (لأن Vercel مش هيحسب الملف الفعلي)
def getchecksum():
    return "dummyhash"

# دوال المساعدة
def format_expiry(unix_timestamp):
    try:
        return datetime.fromtimestamp(int(unix_timestamp)).strftime('%Y-%m-%d %I:%M:%S %p')
    except:
        return "Unknown"

def get_time_left(unix_timestamp):
    try:
        expiry_dt = datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = expiry_dt - now
        if delta.total_seconds() <= 0:
            return "Expired"
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    except:
        return "Not available"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except:
        pass

def send_discord(msg):
    try:
        data = {"content": msg}
        requests.post(DISCORD_WEBHOOK, data=data)
    except:
        pass

# شكل البيانات المطلوبة من المستخدم
class LicenseRequest(BaseModel):
    license_key: str

# نقطة الدخول
@app.post("/")
async def activate_license(data: LicenseRequest):
    try:
        keyauthapp = Keyauth(name, owner_id, secret, version, getchecksum())
        keyauthapp.license(data.license_key)

        user = keyauthapp.user
        pc_name = platform.node()
        user_key = getattr(user, "username", data.license_key)
        raw_expiry = getattr(user, "expires", None)
        expiry = format_expiry(raw_expiry)
        remaining = get_time_left(raw_expiry)
        hwid = getattr(user, "hwid", "N/A")
        user_ip = getattr(user, "ip", "Unknown")
        os_info = f"{platform.system()} {platform.release()}"

        local_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p')

        msg = f"""🔐 **[License Activated]**

📅 **Activation Time:**
   ├ 🕒 Local: {local_time}
   └ 🌐 UTC: {utc_time}

👤 **PC Name:** `{pc_name}`
🖥️ **HWID:** `{hwid}`
💻 **OS:** {os_info}
📍 **IP:** {user_ip}
🆔 **License:** `{user_key}`
🕒 **Expiry:** {expiry}
⌛ **Remaining:** {remaining}
"""
        send_telegram(msg)
        send_discord(msg)

        return {"status": "success", "message": "Activated", "user": user_key}
    except Exception as e:
        return {"status": "error", "message": str(e)}
