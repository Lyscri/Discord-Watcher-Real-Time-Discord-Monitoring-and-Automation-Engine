import logging
import json
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from src.config import Config
from src.telegram_notifier import TelegramNotifier

STATE_FILE = "data/state.json"
BROWSER_DATA_DIR = "data/browser"

class DiscordWatcher:

    def __init__(self):
        self.last_message = self._load_state()

    # =========================
    # STATE MANAGEMENT
    # =========================

    def _load_state(self):
        try:
            if not os.path.exists(STATE_FILE):
                return None
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("last_message")
        except Exception as e:
            logging.error(f"Error loading state: {e}")
            return None

    def _save_state(self, message):
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {"last_message": message},
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    # =========================
    # BROWSER SETUP
    # =========================

    def _create_browser(self, playwright):
        os.makedirs(BROWSER_DATA_DIR, exist_ok=True)
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=True,  # ← Cambia a False si necesitas loguearte visualmente
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        return browser

    # =========================
    # LOGIN CHECK
    # =========================

    def _ensure_logged_in(self, page):
        logging.info("Opening Discord...")
        page.goto("https://discord.com/channels/@me")
        time.sleep(5)
        if "login" in page.url:
            logging.warning("Discord login required")
            logging.warning("Please login manually. After login, restart the script.")
            input("Press ENTER after login...")

    # =========================
    # GET LAST MESSAGE (CORREGIDO: Ahora está dentro de la clase)
    # =========================

    def _get_last_message(self, page):
        try:
            messages = page.query_selector_all("li[class*='messageListItem']")
            if not messages:
                return None

            for message in reversed(messages):
                thread_indicator = message.query_selector("div[class*='thread']")
                if thread_indicator:
                    continue 

                content = message.query_selector("div[class*='messageContent']")
                if content:
                    text = content.inner_text().strip()
                    if text:
                        return text
            return None
        except Exception as e:
            logging.error(f"Error reading messages: {e}")
            return None

    # =========================
    # MAIN LOOP (CORREGIDO: Indentación alineada)
    # =========================

    def run(self):
        logging.info("Starting Discord watcher...")
        with sync_playwright() as p:
            browser = self._create_browser(p)
            page = browser.pages[0] if browser.pages else browser.new_page()

            try:
                self._ensure_logged_in(page)
                logging.info(f"Opening target channel: {Config.DISCORD_CHANNEL_URL}")
                page.goto(Config.DISCORD_CHANNEL_URL, timeout=60000)
                time.sleep(5)
                logging.info("Monitoring started successfully")

                while True:
                    try:
                        current_message = self._get_last_message(page)
                        if current_message:
                            if self.last_message is None:
                                self.last_message = current_message
                                self._save_state(current_message)
                                logging.info("Initial message stored (no notification sent)")
                            
                            elif current_message != self.last_message:
                                logging.info(f"New message detected: {current_message}")
                                TelegramNotifier.send(current_message)
                                self.last_message = current_message
                                self._save_state(current_message)

                        time.sleep(Config.CHECK_INTERVAL)

                    except PlaywrightTimeoutError:
                        logging.warning("Timeout while reading page, retrying...")
                    except Exception as e:
                        logging.error(f"Monitoring error: {e}")
                        time.sleep(5)

            except Exception as e:
                logging.error(f"Fatal error: {e}")
            finally:
                browser.close()
                logging.info("Browser closed")