import pytest

from rag.llm import GeneratedAnswer
from rag.retrieval import RetrievalResult
from rag.service import answer_question, ConversationMessage


class FakeLLMProvider:
    def __init__(
        self,
        response: GeneratedAnswer,
    ) -> None:
        self.response = response

    def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> GeneratedAnswer:
        return self.response


def make_result(
    *,
    result_id: str,
    document_id: str,
    section: str,
    distance: float,
) -> RetrievalResult:
    return RetrievalResult(
        id=result_id,
        document_id=document_id,
        language="pl",
        title="Test",
        source_type="project",
        source_slug="test",
        source_path="/projekty/test",
        section=section,
        subsection=None,
        chunk_index=0,
        content=f"Treść źródła: {section}",
        distance=distance,
    )


def test_answer_question_returns_only_used_sources(
    monkeypatch,
):
    results = [
        make_result(
            result_id="project.test:pl:0",
            document_id="project.test",
            section="Pierwsza sekcja",
            distance=0.2,
        ),
        make_result(
            result_id="project.test:pl:1",
            document_id="project.test",
            section="Druga sekcja",
            distance=0.3,
        ),
    ]

    monkeypatch.setattr(
        "rag.service.search_chunks",
        lambda **kwargs: results,
    )

    llm_provider = FakeLLMProvider(
        GeneratedAnswer(
            answerable=True,
            answer="Odpowiedź oparta na drugim źródle. [2]",
            citations=[2],
        )
    )

    result = answer_question(
        query="Pytanie testowe",
        language="pl",
        embedding_provider=object(),
        llm_provider=llm_provider,
    )

    assert result.answerable is True
    assert (
        result.answer
        == "Odpowiedź oparta na drugim źródle. [2]"
    )

    assert len(result.sources) == 1
    assert result.sources[0].number == 2
    assert (
        result.sources[0].section
        == "Druga sekcja"
    )


def test_answer_question_returns_no_sources_when_unanswerable(
    monkeypatch,
):
    results = [
        make_result(
            result_id="project.test:pl:0",
            document_id="project.test",
            section="Sekcja",
            distance=0.5,
        ),
    ]

    monkeypatch.setattr(
        "rag.service.search_chunks",
        lambda **kwargs: results,
    )

    llm_provider = FakeLLMProvider(
        GeneratedAnswer(
            answerable=False,
            answer=(
                "Dostarczone źródła nie zawierają "
                "wystarczających informacji."
            ),
            citations=[],
        )
    )

    result = answer_question(
        query="Nieznane pytanie",
        language="pl",
        embedding_provider=object(),
        llm_provider=llm_provider,
    )

    assert result.answerable is False
    assert result.sources == []


def test_answer_question_rejects_invalid_citation(
    monkeypatch,
):
    results = [
        make_result(
            result_id="project.test:pl:0",
            document_id="project.test",
            section="Sekcja",
            distance=0.2,
        ),
    ]

    monkeypatch.setattr(
        "rag.service.search_chunks",
        lambda **kwargs: results,
    )

    llm_provider = FakeLLMProvider(
        GeneratedAnswer(
            answerable=True,
            answer="Niepoprawne źródło. [99]",
            citations=[99],
        )
    )

    with pytest.raises(
        RuntimeError,
        match="invalid source numbers",
    ):
        answer_question(
            query="Pytanie",
            language="pl",
            embedding_provider=object(),
            llm_provider=llm_provider,
        )


def test_answer_question_uses_user_history_for_retrieval(
    monkeypatch,
):
    captured_query = {}

    results = [
        make_result(
            result_id="project.test:pl:0",
            document_id="project.test",
            section="Technologie",
            distance=0.2,
        ),
    ]

    def fake_search_chunks(**kwargs):
        captured_query["value"] = kwargs["query"]
        return results

    monkeypatch.setattr(
        "rag.service.search_chunks",
        fake_search_chunks,
    )

    llm_provider = FakeLLMProvider(
        GeneratedAnswer(
            answerable=True,
            answer="Odpowiedź. [1]",
            citations=[1],
        )
    )

    history = [
        ConversationMessage(
            role="user",
            content=(
                "Jakich technologii użyto "
                "w DiagnoseMe?"
            ),
        ),
        ConversationMessage(
            role="assistant",
            content="C#, WPF i Azure SQL.",
        ),
    ]

    answer_question(
        query=(
            "Które z nich były związane "
            "z bazą danych?"
        ),
        language="pl",
        embedding_provider=object(),
        llm_provider=llm_provider,
        history=history,
    )

    assert (
        "Jakich technologii użyto w DiagnoseMe?"
        in captured_query["value"]
    )

    assert (
        "Które z nich były związane z bazą danych?"
        in captured_query["value"]
    )

    assert (
        "C#, WPF i Azure SQL."
        not in captured_query["value"]
    )


def test_answer_question_rejects_citation_mismatch(
    monkeypatch,
):
    results = [
        make_result(
            result_id="project.test:pl:0",
            document_id="project.test",
            section="Pierwsza",
            distance=0.2,
        ),
        make_result(
            result_id="project.test:pl:1",
            document_id="project.test",
            section="Druga",
            distance=0.3,
        ),
    ]

    monkeypatch.setattr(
        "rag.service.search_chunks",
        lambda **kwargs: results,
    )

    llm_provider = FakeLLMProvider(
        GeneratedAnswer(
            answerable=True,
            answer="Odpowiedź. [1]",
            citations=[2],
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Inline citations",
    ):
        answer_question(
            query="Test",
            language="pl",
            embedding_provider=object(),
            llm_provider=llm_provider,
        )


def test_answer_question_requires_citation_for_answer(
    monkeypatch,
):
    results = [
        make_result(
            result_id="project.test:pl:0",
            document_id="project.test",
            section="Sekcja",
            distance=0.2,
        )
    ]

    monkeypatch.setattr(
        "rag.service.search_chunks",
        lambda **kwargs: results,
    )

    llm_provider = FakeLLMProvider(
        GeneratedAnswer(
            answerable=True,
            answer="Odpowiedź bez źródła.",
            citations=[],
        )
    )

    with pytest.raises(
        RuntimeError,
        match="at least one citation",
    ):
        answer_question(
            query="Test",
            language="pl",
            embedding_provider=object(),
            llm_provider=llm_provider,
        )