import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Retail Demand Forecasting API"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    ARTIFACTS_DIR: str = os.path.join(BASE_DIR, "artifacts")
    
    # Specific artifact paths
    MODEL_PATH: str = os.path.join(ARTIFACTS_DIR, "latest.pkl")
    METRICS_PATH: str = os.path.join(ARTIFACTS_DIR, "metrics.json")
    FEATURES_PATH: str = os.path.join(ARTIFACTS_DIR, "features.json")
    
    # External API
    GROQ_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
