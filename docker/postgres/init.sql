CREATE EXTENSION IF NOT EXISTS vector;


CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id TEXT PRIMARY KEY,

    document_id TEXT NOT NULL,

    language TEXT NOT NULL
        CHECK (language IN ('pl', 'en')),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    source_type TEXT NOT NULL
        CHECK (
            source_type IN (
                'profile',
                'experience',
                'education',
                'skills',
                'project'
            )
        ),

    source_slug TEXT,

    source_path TEXT NOT NULL
        CHECK (source_path LIKE '/%'),

    section TEXT NOT NULL
        CHECK (length(trim(section)) > 0),

    subsection TEXT,

    chunk_index INTEGER NOT NULL
        CHECK (chunk_index >= 0),

    content TEXT NOT NULL
        CHECK (length(trim(content)) > 0),

    embedding vector(1536),

    ingested_at TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    CONSTRAINT uq_knowledge_chunk_position
        UNIQUE (
            document_id,
            language,
            chunk_index
        ),

    CONSTRAINT ck_source_slug_by_type
        CHECK (
            (
                source_type = 'project'
                AND source_slug IS NOT NULL
            )
            OR
            (
                source_type <> 'project'
                AND source_slug IS NULL
            )
        )
);


CREATE INDEX IF NOT EXISTS
    idx_knowledge_chunks_language
ON knowledge_chunks(language);


CREATE INDEX IF NOT EXISTS
    idx_knowledge_chunks_document
ON knowledge_chunks(document_id, language);


CREATE INDEX IF NOT EXISTS
    idx_knowledge_chunks_source_type
ON knowledge_chunks(source_type);