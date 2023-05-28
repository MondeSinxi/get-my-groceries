import logging
import re
import sys
from typing import List, Tuple
from datetime import datetime
from pprint import pprint

from bs4 import BeautifulSoup

from configs import Item
from .base import SiteScraper


logging.basicConfig(level=logging.DEBUG)

PNP_URL = "https://www.pnp.co.za/"
URL_VEG_ROUTE = (
    "pnpstorefront/pnp/en/All-Products/Fresh-Food/Vegetables/c/vegetables703655157"
)

run_date = datetime.now().strftime("%Y-%m-%d")


class PnpScraper(SiteScraper):
    """Pick n Pay scraper"""

    def __init__(self):
        super().__init__("pick n pay")

    def __len__(self):
        return len(self._grocery_items)

    def __getitem__(self, position):
        return self._grocery_items[position]

    def __call__(self):
        pprint(self._grocery_items)

    @property
    def grocery_items(self) -> List[Item]:
        """Class property of grocery items."""
        return self._grocery_items

    def extract_data(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """Returns name and price from bs component."""
        product_items = soup.find_all("div", class_="productCarouselItemContainer")

        assert product_items, "No products found"
        results = [
            (
                p.find("div", class_="item-name").text,
                p.find("div", class_="item-price").text,
            )
            for p in product_items
        ]
        if results:
            return results
        logging.info("results from page empty: %s", results)
        self.close_browser()
        sys.exit("Empty results page")

    def navigate(self, soup):
        """Update navigation route"""
        nav_url_div = soup.find_all("li", class_="pagination-next")[0]("a")
        if nav_url_div:
            # extract href
            updated_route = nav_url_div[0]["href"]
            return (True, PNP_URL + updated_route)
        return (False, PNP_URL)

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

    def scrape_page(self, browser, url: str) -> BeautifulSoup:
        """Scrapes HTML to populate with PnP Items"""
        browser.get(url)

        page = browser.page_source
        soup = BeautifulSoup(page, "html.parser")
        results = self.extract_data(soup)
        clean_results = [(r[0], float(self.clean_price_string(r[1]))) for r in results]

        # # create document
        docs = [
            Item(item_name=item[0], original_price=item[1], date=run_date, store_name="pnp")
            for item in clean_results
        ]
        self.update_grocery_items(docs)
        return soup

    def clean_price_string(self, price_text: str) -> str:
        """Take the price string ad returns a cleaner reresentation"""
        match = re.match(r"(R)([0-9]+)([0-9][0-9])", price_text.strip())
        return match.group(2) + "." + match.group(3)


if __name__ == "__main__":
    scraper = PnpScraper()
    scraper.scrape_site(PNP_URL + URL_VEG_ROUTE)
