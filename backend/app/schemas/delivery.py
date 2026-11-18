from typing import Optional

from pydantic import BaseModel, ConfigDict


class DeliveryCheckIn(BaseModel):
    lat: float
    lng: float


class DeliveryCheckResult(BaseModel):
    allowed: bool
    charges: float
    zone_name: str
    reason: str


class DeliverySettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    center_name: str
    center_lat: float
    center_lng: float
    radius_km: float
    base_fee: float
    min_order: float
    block_outside: bool


class DeliverySettingsUpdate(BaseModel):
    center_name: Optional[str] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    radius_km: Optional[float] = None
    base_fee: Optional[float] = None
    min_order: Optional[float] = None
    block_outside: Optional[bool] = None


class DeliveryAreaCreate(BaseModel):
    name: str
    lat: float
    lng: float
    radius_km: float
    delivery_charges: float
    is_active: bool = True


class DeliveryAreaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    lat: float
    lng: float
    radius_km: float
    fee: float
    is_active: bool
    created_at: object  # datetime
