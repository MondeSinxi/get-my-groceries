import pandas as pd
import pickle
from sqlalchemy import create_engine
from typing import List
from elasticsearch import Elasticsearch

class DataLoader(object):
    def __init__(self, backend_db):
        self.backend_db = backend_db

    def load_data(self, docs):
        if self.backend_db == "sqlite":
            LoadSqlite()
        elif self.backend_db == "mongodb":
            LoadMongo()
        elif self.backend_db == "elasticsearch":
            LoadElasticsearch()

class LoadSqlite(object):
    def __init__(self, connection_string="sqlite:///data/products.db"):
        self.engine = create_engine(connection_string, echo=True)

    def load_to_sqlite(self, data: List[dict]) -> pd.DataFrame:
        """
        load data into sqlite database
        """
        engine = create_engine("sqlite:///data/products.db", echo=True)
        df = pd.DataFrame(data)
        print(df)
        df.to_sql("stg_products", con=self.engine, if_exists="append", index=False)
        return df

class LoadMongo(object):
    def __init__(self, details):
        self.details = details

    def load_to_mongodb(self, data: List[dict]) -> pd.DataFrame:
        df = pd.DataFrame(data)
        return df


class LoadElasticsearch(object):
    def __init__(self, index="my-products"):
        self.index = index

    def load_to_elasticsearch(self, data: List[dict]) -> pd.DataFrame:
        es = Elasticsearch()
        for doc in data:
            print(doc)
            res = es.index(index=self.index, body=doc, doc_type="items")
            print(res['result'])

    @staticmethod
    def dump_page_source(self, page: str) -> None:
        """
        pickle page for later inspection
        """
        pickle.dump(page, open("data/page.pkl", "wb"))
        return
