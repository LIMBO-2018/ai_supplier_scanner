"""
main.py
AI Supplier Scanner – entry point.

Run:
    python main.py
"""
from __future__ import annotations

import logging
import sys

from telegram.ext import Application

from config.settings import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY
from bot.handlers import register_handlers

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scanner.log"),
    ],
)
logger = logging.getLogger(__name__)


# ── Startup checks ────────────────────────────────────────────────────────────

def _validate_config() -> None:
    errors = []
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set in .env")
    if not GEMINI_API_KEY:
        logger.warning(
            "GEMINI_API_KEY is not set – AI features will be disabled. "
            "Scanning will still work."
        )
    if errors:
        for e in errors:
            logger.critical(e)
        sys.exit(1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _validate_config()

    logger.info("=" * 50)
    logger.info("  AI Supplier Scanner – Starting up")
    logger.info("  Gemini AI: %s", "✓ enabled" if GEMINI_API_KEY else "✗ disabled")
    logger.info("=" * 50)

    app: Application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    register_handlers(app)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()

