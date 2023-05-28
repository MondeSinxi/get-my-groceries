"""Command line utility for running scrapers."""
import logging
import click
import scrapers
from utils import data_processor

subclasses = scrapers.SiteScraper.subclasses

URLS = {
    "pnp": "https://www.pnp.co.za/"
    "pnpstorefront/pnp/en/All-Products/Fresh-Food/Vegetables/c/vegetables703655157",
    "woolworths": "https://www.woolworths.co.za/"
    "cat/Food/Fruit-Vegetables-Salads/_/N-lllnam",
}

pass_state = click.make_pass_decorator(dict, ensure=True)


@click.group(chain=True)
@click.command()
@click.option(
    "--store",
    default="pnp",
    help=f"select the store to scrape: {list(subclasses.keys())}",
)
@pass_state
def scrape(state, store):
    """ "Scrapes the chosen site."""
    try:
        scraper_cls = subclasses[store]
        scraper_obj = scraper_cls()
        state["docs"] = scraper_obj.scrape_site(URLS[store])
    except KeyError:
        logging.error("No scraper for store: %s", store)


@scrape.command(name="save")
@click.option(
    "--backend_db",
    default="sqlite",
    help="database used to store data",
)
@pass_state
def load_data(state, backend):
    """Saves scraped data to the chosen database"""
    if backend == "sqlite":
        loader = data_processor.LoadToSqlite()
    loader.load_data(state["docs"])
