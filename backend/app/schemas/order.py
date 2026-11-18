from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
    food_id: Optional[str] = None
    title: str
    quantity: int
    price: float


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_id: str
    food_id: Optional[str] = None
    name: str
    unit_price: float
    quantity: int
    line_total: float


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
    order_type: str = "delivery"
    payment_method: str = "cash"
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    table_no: Optional[str] = None
    coupon_code: Optional[str] = None
    notes: Optional[str] = None
    discount_amount: Optional[float] = 0.0
    delivery_charges: Optional[float] = 0.0
    amount_paid: Optional[float] = None
    source: str = "website"


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_number: int
    user_id: Optional[str] = None
    rider_id: Optional[str] = None
    customer_name: str
    customer_phone: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    order_type: str
    source: str
    status: str
    payment_method: str
    subtotal: float
    delivery_fee: float
    discount: float
    total: float
    coupon_code: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    delivered_at: Optional[datetime] = None
    items: list[OrderItemOut] = []


class StatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None
