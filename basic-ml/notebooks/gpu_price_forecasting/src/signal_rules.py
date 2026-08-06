"""
Buy / Wait Decision Signal Engine.
Translates forecasted GPU prices and volatility metrics into target-price probability and decision labels.
"""
import numpy as np
from typing import Dict, Any

def evaluate_buy_wait_signal(
    current_price_inr: float,
    forecasted_price_7d: float,
    msrp_inr: float,
    volatility_7d: float,
    in_stock: bool,
    target_discount_pct: float = 0.05
) -> Dict[str, Any]:
    """
    Generate buy/wait decision signal.
    - target_price: msrp * (1 + discount/premium target)
    - price_trend_pct: percent change expected in next 7 days
    - buy_confidence: probability/confidence score between 0.0 and 1.0
    - recommended_action: 'STRONG_BUY', 'BUY_NOW', 'WAIT', 'OUT_OF_STOCK'
    """
    if not in_stock:
        return {
            "recommended_action": "OUT_OF_STOCK",
            "buy_confidence": 0.0,
            "expected_price_change_pct": 0.0,
            "target_price_inr": msrp_inr,
            "rationale": "Item is currently out of stock across listed retailers."
        }

    target_price = round(msrp_inr * (1.0 - target_discount_pct), 2)
    expected_change_pct = round(((forecasted_price_7d - current_price_inr) / current_price_inr) * 100, 2)

    # If forecasted price drops below target price or decreases significantly
    if forecasted_price_7d < current_price_inr and expected_change_pct <= -2.0:
        action = "WAIT"
        confidence = 0.85
        rationale = f"Price is projected to drop by {abs(expected_change_pct):.1f}% over the next 7 days to ₹{forecasted_price_7d:,.0f}."
    elif current_price_inr <= target_price:
        action = "STRONG_BUY"
        confidence = 0.95
        rationale = f"Current price (₹{current_price_inr:,.0f}) is at or below target price (₹{target_price:,.0f})."
    elif current_price_inr <= msrp_inr * 1.02 and expected_change_pct >= 0:
        action = "BUY_NOW"
        confidence = 0.78
        rationale = f"Price is near MSRP (₹{msrp_inr:,.0f}) and projected to remain stable or rise slightly."
    else:
        action = "WAIT"
        confidence = 0.70
        rationale = f"Current price (₹{current_price_inr:,.0f}) remains above MSRP/target. Forecast expects minimal immediate drop ({expected_change_pct:.1f}%)."

    return {
        "recommended_action": action,
        "buy_confidence": confidence,
        "expected_price_change_pct": expected_change_pct,
        "target_price_inr": target_price,
        "forecasted_price_7d_inr": round(forecasted_price_7d, 2),
        "current_price_inr": current_price_inr,
        "rationale": rationale
    }
