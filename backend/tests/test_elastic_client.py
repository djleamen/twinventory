import os
import unittest
from unittest.mock import patch

os.environ.setdefault("ELASTICSEARCH_URL", "http://localhost:9200")
os.environ.setdefault("ELASTICSEARCH_API_KEY", "test-key")

from services.elastic_client import Product, insert_products, list_products, query_products


class ElasticClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.product = Product(
            id="dress-1",
            title="Blue Dress",
            description="Formal summer dress",
            image="https://example.com/dress.jpg",
            price=89.0,
            category="dress",
            url="https://example.com/products/dress",
        )

    @patch("services.elastic_client.bulk")
    def test_insert_products_builds_semantic_text(self, bulk) -> None:
        insert_products([self.product])

        actions = bulk.call_args.args[1]
        self.assertEqual(actions[0]["_id"], "dress-1")
        self.assertEqual(
            actions[0]["_source"]["semantic_text"],
            "Blue Dress\n\nFormal summer dress",
        )

    @patch("services.elastic_client.client.search")
    def test_query_products_builds_semantic_search(self, search) -> None:
        search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "id": self.product.id,
                            "title": self.product.title,
                            "description": self.product.description,
                            "image": self.product.image,
                            "price": self.product.price,
                            "category": self.product.category,
                            "url": self.product.url,
                        }
                    }
                ]
            }
        }

        results = query_products(
            "summer wedding",
            category="dress",
            limit=5,
        )

        self.assertEqual(results, [self.product])
        request = search.call_args.kwargs
        self.assertEqual(
            request["query"],
            {
                "bool": {
                    "must": [{"match": {"semantic_text": "summer wedding"}}],
                    "filter": [{"term": {"category": "dress"}}],
                }
            },
        )
        self.assertEqual(request["size"], 5)
        self.assertEqual(request["source_excludes"], ["semantic_text"])

    @patch("services.elastic_client.client.search")
    def test_list_products_filters_by_category(self, search) -> None:
        search.return_value = {"hits": {"hits": []}}

        results = list_products(category="dress", limit=10)

        self.assertEqual(results, [])
        search.assert_called_once_with(
            index="products",
            query={"term": {"category": "dress"}},
            size=10,
            source_excludes=["semantic_text"],
        )


if __name__ == "__main__":
    unittest.main()
