import os

from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine


load_dotenv()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set"
        )

    return database_url


def create_database_engine() -> Engine:
    engine = create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def register_vector_types(
        dbapi_connection,
        connection_record,
    ) -> None:
        register_vector(dbapi_connection)

    return engine