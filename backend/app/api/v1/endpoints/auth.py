"""Authentication & user management endpoints."""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, role_required
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserAddress, UserRole
from app.schemas.auth import AddressCreate, AddressOut, StaffCreate, Token, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])

DB = Annotated[AsyncSession, Depends(get_db)]


def _user_to_out(user: User) -> UserOut:
    roles = [r.role for r in user.roles] if hasattr(user, "roles") and user.roles else []
    primary_role = roles[0] if roles else "customer"
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        is_active=user.is_active,
        created_at=user.created_at,
        role=primary_role,
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: DB):
    existing = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    db.add(UserRole(user_id=user.id, role="customer"))
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": user.id})
    return Token(access_token=token, user=_user_to_out(user))


@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    user = (await db.execute(select(User).where(User.email == form.username))).scalar_one_or_none()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is disabled")
    token = create_access_token({"sub": user.id})
    return Token(access_token=token, user=_user_to_out(user))


@router.get("/me", response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return _user_to_out(current_user)


@router.put("/me", response_model=UserOut)
async def update_me(
    payload: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    db: DB,
):
    allowed = {"full_name", "phone"}
    for key, value in payload.items():
        if key in allowed:
            setattr(current_user, key, value)
    await db.commit()
    await db.refresh(current_user)
    return _user_to_out(current_user)


@router.post("/staff", response_model=UserOut, status_code=201)
async def create_staff(
    payload: StaffCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    existing = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    db.add(UserRole(user_id=user.id, role=payload.role))
    await db.commit()
    await db.refresh(user)
    return _user_to_out(user)


@router.get("/staff", response_model=list[UserOut])
async def list_staff(
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    # Users who have a role other than customer
    subq = select(UserRole.user_id).where(UserRole.role != "customer").distinct()
    rows = (await db.execute(select(User).where(User.id.in_(subq)))).scalars().all()
    return [_user_to_out(u) for u in rows]


@router.put("/staff/{user_id}/toggle", response_model=UserOut)
async def toggle_staff(
    user_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)
    return _user_to_out(user)
