"""
bot/formatters.py
Formats ScanResult objects into clean Telegram-ready messages.
"""
from __future__ import annotations

from typing import List, Optional
from scrapers.base_scraper import ProductListing
from core.analyzer import ScanResult
from core.trust_scorer import trust_emoji


MAX_LISTINGS_IN_SUMMARY = 8   # cap to keep message readable


def format_scan_result(result: ScanResult, ai_tip: str = "") -> str:
    """
    Produces the full Telegram message for a scan result.
    Uses HTML parse mode.
    """
    lines: List[str] = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines.append(f"🔍 <b>Scan Results: {_esc(result.query)}</b>")
    lines.append("─" * 32)

    # ── Listings ─────────────────────────────────────────────────────────────
    shown = result.listings[:MAX_LISTINGS_IN_SUMMARY]
    priced = [l for l in shown if l.price > 0]
    unpriced = [l for l in shown if l.price <= 0]
    all_shown = priced + unpriced   # priced first

    if not all_shown:
        lines.append("⚠️ No listings found. Try a different search term.")
        return "\n".join(lines)

    for idx, listing in enumerate(all_shown, 1):
        lines.append(format_listing(idx, listing))

    lines.append("─" * 32)

    # ── Cheapest / Best Value ─────────────────────────────────────────────────
    if result.cheapest:
        lines.append(
            f"🏆 <b>Cheapest:</b> {_esc(result.cheapest.marketplace)} "
            f"→ {result.cheapest.price_str()}"
        )
    if result.best_value and result.best_value != result.cheapest:
        lines.append(
            f"⭐ <b>Best Value:</b> {_esc(result.best_value.marketplace)} "
            f"→ {result.best_value.price_str()} "
            f"({trust_emoji(result.best_value.trust_label)} {result.best_value.trust_label} trust)"
        )

    # ── Profit section ────────────────────────────────────────────────────────
    if result.profit and result.profit.cost > 0:
        lines.append("")
        lines.append("💹 <b>Profit Analysis</b>")
        lines.append(result.profit.summary())
        lines.append(f"💡 Suggested Sell Price: <b>${result.suggested_price:.2f}</b>")

    # ── AI tip ────────────────────────────────────────────────────────────────
    if ai_tip:
        lines.append("")
        lines.append(f"🤖 <b>AI Tip:</b> {_esc(ai_tip)}")

    # ── AI summary ───────────────────────────────────────────────────────────
    if result.ai_summary:
        lines.append("")
        lines.append(f"📝 <b>Analysis:</b> {_esc(result.ai_summary)}")

    # ── Footer ────────────────────────────────────────────────────────────────
    lines.append("")
    lines.append("🔄 Send another product name to scan again.")

    return "\n".join(lines)


def format_listing(idx: int, listing: ProductListing) -> str:
    te = trust_emoji(listing.trust_label)
    price_str = listing.price_str()
    seller_str = f"  👤 Seller: {_esc(listing.seller)}\n" if listing.seller != "N/A" else ""
    rating_str = f"  ⭐ Rating: {listing.rating:.1f}/5\n" if listing.rating else ""
    payments_str = "  💳 " + " | ".join(listing.payments[:4]) + "\n" if listing.payments else ""
    link_str = f'  🔗 <a href="{listing.link}">View listing</a>\n' if listing.link else ""

    return (
        f"\n<b>{idx}. {_esc(listing.marketplace)}</b>\n"
        f"  📦 {_esc(listing.title[:60])}\n"
        f"  💵 Price: <b>{price_str}</b>\n"
        f"{seller_str}"
        f"{rating_str}"
        f"  {te} Trust: {listing.trust_label}\n"
        f"{payments_str}"
        f"{link_str}"
    )


def format_help() -> str:
    return (
        "👋 <b>Welcome to AI Supplier Scanner</b>\n\n"
        "I help digital product resellers find the best wholesale suppliers.\n\n"
        "<b>How to use:</b>\n"
        "1. Simply type any product name and I'll scan all major marketplaces.\n"
        "2. Use <code>/search &lt;product&gt;</code> for explicit searches.\n"
        "3. Use <code>/profit &lt;product&gt; &lt;sell_price&gt;</code> to calculate profit.\n\n"
        "<b>Supported Marketplaces:</b>\n"
        "• GamsGo  • GGsel  • Plati Market\n"
        "• Peakerr  • CDkeys\n\n"
        "<b>Commands:</b>\n"
        "/start – Show this message\n"
        "/search &lt;product&gt; – Scan marketplaces\n"
        "/profit &lt;product&gt; &lt;price&gt; – Profit calculator\n"
        "/help – Help guide"
    )


def format_searching(query: str) -> str:
    return (
        f"🔍 Scanning marketplaces for: <b>{_esc(query)}</b>\n\n"
        "⏳ Please wait, this takes 10-20 seconds…"
    )


def format_error(message: str) -> str:
    return f"❌ <b>Error:</b> {_esc(message)}\n\nPlease try again or type /help for guidance."


def _esc(text: str) -> str:
    """Minimal HTML escaping for Telegram HTML mode."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

