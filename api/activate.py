from fastapi import FastAPI
from pydantic import BaseModel
from keyauth.api import Keyauth, KeyauthError
from datetime import datetime, timezone
import requests

app = FastAPI()

# إعدادات KeyAuth
name = "123"
owner_id = "hKsGVXgQWd"
secret = "caf9850754119109448034765052eae71bac6d7f791e60e3b1c3aeb487ce1fb3"
version = "1.0"
BOT_TOKEN = "7599892515:AAFx6GXQJKL9pZDYXttyCFszxFFbUkNE5TA"
CHAT_ID = "7946491186"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/xxxxxxxxx/xxxxxxxxx"

# ✅ البيانات المطلوبة من جهاز المستخدم
class LicenseRequest(BaseModel):
    license_key: str
    pc_name: str
    hwid: str
    os_info: str
    ip: str

# إرسال لتليجرام
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        res = requests.post(url, data=data)
    except:
        pass

# إرسال لديسكورد
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

        license_key = data.license_key
        expiry = keyauthapp.user.expires
        local_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p (Local Time)')
        utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p (UTC)')

        expiry_dt = datetime.strptime(expiry, "%Y-%m-%d")
        now = datetime.now()
        remaining = expiry_dt - now
        rem_str = f"Ends in {remaining.days} days" if remaining.total_seconds() > 0 else "Expired"

        # ✅ الرسالة المرتبة بتنسيق Markdown
        msg = f"""🔐 *License Activated*

📅 *Activation Time:*
├ 🕒 *Local:* `{local_time}`
└ 🌐 *UTC:* `{utc_time}`

👤 *PC Name:* `{data.pc_name}`
🖥️ *HWID:* `{data.hwid}`
💻 *OS:* `{data.os_info}`
📍 *IP:* `{data.ip}`
🆔 *License:* `{license_key}`
🕒 *Expiry:* `{expiry}`
⌛ *Remaining:* `{rem_str}`
"""
        send_telegram(msg)
        send_discord(msg)

        return {"status": "success", "message": "Activated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
