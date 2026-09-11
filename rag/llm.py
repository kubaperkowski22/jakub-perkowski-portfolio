import os
from typing import Protocol

from dotenv import load_dotenv
from openai import OpenAI

from pydantic import BaseModel, Field


load_dotenv()


class GeneratedAnswer(BaseModel):
    answerable: bool

    answer: str = Field(min_length=1)

    citations: list[int]


class LLMProvider(Protocol):
    def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> GeneratedAnswer:
        ...


class OpenAILLMProvider:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("LLM_MODEL")
        max_output_tokens = os.getenv(
            "LLM_MAX_OUTPUT_TOKENS"
        )

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set"
            )

        if not model:
            raise RuntimeError(
                "LLM_MODEL is not set"
            )

        if not max_output_tokens:
            raise RuntimeError(
                "LLM_MAX_OUTPUT_TOKENS is not set"
            )

        self._client = OpenAI(
            api_key=api_key
        )

        self._model = model
        self._max_output_tokens = int(
            max_output_tokens
        )

    def generate(
        self,
        *,
        instructions: str,
        input_text: str,
    ) -> GeneratedAnswer:
        response = self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=input_text,
            max_output_tokens=self._max_output_tokens,
            store=False,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "rag_answer",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "answerable": {
                                "type": "boolean"
                            },
                            "answer": {
                                "type": "string"
                            },
                            "citations": {
                                "type": "array",
                                "items": {
                                    "type": "integer"
                                }
                            },
                        },
                        "required": [
                            "answerable",
                            "answer",
                            "citations",
                        ],
                        "additionalProperties": False,
                    },
                }
            },
        )

        return GeneratedAnswer.model_validate_json(
            response.output_text
        )