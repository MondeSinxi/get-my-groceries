import click
import logging
import scrapers

subclasses = scrapers.SiteScraper._subclasses

URLS = {
    "pnp": "https://www.pnp.co.za/"
    "pnpstorefront/pnp/en/All-Products/Fresh-Food/Vegetables/c/vegetables703655157",
    "woolworths": "https://www.woolworths.co.za/"
    "cat/Food/Fruit-Vegetables-Salads/_/N-lllnam",
}


@click.command()
@click.option(
    "--store",
    default="pnp",
    help=f"select the store to scrape: {list(subclasses.keys())}",
)
@click.option(
    "--backend_db", 
    default="sqlite", 
    help="database used to store data",
)
def scrape(store, backend_db):
    try:
        scraper_cls = subclasses[store]
        scraper_obj = scraper_cls(backend_db=backend_db)
        scraper_obj.scrape_site(URLS[store])
    except KeyError:
        logging.error(f"No scraper for store: {store}")


if __name__ == "__main__":
    scrape()
