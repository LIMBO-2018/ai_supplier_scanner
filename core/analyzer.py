"""
core/analyzer.py
Orchestrates scraping, ranking, and analysis across all marketplaces.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import logging
from typing import List, Optional, Tuple

from scrapers import ALL_SCRAPERS
from scrapers.base_scraper import ProductListing
from core.profit_calculator import calculate_profit, suggested_sell_price, ProfitResult

logger = logging.getLogger(__name__)


class ScanResult:
    """Full scan result for a single product query."""

    def __init__(
        self,
        query: str,
        listings: List[ProductListing],
        cheapest: Optional[ProductListing],
        best_value: Optional[ProductListing],
        profit: Optional[ProfitResult],
        suggested_price: float,
        ai_summary: str = "",
    ):
        self.query = query
        self.listings = listings
        self.cheapest = cheapest
        self.best_value = best_value
        self.profit = profit
        self.suggested_price = suggested_price
        self.ai_summary = ai_summary


def run_scan(query: str, sell_price: Optional[float] = None) -> ScanResult:
    """
    Run all scrapers concurrently and aggregate results.
    Returns a ScanResult ready for formatting.
    """
    logger.info("Starting scan for: %s", query)
    listings: List[ProductListing] = []

    # Run scrapers in a thread pool (avoid blocking event loop)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ALL_SCRAPERS)) as executor:
        futures = {executor.submit(scraper.search, query): scraper for scraper in ALL_SCRAPERS}
        for future in concurrent.futures.as_completed(futures, timeout=30):
            scraper = futures[future]
            try:
                results = future.result()
                listings.extend(results)
                logger.info("[%s] returned %d listings", scraper.name, len(results))
            except Exception as exc:
                logger.warning("[%s] failed: %s", scraper.name, exc)

    # De-duplicate by (marketplace, title)
    seen: set = set()
    unique: List[ProductListing] = []
    for l in listings:
        key = (l.marketplace, l.title[:40].lower())
        if key not in seen:
            seen.add(key)
            unique.append(l)

    # Find cheapest (must have a real price)
    priced = [l for l in unique if l.price > 0]
    cheapest = min(priced, key=lambda x: x.price) if priced else None

    # Best value = highest trust among lowest-price quintile
    best_value = _best_value(priced)

    # Profit
    profit: Optional[ProfitResult] = None
    suggested: float = 0.0
    if cheapest:
        suggested = suggested_sell_price(cheapest.price)
        profit = calculate_profit(cheapest.price, sell_price)

    return ScanResult(
        query=query,
        listings=unique,
        cheapest=cheapest,
        best_value=best_value,
        profit=profit,
        suggested_price=suggested,
    )


def _best_value(priced: List[ProductListing]) -> Optional[ProductListing]:
    if not priced:
        return None
    sorted_by_price = sorted(priced, key=lambda x: x.price)
    # Take bottom 40% by price
    cutoff = max(1, int(len(sorted_by_price) * 0.4))
    candidates = sorted_by_price[:cutoff]
    return max(candidates, key=lambda x: x.trust_score)

