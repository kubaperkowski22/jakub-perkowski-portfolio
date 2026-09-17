import logging
from typing import Annotated, Literal
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)
from api.dependencies import (
    get_embedding_provider,
    get_llm_provider,
)
from rag.embeddings import EmbeddingProvider
from rag.llm import LLMProvider
from rag.service import (
    ConversationMessage,
    answer_question,
    RAGAnswer
)
import json
from api.rate_limit import (
    enforce_chat_rate_limit,
)
from pydantic import model_validator


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["chat"],
)


class ChatHistoryMessage(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    role: Literal["user", "assistant"]

    content: str = Field(
        min_length=1,
        max_length=4000,
    )


class ChatRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    message: str = Field(
        min_length=1,
        max_length=2000,
    )

    language: Literal["pl", "en"] = "pl"

    history: list[ChatHistoryMessage] = Field(
        default_factory=list,
        max_length=4,
    )

    @field_validator("history")
    @classmethod
    def validate_history(
        cls,
        history: list[ChatHistoryMessage],
    ) -> list[ChatHistoryMessage]:
        if len(history) % 2 != 0:
            raise ValueError(
                "history must contain complete "
                "user/assistant turns"
            )

        for index, message in enumerate(history):
            expected_role = (
                "user"
                if index % 2 == 0
                else "assistant"
            )

            if message.role != expected_role:
                raise ValueError(
                    "history messages must alternate "
                    "between user and assistant"
                )

        return history

    @model_validator(mode="after")
    def validate_total_context_length(
        self,
    ):
        total_characters = (
            len(self.message)
            + sum(
                len(message.content)
                for message in self.history
            )
        )

        if total_characters > 10_000:
            raise ValueError(
                "message and history exceed "
                "the maximum context size"
            )

        return self


class ChatSourceResponse(BaseModel):
    number: int
    title: str
    source_path: str
    section: str
    subsection: str | None


class ChatResponse(BaseModel):
    answerable: bool
    answer: str
    sources: list[ChatSourceResponse]


@router.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[
        Depends(enforce_chat_rate_limit),
    ],
    name="chat_api",
)
def chat(
    request: ChatRequest,
    embedding_provider: Annotated[
        EmbeddingProvider,
        Depends(get_embedding_provider),
    ],
    llm_provider: Annotated[
        LLMProvider,
        Depends(get_llm_provider),
    ],
) -> ChatResponse:
    
    history = [
        ConversationMessage(
            role=message.role,
            content=message.content,
        )
        for message in request.history
    ]

    try:
        result = answer_question(
            query=request.message,
            language=request.language,
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
            history=history,
        )

    except Exception as exc:
        logger.exception(
            "Chat request failed"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Chat service is temporarily unavailable."
            ),
        ) from exc

    return build_chat_response(result)

def build_chat_response(
        result: RAGAnswer,
) -> ChatResponse:
    sources = [
        ChatSourceResponse(
            number=source.number,
            title=source.title,
            source_path=source.source_path,
            section=source.section,
            subsection=source.subsection,
        )
        for source in result.sources
    ]

    return ChatResponse(
        answerable=result.answerable,
        answer=result.answer,
        sources=sources,
    )

def format_sse(
    event: str,
    data: dict,
) -> str:
    payload = json.dumps(
        data,
        ensure_ascii=False,
    )

    return (
        f"event: {event}\n"
        f"data: {payload}\n\n"
    )

@router.post(
        "/chat/stream",
        dependencies=[
            Depends(enforce_chat_rate_limit),
        ],
        name="chat_stream",
)
def chat_stream(
    request: ChatRequest,
    embedding_provider: Annotated[
        EmbeddingProvider,
        Depends(get_embedding_provider),
    ],
    llm_provider: Annotated[
        LLMProvider,
        Depends(get_llm_provider),
    ],
) -> StreamingResponse:
    history = [
        ConversationMessage(
            role=message.role,
            content=message.content,
        )
        for message in request.history
    ]

    def event_generator():
        try:
            yield format_sse(
                "status",
                {
                    "stage": "processing",
                },
            )

            result = answer_question(
                query=request.message,
                language=request.language,
                embedding_provider=(
                    embedding_provider
                ),
                llm_provider=llm_provider,
                history=history,
            )

            response = build_chat_response(
                result
            )

            yield format_sse(
                "result",
                response.model_dump(),
            )

        except Exception:
            logger.exception(
                "Streaming chat request failed"
            )

            yield format_sse(
                "error",
                {
                    "detail": (
                        "Chat service is "
                        "temporarily unavailable."
                    )
                },
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )