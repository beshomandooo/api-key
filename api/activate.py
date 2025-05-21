from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from keyauth.api import Keyauth, KeyauthError
import platform
import hashlib
import requests
from datetime import datetime, timezone

app = FastAPI()

# KeyAuth Settings
name = "123"
owner_id = "hKsGVXgQWd"
secret = "caf9850754119109448034765052eae71bac6d7f791e60e3b1c3aeb487ce1fb3"
version = "1.0"

# Telegram & Discord
BOT_TOKEN = "7599892515:AAFx6GXQJKL9pZDYXttyCFszxFFbUkNE5TA"
CHAT_ID = "7946491186"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/xxxxxxxxx/xxxxxxxxx"

# Checksum

def getchecksum():
    return hashlib.sha256(open(__file__, 'rb').read()).hexdigest()

# Send notifications

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

def send_discord(msg):
    try:
        requests.post(DISCORD_WEBHOOK, data={"content": msg})
    except: pass

# Format expiry & time left

def format_expiry(unix_timestamp):
    try:
        return datetime.fromtimestamp(int(unix_timestamp)).strftime('%Y-%m-%d %I:%M:%S %p (Local Time)')
    except: return "Unknown"

def get_time_left(unix_timestamp):
    try:
        expiry = datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = expiry - now
        if delta.total_seconds() <= 0: return "Expired"
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        return f"Ends in {days}d {hours}h {minutes}m"
    except: return "N/A"

# Request model
class LicenseData(BaseModel):
    license_key: str
    hwid: str
    pc_name: str
    os: str
    mac: str

@app.post("/api/activate")
async def activate_license(data: LicenseData, request: Request):
    try:
        keyauthapp = Keyauth(name, owner_id, secret, version, getchecksum())
        keyauthapp.license(data.license_key)

        user = keyauthapp.user
        user_ip = request.client.host or "Unknown"
        user_key = getattr(user, "username", data.license_key)
        raw_expiry = getattr(user, "expires", None)
        user_expiry = format_expiry(raw_expiry) if raw_expiry else "Unknown"
        remaining = get_time_left(raw_expiry) if raw_expiry else "N/A"

        local_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p (UTC)')

        msg = f"""🔐 **[License Activated]**

📅 **Activation Time:**
├ 🕒 Local: {local_time}
└ 🌐 UTC: {utc_time}

👤 **PC Name:** `{data.pc_name}`
🖥️ **HWID:** `{data.hwid}`
💻 **OS:** {data.os}
🔌 **MAC:** `{data.mac}`
📍 **IP:** {user_ip}
🆔 **License:** `{user_key}`
🕒 **Expiry:** {user_expiry}
⌛ **Remaining:** {remaining}
"""

        send_telegram(msg)
        send_discord(msg)

        return {
            "status": "success",
            "message": "License activated",
            "data": {
                "license": user_key,
                "expiry": user_expiry,
                "remaining": remaining,
                "ip": user_ip,
                "hwid": data.hwid,
                "pc_name": data.pc_name,
                "os": data.os,
                "mac": data.mac
            }
        }

    except KeyauthError as e:
        raise HTTPException(status_code=401, detail=f"❌ Activation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Unexpected error: {str(e)}")
