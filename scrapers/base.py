"""Base class for all scrapers"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import logging
import sys

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

from configs import Item

logging.basicConfig(level=logging.DEBUG)


class SiteScraper(ABC):
    """
    Object scrapes data from site and loads to selected database
    """

    subclasses = {}

    def __init__(self, site_name: str):
        self.site_name = site_name
        self._grocery_items = []
        self.opts = Options()
        self.opts.headless = True
        assert self.opts.headless  # Operating in headless mode
        self.browser = Firefox(options=self.opts)

    @classmethod
    def register_scraper(cls, subcls):
        """
        Register class as scraper
        """
        if issubclass(subcls, cls):
            name = subcls.__name__[: -len("Scraper")].lower()
            cls.subclasses[name] = subcls

    @classmethod
    def select_scraper(cls, scraper, *args, **kwargs):
        """
        Returns registered scraper object
        """
        return cls.subclasses[scraper](*args, **kwargs)

    @abstractmethod
    def extract_data(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """Returns name and price from bs component."""

    @abstractmethod
    def navigate(self, soup: BeautifulSoup) -> Tuple[bool, str]:
        """Update navigation route returning True if there is a next page and url of that route"""

    @abstractmethod
    def scrape_page(self, browser, url: str) -> BeautifulSoup:
        """Scrapes HTML to populate with PnP Items"""

    @abstractmethod
    @property
    def grocery_items(self) -> List[Item]:
        """Class property of grocery items."""

    def scrape_site(self, url: str) -> List[Item]:
        """
        Driver crawls through site and scrapes each page
        """
        docs = []
        state = {"next": False, "soup": self.scrape_page(self.browser, url)}
        state["next"], url = self.navigate(state["soup"])
        while state["next"]:
            state["next"], url = self.navigate(state["soup"])
            if state["next"]:
                state["soup"], doc = self.scrape_page(self.browser, url)
                docs = [*docs, *doc]
            else:
                logging.info("scraping complete!")
        self.close_browser()
        return docs

    def update_grocery_items(self, docs: List[Item]) -> None:
        """Updates the grocery items property"""
        self._grocery_items += docs

    def close_browser(self):
        """Closes the connection to the browser"""
        logging.info("Closing connection...")
        self.browser.close()
        # sys.exit("Empty results page")

    def quit(self, results):
        """Exits scraping when no results are found"""
        logging.info("results from page empty: %s", results)
        self.close_browser()
        sys.exit("Empty results page")
