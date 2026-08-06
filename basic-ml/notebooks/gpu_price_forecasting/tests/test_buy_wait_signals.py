"""
Functional tests for ML Forecasting and Buy/Wait Signal Evaluation.
"""
import unittest
import sys
from pathlib import Path
import pandas as pd

workspace_dir = Path(__file__).resolve().parent.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

from src.io_utils import load_sample_dataset
from src.clean_prices import clean_price_observations
from src.normalize_prices import normalize_price_series
from src.feature_builder import build_gpu_features
from src.ml_forecast import MLGPUPriceForecaster
from src.signal_rules import evaluate_buy_wait_signal

class TestBuyWaitSignals(unittest.TestCase):

    def setUp(self):
        self.products_df = load_sample_dataset("products.csv")
        self.listings_df = load_sample_dataset("product_listings.csv")
        self.obs_df = load_sample_dataset("daily_price_observations.csv")
        self.ext_df = load_sample_dataset("external_market_signals.csv")

    def test_buy_wait_signal_inflated_prices(self):
        """Verify buy/wait signal returns 'WAIT' when market prices are elevated far above MSRP."""
        msrp = 49999.0
        current_market_price = 97500.0 # ~1.95x MSRP
        forecast_7d = 96000.0 # small drop but still ~1.92x MSRP
        
        signal = evaluate_buy_wait_signal(
            current_price_inr=current_market_price,
            forecasted_price_7d=forecast_7d,
            msrp_inr=msrp,
            volatility_7d=0.015,
            in_stock=True
        )
        
        self.assertEqual(signal["recommended_action"], "WAIT", "Should recommend WAIT when market price is double MSRP.")
        self.assertIn("above MSRP/target", signal["rationale"])

    def test_ml_forecaster_pipeline(self):
        """Test ML forecaster model training and signal generation across all 7 SKUs."""
        cleaned_obs = clean_price_observations(self.obs_df)
        norm_df = normalize_price_series(cleaned_obs, self.listings_df, self.products_df)
        featured_df = build_gpu_features(norm_df, external_df=self.ext_df)
        
        forecaster = MLGPUPriceForecaster(alpha=1.0)
        results = forecaster.train_and_evaluate(featured_df, train_ratio=0.8)
        
        self.assertIn("metrics", results)
        self.assertIn("MAE_INR", results["metrics"])
        self.assertIn("RMSE_INR", results["metrics"])
        
        # Verify signal generation for all SKUs
        signals = []
        for sku_id, group in norm_df.groupby("sku_id"):
            latest = group.sort_values("date").iloc[-1]
            sig = evaluate_buy_wait_signal(
                current_price_inr=float(latest["total_effective_price_inr"]),
                forecasted_price_7d=float(latest["total_effective_price_inr"]) * 0.985,
                msrp_inr=float(latest["msrp_inr"]),
                volatility_7d=0.015,
                in_stock=bool(latest["in_stock"])
            )
            sig["sku_id"] = sku_id
            signals.append(sig)
            
        self.assertEqual(len(signals), 7, "Should generate recommendation signals for all 7 SKUs.")

if __name__ == "__main__":
    unittest.main()
