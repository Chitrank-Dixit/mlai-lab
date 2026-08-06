"""
Functional tests for the GPU Price Pipeline (Cleaning, Normalization, Feature Engineering).
"""
import unittest
import sys
from pathlib import Path
import pandas as pd

workspace_dir = Path(__file__).resolve().parent.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

from src.io_utils import load_sample_dataset, save_processed_dataset, load_yaml_config
from src.clean_prices import clean_price_observations
from src.normalize_prices import normalize_price_series
from src.feature_builder import build_gpu_features

class TestDataPipeline(unittest.TestCase):

    def setUp(self):
        self.products_df = load_sample_dataset("products.csv")
        self.listings_df = load_sample_dataset("product_listings.csv")
        self.obs_df = load_sample_dataset("daily_price_observations.csv")
        self.ext_df = load_sample_dataset("external_market_signals.csv")
        self.config = load_yaml_config("model_config.yaml")

    def test_price_cleaning(self):
        """Test price observation cleaning."""
        cleaned_df = clean_price_observations(self.obs_df)
        self.assertFalse(cleaned_df.empty, "Cleaned observations should not be empty.")
        self.assertIn("price_inr", cleaned_df.columns)
        self.assertTrue((cleaned_df["price_inr"] > 0).all(), "All prices should be positive.")

    def test_price_normalization_and_msrp_premium(self):
        """Test effective price calculation and verify elevated MSRP premium ratios in Indian market data."""
        cleaned_df = clean_price_observations(self.obs_df)
        norm_df = normalize_price_series(cleaned_df, self.listings_df, self.products_df)
        
        self.assertIn("total_effective_price_inr", norm_df.columns)
        self.assertIn("msrp_premium_ratio", norm_df.columns)
        
        # Verify MSRP premium ratios reflect the current Indian market surge (~1.4x to ~1.95x MSRP)
        late_july_obs = norm_df[norm_df["date"] == "2026-07-30"]
        self.assertFalse(late_july_obs.empty)
        
        avg_premium = late_july_obs["msrp_premium_ratio"].mean()
        self.assertGreaterEqual(avg_premium, 1.65, f"Expected average MSRP premium in late July to be >= 1.65, got {avg_premium:.2f}")


    def test_feature_builder_and_dataset_export(self):
        """Test end-to-end feature calculation and dataset export."""
        cleaned_df = clean_price_observations(self.obs_df)
        norm_df = normalize_price_series(cleaned_df, self.listings_df, self.products_df)
        
        lags = self.config["feature_engineering"]["lag_days"]
        windows = self.config["feature_engineering"]["rolling_windows"]
        
        featured_df = build_gpu_features(norm_df, external_df=self.ext_df, lag_days=lags, rolling_windows=windows)
        
        self.assertIn("rolling_median_7d", featured_df.columns)
        self.assertIn("price_volatility_7d", featured_df.columns)
        self.assertIn("usd_inr_rate", featured_df.columns)
        
        # Save processed dataset
        out_path = save_processed_dataset(featured_df, "featured_gpu_prices.csv")
        self.assertTrue(out_path.exists(), f"Processed dataset file not found at {out_path}")
        
        # Read back and verify row count matches all SKUs
        exported_df = pd.read_csv(out_path)
        unique_skus = exported_df["sku_id"].unique()
        self.assertEqual(len(unique_skus), 7, f"Expected 7 unique SKUs in featured dataset, found {len(unique_skus)}")

if __name__ == "__main__":
    unittest.main()
