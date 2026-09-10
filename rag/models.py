from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Language = Literal["pl", "en"]
Visibility = Literal["public", "draft"]
SourceType = Literal[
    "profile",
    "experience",
    "education",
    "skills",
    "project",
]


class KnowledgeDocument(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    id: str = Field(
        min_length=1,
        pattern=r"^[a-z0-9][a-z0-9._-]*$",
    )

    language: Language

    title: str = Field(min_length=1)

    source_type: SourceType

    source_slug: str | None = Field(
        default=None,
        pattern=r"^[a-z0-9][a-z0-9-]*$",
    )

    source_path: str

    visibility: Visibility

    content: str = Field(min_length=1)

    file_path: Path

    @field_validator("source_path")
    @classmethod
    def validate_source_path(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("source_path must start with '/'")

        return value

    @model_validator(mode="after")
    def validate_source_slug(self) -> "KnowledgeDocument":
        if self.source_type == "project" and self.source_slug is None:
            raise ValueError(
                "source_slug is required when source_type is 'project'"
            )

        if self.source_type != "project" and self.source_slug is not None:
            raise ValueError(
                "source_slug is allowed only when source_type is 'project'"
            )

        return self



class KnowledgeChunk(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    id: str = Field(min_length=1)

    document_id: str = Field(min_length=1)

    language: Language

    title: str = Field(min_length=1)

    source_type: SourceType

    source_slug: str | None = None

    source_path: str

    section: str = Field(min_length=1)

    subsection: str | None = None

    chunk_index: int = Field(ge=0)

    content: str = Field(min_length=1)

    @field_validator("source_path")
    @classmethod
    def validate_source_path(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("source_path must start with '/'")

        return value

    @model_validator(mode="after")
    def validate_source_slug(self) -> "KnowledgeChunk":
        if self.source_type == "project" and self.source_slug is None:
            raise ValueError(
                "source_slug is required when source_type is 'project'"
            )

        if self.source_type != "project" and self.source_slug is not None:
            raise ValueError(
                "source_slug is allowed only when source_type is 'project'"
            )

        return self