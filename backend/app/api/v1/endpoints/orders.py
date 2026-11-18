"""Order management endpoints."""
from datetime import datetime, timezone
from io import BytesIO
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, role_required
from app.models.loyalty import Coupon
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, StatusUpdate
from app.services.receipt_service import generate_receipt_pdf
from app.services.websocket_manager import manager

router = APIRouter(prefix="/orders", tags=["Orders"])

DB = Annotated[AsyncSession, Depends(get_db)]


async def _next_order_number(db: AsyncSession) -> int:
    result = await db.execute(select(func.max(Order.order_number)))
    current = result.scalar_one_or_none()
    return (current or 0) + 1


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(payload: OrderCreate, db: DB):
    # Compute subtotal
    subtotal = sum(item.quantity * item.price for item in payload.items)
    discount = payload.discount_amount or 0.0

    # Validate coupon
    if payload.coupon_code:
        coupon = (
            await db.execute(
                select(Coupon).where(Coupon.code == payload.coupon_code, Coupon.is_active.is_(True))
            )
        ).scalar_one_or_none()
        if coupon:
            if float(coupon.min_order) <= subtotal:
                if coupon.discount_type == "percent":
                    discount = subtotal * float(coupon.value) / 100
                else:
                    discount = float(coupon.value)
                coupon.used_count = (coupon.used_count or 0) + 1

    delivery_charges = payload.delivery_charges or 0.0
    total = subtotal - discount + delivery_charges
    order_number = await _next_order_number(db)

    order = Order(
        order_number=order_number,
        customer_name=payload.customer_name or "Guest",
        customer_phone=payload.customer_phone or "",
        address=payload.customer_address,
        lat=payload.delivery_lat,
        lng=payload.delivery_lng,
        order_type=payload.order_type,
        source=payload.source,
        payment_method=payload.payment_method,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_charges,
        total=total,
        coupon_code=payload.coupon_code,
        notes=payload.notes,
        status="pending",
    )
    db.add(order)
    await db.flush()

    for item in payload.items:
        db.add(
            OrderItem(
                order_id=order.id,
                food_id=item.food_id,
                name=item.title,
                unit_price=item.price,
                quantity=item.quantity,
                line_total=item.price * item.quantity,
            )
        )

    await db.commit()
    await db.refresh(order)

    # Broadcast to POS and kitchen channels
    await manager.broadcast("pos", {"event": "new_order", "order_id": order.id, "order_number": order_number})
    await manager.broadcast("kitchen", {"event": "new_order", "order_id": order.id, "order_number": order_number})

    return order


@router.get("", response_model=list[OrderOut])
async def list_orders(
    db: DB,
    _: Annotated[User, Depends(role_required("admin", "staff"))],
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
):
    q = select(Order)
    if status:
        q = q.where(Order.status == status)
    if source:
        q = q.where(Order.source == source)
    rows = (await db.execute(q.order_by(Order.created_at.desc()).offset(skip).limit(limit))).scalars().all()
    return rows


@router.get("/my", response_model=list[OrderOut])
async def my_orders(
    db: DB,
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0),
    limit: int = Query(20),
):
    q = select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    rows = (await db.execute(q.offset(skip).limit(limit))).scalars().all()
    return rows


@router.get("/active-delivery", response_model=list[OrderOut])
async def active_delivery(
    db: DB,
    current_user: Annotated[User, Depends(role_required("rider"))],
):
    rows = (
        await db.execute(
            select(Order).where(
                Order.rider_id == current_user.id,
                Order.status == "out_for_delivery",
            )
        )
    ).scalars().all()
    return rows


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: str,
    db: DB,
    current_user: Annotated[User, Depends(get_current_user)],
):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    roles = [r.role for r in current_user.roles] if current_user.roles else []
    if order.user_id != current_user.id and not any(r in roles for r in ("admin", "staff")):
        raise HTTPException(status_code=403, detail="Access denied")
    return order


@router.put("/{order_id}/status", response_model=OrderOut)
async def update_status(
    order_id: str,
    payload: StatusUpdate,
    db: DB,
    current_user: Annotated[User, Depends(role_required("admin", "staff", "rider"))],
):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = payload.status
    if payload.status == "delivered":
        order.delivered_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(order)
    await manager.broadcast(
        "pos",
        {"event": "status_update", "order_id": order.id, "status": order.status},
    )
    return order


@router.delete("/{order_id}", status_code=204)
async def cancel_order(
    order_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "cancelled"
    await db.commit()


@router.get("/{order_id}/invoice")
async def get_invoice(
    order_id: str,
    db: DB,
    current_user: Annotated[User, Depends(get_current_user)],
):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    pdf_bytes = await generate_receipt_pdf(order, order.items)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=invoice-{order_id[-8:]}.pdf"},
    )
