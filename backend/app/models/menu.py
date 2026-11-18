from sqlalchemy import String, Boolean, ForeignKey, Integer, Numeric, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models._base import IdMixin


class Category(IdMixin, Base):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(String(120))
    name_ur: Mapped[str | None] = mapped_column(String(120))
    image_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Food(IdMixin, Base):
    __tablename__ = "foods"
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    name_ur: Mapped[str | None] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(500))
    sku: Mapped[str | None] = mapped_column(String(60), unique=True)
    stock: Mapped[int | None] = mapped_column(Integer)
    options: Mapped[dict | None] = mapped_column(JSON)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)


class Deal(IdMixin, Base):
    __tablename__ = "deals"
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    original_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(500))
    items: Mapped[list | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Review(IdMixin, Base):
    __tablename__ = "reviews"
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    food_id: Mapped[str | None] = mapped_column(ForeignKey("foods.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
