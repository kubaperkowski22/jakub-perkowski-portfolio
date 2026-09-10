from pathlib import Path

import pytest

from rag.loader import KnowledgeBaseLoadError, load_knowledge_base


def write_document(
    knowledge_base_dir: Path,
    *,
    filename: str,
    language: str = "pl",
    document_id: str = "project.test",
    visibility: str = "public",
) -> Path:
    projects_dir = (
        knowledge_base_dir
        / language
        / "projects"
    )
    projects_dir.mkdir(parents=True, exist_ok=True)

    file_path = projects_dir / filename

    file_path.write_text(
        f"""---
id: {document_id}
language: {language}
title: Test Project
source_type: project
source_slug: test
source_path: /projekty/test
visibility: {visibility}
---

# Test Project

## Description

Example project description.
""",
        encoding="utf-8",
    )

    return file_path


def test_loader_loads_public_document(tmp_path: Path):
    knowledge_base_dir = tmp_path / "knowledge_base"

    write_document(
        knowledge_base_dir,
        filename="test.md",
    )

    documents = load_knowledge_base(
        knowledge_base_dir
    )

    assert len(documents) == 1

    document = documents[0]

    assert document.id == "project.test"
    assert document.language == "pl"
    assert document.visibility == "public"
    assert "Example project description." in document.content


def test_loader_skips_draft_document(tmp_path: Path):
    knowledge_base_dir = tmp_path / "knowledge_base"

    write_document(
        knowledge_base_dir,
        filename="public.md",
        document_id="project.public",
        visibility="public",
    )

    write_document(
        knowledge_base_dir,
        filename="draft.md",
        document_id="project.draft",
        visibility="draft",
    )

    documents = load_knowledge_base(
        knowledge_base_dir
    )

    assert len(documents) == 1
    assert documents[0].id == "project.public"


def test_loader_rejects_language_mismatch(
    tmp_path: Path,
):
    knowledge_base_dir = tmp_path / "knowledge_base"

    file_path = write_document(
        knowledge_base_dir,
        filename="test.md",
        language="pl",
    )

    content = file_path.read_text(
        encoding="utf-8"
    )

    content = content.replace(
        "language: pl",
        "language: en",
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    with pytest.raises(
        KnowledgeBaseLoadError
    ) as exc_info:
        load_knowledge_base(
            knowledge_base_dir
        )

    assert "Language mismatch" in str(
        exc_info.value
    )


def test_loader_rejects_duplicate_document_identity(
    tmp_path: Path,
):
    knowledge_base_dir = tmp_path / "knowledge_base"

    write_document(
        knowledge_base_dir,
        filename="first.md",
        document_id="project.duplicate",
    )

    write_document(
        knowledge_base_dir,
        filename="second.md",
        document_id="project.duplicate",
    )

    with pytest.raises(
        KnowledgeBaseLoadError
    ) as exc_info:
        load_knowledge_base(
            knowledge_base_dir
        )

    assert "Duplicate knowledge document" in str(
        exc_info.value
    )