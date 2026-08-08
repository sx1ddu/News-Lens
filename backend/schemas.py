"""Pydantic request/response models for the /search endpoint."""

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=100)
    page_size: int = Field(default=10, ge=1, le=15)

    @field_validator("query")
    @classmethod
    def query_must_have_real_content(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 2:
            raise ValueError("query must contain at least 2 non-whitespace characters")
        return stripped


class Prediction(BaseModel):
    label: str
    confidence: float


class ArticleResult(BaseModel):
    title: str
    source: str
    url: str
    image: str | None = None
    published: str | None = None
    summary: str
    bias: Prediction
    stance: Prediction | None = None


class StanceGroup(BaseModel):
    count: int
    consensus: str
    articles: list[ArticleResult]


class SearchResponse(BaseModel):
    topic: str
    total_articles: int
    processed_articles: int
    failed_articles: int

    articles: list[ArticleResult]

    bias_groups: dict[str, list[ArticleResult]]
    stance_groups: dict[str, StanceGroup] | None = None

    # Set when the loaded stance model doesn't match the required
    # Supports/Neutral/Questions-Critical scheme - see services/labels.py
    stance_unavailable_reason: str | None = None
