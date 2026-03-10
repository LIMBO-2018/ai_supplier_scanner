"""
scrapers/plati.py
Scraper for plati.market
"""
from __future__ import annotations

import logging
import re
from typing import List

from scrapers.base_scraper import BaseScraper, ProductListing
from config.settings import MAX_RESULTS_PER_MARKET

logger = logging.getLogger(__name__)


class PlatiScraper(BaseScraper):
    name = "Plati Market"
    search_url_template = "https://plati.market/search/{query}"
    trust_base = 65
    payments = ["Visa", "Mastercard", "Payeer", "USDT TRC20"]
    currency = "USD"

    def _parse(self, html: str, query: str, search_url: str) -> List[ProductListing]:
        soup = self._soup(html)
        listings: List[ProductListing] = []

        cards = (
            soup.select(".goods-item")
            or soup.select(".item-card")
            or soup.select(".goods_info")
            or soup.select("[class*='goods']")
            or soup.select("article")
        )

        for card in cards[:MAX_RESULTS_PER_MARKET]:
            try:
                title_el = (
                    card.select_one(".goods-title")
                    or card.select_one(".item_name")
                    or card.select_one("h3")
                    or card.select_one("h2")
                    or card.select_one(".title")
                    or card.select_one("a")
                )
                title = title_el.get_text(strip=True) if title_el else query

                price_el = (
                    card.select_one(".price-inner")
                    or card.select_one(".cost")
                    or card.select_one("[class*='price']")
                )
                price = _parse_price(price_el.get_text() if price_el else "")

                seller_el = (
                    card.select_one(".seller-name")
                    or card.select_one(".merchant")
                    or card.select_one("[class*='seller']")
                )
                seller = seller_el.get_text(strip=True) if seller_el else "N/A"

                rating_el = card.select_one("[class*='rating']")
                rating = _parse_rating(rating_el.get_text() if rating_el else "")

                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://plati.market" + href

                if title:
                    listings.append(ProductListing(
                        marketplace=self.name,
                        title=title,
                        price=price,
                        seller=seller,
                        rating=rating,
                        link=href or search_url,
                    ))
            except Exception as e:
                logger.debug("Plati card parse error: %s", e)

        return listings


def _parse_price(text: str) -> float:
    text = text.replace(",", "").replace(" ", "").replace("\xa0", "")
    m = re.search(r"([\d]+\.?\d*)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 0.0


def _parse_rating(text: str) -> float | None:
    m = re.search(r"([\d]+\.?\d*)", text)
    if m:
        try:
            val = float(m.group(1))
            return val if val <= 5 else val / 20  # normalise 100→5
        except ValueError:
            pass
    return None

