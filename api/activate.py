from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from keyauth.api import Keyauth, KeyauthError
import os
import platform
import hashlib
import requests
from datetime import datetime, timezone

# إعداد Vercel API
app = FastAPI()

# KeyAuth Settings
name = "123"
owner_id = "hKsGVXgQWd"
secret = "caf9850754119109448034765052eae71bac6d7f791e60e3b1c3aeb487ce1fb3"
version = "1.0"

# Telegram
BOT_TOKEN = "7599892515:AAFx6GXQJKL9pZDYXttyCFszxFFbUkNE5TA"
CHAT_ID = "7946491186"

# Discord
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/xxxxxxxxx/xxxxxxxxx"

def getchecksum():
    with open(os.path.abspath(__file__), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except:
        pass

def send_discord(message):
    try:
        requests.post(DISCORD_WEBHOOK, data={"content": message})
    except:
        pass

def format_expiry(unix_timestamp):
    try:
        return datetime.fromtimestamp(int(unix_timestamp)).strftime('%Y-%m-%d %I:%M:%S %p (Local Time)')
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
        parts = []
        if days > 0: parts.append(f"{days} days")
        if hours > 0: parts.append(f"{hours} hours")
        if minutes > 0: parts.append(f"{minutes} minutes")
        return "Ends in " + " and ".join(parts)
    except:
        return "Not available"

class LicenseData(BaseModel):
    license_key: str

@app.post("/api/activate")
async def activate_license(data: LicenseData, request: Request):
    try:
        keyauthapp = Keyauth(name, owner_id, secret, version, getchecksum())
        keyauthapp.license(data.license_key)

        user = keyauthapp.user
        pc_name = "Unknown"
        hwid = getattr(user, "hwid", "Unknown")
        user_ip = request.client.host or "Unknown"
        user_key = getattr(user, "username", data.license_key)
        raw_expiry = getattr(user, "expires", None)
        user_expiry = format_expiry(raw_expiry) if raw_expiry else "Unknown"
        user_remaining = get_time_left(raw_expiry) if raw_expiry else "N/A"
        os_info = f"{platform.system()} {platform.release()}"

        # توقيت التفعيل
        activation_local = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p (Local Time)')
        activation_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p (UTC)')

        msg = f"""🔐 **[License Activated]**

📅 **Activation Time:**
   ├ 🕒 Local: {activation_local}
   └ 🌐 UTC: {activation_utc}

👤 **PC Name:** `{pc_name}`
🖥️ **HWID:** `{hwid}`
💻 **OS:** {os_info}
📍 **IP:** {user_ip}
🆔 **License:** `{user_key}`
🕒 **Expiry:** {user_expiry}
⌛ **Remaining:** {user_remaining}
"""

        send_telegram(msg)
        send_discord(msg)

        return {
            "status": "success",
            "message": "License activated",
            "details": {
                "license": user_key,
                "ip": user_ip,
                "hwid": hwid,
                "expiry": user_expiry,
                "remaining": user_remaining
            }
        }
    except KeyauthError as e:
        raise HTTPException(status_code=401, detail=f"❌ Activation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Unexpected error: {str(e)}")
