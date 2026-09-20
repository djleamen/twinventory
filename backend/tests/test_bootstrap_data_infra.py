import os
import unittest

os.environ.setdefault("ELASTICSEARCH_URL", "http://localhost:9200")
os.environ.setdefault("ELASTICSEARCH_API_KEY", "test-key")

from scripts.bootstrap_data_infra import product_mappings


class DataInfrastructureBootstrapTests(unittest.TestCase):
    def test_product_mapping_matches_current_schema(self) -> None:
        properties = product_mappings()["properties"]

        self.assertEqual(properties["id"]["type"], "keyword")
        self.assertEqual(properties["category"]["type"], "keyword")
        self.assertEqual(properties["semantic_text"]["type"], "semantic_text")
        self.assertNotIn("embedding", properties)


if __name__ == "__main__":
    unittest.main()