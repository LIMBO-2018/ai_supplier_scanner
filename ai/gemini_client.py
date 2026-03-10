"""
ai/gemini_client.py
Google Gemini AI integration – product detection, keyword extraction,
and intelligent scan summaries.
"""
from __future__ import annotations

import logging
from typing import Optional

import google.generativeai as genai

from config.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Initialise once
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

_MODEL_NAME = "gemini-1.5-flash"   # fast & cost-efficient


def _get_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(_MODEL_NAME)


# ── Product keyword extraction ────────────────────────────────────────────────

def extract_product_keyword(user_message: str) -> str:
    """
    Use Gemini to extract the cleanest product search keyword from a
    potentially messy user message.
    Returns the raw user message if Gemini is unavailable.
    """
    if not GEMINI_API_KEY:
        return user_message.strip()

    prompt = (
        "You are a product keyword extractor for a digital goods marketplace scanner.\n"
        "Extract the most specific product name / keyword from this user message.\n"
        "Return ONLY the product keyword – no explanations, no punctuation at the end.\n\n"
        f"User message: {user_message}"
    )
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        keyword = response.text.strip().strip('"').strip("'")
        logger.info("Gemini extracted keyword: '%s' from '%s'", keyword, user_message)
        return keyword or user_message.strip()
    except Exception as e:
        logger.warning("Gemini keyword extraction failed: %s", e)
        return user_message.strip()


# ── Scan summary generation ───────────────────────────────────────────────────

def generate_scan_summary(query: str, marketplace_data: str) -> str:
    """
    Generate an AI-written human-readable summary of the scan results.
    Falls back to empty string if unavailable.
    """
    if not GEMINI_API_KEY:
        return ""

    prompt = (
        "You are an expert digital product reseller advisor.\n"
        "Given the following marketplace scan results for a product, write a concise 2-3 sentence\n"
        "buying recommendation. Mention the best deal, any trust concerns, and resell potential.\n"
        "Be specific and helpful. Keep it under 60 words.\n\n"
        f"Product: {query}\n\n"
        f"Marketplace data:\n{marketplace_data}"
    )
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning("Gemini summary generation failed: %s", e)
        return ""


# ── Profit advice ─────────────────────────────────────────────────────────────

def generate_profit_advice(query: str, cost: float, suggested: float) -> str:
    """Short AI tip for resellers."""
    if not GEMINI_API_KEY:
        return ""

    prompt = (
        f"You are a digital product resale expert. The product is '{query}'.\n"
        f"Cost price: ${cost:.2f}. Suggested sell price: ${suggested:.2f}.\n"
        "Give ONE short actionable tip (max 25 words) to maximise profit on resale."
    )
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning("Gemini profit advice failed: %s", e)
        return ""

