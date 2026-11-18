from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, Numeric, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models._base import IdMixin


class PosTable(IdMixin, Base):
    __tablename__ = "pos_tables"
    number: Mapped[int] = mapped_column(Integer, unique=True)
    seats: Mapped[int] = mapped_column(Integer, default=4)
    status: Mapped[str] = mapped_column(String(20), default="available")  # available|occupied|reserved
    qr_code: Mapped[str | None] = mapped_column(String(64), unique=True)
    current_order_id: Mapped[str | None] = mapped_column(String(36))


class PosShift(IdMixin, Base):
    __tablename__ = "pos_shifts"
    staff_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    opening_cash: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    closing_cash: Mapped[float | None] = mapped_column(Numeric(10, 2))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)


class PosExpense(IdMixin, Base):
    __tablename__ = "pos_expenses"
    staff_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    category: Mapped[str] = mapped_column(String(60))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    description: Mapped[str | None] = mapped_column(Text)
