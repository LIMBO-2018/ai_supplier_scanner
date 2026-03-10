"""
scrapers/cdkeys.py
Scraper for cdkeys.com
"""
from __future__ import annotations

import logging
import re
from typing import List

from scrapers.base_scraper import BaseScraper, ProductListing
from config.settings import MAX_RESULTS_PER_MARKET

logger = logging.getLogger(__name__)


class CDkeysScraper(BaseScraper):
    name = "CDkeys"
    search_url_template = "https://www.cdkeys.com/catalogsearch/result/?q={query}"
    trust_base = 90
    payments = ["Visa", "Mastercard", "PayPal", "Crypto"]
    currency = "USD"

    def _parse(self, html: str, query: str, search_url: str) -> List[ProductListing]:
        soup = self._soup(html)
        listings: List[ProductListing] = []

        cards = (
            soup.select(".product-item-info")
            or soup.select(".product-item")
            or soup.select(".item.product")
            or soup.select("[class*='product-item']")
        )

        for card in cards[:MAX_RESULTS_PER_MARKET]:
            try:
                title_el = (
                    card.select_one(".product-item-name")
                    or card.select_one(".product-name")
                    or card.select_one("h2")
                    or card.select_one("h3")
                    or card.select_one("a.product-item-link")
                )
                title = title_el.get_text(strip=True) if title_el else query

                price_el = (
                    card.select_one(".price")
                    or card.select_one("[class*='price']")
                    or card.select_one(".special-price")
                )
                price = _parse_price(price_el.get_text() if price_el else "")

                rating_el = card.select_one(".rating-result") or card.select_one("[class*='rating']")
                rating = _parse_rating(rating_el) if rating_el else None

                link_el = card.select_one("a.product-item-link") or card.select_one("a[href]")
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.cdkeys.com" + href

                if title:
                    listings.append(ProductListing(
                        marketplace=self.name,
                        title=title,
                        price=price,
                        rating=rating,
                        link=href or search_url,
                    ))
            except Exception as e:
                logger.debug("CDkeys card parse error: %s", e)

        return listings


def _parse_price(text: str) -> float:
    text = text.replace(",", "").strip()
    m = re.search(r"[\$£€]?\s*([\d]+\.?\d*)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 0.0


def _parse_rating(el) -> float | None:
    # CDkeys uses title attribute like "60%" or inner text
    title = el.get("title", "") or el.get_text()
    m = re.search(r"([\d]+\.?\d*)%", title)
    if m:
        try:
            return float(m.group(1)) / 20  # convert 100% scale to 5-star
        except ValueError:
            pass
    m2 = re.search(r"([\d]+\.?\d*)", title)
    if m2:
        try:
            val = float(m2.group(1))
            return val if val <= 5 else val / 20
        except ValueError:
            pass
    return None

