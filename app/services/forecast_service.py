import os
import joblib
import pandas as pd
import numpy as np
import json
from app.core.config import settings
from pipeline.preprocessing.preprocess import get_inference_features

class ForecastService:
    def __init__(self):
        self.model = None
        self.feature_names = []
        try:
            self._load_model()
        except Exception as e:
            print(f"Warning: Model could not be loaded at startup: {e}")
            
    def _load_model(self):
        """Loads the XGBoost model and feature names from artifacts."""
        if not os.path.exists(settings.MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {settings.MODEL_PATH}.")
        if not os.path.exists(settings.FEATURES_PATH):
            raise FileNotFoundError(f"Features contract not found at {settings.FEATURES_PATH}.")
            
        self.model = joblib.load(settings.MODEL_PATH)
        with open(settings.FEATURES_PATH, "r") as f:
            self.feature_names = json.load(f)["features"]
            
    def predict(self, store_id: int, product_id: int, date: str, recent_sales: list) -> float:
        """
        Predicts demand for a specific store and product.
        Transforms recent sales into the matching feature vector.
        """
        if not self.model:
            self._load_model()
            
        raw_features = get_inference_features(recent_sales, date, store_id, product_id)
        
        # Ensure correct order of features and fill missing with 0
        feature_vector = {f: raw_features.get(f, 0) for f in self.feature_names}
        df_features = pd.DataFrame([feature_vector])
        
        forecast = self.model.predict(df_features)[0]
        return float(round(forecast, 2))

forecast_service = ForecastService()
