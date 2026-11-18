from typing import Optional

from pydantic import BaseModel


class DailySalesSummary(BaseModel):
    date: str
    total_orders: int
    total_revenue: float
    avg_order_value: float
    by_source: dict
    by_payment_method: dict


class TopItem(BaseModel):
    food_id: Optional[str] = None
    title: str
    quantity_sold: int
    revenue: float


class TopSellingItems(BaseModel):
    period: str
    items: list[TopItem]


class RevenueStats(BaseModel):
    period: str
    data: list[dict]  # [{date, revenue, orders}, ...]
