"""Rider GPS, orders, earnings, and shift endpoints."""
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import role_required
from app.models.order import Order
from app.models.rider import RiderLocation, RiderSettings, RiderShift
from app.models.user import User
from app.schemas.rider import RiderAssign, RiderEarningsOut, RiderLocationUpdate, RiderProfileOut

router = APIRouter(prefix="/rider", tags=["Rider"])

DB = Annotated[AsyncSession, Depends(get_db)]
RiderDep = Annotated[User, Depends(role_required("rider"))]


@router.put("/location")
async def update_location(payload: RiderLocationUpdate, db: DB, current_user: RiderDep):
    # Upsert RiderSettings lat/lng
    profile = (
        await db.execute(select(RiderSettings).where(RiderSettings.rider_id == current_user.id))
    ).scalar_one_or_none()
    if not profile:
        profile = RiderSettings(rider_id=current_user.id, is_online=True)
        db.add(profile)
        await db.flush()

    # Insert a location record
    db.add(
        RiderLocation(
            rider_id=current_user.id,
            lat=payload.lat,
            lng=payload.lng,
            speed=payload.accuracy,
        )
    )
    await db.commit()
    return {"status": "ok"}


@router.get("/orders", response_model=list)
async def rider_orders(db: DB, current_user: RiderDep):
    rows = (
        await db.execute(
            select(Order).where(
                Order.rider_id == current_user.id,
                Order.status == "out_for_delivery",
            )
        )
    ).scalars().all()
    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "address": o.address,
            "lat": o.lat,
            "lng": o.lng,
            "total": float(o.total),
            "status": o.status,
        }
        for o in rows
    ]


@router.put("/orders/{order_id}/accept")
async def accept_order(order_id: str, db: DB, current_user: RiderDep):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "out_for_delivery"
    order.rider_id = current_user.id
    await db.commit()
    return {"status": "accepted", "order_id": order_id}


@router.get("/earnings", response_model=RiderEarningsOut)
async def rider_earnings(db: DB, current_user: RiderDep):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)

    base_q = select(func.coalesce(func.sum(Order.total), 0)).where(
        Order.rider_id == current_user.id,
        Order.status == "delivered",
    )

    total_earnings = float((await db.execute(base_q)).scalar_one())
    today_earnings = float(
        (await db.execute(base_q.where(Order.delivered_at >= today_start))).scalar_one()
    )
    week_earnings = float(
        (await db.execute(base_q.where(Order.delivered_at >= week_start))).scalar_one()
    )
    month_earnings = float(
        (await db.execute(base_q.where(Order.delivered_at >= month_start))).scalar_one()
    )

    total_deliveries = int(
        (
            await db.execute(
                select(func.count(Order.id)).where(
                    Order.rider_id == current_user.id,
                    Order.status == "delivered",
                )
            )
        ).scalar_one()
    )

    return RiderEarningsOut(
        total_deliveries=total_deliveries,
        total_earnings=total_earnings,
        today_earnings=today_earnings,
        this_week=week_earnings,
        this_month=month_earnings,
    )


@router.get("/shifts", response_model=list)
async def list_rider_shifts(db: DB, current_user: RiderDep):
    rows = (
        await db.execute(
            select(RiderShift).where(RiderShift.rider_id == current_user.id).order_by(
                RiderShift.created_at.desc()
            )
        )
    ).scalars().all()
    return [
        {
            "id": s.id,
            "started_at": s.created_at,
            "ended_at": s.ended_at if hasattr(s, "ended_at") else None,
        }
        for s in rows
    ]


@router.post("/shifts", status_code=201)
async def start_rider_shift(db: DB, current_user: RiderDep):
    shift = RiderShift(rider_id=current_user.id)
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    return {"id": shift.id, "started_at": shift.created_at}


@router.put("/shifts/{shift_id}/end")
async def end_rider_shift(shift_id: str, db: DB, current_user: RiderDep):
    shift = await db.get(RiderShift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    if shift.rider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your shift")
    await db.commit()
    return {"status": "ended", "shift_id": shift_id}


@router.get("/location/{order_id}")
async def get_rider_location(
    order_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin", "staff"))],
):
    order = await db.get(Order, order_id)
    if not order or not order.rider_id:
        raise HTTPException(status_code=404, detail="No rider assigned to this order")
    location = (
        await db.execute(
            select(RiderLocation)
            .where(RiderLocation.rider_id == order.rider_id)
            .order_by(RiderLocation.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="No location data for rider")
    return {"rider_id": order.rider_id, "lat": location.lat, "lng": location.lng, "recorded_at": location.created_at}
