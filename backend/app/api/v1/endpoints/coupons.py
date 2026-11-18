"""Coupon validation and CRUD."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import role_required
from app.models.loyalty import Coupon
from app.models.user import User

router = APIRouter(prefix="/coupons", tags=["Coupons"])

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post("/validate")
async def validate_coupon(payload: dict, db: DB):
    code: str = payload.get("code", "")
    order_total: float = float(payload.get("order_total", 0))

    coupon = (
        await db.execute(
            select(Coupon).where(Coupon.code == code.upper(), Coupon.is_active.is_(True))
        )
    ).scalar_one_or_none()

    if not coupon:
        return {"valid": False, "discount_amount": 0.0, "message": "Invalid or expired coupon code"}

    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        return {"valid": False, "discount_amount": 0.0, "message": "Coupon usage limit reached"}

    if coupon.expires_at and coupon.expires_at < datetime.now(timezone.utc):
        return {"valid": False, "discount_amount": 0.0, "message": "Coupon has expired"}

    min_order = float(coupon.min_order or 0)
    if order_total < min_order:
        return {
            "valid": False,
            "discount_amount": 0.0,
            "message": f"Minimum order amount of Rs {min_order:,.0f} required",
        }

    if coupon.discount_type == "percent":
        discount = order_total * float(coupon.value) / 100
    else:
        discount = float(coupon.value)

    return {
        "valid": True,
        "discount_amount": round(discount, 2),
        "message": f"Coupon applied! You save Rs {discount:,.0f}",
    }


@router.get("")
async def list_coupons(
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    rows = (await db.execute(select(Coupon).order_by(Coupon.created_at.desc()))).scalars().all()
    return [
        {
            "id": c.id,
            "code": c.code,
            "discount_type": c.discount_type,
            "value": float(c.value),
            "min_order": float(c.min_order),
            "max_uses": c.max_uses,
            "used_count": c.used_count,
            "expires_at": c.expires_at,
            "is_active": c.is_active,
        }
        for c in rows
    ]


@router.post("", status_code=201)
async def create_coupon(
    payload: dict,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    coupon = Coupon(
        code=str(payload.get("code", "")).upper(),
        discount_type=payload.get("discount_type", "percent"),
        value=payload.get("value", 0),
        min_order=payload.get("min_order", 0),
        max_uses=payload.get("max_uses"),
        expires_at=payload.get("expires_at"),
        is_active=payload.get("is_active", True),
    )
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    return {"id": coupon.id, "code": coupon.code}


@router.put("/{coupon_id}")
async def update_coupon(
    coupon_id: str,
    payload: dict,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    coupon = await db.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    allowed = {"code", "discount_type", "value", "min_order", "max_uses", "expires_at", "is_active"}
    for key, val in payload.items():
        if key in allowed:
            if key == "code":
                val = str(val).upper()
            setattr(coupon, key, val)
    await db.commit()
    await db.refresh(coupon)
    return {"id": coupon.id, "code": coupon.code}


@router.delete("/{coupon_id}", status_code=204)
async def delete_coupon(
    coupon_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    coupon = await db.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    await db.delete(coupon)
    await db.commit()
