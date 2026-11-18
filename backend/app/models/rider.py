from datetime import datetime
from sqlalchemy import String, ForeignKey, Numeric, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models._base import IdMixin


class RiderLocation(IdMixin, Base):
    __tablename__ = "rider_locations"
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lat: Mapped[float]
    lng: Mapped[float]
    speed: Mapped[float | None]


class RiderSettings(IdMixin, Base):
    __tablename__ = "rider_settings"
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    vehicle: Mapped[str | None] = mapped_column(String(60))
    prefs: Mapped[dict | None] = mapped_column(JSON)


class RiderDocument(IdMixin, Base):
    __tablename__ = "rider_documents"
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    doc_type: Mapped[str] = mapped_column(String(40))
    url: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="pending")


class RiderSchedule(IdMixin, Base):
    __tablename__ = "rider_schedule"
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RiderMessage(IdMixin, Base):
    __tablename__ = "rider_messages"
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    from_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    body: Mapped[str] = mapped_column(Text)


class RiderNotification(IdMixin, Base):
    __tablename__ = "rider_notifications"
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str | None] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class RiderPayout(IdMixin, Base):
    __tablename__ = "rider_payouts"
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    note: Mapped[str | None] = mapped_column(Text)
