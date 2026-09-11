from typing import Protocol
from rag.models import KnowledgeChunk
import os
from openai import OpenAI
from rag.models import KnowledgeChunk
from dotenv import load_dotenv

load_dotenv()


class OpenAIEmbeddingProvider:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("EMBEDDING_MODEL")
        dimensions = os.getenv(
            "EMBEDDING_DIMENSIONS"
        )

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set"
            )

        if not model:
            raise RuntimeError(
                "EMBEDDING_MODEL is not set"
            )

        if not dimensions:
            raise RuntimeError(
                "EMBEDDING_DIMENSIONS is not set"
            )

        self._model = model
        self._dimensions = int(dimensions)
        self._client = OpenAI(
            api_key=api_key,
        )

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        response = self._client.embeddings.create(
            model=self._model,
            input=texts,
            dimensions=self._dimensions,
        )

        embeddings = [
            item.embedding
            for item in sorted(
                response.data,
                key=lambda item: item.index,
            )
        ]

        if len(embeddings) != len(texts):
            raise RuntimeError(
                "Embedding provider returned "
                "an unexpected number of vectors"
            )

        for embedding in embeddings:
            if len(embedding) != self._dimensions:
                raise RuntimeError(
                    "Embedding provider returned "
                    f"{len(embedding)} dimensions, "
                    f"expected {self._dimensions}"
                )

        return embeddings


class EmbeddingProvider(Protocol):
    @property
    def dimensions(self) -> int:
        ...

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...


def build_embedding_text(
    chunk: KnowledgeChunk,
) -> str:
    parts = [
        chunk.title,
        chunk.section,
    ]

    if chunk.subsection:
        parts.append(chunk.subsection)

    parts.append(chunk.content)

    return "\n\n".join(parts)