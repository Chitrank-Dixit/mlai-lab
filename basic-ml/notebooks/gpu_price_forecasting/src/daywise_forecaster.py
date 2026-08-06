"""
Daywise GPU Price Forecaster Module.
Provides 30-day daywise price forecasting given any GPU name, substring, or SKU ID.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

workspace_dir = Path(__file__).resolve().parent.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

from src.io_utils import load_sample_dataset, load_yaml_config
from src.clean_prices import clean_price_observations
from src.normalize_prices import normalize_price_series
from src.feature_builder import build_gpu_features
from src.ml_forecast import MLGPUPriceForecaster
from src.signal_rules import evaluate_buy_wait_signal


def resolve_gpu_identifier(gpu_input: str, products_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Resolve a user-provided GPU name, substring, or SKU ID to product catalog metadata.
    """
    clean_input = gpu_input.strip().lower()
    
    # 1. Exact match on sku_id
    sku_match = products_df[products_df["sku_id"].str.lower() == clean_input]
    if not sku_match.empty:
        return sku_match.iloc[0].to_dict()

    # 2. Match model_name contains input
    model_match = products_df[products_df["model_name"].str.lower().str.contains(clean_input)]
    if not model_match.empty:
        return model_match.iloc[0].to_dict()

    # 3. Substring keywords token matching
    tokens = [t for t in clean_input.split() if len(t) > 2]
    best_score = 0
    best_row = None
    
    for _, row in products_df.iterrows():
        name_lower = f"{row['brand']} {row['model_name']} {row['sku_id']}".lower()
        matches = sum(1 for token in tokens if token in name_lower)
        if matches > best_score:
            best_score = matches
            best_row = row
            
    if best_row is not None and best_score >= 2:
        return best_row.to_dict()
        
    raise ValueError(f"Could not resolve GPU identifier '{gpu_input}'. Please check spelling or SKU catalog.")

def forecast_gpu_month_daywise(
    gpu_input: str,
    horizon_days: int = 30
) -> Dict[str, Any]:
    """
    Forecast GPU prices day-by-day for a full month (horizon_days=30) given any GPU name or SKU ID.
    
    Returns:
        Dict containing GPU metadata, current price, monthly forecast summary,
        daywise forecast DataFrame, and buy/wait recommendations.
    """
    products_df = load_sample_dataset("products.csv")
    listings_df = load_sample_dataset("product_listings.csv")
    obs_df = load_sample_dataset("daily_price_observations.csv")
    ext_df = load_sample_dataset("external_market_signals.csv")
    
    gpu_info = resolve_gpu_identifier(gpu_input, products_df)
    sku_id = gpu_info["sku_id"]
    msrp_inr = float(gpu_info["msrp_inr"])
    
    # Run cleaning & normalization
    cleaned_obs = clean_price_observations(obs_df)
    norm_df = normalize_price_series(cleaned_obs, listings_df, products_df)
    featured_df = build_gpu_features(norm_df, external_df=ext_df)
    
    # Fit forecaster model on overall dataset
    forecaster = MLGPUPriceForecaster(alpha=1.0)
    _ = forecaster.train_and_evaluate(featured_df, train_ratio=0.8)
    
    # Filter series for target SKU
    sku_series = norm_df[norm_df["sku_id"] == sku_id].sort_values("date")
    if sku_series.empty:
        raise ValueError(f"No price observation series found for SKU ID '{sku_id}'.")
        
    last_row = sku_series.iloc[-1]
    current_price = float(last_row["total_effective_price_inr"])
    last_date = pd.to_datetime(last_row["date"])
    last_date_str = last_date.strftime("%Y-%m-%d")

    
    # Calculate historical daily trend rate & volatility std dev
    recent_prices = sku_series["total_effective_price_inr"].values
    if len(recent_prices) >= 3:
        price_diffs = np.diff(recent_prices)
        daily_drift = float(np.mean(price_diffs))
        daily_volatility = float(np.std(price_diffs) if len(price_diffs) > 1 else 300.0)
    else:
        daily_drift = 50.0
        daily_volatility = 300.0
        
    # Generate daywise forecasts for 30 days
    forecast_rows = []
    for day in range(1, horizon_days + 1):
        fc_date = (last_date + timedelta(days=day)).strftime("%Y-%m-%d")
        
        # Expected price trajectory (linear drift with damping factor + slight mean reversion)
        projected_price = current_price + (daily_drift * day * (0.98 ** day))
        projected_price = round(max(projected_price, msrp_inr * 0.90), 2)
        
        # Confidence interval width expands as sqrt of forecast horizon
        ci_margin = round(1.96 * daily_volatility * np.sqrt(day), 2)
        lower_bound = round(max(projected_price - ci_margin, msrp_inr * 0.85), 2)
        upper_bound = round(projected_price + ci_margin, 2)
        
        msrp_premium = round(projected_price / msrp_inr, 4)
        pct_change = round(((projected_price - current_price) / current_price) * 100, 2)
        
        forecast_rows.append({
            "day_index": day,
            "date": fc_date,
            "sku_id": sku_id,
            "model_name": gpu_info["model_name"],
            "forecasted_price_inr": projected_price,
            "lower_bound_inr": lower_bound,
            "upper_bound_inr": upper_bound,
            "msrp_inr": msrp_inr,
            "msrp_premium_ratio": msrp_premium,
            "expected_change_pct": pct_change
        })
        
    forecast_df = pd.DataFrame(forecast_rows)
    
    # 7-day and 30-day Buy/Wait Signal evaluation
    fc_7d = float(forecast_df.iloc[min(6, horizon_days - 1)]["forecasted_price_inr"])
    fc_30d = float(forecast_df.iloc[-1]["forecasted_price_inr"])
    
    signal_7d = evaluate_buy_wait_signal(
        current_price_inr=current_price,
        forecasted_price_7d=fc_7d,
        msrp_inr=msrp_inr,
        volatility_7d=daily_volatility / current_price,
        in_stock=bool(last_row["in_stock"])
    )
    
    end_price = float(forecast_df.iloc[-1]["forecasted_price_inr"])
    min_price = float(forecast_df["forecasted_price_inr"].min())
    max_price = float(forecast_df["forecasted_price_inr"].max())
    month_change_pct = round(((end_price - current_price) / current_price) * 100, 2)
    
    return {
        "gpu_info": gpu_info,
        "last_observed_date": last_date_str,
        "current_price_inr": current_price,
        "end_of_month_forecast_inr": end_price,
        "monthly_min_forecast_inr": min_price,
        "monthly_max_forecast_inr": max_price,
        "monthly_price_change_pct": month_change_pct,
        "signal_7d": signal_7d,
        "forecast_df": forecast_df
    }

if __name__ == "__main__":
    test_input = "Gigabyte Eagle Max GeForce RTX 5060 Ti 16GB GDDR7 OC Triple Fan"
    res = forecast_gpu_month_daywise(test_input, horizon_days=30)
    print(f"Forecast for {res['gpu_info']['model_name']}:")
    print(f"Current Price: ₹{res['current_price_inr']:,.2f}")
    print(f"30-Day Forecast End Price: ₹{res['end_of_month_forecast_inr']:,.2f} ({res['monthly_price_change_pct']:+.2f}%)")
    print(res["forecast_df"].head(10))
