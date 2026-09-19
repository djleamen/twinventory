from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from services.elastic_client import Product, list_products, query_products
from services.openai_client import combine_images

router = APIRouter(prefix="/products", tags=["products"])


class TryOnRequest(BaseModel):
    image_urls: list[str] = Field(min_length=2)


@router.get("")
def get_products(
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, list[Product]]:
    return {"products": list_products(category=category, limit=limit)}


@router.get("/list", include_in_schema=False)
def list_products_route(
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, list[Product]]:
    return get_products(category=category, limit=limit)


@router.get("/search")
def search_products_route(
    q: Annotated[str, Query(min_length=1)],
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, list[Product]]:
    return {"products": query_products(q, category=category, limit=limit)}


@router.post("/try")
def try_on_route(request: TryOnRequest) -> dict[str, str]:
    image = combine_images(request.image_urls)
    return {"image": image}
