
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
        res = requests.post(url, data=data)

        # Debug - طباعة نتيجة الطلب
        print("[Telegram] Status:", res.status_code)
        print("[Telegram] Response:", res.text)

    except Exception as e:
        print(f"[Telegram Error]: {e}")

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
        hwid = getattr(user, "hwid", "N/A")
        os_info = f"{platform.system()} {platform.release()}"
        ip = getattr(user, "ip", "Unknown")
        license_key = getattr(user, "username", data.license_key)
        expiry = getattr(user, "expires", "N/A")

        local_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p (Local Time)')
        utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p (UTC)')

        expiry_dt = datetime.strptime(expiry, "%Y-%m-%d")
        now = datetime.now()
        remaining = expiry_dt - now
        if remaining.total_seconds() > 0:
            rem_str = f"Ends in {remaining.days} days"
        else:
            rem_str = "Expired"

        msg = f"""🔐 *License Activated*

📅 *Activation Time:*
├ 🕒 *Local:* `{local_time}`
└ 🌐 *UTC:* `{utc_time}`

👤 *PC Name:* `{pc_name}`
🖥️ *HWID:* `{hwid}`
💻 *OS:* `{os_info}`
📍 *IP:* `{ip}`
🆔 *License:* `{license_key}`
🕒 *Expiry:* `{expiry}`
⌛ *Remaining:* `{rem_str}`
"""


        send_telegram(msg)
        send_discord(msg)

        return {"status": "success", "message": "Activated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
