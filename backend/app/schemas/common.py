from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(LoginIn):
    full_name: str | None = None
    phone: str | None = None
    password: str = Field(min_length=8)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    roles: list[str]


class UserOut(ORM):
    id: str
    email: str
    full_name: str | None
    phone: str | None
    is_active: bool
    role_names: list[str]
    created_at: datetime


class StaffCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    phone: str | None = None
    role: str = Field(pattern="^(admin|staff|rider)$")


class CartItem(BaseModel):
    food_id: str
    quantity: int = Field(ge=1, le=100)


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    order_type: str = Field(default="delivery", pattern="^(delivery|takeaway|dine_in)$")
    source: str = Field(default="website", pattern="^(website|pos|whatsapp|table_qr)$")
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    table_id: str | None = None
    payment_method: str = "cash"
    coupon_code: str | None = None
    notes: str | None = None
    items: list[CartItem] = Field(min_length=1)


class OrderItemOut(ORM):
    id: str
    food_id: str | None
    name: str
    unit_price: float
    quantity: int
    line_total: float


class OrderOut(ORM):
    id: str
    order_number: int
    user_id: str | None
    rider_id: str | None
    table_id: str | None
    customer_name: str
    customer_phone: str
    address: str | None
    lat: float | None
    lng: float | None
    distance_km: float | None
    order_type: str
    source: str
    status: str
    payment_method: str
    subtotal: float
    delivery_fee: float
    discount: float
    total: float
    coupon_code: str | None
    notes: str | None
    created_at: datetime
    items: list[OrderItemOut]


class StatusIn(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|preparing|ready|out_for_delivery|delivered|completed|cancelled)$")


class AssignRiderIn(BaseModel):
    rider_id: str


class DeliveryCheckIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class DeliveryCheckOut(BaseModel):
    allowed: bool
    distance_km: float
    fee: float
    area: str | None
    reason: str | None = None


class CouponCheckIn(BaseModel):
    code: str
    subtotal: float


class GpsIn(BaseModel):
    lat: float
    lng: float
    speed: float | None = None
