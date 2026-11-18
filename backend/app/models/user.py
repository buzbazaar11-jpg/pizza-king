from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models._base import IdMixin

ROLES = ("admin", "staff", "rider", "customer")


class User(IdMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    roles: Mapped[list["UserRole"]] = relationship(back_populates="user", lazy="selectin", cascade="all, delete-orphan")

    @property
    def role_names(self) -> list[str]:
        return [r.role for r in self.roles]


class UserRole(IdMixin, Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role"),)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))
    user: Mapped[User] = relationship(back_populates="roles")


class UserAddress(IdMixin, Base):
    __tablename__ = "user_addresses"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(50), default="Home")
    address: Mapped[str] = mapped_column(String(500))
    lat: Mapped[float | None]
    lng: Mapped[float | None]
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class PushToken(IdMixin, Base):
    __tablename__ = "push_tokens"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(500), unique=True)
    app: Mapped[str] = mapped_column(String(20), default="web")
