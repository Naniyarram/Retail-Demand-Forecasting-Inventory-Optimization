import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Add root folder to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.core.config import settings
from pipeline.preprocessing.preprocess import load_and_preprocess_data, generate_features

def main():
    print("🚀 Starting Data Pipeline & Model Training...")
    
    raw_path = os.path.join(settings.DATA_DIR, "train.csv")
    if not os.path.exists(raw_path):
        print(f"Error: Training file not found at {raw_path}")
        return
        
    print(f"Loading data from {raw_path}...")
    df = load_and_preprocess_data(raw_path)
    
    print("Generating features...")
    df = generate_features(df)
    
    print("Reading feature contract...")
    try:
        with open(settings.FEATURES_PATH, "r") as f:
            feature_contract = json.load(f)["features"]
    except FileNotFoundError:
        print(f"Features file {settings.FEATURES_PATH} not found!")
        return
        
    print(f"Using features: {feature_contract}")
    
    # Split Data (Time-based: 80% train, 20% test)
    split_date = df["date"].quantile(0.8)
    train_df = df[df["date"] <= split_date]
    test_df = df[df["date"] > split_date]
    
    X_train = train_df[feature_contract]
    y_train = train_df["sales"]
    X_test = test_df[feature_contract]
    y_test = test_df["sales"]
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    print("Training XGBRegressor...")
    model = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    preds = model.predict(X_test)
    
    # Mask zeros to avoid division by zero in MAPE
    non_zero = y_test != 0
    mape = float(np.mean(np.abs((y_test[non_zero] - preds[non_zero]) / y_test[non_zero])) * 100)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    mae = float(mean_absolute_error(y_test, preds))
    
    metrics = {
        "RMSE": rmse,
        "MAPE": mape,
        "MAE": mae
    }
    print(f"📊 Metrics: {metrics}")
    
    print("Saving artifacts...")
    os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
    
    # Model Versioning Logic
    existing_models = [f for f in os.listdir(settings.ARTIFACTS_DIR) if f.startswith("model_v") and f.endswith(".pkl")]
    versions = [int(f.replace("model_v", "").replace(".pkl", "")) for f in existing_models]
    next_v = max(versions) + 1 if versions else 1
    
    versioned_model_path = os.path.join(settings.ARTIFACTS_DIR, f"model_v{next_v}.pkl")
    joblib.dump(model, versioned_model_path)
    joblib.dump(model, settings.MODEL_PATH) # latest.pkl
    
    with open(settings.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"✅ Training complete. Model saved to {versioned_model_path} and {settings.MODEL_PATH}")

if __name__ == "__main__":
    main()
