import re
from collections import defaultdict
from pathlib import Path

from rag.chunker import HEADING_PATTERN, chunk_documents
from rag.loader import load_knowledge_base


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

H1_PATTERN = re.compile(r"^#\s+(.+?)\s*$")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def content_without_headings(content: str) -> str:
    lines = [
        line
        for line in content.splitlines()
        if HEADING_PATTERN.match(line) is None
    ]

    return "\n".join(lines)


def validate_chunks() -> None:
    documents = load_knowledge_base(KNOWLEDGE_BASE_DIR)
    chunks = chunk_documents(documents)

    chunks_by_document = defaultdict(list)

    for chunk in chunks:
        identity = (chunk.document_id, chunk.language)
        chunks_by_document[identity].append(chunk)

    chunk_ids = [chunk.id for chunk in chunks]

    if len(chunk_ids) != len(set(chunk_ids)):
        raise RuntimeError("Duplicate chunk IDs detected")

    for document in documents:
        identity = (document.id, document.language)
        document_chunks = chunks_by_document[identity]

        if not document_chunks:
            raise RuntimeError(
                f"Document produced no chunks: {identity}"
            )

        h1_headings = []

        for line in document.content.splitlines():
            match = H1_PATTERN.match(line)

            if match:
                h1_headings.append(match.group(1))

        if len(h1_headings) != 1:
            raise RuntimeError(
                f"Expected exactly one H1 in {identity}, "
                f"found {len(h1_headings)}: {h1_headings}"
            )

        if h1_headings[0] != document.title:
            raise RuntimeError(
                f"H1/title mismatch in {identity}: "
                f"H1='{h1_headings[0]}', "
                f"title='{document.title}'"
            )

        expected_indices = list(range(len(document_chunks)))

        actual_indices = [
            chunk.chunk_index
            for chunk in document_chunks
        ]

        if actual_indices != expected_indices:
            raise RuntimeError(
                f"Invalid chunk indexes in {identity}: "
                f"{actual_indices}"
            )

        for chunk in document_chunks:
            if chunk.title != document.title:
                raise RuntimeError(
                    f"Title mismatch in chunk {chunk.id}"
                )

            if chunk.source_type != document.source_type:
                raise RuntimeError(
                    f"source_type mismatch in chunk {chunk.id}"
                )

            if chunk.source_slug != document.source_slug:
                raise RuntimeError(
                    f"source_slug mismatch in chunk {chunk.id}"
                )

            if chunk.source_path != document.source_path:
                raise RuntimeError(
                    f"source_path mismatch in chunk {chunk.id}"
                )

        expected_content = normalize_text(
            content_without_headings(document.content)
        )

        actual_content = normalize_text(
            "\n".join(
                chunk.content
                for chunk in document_chunks
            )
        )

        """ if identity == ("profile.education", "en"):
            print("\nCHUNKS FOR EDUCATION EN:")

            for chunk in document_chunks:
                print(
                    f"\n--- CHUNK {chunk.chunk_index} ---"
                )
                print(f"Section: {chunk.section}")
                print(f"Subsection: {chunk.subsection}")
                print(repr(chunk.content)) """

        if expected_content != actual_content:
            print(f"\nCONTENT MISMATCH: {identity}")
            print(f"Expected length: {len(expected_content)}")
            print(f"Actual length:   {len(actual_content)}")

            mismatch_index = next(
                (
                    i
                    for i, (expected_char, actual_char)
                    in enumerate(zip(expected_content, actual_content))
                    if expected_char != actual_char
                ),
                min(len(expected_content), len(actual_content)),
            )

            context_start = max(0, mismatch_index - 150)
            context_end = mismatch_index + 150

            print("\nEXPECTED:")
            print(repr(expected_content[context_start:context_end]))

            print("\nACTUAL:")
            print(repr(actual_content[context_start:context_end]))

            raise RuntimeError(
                f"Content lost or modified during chunking: "
                f"{identity}"
            )

    sizes = [
        len(chunk.content.split())
        for chunk in chunks
    ]

    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")
    print(f"PL: {sum(c.language == 'pl' for c in chunks)} chunks")
    print(f"EN: {sum(c.language == 'en' for c in chunks)} chunks")
    print(f"Min words: {min(sizes)}")
    print(f"Max words: {max(sizes)}")
    print(
        f"Average words: "
        f"{sum(sizes) / len(sizes):.1f}"
    )
    print("Unique chunk IDs: OK")
    print("Chunk indexes: OK")
    print("Metadata propagation: OK")
    print("Content preservation: OK")
    print("H1 structure: OK")
    print("Validation: OK")


if __name__ == "__main__":
    validate_chunks()