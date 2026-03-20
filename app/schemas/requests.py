from pydantic import BaseModel, Field
from typing import List

class ForecastRequest(BaseModel):
    store_id: int
    product_id: int
    date: str
    recent_sales: List[float] = Field(..., description="Chronological list of recent sales, oldest to newest")

class ReorderRequest(ForecastRequest):
    lead_time: int = Field(2, description="Lead time in weeks")
    service_level_z: float = Field(1.65, description="Z-score for safety stock")
    current_inventory: float
    error_std: float = Field(..., description="Standard deviation of past forecast errors for safety stock calculation")

class BatchPredictRequest(BaseModel):
    requests: List[ForecastRequest]

