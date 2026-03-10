"""
bot/handlers.py
All Telegram bot handlers – commands and free-text messages.
"""
from __future__ import annotations

import logging
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ai.gemini_client import (
    extract_product_keyword,
    generate_scan_summary,
    generate_profit_advice,
)
from bot.formatters import (
    format_error,
    format_help,
    format_scan_result,
    format_searching,
)
from core.analyzer import run_scan
from core.profit_calculator import calculate_profit, suggested_sell_price

logger = logging.getLogger(__name__)


# ── /start ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(format_help(), parse_mode=ParseMode.HTML)


# ── /help ─────────────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(format_help(), parse_mode=ParseMode.HTML)


# ── /search <product> ─────────────────────────────────────────────────────────

async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args).strip() if context.args else ""
    if not raw:
        await update.message.reply_text(
            "⚠️ Usage: <code>/search &lt;product name&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return
    await _do_scan(update, context, raw)


# ── /profit <product> <sell_price> ───────────────────────────────────────────

async def cmd_profit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: <code>/profit &lt;product&gt; &lt;sell_price&gt;</code>\n"
            "Example: <code>/profit ChatGPT Plus 18</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Last arg might be the price
    try:
        sell_price = float(context.args[-1])
        product = " ".join(context.args[:-1]).strip()
    except ValueError:
        await update.message.reply_text(
            format_error("Sell price must be a number. E.g. /profit ChatGPT Plus 18"),
            parse_mode=ParseMode.HTML,
        )
        return

    await _do_scan(update, context, product, sell_price=sell_price)


# ── Free-text message ─────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip() if update.message.text else ""
    if not text:
        return

    # Ignore commands accidentally caught here
    if text.startswith("/"):
        return

    # Use Gemini to clean up the product keyword
    keyword = extract_product_keyword(text)
    await _do_scan(update, context, keyword)


# ── Core scan flow ────────────────────────────────────────────────────────────

async def _do_scan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    query: str,
    sell_price: Optional[float] = None,
) -> None:
    """Run the scan, stream progress messages, then reply with results."""
    chat_id = update.effective_chat.id

    # Send "searching…" message
    waiting_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=format_searching(query),
        parse_mode=ParseMode.HTML,
    )

    try:
        # Run blocking scan in executor
        result = await context.application.create_task(
            _run_scan_async(query, sell_price)
        )

        # Build marketplace summary text for Gemini
        marketplace_text = _build_marketplace_text(result)

        # Generate AI summary & tip concurrently
        ai_summary = generate_scan_summary(query, marketplace_text)
        ai_tip = ""
        if result.cheapest and result.cheapest.price > 0:
            ai_tip = generate_profit_advice(
                query,
                result.cheapest.price,
                result.suggested_price,
            )

        result.ai_summary = ai_summary

        # Delete "searching…" message
        await waiting_msg.delete()

        # Send formatted result
        formatted = format_scan_result(result, ai_tip=ai_tip)
        # Telegram has 4096 char limit – split if needed
        for chunk in _split_message(formatted):
            await context.bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

    except Exception as exc:
        logger.exception("Scan failed for '%s': %s", query, exc)
        await waiting_msg.edit_text(
            format_error(f"Scan failed: {exc}"),
            parse_mode=ParseMode.HTML,
        )


async def _run_scan_async(query: str, sell_price: Optional[float]):
    """Wraps the blocking run_scan in an async-friendly way."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_scan, query, sell_price)


def _build_marketplace_text(result) -> str:
    lines = []
    for l in result.listings[:6]:
        price_str = f"${l.price:.2f}" if l.price > 0 else "N/A"
        lines.append(f"- {l.marketplace}: {l.title[:40]} | {price_str} | Trust: {l.trust_label}")
    return "\n".join(lines)


def _split_message(text: str, limit: int = 4000) -> list[str]:
    """Split long messages at newline boundaries."""
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return parts


# ── Register all handlers ─────────────────────────────────────────────────────

def register_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("profit", cmd_profit))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("All handlers registered.")

