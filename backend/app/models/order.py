from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, Numeric, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models._base import IdMixin

ORDER_STATUSES = ("pending", "confirmed", "preparing", "ready", "out_for_delivery", "delivered", "completed", "cancelled")
ORDER_TYPES = ("delivery", "takeaway", "dine_in")
ORDER_SOURCES = ("website", "pos", "whatsapp", "table_qr")


class Order(IdMixin, Base):
    __tablename__ = "orders"
    order_number: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    rider_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    table_id: Mapped[str | None] = mapped_column(ForeignKey("pos_tables.id", ondelete="SET NULL"))
    customer_name: Mapped[str] = mapped_column(String(160))
    customer_phone: Mapped[str] = mapped_column(String(32))
    address: Mapped[str | None] = mapped_column(String(500))
    lat: Mapped[float | None]
    lng: Mapped[float | None]
    distance_km: Mapped[float | None]
    order_type: Mapped[str] = mapped_column(String(20), default="delivery")
    source: Mapped[str] = mapped_column(String(20), default="website")
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    payment_method: Mapped[str] = mapped_column(String(20), default="cash")
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    delivery_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    coupon_code: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    items: Mapped[list["OrderItem"]] = relationship(lazy="selectin", cascade="all, delete-orphan")


class OrderItem(IdMixin, Base):
    __tablename__ = "order_items"
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    food_id: Mapped[str | None] = mapped_column(ForeignKey("foods.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(160))
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int] = mapped_column(Integer)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2))
