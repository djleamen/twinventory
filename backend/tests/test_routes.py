import os
import unittest
from unittest.mock import patch

from fastapi import Response
from pydantic import ValidationError

import main
from routers.recs import RecommendationQuery, query_recommendations
from services.elastic_client import Product


class RecommendationRouteTests(unittest.TestCase):
    @patch("routers.recs.query_products")
    def test_query_with_text_forwards_to_query_products(self, query_products) -> None:
        query_products.return_value = [
            Product(
                id="dress-1",
                title="Dress",
                description="desc",
                image="img",
                price=10.0,
                category="dress",
                url="url",
            )
        ]
        request = RecommendationQuery(query_text="wedding", category="dress", limit=5)

        response = query_recommendations(request)

        self.assertEqual(response["results"][0].id, "dress-1")
        query_products.assert_called_once_with("wedding", category="dress", limit=5)

    @patch("routers.recs.list_products")
    def test_query_without_text_forwards_to_list_products(self, list_products) -> None:
        list_products.return_value = []
        request = RecommendationQuery(category="dress", limit=5)

        query_recommendations(request)

        list_products.assert_called_once_with(category="dress", limit=5)

    def test_query_rejects_out_of_range_limit(self) -> None:
        with self.assertRaises(ValidationError):
            RecommendationQuery(limit=0)


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