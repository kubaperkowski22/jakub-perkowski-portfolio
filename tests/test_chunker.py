from pathlib import Path

from rag.chunker import chunk_document
from rag.models import KnowledgeDocument


def test_chunker_preserves_document_content():
    document = KnowledgeDocument(
        id="project.test",
        language="pl",
        title="Test Project",
        source_type="project",
        source_slug="test",
        source_path="/projekty/test",
        visibility="public",
        file_path=Path("knowledge_base/pl/projects/test.md"),
        content="""# Test Project

## First section

First paragraph.

### Details

Detailed information.

## Second section

Last paragraph in the document.
""",
    )

    chunks = chunk_document(document)

    assert len(chunks) == 3

    combined_content = "\n".join(
        chunk.content for chunk in chunks
    )

    assert "First paragraph." in combined_content
    assert "Detailed information." in combined_content
    assert "Last paragraph in the document." in combined_content


def test_chunker_preserves_heading_context():
    document = KnowledgeDocument(
        id="project.test",
        language="en",
        title="Test Project",
        source_type="project",
        source_slug="test",
        source_path="/projekty/test",
        visibility="public",
        file_path=Path("knowledge_base/en/projects/test.md"),
        content="""# Test Project

## Architecture

General architecture description.

### Database

PostgreSQL description.
""",
    )

    chunks = chunk_document(document)

    assert len(chunks) == 2

    assert chunks[0].section == "Architecture"
    assert chunks[0].subsection is None

    assert chunks[1].section == "Architecture"
    assert chunks[1].subsection == "Database"