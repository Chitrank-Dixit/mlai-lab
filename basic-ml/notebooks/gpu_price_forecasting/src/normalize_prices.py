"""
Price Normalization and Relative Metrics Calculation.
Calculates effective prices (price + shipping), MSRP premium ratios, and comparison against reference SKU.
"""
import pandas as pd

def normalize_price_series(
    obs_df: pd.DataFrame,
    listings_df: pd.DataFrame,
    products_df: pd.DataFrame,
    reference_sku_id: str = "RTX5070-12G-ASUS-TUF"
) -> pd.DataFrame:
    """
    Merge listings and products to compute:
    - total_effective_price_inr: price_inr + shipping_cost_inr
    - msrp_premium_ratio: total_effective_price_inr / msrp_inr
    - premium_over_reference: price ratio compared to baseline reference SKU on the same date
    """
    # Merge listings info
    merged = obs_df.merge(listings_df[["listing_id", "sku_id", "retailer_id"]], on="listing_id", how="left")
    merged = merged.merge(products_df[["sku_id", "chipset", "brand", "model_name", "vram_gb", "msrp_inr", "is_reference_spec"]], on="sku_id", how="left")

    # Effective total price
    merged["total_effective_price_inr"] = merged["price_inr"] + merged["shipping_cost_inr"]

    # MSRP Premium Ratio (1.0 = MSRP, 1.10 = 10% markup)
    merged["msrp_premium_ratio"] = (merged["total_effective_price_inr"] / merged["msrp_inr"]).round(4)

    # Reference SKU daily median price
    ref_prices = merged[merged["sku_id"] == reference_sku_id].groupby("date")["total_effective_price_inr"].median().reset_index()
    ref_prices.rename(columns={"total_effective_price_inr": "ref_sku_daily_price_inr"}, inplace=True)

    merged = merged.merge(ref_prices, on="date", how="left")
    merged["premium_over_reference"] = (merged["total_effective_price_inr"] / merged["ref_sku_daily_price_inr"]).round(4)

    return merged
