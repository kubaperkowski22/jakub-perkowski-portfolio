from functools import lru_cache

from rag.embeddings import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from rag.llm import (
    LLMProvider,
    OpenAILLMProvider,
)


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider()


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    return OpenAILLMProvider()