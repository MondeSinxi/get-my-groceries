from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import utils
from datetime import datetime

PNP_URL = "https://www.pnp.co.za/"
URL_VEG_ROUTE = "pnpstorefront/pnp/en/All-Products/Fresh-Food/Vegetables/c/vegetables703655157"

run_date = datetime.now().strftime("%Y-%m-%d")

Item = tuple[str, str]

def extract_pnp_data(soup: BeautifulSoup) -> Item:
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


def navigate(soup):
    # go to the next page
    nav_url_div = soup.find_all("li", class_="pagination-next")[0]("a")
    print(nav_url_div)
    if nav_url_div:
    # extract href
        updated_route = nav_url_div[0]['href']
        return (True, PNP_URL + updated_route)
    else:
        return (False, PNP_URL)


def scrape_page(browser, URL, backend_db, test=False):
    browser.get(URL)

    page = browser.page_source

    if test:
        utils.dump_page_source(page)
        return
    soup = BeautifulSoup(page, "html.parser")
    results = extract_pnp_data(soup)
    clean_results = [(r[0], float(clean_price_string_pnp(r[1]))) for r in results]

    # # create document
    docs = [
        {
            "name": item[0],
            "price": item[1],
            "store": "pick n pay",
            "date": run_date,
        }
        for item in clean_results
    ]
    if backend_db == 'sqlite':
        utils.load_to_sqlite(docs)
    elif backend_db == 'mongodb':
        utils.load_to_mongodb(docs)

    return soup


def clean_price_string_pnp(price_text: str) -> str:
    m = re.match(r"(R)([0-9]+)([0-9][0-9])", price_text.strip())
    clean_price = m.group(2) +'.' + m.group(3)
    return clean_price


def scrape_pnp_site(URL: str, backend_db="sqlite") -> None:
    opts = Options()
    opts.headless = True
    assert opts.headless  # Operating in headless mode
    browser = Firefox(options=opts)
    state = {'next': False, 'soup': ''}
    # intial run
    state['soup'] = scrape_page(browser, URL, backend_db, test=False)
    state['next'], URL = navigate(state['soup'])
    while state['next']:
        state['next'], URL = navigate(state['soup'])
        if state['next']:
            state['soup'] = scrape_page(browser, URL, backend_db)
        else:
            print("scraping complete!")
    browser.close()

    return

if __name__ == "__main__":
    scrape_pnp_site(PNP_URL + URL_VEG_ROUTE, backend_db="sqlite")
