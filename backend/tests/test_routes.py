import os
import unittest
from unittest.mock import patch

from fastapi import Response
from pydantic import ValidationError

import main
from routers.recs import RecommendationQuery, query_recommendations


class RecommendationRouteTests(unittest.TestCase):
    @patch("routers.recs.search_products")
    def test_query_forwards_vector_text_filters_and_limit(self, search_products) -> None:
        search_products.return_value = [{"product_id": "dress-1", "score": 0.9}]
        request = RecommendationQuery(
            query_vector=[0.0] * 1536,
            query_text="wedding",
            category="dress",
            limit=5,
        )

        response = query_recommendations(request)

        self.assertEqual(response["results"][0]["product_id"], "dress-1")
        search_products.assert_called_once_with(
            request.query_vector,
            query_text="wedding",
            filters={"category": "dress"},
            limit=5,
        )

    def test_query_rejects_out_of_range_limit(self) -> None:
        with self.assertRaises(ValidationError):
            RecommendationQuery(query_vector=[0.0] * 1536, limit=0)

    def test_query_rejects_wrong_embedding_size(self) -> None:
        with self.assertRaises(ValidationError):
            RecommendationQuery(query_vector=[0.0])


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