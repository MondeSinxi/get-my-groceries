"""Woolworths scraper."""
from datetime import datetime
import logging
from pprint import pprint
import re
from typing import Union, Tuple

from bs4 import BeautifulSoup
from configs import Item
from .base import SiteScraper


logging.basicConfig(level=logging.DEBUG)

WOOLWORTHS_URL = "https://www.woolworths.co.za"

INITIAL_ROOT = "/cat/Food/Fruit-Vegetables-Salads/_/N-lllnam"

run_date = datetime.now().strftime("%Y-%m-%d")


class WoolworthsScraper(SiteScraper):
    """A Woolworths scraper."""

    def __init__(self):
        super().__init__("woolworths")

    def __len__(self):
        return len(self._grocery_items)

    def __getitem__(self, position):
        return self._grocery_items[position]

    def __call__(self):
        pprint(self._grocery_items)

    @property
    def grocery_items(self):
        """List of grocery Item types"""
        return self._grocery_items

    def extract_data(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """Gets BS components ad returns the product name and price"""
        product_items = soup.find_all("div", class_="product-list__item")
        results = [
            (
                p.find("div", class_="range--title").text,
                p.find("div", class_="product__price-field").text,
            )
            for p in product_items
        ]
        if not results:
            self.quit(results)
        return results

    def clean_price_string(self, price_text: str) -> Tuple[float, Union[float, None]]:
        """Parses price text to return original and base price"""
        discount_match = re.match(r"(R) ([0-9]+.[0-9]+)(R)([0-9]+.[0-9]+)", price_text)
        if discount_match:
            discounted_price = discount_match.group(2)
            original_price = discount_match.group(4)
            return (
                original_price,
                discounted_price,
            )
        discounted_price = None
        original_price = price_text.split()[1]
        return (original_price, discounted_price)

    def navigate(self, soup) -> Tuple[bool, str]:
        """Update navigation route"""
        nav_url_div = soup.find_all("div", class_="pagination__info")
        pagination_nav = [i.text for i in soup.find_all("span", class_="icon-text")]
        if "Next" not in pagination_nav:
            return (False, WOOLWORTHS_URL)

        # extract href
        updated_route = nav_url_div[-1]("a")[-1]["href"]
        return (True, WOOLWORTHS_URL + updated_route)

    def scrape_page(self, browser, url: str) -> BeautifulSoup:
        """Scrapes HTML to populate with PnP Items"""
        browser.get(url)
        page = browser.page_source
        # dump_page_source(page)
        soup = BeautifulSoup(page, "html.parser")
        results = self.extract_data(soup)
        clean_results = [(r[0], self.clean_price_string(r[1])) for r in results]

        # create document
        docs = [
            Item(
                item_name=item[0],
                original_price=item[1][0],
                discounted_price=item[1][1],
                store_name="woolworths",
                date=run_date,
            )
            for item in clean_results
        ]
        self.update_grocery_items(docs)
        return soup


if __name__ == "__main__":
    scraper = WoolworthsScraper()
    scraper.scrape_site(WOOLWORTHS_URL + INITIAL_ROOT)
