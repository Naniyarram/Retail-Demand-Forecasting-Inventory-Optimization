import sys
import os
import pandas as pd

# Add root folder to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_and_preprocess_data(csv_path: str) -> pd.DataFrame:
    """
    Load raw CSV and standardize schema to Step 0 contract:
    date, store_id, product_id, sales
    """
    df = pd.read_csv(csv_path)
    
    # Standardize column names
    df = df.rename(columns={
        "Store": "store_id",
        "Dept": "product_id",
        "Date": "date",
        "Weekly_Sales": "sales"
    })
    
    # Ensure date is datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # Sort for proper time series lag calculations
    df = df.sort_values(by=["store_id", "product_id", "date"]).reset_index(drop=True)
    
    return df

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate required features defined in artifacts/features.json
    - lag_1, lag_7, rolling_mean_7, month, week
    """
    df = df.copy()
    
    # Calendar features
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    
    # Lags and Rolling calculations (using shift for time-sensitive groups)
    # Group by store_id and product_id
    grouped = df.groupby(["store_id", "product_id"])["sales"]
    
    df["lag_1"] = grouped.shift(1)
    df["lag_7"] = grouped.shift(7)
    df["rolling_mean_7"] = grouped.transform(lambda x: x.shift(1).rolling(window=7, min_periods=1).mean())
    fill_mean = df["rolling_mean_7"].mean()
    if pd.isna(fill_mean):
        fill_mean = 0
    df["rolling_mean_7"] = df["rolling_mean_7"].fillna(fill_mean)
    
    # Drop rows with NaN from lagging (first few weeks per product)
    df = df.dropna().reset_index(drop=True)
    
    return df

def get_inference_features(recent_sales: list, date_str: str, store_id: int, product_id: int) -> dict:
    """
    Generate features for inference given a single request's recent sales history.
    recent_sales should be ordered oldest to newest.
    """
    if not recent_sales:
        return {}

    date_obj = pd.to_datetime(date_str)
    
    lag_1 = recent_sales[-1]
    lag_7 = recent_sales[-7] if len(recent_sales) >= 7 else recent_sales[0]
    rolling_samples = recent_sales[-7:]
    rolling_mean_7 = sum(rolling_samples) / len(rolling_samples)
    
    features = {
        "store_id": store_id,
        "product_id": product_id,
        "lag_1": lag_1,
        "lag_7": lag_7,
        "rolling_mean_7": rolling_mean_7,
        "month": date_obj.month,
        "week": date_obj.isocalendar()[1]
    }
    return features
