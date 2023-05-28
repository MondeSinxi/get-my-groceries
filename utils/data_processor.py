"""Databases."""
from abc import ABC, abstractmethod
from dataclasses import asdict
import pickle
from typing import List

from loguru import logger
import pandas as pd
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch

from configs import Item


def dump_page_source(page: str) -> None:
    """
    pickle page for later inspection
    """
    with open("data/page.pkl", "wb") as pickle_file:
        pickle.dump(page, pickle_file)


class LoadToDB(ABC):
    """Interface that describes the data loader"""

    def __init__(self, database: str):
        self.databse = database

    @abstractmethod
    def load_data(self, data: List[Item]):
        """Loads data to the database"""

    @abstractmethod
    def show_data(self):
        """Show a sample of the data in the database"""


class LoadToSqlite(LoadToDB):
    """Loads data to sqlite"""

    def __init__(self, connection_string="sqlite:///data/products.db"):
        self.engine = create_engine(connection_string, echo=True)
        super().__init__(database="sqlite")

    def load_data(self, data: List[Item]):
        """
        load data into sqlite database
        """
        collated_data = pd.DataFrame(data)
        logger.info(collated_data)
        collated_data.to_sql(
            "stg_products", con=self.engine, if_exists="append", index=False
        )

    def show_data(self):
        pass


class LoadToMongo(LoadToDB):
    """Loads data to Mongo"""

    def __init__(self, details):
        self.details = details
        super().__init__(database="mongodb")

    def load_data(self, data: List[Item]):
        pass

    def show_data(self):
        pass


class LoadToElasticsearch(LoadToDB):
    """Loads data to ElasticSearch"""

    def __init__(self, index="my-products"):
        self.index = index
        super().__init__(database="elastic_search")

    def load_data(self, data: List[Item]) -> pd.DataFrame:
        elastic_search = Elasticsearch()
        for doc in data:
            logger.info(doc)
            res = elastic_search.index(index=self.index, document=asdict(doc))
            logger.info(res["result"])

    def show_data(self):
        pass
