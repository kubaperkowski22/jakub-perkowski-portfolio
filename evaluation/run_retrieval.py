import json
from pathlib import Path

from rag.embeddings import OpenAIEmbeddingProvider
from rag.retrieval import search_chunks


BASE_DIR = Path(__file__).resolve().parent.parent

QUESTIONS_PATH = (
    BASE_DIR
    / "evaluation"
    / "retrieval_questions.json"
)

MAX_K = 10
K_VALUES = (1, 5, 8, 10)


def load_questions() -> list[dict]:
    with QUESTIONS_PATH.open(
        encoding="utf-8"
    ) as file:
        return json.load(file)


def document_match(
    result,
    question: dict,
) -> bool:
    return (
        result.document_id
        in question["expected_document_ids"]
    )


def section_match(
    result,
    question: dict,
) -> bool:
    expected_sections = question.get(
        "expected_sections"
    )

    if not expected_sections:
        return document_match(
            result,
            question,
        )

    return (
        document_match(result, question)
        and result.section
        in expected_sections
    )


def reciprocal_rank(
    results,
    question: dict,
) -> float:
    for rank, result in enumerate(
        results,
        start=1,
    ):
        if section_match(
            result,
            question,
        ):
            return 1.0 / rank

    return 0.0


def main() -> None:
    questions = load_questions()

    provider = OpenAIEmbeddingProvider()

    document_hits = {
        k: 0
        for k in K_VALUES
    }

    section_hits = {
        k: 0
        for k in K_VALUES
    }

    reciprocal_ranks: list[float] = []

    for question in questions:
        results = search_chunks(
            query=question["question"],
            language=question["language"],
            provider=provider,
            limit=MAX_K,
        )

        print(
            f"\n[{question['id']}] "
            f"{question['question']}"
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank:>2}. "
                f"{result.document_id} | "
                f"{result.section} | "
                f"{result.subsection} | "
                f"{result.distance:.4f}"
            )

        for k in K_VALUES:
            top_results = results[:k]

            if any(
                document_match(
                    result,
                    question,
                )
                for result in top_results
            ):
                document_hits[k] += 1

            if any(
                section_match(
                    result,
                    question,
                )
                for result in top_results
            ):
                section_hits[k] += 1

        reciprocal_ranks.append(
            reciprocal_rank(
                results,
                question,
            )
        )

    total = len(questions)

    print("\n=== SUMMARY ===")

    for k in K_VALUES:
        print(
            f"Document Hit@{k}: "
            f"{document_hits[k]}/{total} "
            f"({document_hits[k] / total:.1%})"
        )

    print()

    for k in K_VALUES:
        print(
            f"Section Hit@{k}: "
            f"{section_hits[k]}/{total} "
            f"({section_hits[k] / total:.1%})"
        )

    mrr = (
        sum(reciprocal_ranks)
        / len(reciprocal_ranks)
    )

    print()
    print(f"MRR: {mrr:.3f}")


if __name__ == "__main__":
    main()