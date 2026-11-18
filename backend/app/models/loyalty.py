from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, Numeric, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models._base import IdMixin


class Coupon(IdMixin, Base):
    __tablename__ = "coupons"
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    discount_type: Mapped[str] = mapped_column(String(10), default="percent")  # percent|fixed
    value: Mapped[float] = mapped_column(Numeric(10, 2))
    min_order: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    max_uses: Mapped[int | None] = mapped_column(Integer)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CouponRedemption(IdMixin, Base):
    __tablename__ = "coupon_redemptions"
    coupon_id: Mapped[str] = mapped_column(ForeignKey("coupons.id", ondelete="CASCADE"))
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))


class LoyaltyTransaction(IdMixin, Base):
    __tablename__ = "loyalty_transactions"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    order_id: Mapped[str | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))
    points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(60))


class Referral(IdMixin, Base):
    __tablename__ = "referrals"
    referrer_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    referred_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    rewarded: Mapped[bool] = mapped_column(Boolean, default=False)
