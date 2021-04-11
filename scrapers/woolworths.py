from .base import SiteScraper
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from pprint import pprint
import re
import sys
from typing import Union, Tuple

logging.basicConfig(level=logging.DEBUG)

WOOLWORTHS_URL = "https://www.woolworths.co.za"

INITIAL_ROOT = "/cat/Food/Fruit-Vegetables-Salads/_/N-lllnam"

run_date = datetime.now().strftime("%Y-%m-%d")


class WoolworthsScraper(SiteScraper):
    """A Woolworths scraper.
    """
    def __init__(self, backend_db="sqlite"):
        self._grocery_items = []
        super().__init__(backend_db=backend_db)

    def __repr__(self):
        return f"WoolworthsScraper('{self.backend_db}')"

    def __str__(self):
        return f"Woolworths scraper writing to {self.backend_db}"

    def __len__(self):
        return len(self._grocery_items)

    def __getitem__(self, position):
        return self._grocery_items[position]

    def __call__(self):
        pprint(self._grocery_items)

    @property
    def grocery_items(self):
        return self._grocery_items

    def extract_data(self, soup: BeautifulSoup) -> Tuple[str, str]:
        product_items = soup.find_all("div", class_="product-list__item")
        results = [
            (
                p.find("div", class_="range--title").text,
                p.find("div", class_="product__price-field").text,
            )
            for p in product_items
        ]
        if results:
            return results
        logging.info(f"results from page empty: {results}")
        self.close_browser()
        sys.exit("Empty results page")

    def clean_price_string(self, price_text: str) -> Tuple[float, Union[float, None]]:
        discount_match = re.match(
            r"(R) ([0-9]+.[0-9]+)(R)([0-9]+.[0-9]+)",
            price_text)
        if discount_match:
            discounted_price = discount_match.group(2)
            original_price = discount_match.group(4)
            return (original_price, discounted_price,)
        discounted_price = None
        original_price = price_text.split()[1]
        return (original_price, discounted_price)

    def navigate(self, soup) -> Tuple[bool, str]:
        # go to the next page
        nav_url_div = soup.find_all("div", class_="pagination__info")
        pagination_nav = [i.text for i in soup.find_all(
            "span", class_="icon-text"
        )]
        if "Next" not in pagination_nav:
            return (False, WOOLWORTHS_URL)

        # extract href
        updated_route = nav_url_div[-1]("a")[-1]["href"]
        return (True, WOOLWORTHS_URL + updated_route)

    def scrape_page(self, browser, URL: str) -> BeautifulSoup:
        browser.get(URL)
        page = browser.page_source
        # dump_page_source(page)
        soup = BeautifulSoup(page, "html.parser")
        results = self.extract_data(soup)
        clean_results = [
            (r[0], self.clean_price_string(r[1])) for r in results
        ]

        # create document
        docs = [
            {
                "name": item[0],
                "original_price": item[1][0],
                "discounted_price": item[1][1],
                "store": "woolworths",
                "date": run_date,
            }
            for item in clean_results
        ]
        self._grocery_items += docs
        self.load_to_db(docs)
        return soup


if __name__ == "__main__":
    scraper = WoolworthsScraper(backend_db="sqlite")
    scraper.scrape_site(WOOLWORTHS_URL + INITIAL_ROOT)
