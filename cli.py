from click
from scrapers import SiteScrapers

scrapers = SiteScrapers._subclasses

PNP_URL = "https://www.pnp.co.za/"
PNP_URL_VEG_ROUTE = "pnpstorefront/pnp/en/All-Products/Fresh-Food/Vegetables/c/vegetables703655157"

WOOLWORTHS_URL = "https://www.woolworths.co.za"
INITIAL_ROOT = "/cat/Food/Fruit-Vegetables-Salads/_/N-lllnam"


@click.command()
@click.argument("store")
@click.option("--backend_db", default="sqlite", help="database used to store data")
def scrape(store, backend_db):
    click.echo("Preparing to scrape site")


