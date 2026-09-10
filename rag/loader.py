from pathlib import Path
import yaml
from pydantic import ValidationError
from rag.models import KnowledgeDocument


class KnowledgeBaseLoadError(ValueError):
    """Raised when the knowledge base cannot be loaded correctly."""


def _parse_markdown_file(file_path: Path, knowledge_base_dir: Path,) -> KnowledgeDocument:
    try:
        raw_text = file_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise KnowledgeBaseLoadError(
            f"Cannot read knowledge-base file: {file_path}"
        ) from exc

    if not raw_text.startswith("---"):
        raise KnowledgeBaseLoadError(
            f"Missing YAML front matter in: {file_path}"
        )

    parts = raw_text.split("---", maxsplit=2)

    if len(parts) != 3:
        raise KnowledgeBaseLoadError(
            f"Invalid YAML front matter structure in: {file_path}"
        )

    _, yaml_text, content = parts

    try:
        metadata = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise KnowledgeBaseLoadError(
            f"Invalid YAML in: {file_path}"
        ) from exc

    if not isinstance(metadata, dict):
        raise KnowledgeBaseLoadError(
            f"YAML front matter must be a mapping in: {file_path}"
        )

    relative_path = file_path.relative_to(knowledge_base_dir.parent)

    document_data = {
        **metadata,
        "content": content.strip(),
        "file_path": relative_path,
    }

    try:
        document = KnowledgeDocument.model_validate(document_data)
    except ValidationError as exc:
        raise KnowledgeBaseLoadError(
            f"Invalid knowledge document: {relative_path}\n{exc}"
        ) from exc

    expected_language = file_path.relative_to(
        knowledge_base_dir
    ).parts[0]

    if document.language != expected_language:
        raise KnowledgeBaseLoadError(
            f"Language mismatch in {relative_path}: "
            f"folder='{expected_language}', "
            f"metadata='{document.language}'"
        )

    return document


def load_knowledge_base(knowledge_base_dir: Path,) -> list[KnowledgeDocument]:
    if not knowledge_base_dir.exists():
        raise KnowledgeBaseLoadError(
            f"Knowledge-base directory does not exist: "
            f"{knowledge_base_dir}"
        )

    if not knowledge_base_dir.is_dir():
        raise KnowledgeBaseLoadError(
            f"Knowledge-base path is not a directory: "
            f"{knowledge_base_dir}"
        )

    markdown_files = sorted(
        [
            *knowledge_base_dir.glob("pl/**/*.md"),
            *knowledge_base_dir.glob("en/**/*.md"),
        ]
    )

    if not markdown_files:
        raise KnowledgeBaseLoadError(
            f"No Markdown documents found in: {knowledge_base_dir}"
        )

    documents: list[KnowledgeDocument] = []
    identities: set[tuple[str, str]] = set()

    for file_path in markdown_files:
        document = _parse_markdown_file(
            file_path=file_path,
            knowledge_base_dir=knowledge_base_dir,
        )

        identity = (document.id, document.language)

        if identity in identities:
            raise KnowledgeBaseLoadError(
                "Duplicate knowledge document: "
                f"id='{document.id}', "
                f"language='{document.language}'"
            )

        identities.add(identity)
        documents.append(document)

    public_documents = [
        document
        for document in documents
        if document.visibility == "public"
    ]

    return public_documents