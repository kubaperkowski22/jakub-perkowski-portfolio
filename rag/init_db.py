from sqlalchemy import create_engine, text

from rag.database import get_database_url
from rag.schema import metadata


def initialize_database() -> None:
    engine = create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                )
            )

            metadata.create_all(
                bind=connection
            )

    finally:
        engine.dispose()

    print(
        "Database initialized successfully."
    )


if __name__ == "__main__":
    initialize_database()