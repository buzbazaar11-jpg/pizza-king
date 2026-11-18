from sqlalchemy import String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models._base import IdMixin


class WebsiteSettings(IdMixin, Base):
    __tablename__ = "website_settings"
    brand_name: Mapped[str] = mapped_column(String(160), default="The Young Malang")
    tagline: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    whatsapp: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str | None] = mapped_column(String(500))
    opening_hours: Mapped[dict | None] = mapped_column(JSON)
    extra: Mapped[dict | None] = mapped_column(JSON)


class Testimonial(IdMixin, Base):
    __tablename__ = "testimonials"
    name: Mapped[str] = mapped_column(String(120))
    text: Mapped[str] = mapped_column(Text)
    rating: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
