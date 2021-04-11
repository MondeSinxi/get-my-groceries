from .base import SiteScraper
from bs4 import BeautifulSoup
import logging
from pprint import pprint
import re
from typing import Tuple
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

PNP_URL = "https://www.pnp.co.za/"
URL_VEG_ROUTE = "pnpstorefront/pnp/en/All-Products/Fresh-Food/Vegetables/c/vegetables703655157"

run_date = datetime.now().strftime("%Y-%m-%d")

Item = tuple[str, str]


class PnpScraper(SiteScraper):
    def __init__(self, backend_db='sqlite'):
        self._grocery_items = []
        super().__init__(backend_db=backend_db)

    def __repr__(self):
        return f"PnPScraper('{self.backend_db}')"

    def __str__(self):
        return f"PnP Sraper writing to {self.backend_db}"

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
        product_items = soup.find_all("div",
                                      class_="productCarouselItemContainer")

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
        logging.info(f"results from page empty: {results}")
        return results

    def navigate(self, soup):
        # go to the next page
        nav_url_div = soup.find_all("li", class_="pagination-next")[0]("a")
        if nav_url_div:
            # extract href
            updated_route = nav_url_div[0]['href']
            return (True, PNP_URL + updated_route)
        else:
            return (False, PNP_URL)

    def scrape_page(self, browser, URL):
        browser.get(URL)

        page = browser.page_source
        soup = BeautifulSoup(page, "html.parser")
        results = self.extract_data(soup)
        clean_results = [(r[0], float(self.clean_price_string(r[1])))
                         for r in results]

        # # create document
        docs = [
            {
                "name": item[0],
                "original_price": item[1],
                "discounted_price": "not yet implemented",
                "store": "pick n pay",
                "date": run_date,
            }
            for item in clean_results
        ]
        self._grocery_items += docs
        self.load_to_db(docs)
        return soup

    def clean_price_string(self, price_text: str) -> str:
        m = re.match(r"(R)([0-9]+)([0-9][0-9])", price_text.strip())
        return m.group(2) + '.' + m.group(3)


if __name__ == "__main__":
    scraper = PnpScraper("sqlite")
    scraper.scrape_site(PNP_URL + URL_VEG_ROUTE)
