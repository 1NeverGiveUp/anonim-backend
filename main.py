from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import hashlib
import hmac
import requests

# .env dan tokenni yuklash
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
MY_CHAT_ID = "2117053743"  # O'zingizning Telegram ID   

# FastAPI ilovasi
app = FastAPI()

# CORS ruxsatlari (barcha frontendlar uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Telegram login tekshiruvi
@app.post("/api/auth")
async def auth(request: Request):
    data = await request.json()
    print("📥 Auth request data:", data)

    received_hash = data.pop("hash", "")
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data.items())])
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != received_hash:
        print("❌ Invalid login hash")
        return {"ok": False, "message": "Invalid login"}

    user_data = {
        "id": data.get("id"),
        "username": data.get("username", "yoq"),
        "first_name": data.get("first_name", "")
    }
    print("✅ Authenticated user:", user_data)

    return {"ok": True, "user": user_data}

# 📩 Xabar yuborish endpointi
@app.post("/api/message")
async def send_message(request: Request):
    data = await request.json()
    print("📥 Message request:", data)

    text = data.get("text")
    user = data.get("user", {})

    if not text or not user:
        return {"ok": False, "message": "No text or user"}

    msg = f"📩 Yangi xabar:\n\n👤 @{user.get('username', 'yoq')}\n🆔 {user.get('id')}\n\n💬 {text}"

    try:
        response = requests.post(
            f"{BOT_URL}/sendMessage",
            json={"chat_id": MY_CHAT_ID, "text": msg}
        )
        if response.status_code == 200:
            print("✅ Xabar yuborildi")
            return {"ok": True}
        else:
            print("❌ Telegram API xatosi:", response.text)
            return {"ok": False, "message": "Telegram API error"}
    except Exception as e:
        print("❌ Xatolik:", e)
        return {"ok": False, "message": str(e)}
