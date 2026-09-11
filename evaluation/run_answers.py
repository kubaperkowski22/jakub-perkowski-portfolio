import json
import re
from pathlib import Path

from rag.embeddings import OpenAIEmbeddingProvider
from rag.llm import OpenAILLMProvider
from rag.service import answer_question


BASE_DIR = Path(__file__).resolve().parent.parent

QUESTIONS_PATH = (
    BASE_DIR
    / "evaluation"
    / "answer_questions.json"
)

REPORT_PATH = (
    BASE_DIR
    / "evaluation"
    / "answer_report.json"
)

CITATION_PATTERN = re.compile(r"\[(\d+)\]")

data_for_table=[]

def load_questions() -> list[dict]:
    with QUESTIONS_PATH.open(
        encoding="utf-8"
    ) as file:
        return json.load(file)


def extract_citations(
    answer: str,
) -> list[int]:
    return sorted(
        {
            int(value)
            for value
            in CITATION_PATTERN.findall(answer)
        }
    )


def main() -> None:
    questions = load_questions()

    embedding_provider = (
        OpenAIEmbeddingProvider()
    )

    llm_provider = OpenAILLMProvider()

    report = []

    for question in questions:
        result = answer_question(
            query=question["question"],
            language=question["language"],
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
        )

        distances = [
            source.distance
            for source in result.sources
        ]

        top_distance = distances[0]

        top3_average_distance = (
            sum(distances[:3])
            / len(distances[:3])
        )

        citations = extract_citations(
            result.answer
        )

        valid_numbers = {
            source.number
            for source in result.sources
        }

        invalid_citations = [
            citation
            for citation in citations
            if citation not in valid_numbers
        ]

        entry = {
            "id": question["id"],
            "language": question["language"],
            "question": question["question"],
            "expected_behavior": (
                question["expected_behavior"]
            ),
            "expected_facts": (
                question["expected_facts"]
            ),
            "answer": result.answer,
            "citations": citations,
            "invalid_citations": (
                invalid_citations
            ),
            "sources": [
                {
                    "number": source.number,
                    "document_id": (
                        source.document_id
                    ),
                    "section": source.section,
                    "subsection": (
                        source.subsection
                    ),
                    "source_path": (
                        source.source_path
                    ),
                    "distance": (
                        source.distance
                    ),
                }
                for source in result.sources
            ],
            "top_distance": top_distance,
            "top3_average_distance": (
                top3_average_distance
            ),
        }

        report.append(entry)

        print(
            f"\n=== {question['id']} ==="
        )

        print(question["question"])
        print()
        print(result.answer)

        print(
            "\nCitations:",
            citations,
        )

        print(
            "Invalid citations:",
            invalid_citations,
        )

        print(
            f"Top distance: "
            f"{top_distance:.4f}"
        )

        print(
            f"Top-3 average distance: "
            f"{top3_average_distance:.4f}"
        )
        data_for_table.append((question["id"], question["expected_behavior"], top_distance, top3_average_distance))

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"\nReport saved to: {REPORT_PATH}"
    )

    print("id \t expected_behavior \t top_distance \t top3_average_distance")
    for q_id, exp_beh, top_dist, top3_avg_dist in data_for_table:
        print(f"{q_id} \t {exp_beh} \t {top_dist:.4f} \t {top3_avg_dist:.4f}")


if __name__ == "__main__":
    main()