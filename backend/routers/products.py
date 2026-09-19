from fastapi import APIRouter

from scripts.scrape_products import Product, scrape_product_data


router = APIRouter(prefix="/products", tags=["products"])


@router.post("/scrape")
def scrape_products() -> dict[str, list[Product]]:
    return {"products": scrape_product_data()}


