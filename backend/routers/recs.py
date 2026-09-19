from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.elastic_client import embedding_dimensions, search_products


router = APIRouter(prefix="/recs", tags=["recommendations"])


class RecommendationQuery(BaseModel):
    query_vector: list[float] = Field(
        min_length=embedding_dimensions(),
        max_length=embedding_dimensions(),
    )
    query_text: str | None = None
    category: str | None = None
    color: str | None = None
    style: str | None = None
    limit: int = Field(default=12, ge=1, le=50)


@router.post("/query")
def query_recommendations(request: RecommendationQuery) -> dict[str, list[dict[str, Any]]]:
    filters = {
        field: value
        for field in ("category", "color", "style")
        if (value := getattr(request, field)) is not None
    }
    return {
        "results": search_products(
            request.query_vector,
            query_text=request.query_text,
            filters=filters,
            limit=request.limit,
        )
    }