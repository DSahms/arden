"""
main_telegram.py — Start Business Sam with Telegram bridge.
Run this instead of main_base_assistant.py when you want phone access.

Usage:
    .venv\Scripts\python.exe main_telegram.py

Requirements:
    - TELEGRAM_BOT_TOKEN in assistant_config.yml or TELEGRAM_BOT_TOKEN env var
    - TELEGRAM_USER_ID in assistant_config.yml (your personal Telegram ID)
    - Desktop LLM backend running (LM Studio or Ollama)

Setup:
    1. Message @BotFather on Telegram → /newbot → copy the token
    2. Message @userinfobot on Telegram → copy your numeric user ID
    3. Add both to assistant_config.yml (see STEP 4 in setup guide)
    4. Start LM Studio or Ollama
    5. Run this file
"""

import logging
import os
from modules.base_assistant import PlainAssistant
from modules.telegram_bridge import TelegramBridge
from modules.utils import create_session_logger_id, setup_logging
from modules.assistant_config import get_config

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    # Get Telegram bot token — config file first, then environment variable
    token = get_config("telegram_bot_token", default=None) or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("\nERROR: No Telegram bot token found.")
        print("Add to assistant_config.yml:")
        print("  telegram_bot_token: 'YOUR_TOKEN_FROM_BOTFATHER'")
        print("\nOr set environment variable TELEGRAM_BOT_TOKEN")
        print("\nTo get a token: Open Telegram, message @BotFather, say /newbot")
        return

    # Get your personal Telegram user ID for security lockdown
    allowed_user_id = get_config("telegram_user_id", default=None) or os.environ.get("TELEGRAM_USER_ID")
    if not allowed_user_id:
        print("\nWARNING: No telegram_user_id set. Anyone who finds your bot can talk to Sam.")
        print("To lock it down, add your Telegram user ID to assistant_config.yml:")
        print("  telegram_user_id: 123456789")
        print("To find your ID: Message @userinfobot on Telegram\n")

    edition = get_config("edition", default="business")
    assistant_name = get_config("assistant_name", default="Sam")
    print(f"Starting Business Sam with Telegram bridge...")
    print(f"Edition: {edition}")
    print(f"Assistant name: {assistant_name}")

    # Initialize the desktop assistant (PlainAssistant = the actual runtime class)
    session_id = create_session_logger_id()
    assistant_logger = setup_logging(session_id)
    assistant = PlainAssistant(logger=assistant_logger, session_id=session_id)

    # Start Telegram bridge
    bridge = TelegramBridge(
        token=token,
        assistant=assistant,
        allowed_user_id=int(allowed_user_id) if allowed_user_id else None
    )

    print(f"Sam is online. Message your Telegram bot from your phone.")
    print("Press Ctrl+C to stop.\n")

    bridge.run()


if __name__ == "__main__":
    main()
