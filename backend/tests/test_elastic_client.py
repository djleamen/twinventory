import unittest
from unittest.mock import Mock, patch

from services.elastic_client import index_product, search_products


class ElasticClientTests(unittest.TestCase):
    @patch("services.elastic_client.get_elasticsearch_client")
    def test_search_builds_hybrid_query(self, get_client) -> None:
        client = Mock()
        client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_score": 1.25,
                        "_source": {"product_id": "dress-1", "title": "Dress"},
                    }
                ]
            }
        }
        get_client.return_value = client

        results = search_products(
            [0.0] * 1536,
            query_text="wedding",
            filters={"category": "dress", "ignored": "value"},
            limit=5,
        )

        self.assertEqual(results[0]["score"], 1.25)
        request = client.search.call_args.kwargs
        self.assertEqual(request["knn"]["k"], 5)
        self.assertEqual(request["knn"]["num_candidates"], 100)
        self.assertEqual(
            request["knn"]["filter"],
            {"bool": {"filter": [{"term": {"category": "dress"}}]}},
        )
        self.assertEqual(request["source_excludes"], ["embedding"])

    def test_search_rejects_wrong_embedding_size(self) -> None:
        with self.assertRaises(ValueError):
            search_products([0.0, 1.0])

    @patch("services.elastic_client.get_elasticsearch_client")
    def test_index_uses_product_id_as_document_id(self, get_client) -> None:
        client = Mock()
        get_client.return_value = client
        product = {"product_id": "dress-1", "embedding": [0.0] * 1536}

        index_product(product)

        client.index.assert_called_once_with(
            index="products",
            id="dress-1",
            document=product,
        )


if __name__ == "__main__":
    unittest.main()