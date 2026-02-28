import logging
from src.discord_watcher import DiscordWatcher

def setup_logging():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def main():

    setup_logging()

    watcher = DiscordWatcher()

    watcher.run()

if __name__ == "__main__":
    main()