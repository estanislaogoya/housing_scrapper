import logging
import os

from sqlalchemy import create_engine, NullPool, orm  # type: ignore
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine  # type: ignore

logger = logging.getLogger()

class PostgresDbClient:
    logger = logging.getLogger(__name__)
    engine: Engine
    Session = None

    def __init__(self):
        try:
            self.engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(os.environ["PG_DB_USERNAME"], os.environ["PG_DB_PASSWORD"], os.environ["PG_DB_HOST"], os.environ[ "PG_DB_PORT"],os.environ[ "PG_DB_DATABASE"]))
            self.Session = sessionmaker(self.engine)
            print(f"session started: {self.Session}")
        except Exception as e:
            self.logger.error(e)
            raise Exception(
                f"There was an error constructing the DB class: {e}."
            ) from e

    def close_db(self) -> None:
        self.logger.info("Disposing DB engine and sessionmaker..")
        if self.engine:
            self.Session = None
            self.engine.dispose()
            self.engine = None