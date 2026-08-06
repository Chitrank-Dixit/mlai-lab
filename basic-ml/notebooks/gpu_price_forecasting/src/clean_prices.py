"""
Data Cleaning Module for GPU Price Observations.
"""
import pandas as pd
import numpy as np
from typing import Tuple

def clean_price_observations(obs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean price observations:
    - Cast date to datetime
    - Parse numeric prices
    - Handle stock boolean flags
    - Drop missing or non-positive prices
    """
    df = obs_df.copy()

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Ensure price numeric
    if df["price_inr"].dtype == object:
        df["price_inr"] = df["price_inr"].astype(str).str.replace("[^0-9.]", "", regex=True)
    df["price_inr"] = pd.to_numeric(df["price_inr"], errors="coerce")

    # Clean shipping cost
    if "shipping_cost_inr" in df.columns:
        df["shipping_cost_inr"] = pd.to_numeric(df["shipping_cost_inr"], errors="coerce").fillna(0)
    else:
        df["shipping_cost_inr"] = 0

    # Ensure boolean flags
    df["in_stock"] = df["in_stock"].astype(bool)
    if "is_local_quote" in df.columns:
        df["is_local_quote"] = df["is_local_quote"].astype(bool)

    # Filter invalid rows
    df = df[df["price_inr"] > 10000].dropna(subset=["price_inr", "date", "listing_id"])

    # Sort deterministically
    df = df.sort_values(by=["listing_id", "date"]).reset_index(drop=True)
    return df
