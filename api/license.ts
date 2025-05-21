import type { VercelRequest, VercelResponse } from '@vercel/node';
import { KeyAuth } from "../lib/ky"; // ✅ عدّله على حسب مكان الملف فعليًا

import os from 'os'
import crypto from 'crypto'
import axios from 'axios'

const BOT_TOKEN = "7599892515:AAFx6GXQJKL9pZDYXttyCFszxFFbUkNE5TA";
const CHAT_ID = "7946491186";
const DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1374580285395697775/imQe4kz7eB_IzxiXDpCll-IxQf6JG3cXfl5_isQHMyrz87VRtUhl5c-h2-v87CMxnky9";

function getChecksum(): string {
  const str = '3586efa889b0d63c05484ef8fea3cecb35459af1c8564954a8e49c99a4812347' // لأنه مفيش __file__ في Vercel
  return crypto.createHash("sha256").update(str).digest("hex")
}

function formatExpiry(unix?: number) {
  if (!unix) return "Unknown"
  return new Date(unix * 1000).toLocaleString("en-US", { hour12: true })
}

function getTimeLeft(unix?: number) {
  if (!unix) return "غير متاح"
  const now = new Date()
  const expiry = new Date(unix * 1000)
  const diff = expiry.getTime() - now.getTime()
  if (diff <= 0) return "Expired"
  const mins = Math.floor(diff / 60000) % 60
  const hours = Math.floor(diff / 3600000) % 24
  const days = Math.floor(diff / 86400000)
  return `Ends in ${days}d ${hours}h ${mins}m`
}

async function sendTelegram(msg: string) {
  await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
    chat_id: CHAT_ID,
    text: msg,
    parse_mode: "Markdown"
  })
}

async function sendDiscord(msg: string) {
  await axios.post(DISCORD_WEBHOOK, { content: msg })
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") return res.status(405).json({ error: "Only POST allowed" })
  
  const { license_key } = req.body
  if (!license_key) return res.status(400).json({ error: "Missing license_key" })

  const KeyAuthApp = new KeyAuth({
    name: "123",
    ownerid: "hKsGVXgQWd",
    version: "1.0"
  })

  try {
    await KeyAuthApp.init()
    await KeyAuthApp.license(license_key)

    const user = KeyAuthApp.user_data
    const hwid = os.hostname()
    const os_info = `${os.platform()} ${os.release()}`
    const rawExpiry = parseInt(user.subscriptions?.[0]?.expiry || "0")

    const msg = `🔐 **[License Activated]**

📅 **Activation Time:**
   ├ 🕒 Local: ${new Date().toLocaleString()}
   └ 🌐 UTC: ${new Date().toUTCString()}

👤 **PC Name:** \`${hwid}\`
🖥️ **HWID:** \`${hwid}\`
💻 **OS:** ${os_info}
📍 **IP:** ${user.ip || "Unknown"}
🆔 **License:** \`${user.username}\`
🕒 **Expiry:** ${formatExpiry(rawExpiry)}
⌛ **Remaining:** ${getTimeLeft(rawExpiry)}`

    await sendTelegram(msg)
    await sendDiscord(msg)

    res.status(200).json({ status: "success", message: "License activated", user })
  } catch (err: any) {
    res.status(400).json({ status: "error", message: err.message || "Activation failed" })
  }
}
