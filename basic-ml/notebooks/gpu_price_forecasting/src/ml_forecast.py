"""
ML Forecasting Pipeline for GPU Price Forecasting.
Uses scikit-learn Ridge regression / XGBoost with temporal feature windows.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import Dict, Tuple

class MLGPUPriceForecaster:
    def __init__(self, alpha: float = 1.0):
        self.model = Ridge(alpha=alpha)
        self.feature_cols = []

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract feature matrix X and target y (total_effective_price_inr).
        """
        ignore_cols = ["date", "listing_id", "sku_id", "retailer_id", "listing_title", "url_or_ref", "chipset", "brand", "model_name", "observation_id"]
        feature_candidates = [c for c in df.columns if c not in ignore_cols and not c.startswith("target")]

        # Filter numeric features only
        numeric_df = df[feature_candidates].select_dtypes(include=[np.number]).dropna()
        y = df.loc[numeric_df.index, "total_effective_price_inr"]

        self.feature_cols = numeric_df.columns.tolist()
        return numeric_df, y

    def train_and_evaluate(self, df: pd.DataFrame, train_ratio: float = 0.8) -> Dict:
        """
        Train ML forecaster with time-based split and evaluate.
        """
        clean_df = df.dropna(subset=["price_lag_1d", "rolling_median_7d"]).copy()
        X, y = self.prepare_data(clean_df)

        split_idx = int(len(X) * train_ratio)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_test)

        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        mape = float(np.mean(np.abs((y_test - preds) / y_test)) * 100)

        feature_importance = dict(zip(self.feature_cols, self.model.coef_.round(4)))

        return {
            "metrics": {
                "MAE_INR": round(mae, 2),
                "RMSE_INR": round(rmse, 2),
                "MAPE_Percent": round(mape, 2)
            },
            "predictions": preds,
            "y_test": y_test.values,
            "feature_coefficients": feature_importance
        }
