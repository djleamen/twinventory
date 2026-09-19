import logging
import sys

from fastapi import APIRouter

from scripts.scrape_products import DEFAULT_MAX_PRODUCTS, scrape_product_data
from services.elastic_client import Product, list_products, query_products


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(_handler)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/scrape")
def scrape_products(max_products: int = DEFAULT_MAX_PRODUCTS) -> dict[str, list[Product]]:
    logger.info("Received request to scrape products (max_products=%d)", max_products)
    products = scrape_product_data(max_products=max_products)
    logger.info("Scrape request complete: %d products", len(products))
    print(f"Scrape request complete: {len(products)} products")
    return {"products": products}


@router.get("/search")
def search_products(q: str, category: str | None = None, limit: int = 20) -> dict[str, list[Product]]:
    logger.info("Searching products: q=%r category=%r limit=%d", q, category, limit)
    results = query_products(q, category=category, limit=limit)
    logger.info("Search returned %d products", len(results))
    return {"products": results}


@router.get("")
def get_products(category: str | None = None, limit: int = 20) -> dict[str, list[Product]]:
    logger.info("Listing products: category=%r limit=%d", category, limit)
    results = list_products(category=category, limit=limit)
    logger.info("List returned %d products", len(results))
    return {"products": results}
