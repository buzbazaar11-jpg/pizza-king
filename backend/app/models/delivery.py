from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models._base import IdMixin


class DeliverySettings(IdMixin, Base):
    __tablename__ = "delivery_settings"
    center_name: Mapped[str] = mapped_column(String(160), default="Restaurant")
    center_lat: Mapped[float]
    center_lng: Mapped[float]
    radius_km: Mapped[float] = mapped_column(default=7.0)
    base_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    min_order: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    block_outside: Mapped[bool] = mapped_column(Boolean, default=True)


class DeliveryArea(IdMixin, Base):
    __tablename__ = "delivery_areas"
    name: Mapped[str] = mapped_column(String(160))
    lat: Mapped[float]
    lng: Mapped[float]
    radius_km: Mapped[float] = mapped_column(default=1.0)
    fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
