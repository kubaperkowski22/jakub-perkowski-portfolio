from pathlib import Path

from sqlalchemy import delete, insert

from rag.chunker import chunk_documents
from rag.database import create_database_engine
from rag.embeddings import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    build_embedding_text,
)
from rag.loader import load_knowledge_base
from rag.models import KnowledgeChunk
from rag.schema import knowledge_chunks


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

EMBEDDING_BATCH_SIZE = 50


def embed_chunks(
    chunks: list[KnowledgeChunk],
    provider: EmbeddingProvider,
) -> list[list[float]]:
    embeddings: list[list[float]] = []

    for start in range(
        0,
        len(chunks),
        EMBEDDING_BATCH_SIZE,
    ):
        batch = chunks[
            start:start + EMBEDDING_BATCH_SIZE
        ]

        texts = [
            build_embedding_text(chunk)
            for chunk in batch
        ]

        batch_embeddings = provider.embed_texts(
            texts
        )

        embeddings.extend(batch_embeddings)

        print(
            f"Embedded "
            f"{min(start + len(batch), len(chunks))}"
            f"/{len(chunks)} chunks"
        )

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            "Embedding count does not match chunk count"
        )

    return embeddings


def chunk_to_row(
    chunk: KnowledgeChunk,
    embedding: list[float],
) -> dict:
    return {
        "id": chunk.id,
        "document_id": chunk.document_id,
        "language": chunk.language,
        "title": chunk.title,
        "source_type": chunk.source_type,
        "source_slug": chunk.source_slug,
        "source_path": chunk.source_path,
        "section": chunk.section,
        "subsection": chunk.subsection,
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "embedding": embedding,
    }


def ingest_knowledge_base() -> None:
    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    chunks = chunk_documents(documents)

    if not chunks:
        raise RuntimeError(
            "Knowledge base produced no chunks"
        )

    provider = OpenAIEmbeddingProvider()

    embeddings = embed_chunks(
        chunks,
        provider,
    )

    rows = [
        chunk_to_row(chunk, embedding)
        for chunk, embedding
        in zip(
            chunks,
            embeddings,
            strict=True,
        )
    ]

    engine = create_database_engine()

    with engine.begin() as connection:
        connection.execute(
            delete(knowledge_chunks)
        )

        connection.execute(
            insert(knowledge_chunks),
            rows,
        )

    print(
        f"Ingested {len(chunks)} chunks "
        f"from {len(documents)} documents."
    )


if __name__ == "__main__":
    ingest_knowledge_base()