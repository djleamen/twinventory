import unittest
from unittest.mock import patch

from services.elastic_client import Product, insert_products, list_products, query_products


def _product(**overrides) -> Product:
    defaults = dict(
        id="dress-1",
        title="Dress",
        description="A nice dress",
        image="https://example.com/dress.jpg",
        price=49.99,
        category="dresses",
        url="https://example.com/products/dress",
    )
    return Product(**{**defaults, **overrides})


class ElasticClientTests(unittest.TestCase):
    @patch("services.elastic_client.bulk")
    def test_insert_products_bulk_indexes_with_semantic_text(self, bulk) -> None:
        insert_products([_product()])

        bulk.assert_called_once()
        _client_arg, actions = bulk.call_args.args
        self.assertEqual(actions[0]["_index"], "products")
        self.assertEqual(actions[0]["_id"], "dress-1")
        self.assertEqual(actions[0]["_source"]["semantic_text"], "Dress\n\nA nice dress")

    @patch("services.elastic_client.bulk")
    def test_insert_products_skips_bulk_when_empty(self, bulk) -> None:
        insert_products([])
        bulk.assert_not_called()

    @patch("services.elastic_client.client")
    def test_query_products_filters_by_category(self, client) -> None:
        client.search.return_value = {
            "hits": {"hits": [{"_source": vars(_product())}]}
        }

        results = query_products("dress", category="dresses", limit=5)

        self.assertEqual(results[0].id, "dress-1")
        request = client.search.call_args.kwargs
        self.assertEqual(request["size"], 5)
        self.assertEqual(request["query"]["bool"]["filter"], [{"term": {"category": "dresses"}}])

    @patch("services.elastic_client.client")
    def test_list_products_without_category_matches_all(self, client) -> None:
        client.search.return_value = {"hits": {"hits": []}}

        list_products(limit=3)

        request = client.search.call_args.kwargs
        self.assertEqual(request["query"], {"match_all": {}})
        self.assertEqual(request["size"], 3)


if __name__ == "__main__":
    unittest.main()
