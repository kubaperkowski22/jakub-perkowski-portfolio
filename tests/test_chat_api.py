from fastapi.testclient import TestClient

from main import app
from rag.service import (
    AnswerSource,
    RAGAnswer,
)


client = TestClient(app)


def test_chat_returns_answer_with_sources(
    monkeypatch,
):
    def fake_answer_question(**kwargs):
        return RAGAnswer(
            answerable=True,
            answer=(
                "Modele porównano na siedmiu "
                "zbiorach danych. [3]"
            ),
            sources=[
                AnswerSource(
                    number=3,
                    document_id=(
                        "project.survival-analysis"
                    ),
                    title=(
                        "Głębokie sieci neuronowe "
                        "w analizie przeżycia"
                    ),
                    source_path=(
                        "/projekty/"
                        "survival-analysis"
                    ),
                    section=(
                        "Metodologia eksperymentów"
                    ),
                    subsection=(
                        "Główny eksperyment"
                    ),
                    distance=0.42,
                )
            ],
        )

    monkeypatch.setattr(
        "api.chat.answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/api/chat",
        json={
            "message": (
                "Na ilu zbiorach danych "
                "porównano modele?"
            ),
            "language": "pl",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answerable"] is True
    assert (
        data["answer"]
        == (
            "Modele porównano na siedmiu "
            "zbiorach danych. [3]"
        )
    )

    assert len(data["sources"]) == 1

    source = data["sources"][0]

    assert source["number"] == 3
    assert (
        source["source_path"]
        == "/projekty/survival-analysis"
    )
    assert (
        source["section"]
        == "Metodologia eksperymentów"
    )

    assert "distance" not in source


def test_chat_returns_abstention(
    monkeypatch,
):
    def fake_answer_question(**kwargs):
        return RAGAnswer(
            answerable=False,
            answer=(
                "Dostarczone źródła nie zawierają "
                "informacji o certyfikatach AWS."
            ),
            sources=[],
        )

    monkeypatch.setattr(
        "api.chat.answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/api/chat",
        json={
            "message": (
                "Jakie certyfikaty AWS "
                "posiada Jakub?"
            ),
            "language": "pl",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answerable"] is False
    assert data["sources"] == []


def test_chat_rejects_empty_message():
    response = client.post(
        "/api/chat",
        json={
            "message": "",
            "language": "pl",
        },
    )

    assert response.status_code == 422


def test_chat_rejects_unsupported_language():
    response = client.post(
        "/api/chat",
        json={
            "message": "Test",
            "language": "de",
        },
    )

    assert response.status_code == 422


def test_chat_returns_503_when_rag_fails(
    monkeypatch,
):
    def fake_answer_question(**kwargs):
        raise RuntimeError(
            "Simulated RAG failure"
        )

    monkeypatch.setattr(
        "api.chat.answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/api/chat",
        json={
            "message": "Test",
            "language": "pl",
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "Chat service is temporarily "
            "unavailable."
        )
    }


def test_chat_stream_returns_result(
    monkeypatch,
):
    def fake_answer_question(**kwargs):
        return RAGAnswer(
            answerable=True,
            answer="Odpowiedź. [1]",
            sources=[
                AnswerSource(
                    number=1,
                    document_id="project.test",
                    title="Test",
                    source_path="/projekty/test",
                    section="Sekcja",
                    subsection=None,
                    distance=0.2,
                )
            ],
        )

    monkeypatch.setattr(
        "api.chat.answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/api/chat/stream",
        json={
            "message": "Test",
            "language": "pl",
            "history": [],
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["content-type"]
        .startswith("text/event-stream")
    )

    assert "event: status" in response.text
    assert "event: result" in response.text
    assert '"answerable": true' in response.text


def test_chat_stream_returns_error_event(
    monkeypatch,
):
    def fake_answer_question(**kwargs):
        raise RuntimeError(
            "Simulated failure"
        )

    monkeypatch.setattr(
        "api.chat.answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/api/chat/stream",
        json={
            "message": "Test",
            "language": "pl",
            "history": [],
        },
    )

    assert response.status_code == 200
    assert "event: error" in response.text

    assert (
        "Simulated failure"
        not in response.text
    )