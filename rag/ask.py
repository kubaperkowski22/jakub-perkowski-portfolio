import argparse

from rag.embeddings import (
    OpenAIEmbeddingProvider,
)
from rag.llm import OpenAILLMProvider
from rag.service import answer_question


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "question",
    )

    parser.add_argument(
        "--lang",
        choices=["pl", "en"],
        default="pl",
    )

    args = parser.parse_args()

    embedding_provider = (
        OpenAIEmbeddingProvider()
    )

    llm_provider = OpenAILLMProvider()

    result = answer_question(
        query=args.question,
        language=args.lang,
        embedding_provider=embedding_provider,
        llm_provider=llm_provider,
    )

    print("\nANSWER\n")
    print(f"Answerable: {result.answerable}")
    print()
    print(result.answer)

    print("\nSOURCES\n")

    for source in result.sources:
        heading = source.section

        if source.subsection:
            heading += (
                f" > {source.subsection}"
            )

        print(
            f"[{source.number}] "
            f"{source.title} | "
            f"{heading} | "
            f"{source.source_path} | "
            f"distance={source.distance:.4f}"
        )


if __name__ == "__main__":
    main()