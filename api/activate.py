
from fastapi import FastAPI
from pydantic import BaseModel
from keyauth.api import Keyauth, KeyauthError
import platform
from datetime import datetime, timezone
import requests

app = FastAPI()

name = "123"
owner_id = "hKsGVXgQWd"
secret = "caf9850754119109448034765052eae71bac6d7f791e60e3b1c3aeb487ce1fb3"
version = "1.0"
BOT_TOKEN = "7599892515:AAFx6GXQJKL9pZDYXttyCFszxFFbUkNE5TA"
CHAT_ID = "7946491186"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/xxxxxxxxx/xxxxxxxxx"

class LicenseRequest(BaseModel):
    license_key: str

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

@app.post("/api/activate")
async def activate_license(data: LicenseRequest):
    try:
        keyauthapp = Keyauth(name, owner_id, secret, version, "dummyhash")
        keyauthapp.license(data.license_key)

        user = keyauthapp.user
        pc_name = platform.node()

        activation_local = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        activation_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p')

        # 🟡 استخراج وقت انتهاء الاشتراك وتحويله لتاريخ
        expiry_unix = int(user.expires)
        expiry_time = datetime.fromtimestamp(expiry_unix, tz=timezone.utc)
        expiry_str = expiry_time.strftime('%Y-%m-%d %I:%M:%S %p (UTC)')

        # 🟠 حساب الوقت المتبقي
        remaining = expiry_time - datetime.now(timezone.utc)
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        remaining_str = f"{days} يوم، {hours} ساعة، {minutes} دقيقة"

        msg = f"""🔐 **[License Activated]**

📅 **Activation Time:**
   ├ 🕒 Local: {activation_local}
   └ 🌐 UTC: {activation_utc}

🧾 **License Info:**
   ├ 🆔 Key: `{data.license_key}`
   ├ 🖥️ PC Name: `{pc_name}`
   ├ 📆 Expiry Date: {expiry_str}
   └ ⏳ Remaining: {remaining_str}
"""

        send_telegram(msg)
        send_discord(msg)

        return {"status": "success", "message": "Activated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
