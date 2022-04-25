from .base import SiteScraper
from .woolworths import WoolworthsScraper
from .pnp import PnpScraper

SiteScraper.register_scraper(PnpScraper)
SiteScraper.register_scraper(WoolworthsScraper)
