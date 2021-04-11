import logging
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from utils import DataLoader

logging.basicConfig(level=logging.DEBUG)


class SiteScraper:
    """
    Object scrapes data from site and loads to selected database
    """

    _subclasses = {}

    def __init__(self, backend_db="sqlite"):
        self.backend_db = backend_db
        self.opts = Options()
        self.opts.headless = True
        assert self.opts.headless  # Operating in headless mode
        self.browser = Firefox(options=self.opts)

    @classmethod
    def register_scraper(cls, subcls):
        """
        Register class as scraper
        """
        if issubclass(subcls, cls):
            name = subcls.__name__[: -len("Scraper")].lower()
            cls._subclasses[name] = subcls

    @classmethod
    def select_scraper(cls, scraper, *args, **kwargs):
        """
        Returns registered scraper object
        """
        return cls._subclasses[scraper](*args, **kwargs)

    def load_to_db(self, data):
        """
        Loads data to database
        """
        data_loader = DataLoader(self.backend_db)
        loader = data_loader.loader()
        loader.load_data(data)

    def scrape_site(self, url: str) -> None:
        """
        Driver crawls through site and scrapes each page
        """
        state = {"next": False, "soup": ""}
        # intial run
        state["soup"] = self.scrape_page(self.browser, url)
        state["next"], url = self.navigate(state["soup"])
        while state["next"]:
            state["next"], url = self.navigate(state["soup"])
            if state["next"]:
                state["soup"] = self.scrape_page(self.browser, url)
            else:
                logging.info("scraping complete!")
        self.close_browser()

    def close_browser(self):
        logging.info(f"Closing connection...")
        self.browser.close()
        # sys.exit("Empty results page")
