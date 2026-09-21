import os

from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from functools import lru_cache


load_dotenv()


def get_database_url() -> str:
    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set"
        )

    return normalize_database_url(
        database_url
    )


@lru_cache(maxsize=1)
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

def normalize_database_url(database_url: str,) -> str:
    if database_url.startswith(
        "postgresql+psycopg://"
    ):
        return database_url

    if database_url.startswith(
        "postgresql://"
    ):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    if database_url.startswith(
        "postgres://"
    ):
        return database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    return database_url