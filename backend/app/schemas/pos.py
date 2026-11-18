from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TableOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: int
    seats: int
    status: str
    current_order_id: Optional[str] = None
    qr_code: Optional[str] = None


class TableStatusUpdate(BaseModel):
    status: str


class ShiftCreate(BaseModel):
    opening_cash: float
    notes: Optional[str] = None


class ShiftClose(BaseModel):
    closing_cash: float
    notes: Optional[str] = None


class ShiftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    staff_id: str
    created_at: datetime
    closed_at: Optional[datetime] = None
    opening_cash: float
    closing_cash: Optional[float] = None
    notes: Optional[str] = None


class ExpenseCreate(BaseModel):
    category: str
    description: Optional[str] = None
    amount: float


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    staff_id: Optional[str] = None
    category: str
    description: Optional[str] = None
    amount: float
    created_at: datetime
