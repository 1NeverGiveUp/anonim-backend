from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, hashlib, hmac
import requests

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

# CORS ruxsat
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram loginni tekshirish
@app.post("/api/auth")
async def auth(request: Request):
    data = await request.json()
    received_hash = data.pop("hash", "")
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data.items())])
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if calculated_hash != received_hash:
        return {"ok": False, "message": "Invalid login"}
    return {
        "ok": True,
        "user": {
            "id": data["id"],
            "username": data.get("username", "yo'q"),
            "first_name": data.get("first_name", ""),
        }
    }

# Xabar yuborish
@app.post("/api/message")
async def send_message(request: Request):
    data = await request.json()
    text = data.get("text")
    user = data.get("user")
    msg = f"📩 Yangi xabar:\n\n👤 @{user['username']}\n🆔 {user['id']}\n\n💬 {text}"
    requests.post(f"{BOT_URL}/sendMessage", json={"chat_id": "2117053743", "text": msg})
    return {"ok": True}
