import hashlib
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from openai import OpenAIError
from pydantic import BaseModel, Field

from services.elastic_client import Product, list_products, query_products
from services.mongo_client import get_try_on_result, save_try_on_result
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
def try_on_route(request: TryOnRequest) -> dict[str, str | None]:
    # Uploaded-user photos arrive as data URIs and must never be stored.
    ephemeral = any(url.startswith("data:") for url in request.image_urls)
    cache_key = hashlib.sha256("\n".join(request.image_urls).encode()).hexdigest()

    if not ephemeral:
        cached = get_try_on_result(cache_key)
        if cached is not None:
            return {"image": cached, "cache_key": cache_key}

    try:
        image = combine_images(request.image_urls)
    except OpenAIError as exc:
        raise HTTPException(
            status_code=502,
            detail="Try-on generation failed. Retry, or try different items.",
        ) from exc
    if image is None:
        raise HTTPException(
            status_code=422,
            detail="These items can't be used for a try-on. Try a different outfit.",
        )

    if not ephemeral:
        save_try_on_result(cache_key, image)
    # The cache_key lets the 3D view reuse its Meshy task for this exact outfit.
    return {"image": image, "cache_key": None if ephemeral else cache_key}
