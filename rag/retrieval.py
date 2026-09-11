from dataclasses import dataclass

from sqlalchemy import select

from rag.database import create_database_engine
from rag.embeddings import EmbeddingProvider
from rag.schema import knowledge_chunks


@dataclass(frozen=True)
class RetrievalResult:
    id: str
    document_id: str
    language: str
    title: str
    source_type: str
    source_slug: str | None
    source_path: str
    section: str
    subsection: str | None
    chunk_index: int
    content: str
    distance: float


def search_chunks(
    query: str,
    language: str,
    provider: EmbeddingProvider,
    limit: int = 5,
) -> list[RetrievalResult]:
    if language not in {"pl", "en"}:
        raise ValueError(
            "language must be 'pl' or 'en'"
        )

    if not query.strip():
        raise ValueError(
            "query cannot be empty"
        )

    if limit < 1:
        raise ValueError(
            "limit must be at least 1"
        )

    query_embedding = provider.embed_texts(
        [query]
    )[0]

    distance = (
        knowledge_chunks.c.embedding
        .cosine_distance(query_embedding)
        .label("distance")
    )

    statement = (
        select(
            knowledge_chunks.c.id,
            knowledge_chunks.c.document_id,
            knowledge_chunks.c.language,
            knowledge_chunks.c.title,
            knowledge_chunks.c.source_type,
            knowledge_chunks.c.source_slug,
            knowledge_chunks.c.source_path,
            knowledge_chunks.c.section,
            knowledge_chunks.c.subsection,
            knowledge_chunks.c.chunk_index,
            knowledge_chunks.c.content,
            distance,
        )
        .where(
            knowledge_chunks.c.language
            == language,
            knowledge_chunks.c.embedding
            .is_not(None),
        )
        .order_by(distance)
        .limit(limit)
    )

    engine = create_database_engine()

    with engine.connect() as connection:
        rows = connection.execute(
            statement
        ).mappings().all()

    return [
        RetrievalResult(
            id=row["id"],
            document_id=row["document_id"],
            language=row["language"],
            title=row["title"],
            source_type=row["source_type"],
            source_slug=row["source_slug"],
            source_path=row["source_path"],
            section=row["section"],
            subsection=row["subsection"],
            chunk_index=row["chunk_index"],
            content=row["content"],
            distance=float(row["distance"]),
        )
        for row in rows
    ]