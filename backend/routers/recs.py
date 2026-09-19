from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.elastic_client import Product, list_products, query_products


router = APIRouter(prefix="/recs", tags=["recommendations"])


class RecommendationQuery(BaseModel):
    query_text: str | None = None
    category: str | None = None
    limit: int = Field(default=12, ge=1, le=50)


@router.post("/query")
def query_recommendations(request: RecommendationQuery) -> dict[str, list[Product]]:
    if request.query_text:
        results = query_products(request.query_text, category=request.category, limit=request.limit)
    else:
        results = list_products(category=request.category, limit=request.limit)
    return {"results": results}
