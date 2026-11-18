from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RiderLocationUpdate(BaseModel):
    lat: float
    lng: float
    accuracy: Optional[float] = None
    order_id: Optional[str] = None


class RiderAssign(BaseModel):
    order_id: str
    rider_id: str


class RiderEarningsOut(BaseModel):
    total_deliveries: int
    total_earnings: float
    today_earnings: float
    this_week: float
    this_month: float


class RiderProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rider_id: str
    is_online: bool
    vehicle: Optional[str] = None
    created_at: datetime
