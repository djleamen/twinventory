# Scrape product listings from the Shopify stores listed in config.json using
# Browserbase, then upsert the results into MongoDB.

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from browserbase import Browserbase
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright
from pydantic import BaseModel

from services.mongo_client import get_products_collection


CONFIG_PATH = Path(__file__).parents[1] / "config.json"
PRODUCTS_PER_PAGE = 250

load_dotenv(Path(__file__).parents[2] / ".env")


class Product(BaseModel):
    product_id: str
    product_name: str
    product_description: str
    price: float
    source_url: str
    shop_name: str
    image_url: str
    image_type: str


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_shop_urls() -> list[str]:
    config = json.loads(CONFIG_PATH.read_text())
    return config["shops_url"]


def _shop_name(shop_url: str) -> str:
    host = urlparse(shop_url).netloc or shop_url
    return host.removeprefix("www.").split(".")[0]


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def _image_type(image_url: str) -> str:
    suffix = Path(urlparse(image_url).path).suffix.lstrip(".").lower()
    return suffix or "unknown"


def _to_product(shop_url: str, shop_name: str, item: dict[str, Any]) -> Product | None:
    variants = item.get("variants") or []
    images = item.get("images") or []
    handle = item.get("handle")
    if not variants or not images or not handle:
        return None

    price = variants[0].get("price")
    if price is None:
        return None

    image_url = images[0].get("src", "")
    return Product(
        product_id=f"{shop_name}-{item['id']}",
        product_name=item.get("title", ""),
        product_description=_strip_html(item.get("body_html", "")),
        price=float(price),
        source_url=f"{shop_url.rstrip('/')}/products/{handle}",
        shop_name=shop_name,
        image_url=image_url,
        image_type=_image_type(image_url),
    )


def _fetch_products_page(page: Page, shop_url: str, page_number: int) -> list[dict[str, Any]]:
    url = f"{shop_url.rstrip('/')}/products.json?limit={PRODUCTS_PER_PAGE}&page={page_number}"
    page.goto(url)
    body = page.evaluate("() => document.body.innerText")
    return json.loads(body).get("products") or []


def scrape_shop(page: Page, shop_url: str) -> list[Product]:
    shop_name = _shop_name(shop_url)
    products: list[Product] = []
    page_number = 1

    while True:
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

    return products


def save_products(products: list[Product]) -> int:
    if not products:
        return 0

    collection = get_products_collection()
    for product in products:
        collection.update_one(
            {"product_id": product.product_id},
            {"$set": product.model_dump()},
            upsert=True,
        )
    return len(products)


def scrape_product_data(shop_urls: list[str] | None = None) -> list[Product]:
    shop_urls = shop_urls if shop_urls is not None else load_shop_urls()

    bb = Browserbase(api_key=_required_env("BROWSERBASE_API_KEY"))
    session = bb.sessions.create(project_id=_required_env("BROWSERBASE_PROJECT_ID"))

    playwright = sync_playwright().start()
    try:
        browser = playwright.chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        all_products: list[Product] = []
        for shop_url in shop_urls:
            all_products.extend(scrape_shop(page, shop_url))

        page.close()
        browser.close()
    finally:
        playwright.stop()

    save_products(all_products)
    print(
        f"Scraped {len(all_products)} products. "
        f"View recording at https://browserbase.com/sessions/{session.id}"
    )
    return all_products


if __name__ == "__main__":
    scrape_product_data()
