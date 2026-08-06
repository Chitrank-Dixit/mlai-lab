"""
Unit and functional tests for 30-day Daywise GPU Price Forecaster module.
"""
import unittest
import sys
from pathlib import Path
import pandas as pd

workspace_dir = Path(__file__).resolve().parent.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

from src.io_utils import load_sample_dataset
from src.daywise_forecaster import resolve_gpu_identifier, forecast_gpu_month_daywise

class TestDaywiseForecaster(unittest.TestCase):

    def setUp(self):
        self.products_df = load_sample_dataset("products.csv")

    def test_resolve_gpu_identifier_exact_sku(self):
        """Test exact SKU resolution."""
        res = resolve_gpu_identifier("RTX5060TI-16G-GIGA-EAGLE", self.products_df)
        self.assertEqual(res["sku_id"], "RTX5060TI-16G-GIGA-EAGLE")
        self.assertEqual(res["brand"], "Gigabyte")

    def test_resolve_gpu_identifier_full_name(self):
        """Test full model name resolution for user input."""
        user_input = "Gigabyte Eagle Max GeForce RTX 5060 Ti 16GB GDDR7 OC Triple Fan"
        res = resolve_gpu_identifier(user_input, self.products_df)
        self.assertEqual(res["sku_id"], "RTX5060TI-16G-GIGA-EAGLE")

    def test_resolve_gpu_identifier_partial(self):
        """Test partial model name substring resolution."""
        res = resolve_gpu_identifier("Asus Dual 5060 Ti", self.products_df)
        self.assertEqual(res["sku_id"], "RTX5060TI-16G-ASUS-DUAL")

    def test_resolve_gpu_identifier_invalid(self):
        """Test invalid identifier raises ValueError."""
        with self.assertRaises(ValueError):
            resolve_gpu_identifier("NonExistentGPUModel12345", self.products_df)

    def test_forecast_gpu_month_daywise_30_days(self):
        """Test 30-day daywise forecast for Gigabyte Eagle Max 5060 Ti."""
        gpu_name = "Gigabyte Eagle Max GeForce RTX 5060 Ti 16GB GDDR7 OC Triple Fan"
        res = forecast_gpu_month_daywise(gpu_name, horizon_days=30)
        
        self.assertIn("forecast_df", res)
        forecast_df = res["forecast_df"]
        
        # Verify 30 rows generated
        self.assertEqual(len(forecast_df), 30, "Forecast DataFrame must have 30 rows.")
        self.assertEqual(forecast_df["day_index"].tolist(), list(range(1, 31)))
        
        # Verify bounds ordering
        for _, row in forecast_df.iterrows():
            self.assertLessEqual(row["lower_bound_inr"], row["forecasted_price_inr"])
            self.assertGreaterEqual(row["upper_bound_inr"], row["forecasted_price_inr"])
            self.assertGreater(row["msrp_premium_ratio"], 0)

    def test_forecast_all_catalog_skus(self):
        """Verify daywise forecaster runs clean for all 7 catalog SKUs."""
        for sku_id in self.products_df["sku_id"]:
            res = forecast_gpu_month_daywise(sku_id, horizon_days=30)
            self.assertEqual(len(res["forecast_df"]), 30)

    def test_notebook_json_validity(self):
        """Verify that 07_gpu_monthly_daywise_forecaster.ipynb is valid JSON and has no control character errors."""
        import json
        nb_path = workspace_dir / "notebooks" / "07_gpu_monthly_daywise_forecaster.ipynb"
        self.assertTrue(nb_path.exists(), f"Notebook not found at {nb_path}")
        with open(nb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("cells", data)
        self.assertGreaterEqual(len(data["cells"]), 4)

if __name__ == "__main__":
    unittest.main()

