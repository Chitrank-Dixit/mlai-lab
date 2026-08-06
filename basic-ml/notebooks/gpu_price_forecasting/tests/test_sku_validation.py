"""
Unit tests for SKU Catalog Integrity and VRAM Separation.
"""
import unittest
import sys
from pathlib import Path

# Add workspace dir to sys.path
workspace_dir = Path(__file__).resolve().parent.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

from src.io_utils import load_sample_dataset, load_yaml_config
from src.validate_skus import validate_sku_catalog, validate_listing_mappings

class TestSKUValidation(unittest.TestCase):

    def setUp(self):
        self.products_df = load_sample_dataset("products.csv")
        self.listings_df = load_sample_dataset("product_listings.csv")
        self.config = load_yaml_config("products.yaml")

    def test_catalog_validity(self):
        """Test SKU catalog validation passes without errors."""
        is_valid, errors = validate_sku_catalog(self.products_df)
        self.assertTrue(is_valid, f"Catalog validation failed with errors: {errors}")

    def test_listing_mappings_validity(self):
        """Test product listing mappings reference valid existing SKUs."""
        is_valid, errors = validate_listing_mappings(self.listings_df, self.products_df)
        self.assertTrue(is_valid, f"Listing mapping validation failed with errors: {errors}")

    def test_vram_separation_rtx5060ti(self):
        """Verify strict separation between 8GB and 16GB RTX 5060 Ti variants."""
        r5060ti_df = self.products_df[self.products_df["chipset"] == "RTX 5060 Ti"]
        
        skus_8gb = r5060ti_df[r5060ti_df["vram_gb"] == 8]["sku_id"].tolist()
        skus_16gb = r5060ti_df[r5060ti_df["vram_gb"] == 16]["sku_id"].tolist()
        
        self.assertGreaterEqual(len(skus_8gb), 1, "Should have at least one 8GB 5060 Ti SKU.")
        self.assertGreaterEqual(len(skus_16gb), 4, "Should have at least four 16GB 5060 Ti SKUs.")
        
        # Verify no overlap between 8GB and 16GB SKU IDs
        overlap = set(skus_8gb).intersection(set(skus_16gb))
        self.assertEqual(len(overlap), 0, f"Found overlapping SKU IDs between 8GB and 16GB: {overlap}")

    def test_new_card_skus_presence(self):
        """Verify the 3 newly added 5060 Ti 16GB card SKUs are present in catalog."""
        expected_new_skus = [
            "RTX5060TI-16G-ASUS-DUAL",
            "RTX5060TI-16G-MSI-SHADOW",
            "RTX5060TI-16G-GIGA-EAGLE"
        ]
        catalog_skus = self.products_df["sku_id"].tolist()
        for sku in expected_new_skus:
            self.assertIn(sku, catalog_skus, f"Missing expected new SKU: {sku}")

    def test_yaml_config_sync(self):
        """Verify products.yaml and products.csv are in sync."""
        yaml_skus = [p["sku_id"] for p in self.config["products"]]
        csv_skus = self.products_df["sku_id"].tolist()
        self.assertEqual(sorted(yaml_skus), sorted(csv_skus), "products.yaml and products.csv SKUs mismatch!")

if __name__ == "__main__":
    unittest.main()
