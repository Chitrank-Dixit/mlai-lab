"""
Baseline Forecaster Module.
Provides Moving Median and EWMA (Exponentially Weighted Moving Average) baselines for GPU prices.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class MovingMedianForecaster:
    def __init__(self, window: int = 7):
        self.window = window

    def fit_predict(self, series: pd.Series, horizon: int = 7) -> np.ndarray:
        """
        Predict future prices as the moving median over the last `window` observations.
        """
        last_median = series.tail(self.window).median()
        return np.full(horizon, last_median)

class EWMAForecaster:
    def __init__(self, span: int = 7):
        self.span = span

    def fit_predict(self, series: pd.Series, horizon: int = 7) -> np.ndarray:
        """
        Predict future prices using Exponentially Weighted Moving Average.
        """
        ewma_val = series.ewm(span=self.span, adjust=False).mean().iloc[-1]
        return np.full(horizon, ewma_val)

def evaluate_forecast(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate baseline metrics: MAE, RMSE, MAPE.
    """
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mape = float(np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100)

    return {
        "MAE_INR": round(mae, 2),
        "RMSE_INR": round(rmse, 2),
        "MAPE_Percent": round(mape, 2)
    }
