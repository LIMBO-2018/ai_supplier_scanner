"""
scrapers/gamsgo.py
Scraper for gamsgo.com
"""
from __future__ import annotations

import logging
import re
from typing import List

from scrapers.base_scraper import BaseScraper, ProductListing
from config.settings import MAX_RESULTS_PER_MARKET

logger = logging.getLogger(__name__)


class GamsGoScraper(BaseScraper):
    name = "GamsGo"
    search_url_template = "https://www.gamsgo.com/search?keyword={query}"
    trust_base = 85
    payments = ["Crypto", "USDT TRC20", "Visa", "Mastercard", "PayPal"]
    currency = "USD"

    def _parse(self, html: str, query: str, search_url: str) -> List[ProductListing]:
        soup = self._soup(html)
        listings: List[ProductListing] = []

        # GamsGo renders product cards – try multiple selectors
        cards = (
            soup.select(".product-item")
            or soup.select(".goods-item")
            or soup.select("[class*='product']")
            or soup.select("article")
        )

        for card in cards[:MAX_RESULTS_PER_MARKET]:
            try:
                title_el = (
                    card.select_one(".product-name")
                    or card.select_one(".goods-name")
                    or card.select_one("h2")
                    or card.select_one("h3")
                    or card.select_one("a")
                )
                title = title_el.get_text(strip=True) if title_el else query

                price_el = (
                    card.select_one(".price")
                    or card.select_one("[class*='price']")
                    or card.select_one(".amount")
                )
                price = self._extract_price(price_el.get_text() if price_el else "")

                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.gamsgo.com" + href

                if title and (price > 0 or href):
                    listings.append(ProductListing(
                        marketplace=self.name,
                        title=title,
                        price=price,
                        link=href or search_url,
                    ))
            except Exception as e:
                logger.debug("GamsGo card parse error: %s", e)

        return listings

    @staticmethod
    def _extract_price(text: str) -> float:
        m = re.search(r"[\$€£]?\s*([\d,]+\.?\d*)", text.replace(",", ""))
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return 0.0

