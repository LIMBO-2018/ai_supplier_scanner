"""
scrapers/base_scraper.py
Abstract base class for all marketplace scrapers.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from config.settings import HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


@dataclass
class ProductListing:
    """Represents a single product found on a marketplace."""
    marketplace: str
    title: str
    price: float           # USD
    currency: str = "USD"
    seller: str = "N/A"
    rating: Optional[float] = None
    link: str = ""
    trust_score: int = 0   # 0–100
    trust_label: str = "Unknown"
    payments: List[str] = field(default_factory=list)

    def price_str(self) -> str:
        return f"${self.price:.2f}" if self.price > 0 else "N/A"


class BaseScraper(ABC):
    """Base class every marketplace scraper must inherit."""

    name: str = "Unknown"
    search_url_template: str = ""
    trust_base: int = 50
    payments: List[str] = []
    currency: str = "USD"

    # ── Public API ────────────────────────────────────────────────────────────

    def search(self, query: str) -> List[ProductListing]:
        """
        Main entry point. Returns a list of ProductListings.
        Falls back to a single link-only listing if scraping fails.
        """
        encoded = quote_plus(query)
        search_link = self.search_url_template.format(query=encoded)

        listings: List[ProductListing] = []
        try:
            html = self._fetch(search_link)
            if html:
                listings = self._parse(html, query, search_link)
        except Exception as exc:
            logger.warning("[%s] scrape failed (%s). Using fallback link.", self.name, exc)

        if not listings:
            listings = [self._fallback_listing(query, search_link)]

        # Attach metadata
        for l in listings:
            l.marketplace = self.name
            l.payments = self.payments
            from core.trust_scorer import compute_trust
            l.trust_score, l.trust_label = compute_trust(self.name, l.rating)

        return listings

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _fetch(self, url: str) -> Optional[str]:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        if resp.status_code == 200:
            return resp.text
        logger.debug("[%s] HTTP %s for %s", self.name, resp.status_code, url)
        return None

    def _soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def _fallback_listing(self, query: str, link: str) -> ProductListing:
        return ProductListing(
            marketplace=self.name,
            title=f"Search results for '{query}'",
            price=0.0,
            seller="N/A",
            link=link,
        )

    # ── Abstract ──────────────────────────────────────────────────────────────

    @abstractmethod
    def _parse(self, html: str, query: str, search_url: str) -> List[ProductListing]:
        """Parse HTML and return listings. Must be implemented per marketplace."""
        ...

