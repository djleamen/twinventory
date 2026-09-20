import uuid


_items: dict[str, list[dict]] = {}

MOCK_PRODUCTS = [
    {"product_id": "p1", "title": "Floral Summer Dress", "image_url": "https://placehold.co/200x300?text=Dress", "shop_url": "https://example.com/p1", "price": 49.99, "score": 0.95},
    {"product_id": "p2", "title": "Classic White Shirt", "image_url": "https://placehold.co/200x300?text=Shirt", "shop_url": "https://example.com/p2", "price": 34.99, "score": 0.90},
    {"product_id": "p3", "title": "Slim Fit Black Jeans", "image_url": "https://placehold.co/200x300?text=Jeans", "shop_url": "https://example.com/p3", "price": 59.99, "score": 0.85},
    {"product_id": "p4", "title": "Casual Blazer", "image_url": "https://placehold.co/200x300?text=Blazer", "shop_url": "https://example.com/p4", "price": 89.99, "score": 0.80},
    {"product_id": "p5", "title": "White Sneakers", "image_url": "https://placehold.co/200x300?text=Sneakers", "shop_url": "https://example.com/p5", "price": 79.99, "score": 0.75},
]


def save_item(item: dict) -> str:
    item_id = str(uuid.uuid4())
    item["item_id"] = item_id
    _items.setdefault(item["user_id"], []).append(item)
    return item_id


def get_items(user_id: str) -> list[dict]:
    return _items.get(user_id, [])


def search_products(
    query_vector: list[float],
    *,
    query_text: str | None = None,
    filters: dict[str, str] | None = None,
    limit: int = 10,
) -> list[dict]:
    return MOCK_PRODUCTS[:limit]
