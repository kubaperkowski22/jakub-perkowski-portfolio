from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector


metadata = MetaData()


knowledge_chunks = Table(
    "knowledge_chunks",
    metadata,

    Column(
        "id",
        Text,
        primary_key=True,
    ),

    Column(
        "document_id",
        Text,
        nullable=False,
    ),

    Column(
        "language",
        String,
        nullable=False,
    ),

    Column(
        "title",
        Text,
        nullable=False,
    ),

    Column(
        "source_type",
        String,
        nullable=False,
    ),

    Column(
        "source_slug",
        Text,
        nullable=True,
    ),

    Column(
        "source_path",
        Text,
        nullable=False,
    ),

    Column(
        "section",
        Text,
        nullable=False,
    ),

    Column(
        "subsection",
        Text,
        nullable=True,
    ),

    Column(
        "chunk_index",
        Integer,
        nullable=False,
    ),

    Column(
        "content",
        Text,
        nullable=False,
    ),

    Column(
        "ingested_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),

    Column(
        "embedding",
        Vector(1536),
        nullable=True,
    ),

    UniqueConstraint(
        "document_id",
        "language",
        "chunk_index",
        name="uq_knowledge_chunk_position",
    ),

    CheckConstraint(
        "language IN ('pl', 'en')",
        name="ck_knowledge_chunks_language",
    ),

    CheckConstraint(
        "chunk_index >= 0",
        name="ck_knowledge_chunks_chunk_index",
    ),
)