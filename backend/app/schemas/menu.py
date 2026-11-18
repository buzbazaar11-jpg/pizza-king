from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    image_url: Optional[str] = None
    sort_order: int
    is_active: bool
    created_at: datetime


class FoodCreate(BaseModel):
    category_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    sku: Optional[str] = None
    stock: Optional[int] = None
    preparation_time_min: int = 15


class FoodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_available: bool
    is_featured: bool
    sku: Optional[str] = None
    stock: Optional[int] = None
    created_at: datetime


class FoodUpdate(BaseModel):
    category_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    sku: Optional[str] = None
    stock: Optional[int] = None
    preparation_time_min: Optional[int] = None


class DealCreate(BaseModel):
    title: str
    description: Optional[str] = None
    original_price: float
    deal_price: float
    image_url: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: bool = True
    food_item_ids: list[str] = []


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str] = None
    original_price: Optional[float] = None
    price: float
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
