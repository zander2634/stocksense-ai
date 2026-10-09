from pydantic import BaseModel
from typing import List, Optional

class ForecastResponse(BaseModel):
    product_id: int
    forecast_days: int
    predicted_demand: List[int]
    total_predicted_demand: int
    average_daily_demand: float
    confidence: str
    method: str
    forecast_start_date: Optional[str] = None
    note: Optional[str] = None


class ReorderRecommendation(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    reorder_level: int
    average_daily_demand: float
    lead_time_days: int
    safety_stock: float
    reorder_point: float
    recommended_reorder_quantity: int
    urgency: str
    should_reorder: bool
    forecast_30_days: ForecastResponse