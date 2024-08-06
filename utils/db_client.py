import logging
import os

from sqlalchemy import create_engine, NullPool, orm  # type: ignore
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy import text

logger = logging.getLogger()

class PostgresDbClient:
    logger = logging.getLogger(__name__)
    engine: Engine
    Session = None

    def __init__(self):
        try:
            self.engine = create_engine(
                'postgresql://{}:{}@{}:{}/{}'.format(
                    os.environ["PG_DB_USERNAME"],
                    os.environ["PG_DB_PASSWORD"],
                    os.environ["PG_DB_HOST"],
                    os.environ["PG_DB_PORT"],
                    os.environ["PG_DB_DATABASE"]
                )
            )
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
            self.engine.dispose()
            self.engine = None
        self.Session = None
    

    def execute(self, query_content, query_params=None):
        # Ensure query_params is a dictionary
        if query_params is None:
            query_params = {}
        
        if query_content:
            session = self.Session()  # Create a Session instance
            try:
                results = session.execute(text(query_content), query_params)
                session.commit()
                return results
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed query execution: {e}")
                return None
            finally:
                session.close()  # Close the session after use
        else:
            self.logger.error("No query content provided to query executor")
            return None