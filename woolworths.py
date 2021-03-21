from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from utils import load_data, dump_page_source
from datetime import datetime
import logging
import re
from typing import Union, Tuple

logging.basicConfig(level=logging.DEBUG)

WOOLWORTHS_URL = "https://www.woolworths.co.za"

INITIAL_ROOT = "/cat/Food/Fruit-Vegetables-Salads/_/N-lllnam"

Item = tuple[str, str]

run_date = datetime.now().strftime("%Y-%m-%d")


def extract_woolworths_data(soup: BeautifulSoup) -> Item:
    product_items = soup.find_all("div", class_="product-list__item")
    results = [
        (
            p.find("div", class_="range--title").text,
            p.find("div", class_="product__price-field").text,
        )
        for p in product_items
    ]
    assert results, r"results from page empty: {results}"

    return results


def clean_price_string_woolworths(price_text: str) -> Tuple[float, Union[float, None]]:
    discount_match = re.match(r"(R) ([0-9]+.[0-9]+)(R)([0-9]+.[0-9]+)", price_text)
    if discount_match:
        discounted_price = discount_match.group(2)
        original_price = discount_match.group(4)
        return (original_price, discounted_price,)
    else:
        discounted_price = None
        original_price = price_text.split()[1]
        return (original_price, discounted_price)


def navigate(soup) -> Tuple[bool, str]:
    # go to the next page
    nav_url_div = soup.find_all("div", class_="pagination__info")
    pagination_nav = [i.text for i in soup.find_all("span", class_="icon-text")]
    if "Next" in pagination_nav:
        # extract href
        updated_route = nav_url_div[-1]("a")[-1]["href"]
        return (True, WOOLWORTHS_URL + updated_route)
    else:
        return (False, WOOLWORTHS_URL)


def scrape_page(browser, URL: str, backend_db: str) -> BeautifulSoup:
    browser.get(URL)
    page = browser.page_source
    dump_page_source(page)
    soup = BeautifulSoup(page, "html.parser")
    results = extract_woolworths_data(soup)
    clean_results = [(r[0], clean_price_string_woolworths(r[1])) for r in results]

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
    load_data(docs, backend_db)
    return soup


def scrape_woolworths_site(URL: str, backend_db="sqlite") -> None:
    opts = Options()
    opts.headless = True
    assert opts.headless  # Operating in headless mode
    browser = Firefox(options=opts)

    state = {"next": False, "soup": ""}
    # intial run
    state["soup"] = scrape_page(browser, URL, backend_db)
    state["next"], URL = navigate(state["soup"])
    while state["next"]:
        state["next"], URL = navigate(state["soup"])
        if state["next"]:
            state["soup"] = scrape_page(browser, URL, backend_db)
        else:
            print("scraping complete!")
    browser.close()

    return


if __name__ == "__main__":
    scrape_woolworths_site(WOOLWORTHS_URL + INITIAL_ROOT, backend_db="elasticsearch")
