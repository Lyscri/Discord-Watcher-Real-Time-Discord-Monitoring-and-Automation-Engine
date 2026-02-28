import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    DISCORD_CHANNEL_URL = os.getenv("DISCORD_CHANNEL_URL")
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "5"))

    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN no configurado")

    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID no configurado")

    if not DISCORD_CHANNEL_URL:
        raise ValueError("DISCORD_CHANNEL_URL no configurado")