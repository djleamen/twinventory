import os
import unittest
from unittest.mock import patch

from fastapi import Response
from fastapi.testclient import TestClient

os.environ.setdefault("ELASTICSEARCH_URL", "http://localhost:9200")
os.environ.setdefault("ELASTICSEARCH_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

import main
from routers.products import (
    TryOnRequest,
    get_products,
    list_products_route,
    search_products_route,
    try_on_route,
)


class ProductRouteTests(unittest.TestCase):
    @patch("routers.products.list_products")
    def test_list_forwards_category_and_limit(self, list_products) -> None:
        list_products.return_value = [{"id": "dress-1"}]

        response = get_products(category="dress", limit=10)

        self.assertEqual(response, {"products": [{"id": "dress-1"}]})
        list_products.assert_called_once_with(category="dress", limit=10)

    @patch("routers.products.get_products")
    def test_list_alias_uses_current_list_contract(self, get_products) -> None:
        get_products.return_value = {"products": []}

        response = list_products_route(category="dress", limit=10)

        self.assertEqual(response, {"products": []})
        get_products.assert_called_once_with(category="dress", limit=10)

    @patch("routers.products.query_products")
    def test_search_forwards_query_and_category(self, query_products) -> None:
        query_products.return_value = [{"id": "dress-1"}]

        response = search_products_route(q="winter clothing", category="dress", limit=5)

        self.assertEqual(response, {"products": [{"id": "dress-1"}]})
        query_products.assert_called_once_with(
            "winter clothing",
            category="dress",
            limit=5,
        )

    @patch("routers.products.combine_images", return_value="base64-image")
    def test_try_on_combines_requested_images(self, combine_images) -> None:
        request = TryOnRequest(image_urls=["person.jpg", "dress.jpg"])

        response = try_on_route(request)

        self.assertEqual(response, {"image": "base64-image"})
        combine_images.assert_called_once_with(["person.jpg", "dress.jpg"])

    def test_openapi_exposes_current_product_contract(self) -> None:
        paths = TestClient(main.app).get("/openapi.json").json()["paths"]

        self.assertIn("/products", paths)
        self.assertIn("/products/search", paths)
        self.assertIn("/products/try", paths)
        self.assertNotIn("/products/list", paths)
        self.assertNotIn("/products/scrape", paths)
        self.assertNotIn("/recs/query", paths)


class HealthRouteTests(unittest.TestCase):
    @patch("main.elasticsearch_is_ready", return_value=True)
    @patch("main.mongo_is_ready", return_value=True)
    def test_health_reports_dependencies(self, _mongo, _elastic) -> None:
        response = Response()

        result = main.health(response)

        self.assertEqual(result, {"mongodb": "ok", "elasticsearch": "ok"})
        self.assertEqual(response.status_code, 200)

    @patch("main.elasticsearch_is_ready", side_effect=RuntimeError("offline"))
    @patch("main.mongo_is_ready", return_value=True)
    def test_health_returns_503_when_dependency_fails(self, _mongo, _elastic) -> None:
        response = Response()

        result = main.health(response)

        self.assertEqual(result["elasticsearch"], "unavailable")
        self.assertEqual(response.status_code, 503)


class CorsConfigurationTests(unittest.TestCase):
    def test_frontend_origins_defaults_to_vite(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(main.frontend_origins(), ["http://localhost:5173"])

    def test_frontend_origins_parses_comma_separated_values(self) -> None:
        with patch.dict(
            os.environ,
            {"FRONTEND_ORIGINS": "https://app.example.com, http://localhost:4173"},
        ):
            self.assertEqual(
                main.frontend_origins(),
                ["https://app.example.com", "http://localhost:4173"],
            )


if __name__ == "__main__":
    unittest.main()