from pydantic import BaseModel
from typing import Optional

class ForecastResponse(BaseModel):
    store_id: int
    product_id: int
    date: str
    forecast: float

class ReorderResponse(ForecastResponse):
    reorder_point: float
    recommended_reorder_qty: float
    action: str
    inventory_gap: float
    weeks_of_inventory: Optional[float] = None
    target_woi: str
    utilization: float
