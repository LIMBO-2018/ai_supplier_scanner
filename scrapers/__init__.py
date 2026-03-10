"""
scrapers/__init__.py
Registers all marketplace scrapers.
"""
from scrapers.gamsgo import GamsGoScraper
from scrapers.ggsel import GGselScraper
from scrapers.plati import PlatiScraper
from scrapers.peakerr import PeakerrScraper
from scrapers.cdkeys import CDkeysScraper

ALL_SCRAPERS = [
    GamsGoScraper(),
    GGselScraper(),
    PlatiScraper(),
    PeakerrScraper(),
    CDkeysScraper(),
]

