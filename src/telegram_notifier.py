import requests
import logging
from src.config import Config

class TelegramNotifier:

    BASE_URL = f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}"

    @staticmethod
    def send(message: str):

        try:

            response = requests.post(
                f"{TelegramNotifier.BASE_URL}/sendMessage",
                data={
                    "chat_id": Config.TELEGRAM_CHAT_ID,
                    "text": f"🔔 Nuevo empleo en Discord:\n\n{message}"
                },
                timeout=10
            )

            response.raise_for_status()

            logging.info("Notificación enviada")

        except Exception as e:
            logging.error(f"Error enviando Telegram: {e}")