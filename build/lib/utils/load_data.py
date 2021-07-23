import pandas as pd
import pickle
from sqlalchemy import create_engine
from typing import List
from elasticsearch import Elasticsearch


def dump_page_source(page: str) -> None:
    """
    pickle page for later inspection
    """
    pickle.dump(page, open("data/page.pkl", "wb"))
    return


class DataLoader(object):
    def __init__(self, backend_db):
        self.backend_db = backend_db

    def loader(self):
        if self.backend_db == "sqlite":
            return LoadSqlite()
        elif self.backend_db == "mongodb":
            return LoadMongo()
        elif self.backend_db == "elasticsearch":
            return LoadElasticsearch()


class LoadSqlite(object):
    def __init__(self, connection_string="sqlite:///data/products.db"):
        self.engine = create_engine(connection_string, echo=True)

    def load_data(self, data: List[dict]) -> pd.DataFrame:
        """
        load data into sqlite database
        """
        df = pd.DataFrame(data)
        print(df)
        df.to_sql("stg_products", con=self.engine, if_exists="append", index=False)
        return df


class LoadMongo(object):
    def __init__(self, details):
        self.details = details

    def load_data(self, data: List[dict]) -> pd.DataFrame:
        return pd.DataFrame(data)


class LoadElasticsearch(object):
    def __init__(self, index="my-products"):
        self.index = index

    def load_data(self, data: List[dict]) -> pd.DataFrame:
        es = Elasticsearch()
        for doc in data:
            print(doc)
            res = es.index(index=self.index, body=doc, doc_type="items")
            print(res["result"])
