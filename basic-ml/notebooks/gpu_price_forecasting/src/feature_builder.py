"""
Feature Engineering Module for Time-Series GPU Price Forecasting.
Generates price lags, rolling statistics (median, std/volatility), and merges external signals.
"""
import pandas as pd
import numpy as np
from typing import List

def build_gpu_features(
    df: pd.DataFrame,
    external_df: pd.DataFrame = None,
    lag_days: List[int] = [1, 3, 7, 14],
    rolling_windows: List[int] = [3, 7, 14]
) -> pd.DataFrame:
    """
    Build time-series features grouped by SKU or listing.
    """
    feat_df = df.copy()
    feat_df["date"] = pd.to_datetime(feat_df["date"])
    feat_df = feat_df.sort_values(by=["sku_id", "date"]).reset_index(drop=True)

    # Calculate lag features
    for lag in lag_days:
        feat_df[f"price_lag_{lag}d"] = feat_df.groupby("sku_id")["total_effective_price_inr"].shift(lag)
        feat_df[f"price_diff_lag_{lag}d"] = feat_df["total_effective_price_inr"] - feat_df[f"price_lag_{lag}d"]

    # Calculate rolling statistics
    for window in rolling_windows:
        feat_df[f"rolling_median_{window}d"] = feat_df.groupby("sku_id")["total_effective_price_inr"].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).median()
        )
        feat_df[f"rolling_std_{window}d"] = feat_df.groupby("sku_id")["total_effective_price_inr"].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).std()
        ).fillna(0)
        # Volatility = std / rolling_median
        feat_df[f"price_volatility_{window}d"] = (
            feat_df[f"rolling_std_{window}d"] / feat_df[f"rolling_median_{window}d"].replace(0, np.nan)
        ).fillna(0).round(4)

    # Merge external signals if provided
    if external_df is not None and not external_df.empty:
        ext = external_df.copy()
        ext["date"] = pd.to_datetime(ext["date"])
        feat_df = feat_df.merge(ext, on="date", how="left")

    return feat_df
