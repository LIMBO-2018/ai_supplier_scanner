"""
config/settings.py
Central configuration for AI Supplier Scanner.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Credentials ──────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ── Scraper settings ─────────────────────────────────────────────────────────
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RESULTS_PER_MARKET: int = int(os.getenv("MAX_RESULTS_PER_MARKET", "5"))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ── Marketplace definitions ───────────────────────────────────────────────────
MARKETPLACES = {
    "GamsGo": {
        "base_url": "https://www.gamsgo.com",
        "search_url": "https://www.gamsgo.com/search?keyword={query}",
        "trust": "High",
        "payments": ["Crypto", "USDT TRC20", "Visa", "Mastercard", "PayPal"],
        "currency": "USD",
    },
    "GGsel": {
        "base_url": "https://ggsel.net",
        "search_url": "https://ggsel.net/en/catalog?q={query}",
        "trust": "High",
        "payments": ["Crypto", "USDT TRC20", "Visa", "Mastercard", "Payeer"],
        "currency": "USD",
    },
    "Plati Market": {
        "base_url": "https://plati.market",
        "search_url": "https://plati.market/search/{query}",
        "trust": "Medium",
        "payments": ["Visa", "Mastercard", "Payeer", "USDT TRC20"],
        "currency": "USD",
    },
    "Peakerr": {
        "base_url": "https://peakerr.com",
        "search_url": "https://peakerr.com/search?q={query}",
        "trust": "Medium",
        "payments": ["Crypto", "USDT TRC20", "PayPal"],
        "currency": "USD",
    },
    "CDkeys": {
        "base_url": "https://www.cdkeys.com",
        "search_url": "https://www.cdkeys.com/catalogsearch/result/?q={query}",
        "trust": "High",
        "payments": ["Visa", "Mastercard", "PayPal", "Crypto"],
        "currency": "USD",
    },
}

# ── Profit defaults ───────────────────────────────────────────────────────────
DEFAULT_MARGIN_PERCENT: float = 30.0   # suggested markup over cheapest price

# ── Trust scoring ─────────────────────────────────────────────────────────────
PLATFORM_TRUST_SCORES = {
    "GamsGo": 85,
    "GGsel": 82,
    "Plati Market": 65,
    "Peakerr": 60,
    "CDkeys": 90,
}

