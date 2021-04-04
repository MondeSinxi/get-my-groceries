from bs4 import BeautifulSoup
import logging
import pandas as pd
import re
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from utils import DataLoader, dump_page_source
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

PNP_URL = "https://www.pnp.co.za/"
URL_VEG_ROUTE = "pnpstorefront/pnp/en/All-Products/Fresh-Food/Vegetables/c/vegetables703655157"

run_date = datetime.now().strftime("%Y-%m-%d")

Item = tuple[str, str]


class ScrapePnp:
    def __init__(self, backend_db):
        self.backend_db = backend_db

    def extract_data(self, soup: BeautifulSoup) -> Item:
        product_items = soup.find_all("div", class_="productCarouselItemContainer")

        assert product_items, "No products found"
        results = [
            (
                p.find("div", class_="item-name").text,
                p.find("div", class_="item-price").text,
            )
            for p in product_items
        ]
        assert results, "results from page empty"

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
        clean_results = [(r[0], float(self.clean_price_string(r[1]))) for r in results]

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
        self.load_to_db(docs)
        return soup

    def load_to_db(self, data):
        data_loader = DataLoader(self.backend_db)
        loader = data_loader.loader()
        loader.load_data(data)


    def clean_price_string(self, price_text: str) -> str:
        m = re.match(r"(R)([0-9]+)([0-9][0-9])", price_text.strip())
        clean_price = m.group(2) +'.' + m.group(3)
        return clean_price


    def scrape_site(self, URL: str) -> None:
        opts = Options()
        opts.headless = True
        assert opts.headless  # Operating in headless mode
        browser = Firefox(options=opts)
        state = {'next': False, 'soup': ''}
        # intial run
        state['soup'] = self.scrape_page(browser, URL)
        state['next'], URL = self.navigate(state['soup'])
        while state['next']:
            state['next'], URL = self.navigate(state['soup'])
            if state['next']:
                state['soup'] = self.scrape_page(browser, URL)
            else:
                logging.info("scraping complete!")
        browser.close()
        return

if __name__ == "__main__":
    scraper = ScrapePnp("sqlite")
    scraper.scrape_site(PNP_URL + URL_VEG_ROUTE)
