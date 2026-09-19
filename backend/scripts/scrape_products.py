# Scrape product listings from the Shopify stores listed in config.json using
# Browserbase, then index the results into Elasticsearch.

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from browserbase import Browserbase
from playwright.sync_api import Page, sync_playwright

from services.elastic_client import Product, insert_products
from utils import _get_required_env


CONFIG_PATH = Path(__file__).parents[1] / "config.json"
PRODUCTS_PER_PAGE = 250
# Shopify's legacy /products.json endpoint rejects requests once page * limit
# would exceed 25000, regardless of how many products the shop actually has.
MAX_PRODUCTS_JSON_RESULTS = 25_000
MAX_PAGES = MAX_PRODUCTS_JSON_RESULTS // PRODUCTS_PER_PAGE
DEFAULT_MAX_PRODUCTS = 100

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(_handler)


def load_shop_urls() -> list[str]:
    config = json.loads(CONFIG_PATH.read_text())
    return config["shops_url"]


def _shop_name(shop_url: str) -> str:
    host = urlparse(shop_url).netloc or shop_url
    return host.removeprefix("www.").split(".")[0]


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def _to_product(shop_url: str, shop_name: str, item: dict[str, Any]) -> Product | None:
    variants = item.get("variants") or []
    images = item.get("images") or []
    handle = item.get("handle")
    if not variants or not images or not handle:
        logger.debug(
            "Skipping product %s from %s: missing variants, images, or handle",
            item.get("id"),
            shop_url,
        )
        return None

    price = variants[0].get("price")
    if price is None:
        logger.debug("Skipping product %s from %s: missing price", item.get("id"), shop_url)
        return None

    return Product(
        id=f"{shop_name}-{item['id']}",
        title=item.get("title", ""),
        description=_strip_html(item.get("body_html", "")),
        image=images[0].get("src", ""),
        price=float(price),
        category=item.get("product_type") or "",
        url=f"{shop_url.rstrip('/')}/products/{handle}",
    )


def _fetch_products_page(page: Page, shop_url: str, page_number: int) -> list[dict[str, Any]]:
    url = f"{shop_url.rstrip('/')}/products.json?limit={PRODUCTS_PER_PAGE}&page={page_number}"
    logger.info("Fetching %s", url)
    response = page.goto(url)
    if response is None:
        logger.error("No response received for %s", url)
        raise RuntimeError(f"No response received for {url}")
    if not response.ok:
        logger.error("Failed to fetch %s: HTTP %s", url, response.status)
        raise RuntimeError(f"Failed to fetch {url}: HTTP {response.status}")

    items = response.json().get("products") or []
    logger.info("Fetched %d products from %s (page %d)", len(items), shop_url, page_number)
    return items


def scrape_shop(page: Page, shop_url: str, max_products: int) -> list[Product]:
    shop_name = _shop_name(shop_url)
    logger.info("Scraping shop: %s (max %d products)", shop_url, max_products)
    products: list[Product] = []
    page_number = 1

    while page_number <= MAX_PAGES and len(products) < max_products:
        items = _fetch_products_page(page, shop_url, page_number)
        if not items:
            break

        products.extend(
            product
            for item in items
            if (product := _to_product(shop_url, shop_name, item)) is not None
        )

        if len(items) < PRODUCTS_PER_PAGE:
            break
        page_number += 1
    else:
        if len(products) >= max_products:
            logger.info("Reached max_products cap of %d for %s", max_products, shop_url)
        else:
            logger.warning(
                "Stopped at Shopify's %d-product /products.json limit for %s; "
                "the shop may have more products than could be scraped",
                MAX_PRODUCTS_JSON_RESULTS,
                shop_url,
            )

    products = products[:max_products]
    logger.info("Finished scraping %s: %d products", shop_url, len(products))
    return products


def scrape_product_data(
    shop_urls: list[str] | None = None,
    max_products: int = DEFAULT_MAX_PRODUCTS,
) -> list[Product]:
    shop_urls = shop_urls if shop_urls is not None else load_shop_urls()
    logger.info(
        "Starting scrape for %d shop(s) (max %d products total): %s",
        len(shop_urls),
        max_products,
        ", ".join(shop_urls),
    )

    bb = Browserbase(api_key=_get_required_env("BROWSERBASE_API_KEY"))
    session = bb.sessions.create(project_id=_get_required_env("BROWSERBASE_PROJECT_ID"))
    logger.info("Created Browserbase session %s", session.id)

    playwright = sync_playwright().start()
    try:
        browser = playwright.chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        all_products: list[Product] = []
        for shop_url in shop_urls:
            remaining = max_products - len(all_products)
            if remaining <= 0:
                break
            all_products.extend(scrape_shop(page, shop_url, remaining))

        page.close()
        browser.close()
    finally:
        playwright.stop()

    logger.info("Indexing %d products into Elasticsearch", len(all_products))
    insert_products(all_products)
    logger.info(
        "Scraped %d products. View recording at https://browserbase.com/sessions/%s",
        len(all_products),
        session.id,
    )
    return all_products


if __name__ == "__main__":
    scrape_product_data()
