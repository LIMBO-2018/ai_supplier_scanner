"""
scrapers/ggsel.py
Scraper for ggsel.net
"""
from __future__ import annotations

import logging
import re
from typing import List

from scrapers.base_scraper import BaseScraper, ProductListing
from config.settings import MAX_RESULTS_PER_MARKET

logger = logging.getLogger(__name__)


class GGselScraper(BaseScraper):
    name = "GGsel"
    search_url_template = "https://ggsel.net/en/catalog?q={query}"
    trust_base = 82
    payments = ["Crypto", "USDT TRC20", "Visa", "Mastercard", "Payeer"]
    currency = "USD"

    def _parse(self, html: str, query: str, search_url: str) -> List[ProductListing]:
        soup = self._soup(html)
        listings: List[ProductListing] = []

        cards = (
            soup.select(".goods__item")
            or soup.select(".catalog-item")
            or soup.select(".product-card")
            or soup.select("[class*='item']")
        )

        for card in cards[:MAX_RESULTS_PER_MARKET]:
            try:
                title_el = (
                    card.select_one(".goods__item-name")
                    or card.select_one(".item-name")
                    or card.select_one("h3")
                    or card.select_one("h2")
                    or card.select_one(".title")
                )
                title = title_el.get_text(strip=True) if title_el else query

                price_el = (
                    card.select_one(".goods__item-price")
                    or card.select_one(".price")
                    or card.select_one("[class*='price']")
                )
                price = _parse_price(price_el.get_text() if price_el else "")

                link_el = card.select_one("a[href]")
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://ggsel.net" + href

                if title:
                    listings.append(ProductListing(
                        marketplace=self.name,
                        title=title,
                        price=price,
                        link=href or search_url,
                    ))
            except Exception as e:
                logger.debug("GGsel card parse error: %s", e)

        return listings


def _parse_price(text: str) -> float:
    text = text.replace(",", "").replace(" ", "")
    m = re.search(r"[\$€£]?\s*([\d]+\.?\d*)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 0.0

