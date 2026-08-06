"""
SKU Validation and Integrity Engine.
Ensures strict separation between VRAM variants (e.g. 8GB vs 16GB RTX 5060 Ti).
"""
import pandas as pd
from typing import Dict, List, Tuple

def validate_sku_catalog(products_df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate product catalog for missing values, VRAM consistency,
    and distinct SKU definitions.
    """
    errors = []
    required_cols = ["sku_id", "chipset", "brand", "model_name", "vram_gb", "msrp_inr"]
    for col in required_cols:
        if col not in products_df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return False, errors

    # Check for invalid VRAM values
    invalid_vram = products_df[products_df["vram_gb"].isna() | (products_df["vram_gb"] <= 0)]
    if not invalid_vram.empty:
        errors.append(f"Invalid or missing VRAM_GB found in SKUs: {invalid_vram['sku_id'].tolist()}")

    # Verify no SKU has identical chipset & brand but different VRAM mixed under same SKU ID
    sku_counts = products_df.groupby("sku_id")["vram_gb"].nunique()
    mixed_skus = sku_counts[sku_counts > 1]
    if not mixed_skus.empty:
        errors.append(f"Mixed VRAM definitions detected for SKU IDs: {mixed_skus.index.tolist()}")

    # Check for RTX 5060 Ti specific separation (8GB vs 16GB)
    r5060ti_df = products_df[products_df["chipset"].str.contains("5060 Ti", na=False)]
    vram_variants = set(r5060ti_df["vram_gb"].dropna().unique())
    if 8 in vram_variants and 16 in vram_variants:
        # Check if 8GB and 16GB have separate SKU IDs
        skus_8g = r5060ti_df[r5060ti_df["vram_gb"] == 8]["sku_id"].unique()
        skus_16g = r5060ti_df[r5060ti_df["vram_gb"] == 16]["sku_id"].unique()
        overlap = set(skus_8g).intersection(set(skus_16g))
        if overlap:
            errors.append(f"CRITICAL: 8GB and 16GB RTX 5060 Ti variants share SKU IDs: {overlap}")

    is_valid = len(errors) == 0
    return is_valid, errors

def validate_listing_mappings(listings_df: pd.DataFrame, products_df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate that all product listings reference valid existing SKU IDs.
    """
    errors = []
    valid_skus = set(products_df["sku_id"].dropna().unique())
    listing_skus = set(listings_df["sku_id"].dropna().unique())

    unmapped = listing_skus - valid_skus
    if unmapped:
        errors.append(f"Listings reference unknown SKU IDs: {unmapped}")

    is_valid = len(errors) == 0
    return is_valid, errors
