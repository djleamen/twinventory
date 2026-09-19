from fastapi import APIRouter
from pydantic import BaseModel

from services.elastic_client import list_products, query_products
from services.openai_client import combine_images

router = APIRouter(prefix="/products", tags=["products"])


class TryOnRequest(BaseModel):
    image_urls: list[str]


@router.get("/list")
def list_products_route(category: str | None = None):
    return list_products(category=category)


@router.get("/search")
def search_products_route(
    query: str,
    category: str | None = None,
):
    return query_products(
        query=query,
        category=category,
    )


@router.post("/try")
def try_on_route(request: TryOnRequest):
    image = combine_images(request.image_urls)
    return {"image": image}
