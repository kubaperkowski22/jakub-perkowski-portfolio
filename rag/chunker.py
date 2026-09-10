import re
from rag.models import KnowledgeChunk, KnowledgeDocument


HEADING_PATTERN = re.compile(
    r"^(#{1,3})\s+(.+?)\s*$"
)


def chunk_document(document: KnowledgeDocument,) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []

    current_section = document.title
    current_subsection: str | None = None
    current_lines: list[str] = []

    def flush_chunk() -> None:
        nonlocal current_lines

        content = "\n".join(current_lines).strip()

        if not content:
            current_lines = []
            return

        chunk_index = len(chunks)

        chunks.append(
            KnowledgeChunk(
                id=(
                    f"{document.id}:"
                    f"{document.language}:"
                    f"{chunk_index}"
                ),
                document_id=document.id,
                language=document.language,
                title=document.title,
                source_type=document.source_type,
                source_slug=document.source_slug,
                source_path=document.source_path,
                section=current_section,
                subsection=current_subsection,
                chunk_index=chunk_index,
                content=content,
            )
        )

        current_lines = []

    for line in document.content.splitlines():
        heading_match = HEADING_PATTERN.match(line)

        if heading_match is None:
            current_lines.append(line)
            continue

        heading_level, heading_text = heading_match.groups()

        flush_chunk()

        if heading_level == "#":
            continue

        if heading_level == "##":
            current_section = heading_text
            current_subsection = None

        elif heading_level == "###":
            current_subsection = heading_text

    flush_chunk()

    return chunks


def chunk_documents(
    documents: list[KnowledgeDocument],
) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []

    for document in documents:
        chunks.extend(chunk_document(document))

    return chunks